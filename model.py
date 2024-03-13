# %% [markdown]
# # Machine Learning
# 
# Das Modell soll vorhersagen, wer am wahrscheinlichsten der Autor bestimmter Sätze sein soll. Dafür werden vom Nutzer zunächst relevante Autoren ausgewählt und anschließend eine Eingabe des zu prüfenden Satzes oder Ausdrucks gemacht. Für das Modell wird ein Naive-Bayes Algorithmus auf einen Count Vectorizer verwendet.

# %%
import streamlit as st
import pandas as pd

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB

# %%
def analyze(data):
    df = pd.DataFrame()

    for i in data.values():
        df = pd.concat([df,i["data"]], ignore_index = True)                                                             # Daten in Dataframe überführen

    df = df.dropna()                                                                                                    # Missings entfernen

    vect = CountVectorizer()                                        

    wordsCountArray = vect.fit_transform(df["Satz"])                                                                    # Nach Wörtern vektorisieren
    


    X_train, X_test, y_train, y_test = train_test_split(wordsCountArray, df["Autor"], test_size=0.33, random_state=42)  # Trainingsdaten und Testdaten zuweisen

    model = MultinomialNB()                                                                                             # Verwendeter Naive Bayes Algorithmus

    model.fit(X_train, y_train)                                                                                         # Modell wird auf Daten trainiert
    
    autoren = data.keys()                                                                                               # Autoren werden in Variable übergeben

    s = f"Modell trainiert für Autoren: \n\n"                                                                           # Strings werden zeilenweise mitgeliefert zur Information über die Modelleigenschaften

    for i in autoren:                                                                                                   # Und via For-Schleife gelistet
        s += f"\t{i}\n"

    s += f"Mit {X_train.shape[0]} Sätzen.\n\n"                                                                          # Anzahl der Sätze für Trainingsdaten
    s += f"Modellgenauigekeit: {model.score(X_test, y_test)*100: .2f}%"                                                 # Modellgenauigkeit wird ausgegeben

    st.markdown(s)

    return model, vect