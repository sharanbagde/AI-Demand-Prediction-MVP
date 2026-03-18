import requests
import os
from dotenv import load_dotenv
import streamlit as st

# Load .env file
load_dotenv()

try:
    API_KEY = st.secrets["OPENWEATHER_API_KEY"]
except:
    API_KEY = os.getenv("OPENWEATHER_API_KEY")

def get_weather(city):

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

    response = requests.get(url)

    if response.status_code != 200:
        return None

    data = response.json()

    temperature = data["main"]["temp"]
    rainfall = data.get("rain", {}).get("1h", 0)
    is_rainy = 1 if rainfall > 0 else 0

    return temperature, rainfall, is_rainy