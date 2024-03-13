# %% [markdown]
# # Gutenberg Projekt

# %%
import streamlit as st
import pandas as pd
import requests

from bs4 import BeautifulSoup
from bs4.dammit import EncodingDetector

# %%
BASE_URL = "https://www.projekt-gutenberg.org" # Ausgangswebsite

# %% [markdown]
# ## Fehlerselektion innerhalb der Texte

# %%
def _correction(string):
    if len(string) < 4:                         # Filtert alles was nach einem Punkt kommt und unter 4 Zeichen hat. (Fehleranfälligkeit vermeiden, Machine Learning optimieren)
        return None
    else:
        return string

# %% [markdown]
# ## Scraping des Portraits

# %%
def _find_image(author_site):                   # Link zum Bild scrapen
    try:
        return f"{BASE_URL}/autoren/{author_site.find('img', src = True, title = True)['src'][3:]}" 
    except:
        return None

# %% [markdown]
# ## Scraping der Biografie des Autors

# %%
def _find_info(author_site):
    try:
        return author_site.find("p").text       # Erster Absatz der Biografie scrapen
    except:
        return None

# %% [markdown]
# ## Scraping der Autoreninformationen

# %%
# Unterdrückt Warn- und Fehlermeldungen in der Streamlit App
@st.cache(suppress_st_warning=True)
# Funktion zum Scrapen des Autors
def scrape_autor(author):                       
    url = f"{BASE_URL}/autoren/namen/{author.lower()}.html"
    print(f"Scrape Autor {author} [{url}]")

    res = requests.get(url)

# Autor nicht gefunden
    if res.status_code != 200:
        print(f"Autor {author} wurde nicht gefunden!")
        return None
    try:
        print(f"Autor {author} wurde gefunden!")

# Soll nicht xml für das encoding verwenden
        
        author_site = BeautifulSoup(res.content, "lxml", from_encoding=EncodingDetector.find_declared_encoding(res.content, is_html=True))
    except Exception:
        print("Error während dem Decoden")
        return None

# Dictionary mit allen Informationen über den Autor
    infos = {"data"      : None,    # Texte
             "books"     : _find_books(author_site),     # Bücher
             "info"      : _find_info(author_site),     # Biografie
             "image_url" : _find_image(author_site)     # Bild
            }
    df_all = pd.DataFrame()

# Über jeden Autoren iterieren und dessen Werke mitsamt URL printen
    for title, url in infos["books"]:

        st.markdown(f"[{title}]({url})")
        print(f"Scrape Buch '{title}' [{url}]")

# Buch scrapen
        df_temp = _scrape_book(url)

# Dataframes kombinieren
        df_all = pd.concat([df_all, df_temp],ignore_index=True) 
    
    df_all["Autor"] = author.upper()
    infos["data"] = df_all

    print(f"Gefundene Sätze: {df_all.shape}")

    return infos

# %% [markdown]
# ## Scraping des Buchtexts

# %%
def _find_text(books):
    text = ""
    
    for paragraph in books.find_all("p"):
        if paragraph.string:
            text = text + paragraph.text

    return text

# %% [markdown]
# ## Scraping aller Werke des Autors

# %%
def _find_books(books):
    tag = books.find("div",{"class": "archived"}) # Abfrage unter den jeweiligen HTML-Divisions
    if tag == None:
        return []
    book_url = []
    for l in tag.find_all("li"):                  # Abfrage der Listenelemente
        tag = l.find("a", href = True)
        book_title = tag.string                   # Abfrage der genauen Buchtitel
        
        url = f"{BASE_URL}/{tag['href'][6:]}"     # Abfrage der genauen URL 
        url = url[:url.rfind("/")]   

        book_url.append((book_title, url))        # Kombination von Butitel und URL in Tuples

    return book_url
    

# %% [markdown]
# ## Scraping des Buches

# %%
def _scrape_book(url):
    res = requests.get(url)
    book_site = BeautifulSoup(res.content, "lxml", from_encoding=EncodingDetector.find_declared_encoding(res.content, is_html=True))
    subchapters = book_site.find_all("li")
    subchapters_links = []
    for sub in subchapters:
        link = sub.find("a", href = True)
        subchapters_links.append(url + "/" + link["href"])          # Alle Unterkapitel werden gescraped zu einem gegebenen book_link
    
    df = pd.DataFrame(columns = ['Satz'])
    
    progressbar = st.progress(0)                                    # Fortschrittsbalken in Streamlit
    
    for index, temp_url in enumerate(subchapters_links):
        progressbar.progress((index + 1 ) / len(subchapters_links))

        res = requests.get(temp_url)
        
        books = BeautifulSoup(res.content, "lxml", from_encoding=EncodingDetector.find_declared_encoding(res.content, is_html=True))
        data = _find_text(books)

        for satz in data.split("."):                                # Scrapen der einzelnen Sätze
            df.loc[len(df)] = satz
    progressbar. empty()

    df["Satz"] = df["Satz"].map(_correction)                        # Filterfunktion der Sätze

    return df


