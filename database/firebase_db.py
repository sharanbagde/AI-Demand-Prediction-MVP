import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st
import os

if not firebase_admin._apps:
    try:
        # Cloud (Streamlit)
        cred = credentials.Certificate(dict(st.secrets["firebase"]))
    except:
        # Local (your PC)
        base_dir = os.path.dirname(os.path.dirname(__file__))
        json_path = os.path.join(base_dir, "firebase_key.json")
        cred = credentials.Certificate(json_path)

    firebase_admin.initialize_app(cred)

db = firestore.client()

def save_prediction(data):
    db.collection("predictions").add(data)