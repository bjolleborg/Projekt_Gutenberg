#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 19 12:10:01 2023

@author: bjolleborg
"""

import streamlit as st
import pandas as pd
import requests

from bs4 import BeautifulSoup
from bs4.dammit import EncodingDetector

# Definiert die Base-Url, die nie verändert wird.
BASE_URL = "https://www.projekt-gutenberg.org/"

@st.cache_resource()
def scrape_author(author):
    '''
    Einzige Funktion die aufgerufen werden sollte. Alle anderen sind privat!
    Funktion erhält Namen des Autors und scraped alle Informationen über den 
    Autor von der Homepage https://www.projekt-gutenberg.org/
    Gescraped werden alle Sätze aller verfügbaren Werke, alle Bücher mit Url,
    biografische Informationen zum Autor und ein Foto des Autors.
    
    Parameters:
        autor (str): Der Name des Autors
    
    Returns:
        dic (dict): Ein Wörterbuch mit allen relevanten Informationen zum Autor
    '''
    
    # Generiert die autorenspezifische URL.
    url = f"{BASE_URL}autoren/namen/{author.lower()}.html"
    
    print(f"Scrape Autor {author} {url}")
    res = requests.get(url)
    
    # Prüft, ob der Autor gefunden wurde.
    if res.status_code != 200:
        print(f"Autor {author} wurde nicht gefunden!")
        return None
    
    try:
        print(f"Autor {author} wurde gefunden!")
        author_site = BeautifulSoup(res.content, "lxml", from_encoding = EncodingDetector.find_declared_encoding(res.content, is_html = True))
    
    except Exception:
        print("Error während dem Decoden")
        return None
    
    # Dict mit gescrapten Informationen wird angelegt.
    infos = {"data"      : None,
            "books"      : _find_books(author_site),
            "info"       : _find_info(author_site),
            "image_url"  : _find_image(author_site)
            }
    
    # Dataframe, in die die gescrapten Sätze geschrieben werden.
    df_all = pd.DataFrame()

    # Text aller Bücher
    for title, url in infos["books"]:  

        st.markdown(f"[{title}]({url})")
        print(f"Scrape Buch '{title}' [{url}]")

        # Das Buch scrapen
        df_temp = _scrape_book(url)

        # Die Dataframes kombinieren            
        df_all = pd.concat([df_all,df_temp], ignore_index=True)
            
    df_all["Autor"] = author.upper()
    
    infos["data"] = df_all
    
    print(f"Gefundene Sätze: {df_all.shape}")
    
    return infos

# Bücher eines Autoren werden gescraped.
def _find_books(books):
    '''
    Scraped die Titel und url der Bücher des gesuchten Autoren
    
    Parameters:
        books (str): Der HTML-Code der Bücher, die vom Autor geschrieben sind

    Returns:
        Alle Paragraphe oder None
    '''
    
    tag = books.find("div", {"class": "archived"})
    
    if tag == None:
        return []
    
    book_url = []
    
    for l in tag.find_all("li"):
        
        tag = l.find("a", href = True)
        book_title = tag.string
        
        url = f"{BASE_URL}{tag['href'][6:]}"
        url = url[:url.rfind("/")]
                
        book_url.append((book_title, url))
        
    return book_url


def _find_info(author_site):
    '''
    Sucht Informationen zur Biografie des Autors und gibt sie als String aus.
    
    Parameters:
        author_site (str): Der HTML-Code der Informationen des Autors
        
    Returns:
        Ersten Absatz der Biografie oder None    
    '''
    
    try:
        tag = author_site.find_all("p")
        for p in tag:
            if p.text != '\xa0':
                return p.text
    except:
        return None
    

def _find_image(author_site):
    '''
    Lädt die Url des Bildes des Autoren, falls vorhanden.
    
    Parameters:
        author_site (str): Der HTML-Code der Informationen des Autors
    
    Returns:
        Url des Autorenbildes oder None.
    '''
    try:
        return f"{BASE_URL}autoren{author_site.find('img', src = True, title = True)['src'][2:]}"
    
    except:
        return None
    

def _scrape_book(url):
    '''
    Scraped alle verfügbaren Bücher des Autoren Satz für Satz.
    
    Parameters:
        url (str): Url der Seite mit dem Überblick über alle Werke des Autoren
        
    Returns:
        Alle gescrapten Sätze des Autoren.
    '''
    res = requests.get(url) 

    book_site = BeautifulSoup(res.content, 'lxml', from_encoding=EncodingDetector.find_declared_encoding(res.content, is_html=True))

    subchapters = book_site.find_all("li")
    
    print(f"\tAnzahl Unterkapitel: {len(subchapters)}")

    subchapters_links = []
  
    for sub in subchapters:
        link = sub.find("a", href=True)
        subchapters_links.append(url + "/" + link["href"]) 
    
    df = pd.DataFrame(columns=["Satz"])
    
    progressbar = st.progress(0)
    
    for index, temp_url in enumerate(subchapters_links):

        # Zeige die Progressbar an
        progressbar.progress((index+1)/len(subchapters_links))

        res = requests.get(temp_url) 
        books = BeautifulSoup(res.content, 'lxml', from_encoding=EncodingDetector.find_declared_encoding(res.content, is_html=True))

        data = _find_text(books)
        
        for satz in data.split("."):
            df.loc[len(df)] = satz

    # Löschen der ProgressBar
    progressbar.empty()    
    
    df["Satz"] = df["Satz"].map(_correction).dropna()
    
    return df

def _correction(string):
    '''
    Kürzt kurze Sätze mit weniger als 4 Zeichen aus den gescrapten Sätzen heraus
    
    Parameters:
        string (str): Der gescrapte Satz
    
    Retruns:
        Den Satz mit mindestens 4 Zeichen oder None
    '''
    if len(string) < 4:
        return None
    else:
        return string


def _find_text(chapter):
    text = ""
    
    for paragraph in chapter.find_all("p"):
        if paragraph.string:
            text = text + paragraph.text
            
    return text



