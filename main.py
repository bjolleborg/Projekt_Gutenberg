#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 20 16:43:10 2023

@author: bjolleborg
"""

import streamlit as st
from scraping import scrape_author
from analyzer import analyze


st.set_page_config(layout = "wide")


# Titel

st.header("[Projekt Gutenberg](https://www.projekt-gutenberg.org)")

col1, col2 = st.columns(2)


if "vect" not in st.session_state:
    st.session_state.vect = None

if "model" not in st.session_state:
    st.session_state.model = None
    
if "data" not in st.session_state:
    st.session_state.data = {}
    

autor = st.sidebar.text_input("Lade Autor:", value = "Goethe", help = "Der Nachname genügt").upper()

st.sidebar.markdown(("Durch die Verwendung der session_state werden die Daten eines Autoren nur einmal geladen. Bei nochmaliger Abfrage werden automatisch die schon existierenden Daten angezeigt."))

if st.sidebar.button("Starte Scraping...", help = "Lade die Daten von der Webseite."):
    if autor not in st.session_state.data.keys():
        data = scrape_author(autor)
        if data == None:
            st.error("Autor nicht gefunden. Prüfe Eingabe auf Tippfehler oder Autor nicht in Datenbank.")
        
        else:
            st.session_state.data[autor.upper()] = data
    else:
        print("Autor wurde schon geladen.")

if st.sidebar.button("Lösche Daten", help = "Löscht alle Daten", disabled = len(st.session_state.data.keys()) == 0):
    st.session_state.data = {}
    

with col1:
    
    if autor in st.session_state.data.keys():
        st.subheader("Biographie")
        st.write(st.session_state.data[autor.upper()]["info"])
        
        if st.session_state.data[autor.upper()]["image_url"]:
            st.image(st.session_state.data[autor.upper()]["image_url"])
        
        
        st.dataframe(st.session_state.data[autor.upper()]["data"], width = 600)
        st.subheader("Bücher")
        
        for b in st.session_state.data[autor.upper()]["books"]:
            st.markdown(f"[{b[0]}](b[1])")
            

with col2:
  
    selection = st.multiselect("Autoren", st.session_state.data.keys())

    analyse = st.button("Analysiere ausgewählte Autoren", help="Erstellt ein Modell mit den ausgewählten Autoren.")

    if analyse and selection!= []:
        m={}    

        for sel in selection:
            m[sel] = st.session_state.data[sel]
        
        if m!={}:
            st.session_state.model, st.session_state.vect = analyze(m)

    text = st.text_input("Wer hat es (wahrscheinlich) geschrieben?" )

    if st.session_state.model != None and st.session_state.vect != None:
        propas = st.session_state.model.predict_proba(st.session_state.vect.transform([text]))

        for i in range(len(st.session_state.model.classes_)):
            st.markdown(f"**{st.session_state.model.classes_[i]}**: {propas[0][i]*100:.2f} % ")