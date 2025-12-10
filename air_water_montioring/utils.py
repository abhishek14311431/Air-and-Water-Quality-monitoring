import requests
import streamlit as st
import pandas as pd
import os


# ----------------------------------------------------
# 🌫️ FETCH AIR QUALITY FROM OPENWEATHER (LIVE)
# ----------------------------------------------------
def get_air_quality_for_city(city_name: str):
    """
    Returns pollutant values for a given city using OpenWeather API.
    Output = dict with pm2_5, pm10, no2, so2, o3, co
    """

    API_KEY = st.secrets.get("openweather_api_key")

    if not API_KEY:
        raise Exception("API Key missing! Add it in streamlit secrets as openweather_api_key")

    # ----------------------------------------------------
    # 1️⃣ GET LAT + LON FOR THE CITY
    # ----------------------------------------------------
    geo_url = "https://api.openweathermap.org/geo/1.0/direct"
    geo_params = {"q": city_name, "limit": 1, "appid": API_KEY}

    geo_resp = requests.get(geo_url, params=geo_params)
    geo_data = geo_resp.json()

    if not geo_data:
        raise ValueError(f"City '{city_name}' not found")

    lat = geo_data[0]["lat"]
    lon = geo_data[0]["lon"]

    # ----------------------------------------------------
    # 2️⃣ GET AIR POLLUTION DATA
    # ----------------------------------------------------
    air_url = "https://api.openweathermap.org/data/2.5/air_pollution"
    air_params = {"lat": lat, "lon": lon, "appid": API_KEY}

    air_resp = requests.get(air_url, params=air_params)
    air_data = air_resp.json()

    comp = air_data["list"][0]["components"]

    return {
        "pm2_5": comp.get("pm2_5", 0),
        "pm10": comp.get("pm10", 0),
        "no2": comp.get("no2", 0),
        "so2": comp.get("so2", 0),
        "o3": comp.get("o3", 0),
        "co": comp.get("co", 0),
    }


# ----------------------------------------------------
# 💧 LOAD WATER DATASET (9 FEATURES)
# ----------------------------------------------------
def load_water_dataset():
    """
    Loads the water quality dataset from the /data folder.
    """
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(BASE_DIR, "data", "water_quality_cities.csv")

    if not os.path.exists(path):
        raise FileNotFoundError("water_quality_cities.csv not found in /data folder")

    df = pd.read_csv(path)
    return df
