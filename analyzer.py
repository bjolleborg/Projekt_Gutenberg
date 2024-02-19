#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 20 16:42:07 2023

@author: bjolleborg
"""

import streamlit as st
import pandas as pd

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB


def analyze(data):
    df = pd.DataFrame()
    
    for i in data.values():
        df = pd.concat([df, i['data']], ignore_index = True)
    
    df = df.dropna()
    
    vect = CountVectorizer()
    
    wordsCountArray = vect.fit_transform(df['Satz'])
    
    X_train, X_test, y_train, y_test = train_test_split(wordsCountArray, df['Autor'], test_size=0.2, random_state=42)
    
    model = MultinomialNB()
    
    model.fit(X_train, y_train)
    
    autoren = data.keys()
    
    s = "Modell trainiert für Autoren: \n\n"
    
    for i in autoren:
        s += f"\t{i}\n"
        
    s += f"Mit {X_train.shape[0]} Sätzen.\n\n"
    
    s += f"Modelgenauigkeit: {model.score(X_test, y_test) * 100:.2f}%"
    
    st.markdown(s)
    
    return model, vect