# %% [markdown]
# # Streamlit App

# %%
import streamlit as st

from webscraper import scrape_autor
from model import analyze

# %% [markdown]
# ## Konfiguration

# %%
st.set_page_config(layout = "wide")                                                       # Layouting

# %% [markdown]
# ## Titel

# %%
st.header("[Projekt Gutenberg](https://www.projekt-gutenberg.org/)")

# %% [markdown]
# ## Sidebar

# %%
col1, col2 = st.columns(2)

if "vect" not in st.session_state:
    st.session_state.vect = None

if "model" not in st.session_state:
    st.session_state.model = None

if "data" not in st.session_state:
    st.session_state.data = {}

autor = st.sidebar.text_input("Welche*r Autor*in interessiert dich?", value = "Kafka", help = "Der Nachname ist ausreichend.").upper()

st.sidebar.markdown("""Durch die Verwendung der [session_state](https://docs.streamlit.io/library/api-reference/session-state) werden die Daten der Person nur **einmal** gescrapt. Bei erneuter Abfrage werden automatisch die schon existierenden Daten geladen.""")

if st.sidebar.button("Starte Scraping...", help = "Extrahiert sämtliche Werke der genannten Person."):
    if autor not in st.session_state.data.keys():
        data = scrape_autor(autor)

        if data == None:
            st.error("Abfrage fehlerhaft, sorry!")
        
        else:
            st.session_state.data[autor.upper()] = data

    else:
        print("Daten sind bereits vorhanden!")


if st.sidebar.button("Lösche Daten", disabled = len(st.session_state.data.keys())==0, help=f"Löscht alle extrahierten Daten"):
    st.session_state.data = {}

    

# %% [markdown]
# ## Columns

# %%
with col1:
    if autor in st.session_state.data.keys():
        st.subheader("Biographie")
        st.write(st.session_state.data[autor.upper()]["info"])

        if st.session_state.data[autor.upper()]["image_url"]:
            st.image(st.session_state.data[autor.upper()]["image_url"])

        st.dataframe(st.session_state.data[autor.upper()]["data"], width = 600)
        st.subheader("Bücher")
        for b in st.session_state.data[autor.upper()]["books"]:
            st.markdown(f"[{b[0]}]({b[1]})")
    
    with col2:
        selection = st.multiselect("Autoren",st.session_state.data.keys())
        analyse = st.button("Analysiere die Autoren", help = "Analysiert Autoren")
        if analyse and selection != []:
            m = {}

            for sel in selection:
                m[sel] = st.session_state.data[sel]
            
            if m != {}:
                st.session_state.model, st.session_state.vect = analyze(m)

        text = st.text_input("Wer hat es (wahrscheinlich) geschrieben?")

        if st.session_state.model != None and st.session_state.vect != None:                     
            prob = st.session_state.model.predict_proba(st.session_state.vect.transform([text]))

            for i in range(len(st.session_state.model.classes_)):
                st.markdown(f"**{st.session_state.model.classes_[i]}**: {prob[0][i]*100: .2f} %")




