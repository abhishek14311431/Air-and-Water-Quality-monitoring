import requests
import streamlit as st

def get_air_quality_for_city(city_name: str):
    API_KEY = st.secrets.get("openweather_api_key")

    if not API_KEY:
        raise Exception("API Key missing. Add it to secrets.toml")

    # -------- GET LAT & LON --------
    geo_url = "https://api.openweathermap.org/geo/1.0/direct"
    geo_params = {"q": city_name, "limit": 1, "appid": API_KEY}

    geo_resp = requests.get(geo_url, params=geo_params).json()
    if not geo_resp:
        raise ValueError(f"City '{city_name}' not found")

    lat = geo_resp[0]["lat"]
    lon = geo_resp[0]["lon"]

    # -------- GET AIR QUALITY DATA --------
    air_url = "https://api.openweathermap.org/data/2.5/air_pollution"
    air_params = {"lat": lat, "lon": lon, "appid": API_KEY}
    air_data = requests.get(air_url, params=air_params).json()

    comp = air_data["list"][0]["components"]

    pollutants = {
        "pm2_5": comp["pm2_5"],
        "pm10": comp["pm10"],
        "no2": comp["no2"],
        "so2": comp["so2"],
        "o3": comp["o3"],
        "co": comp["co"],
    }

    # -------- GET WEATHER DATA --------
    weather_url = "https://api.openweathermap.org/data/2.5/weather"
    weather_params = {"lat": lat, "lon": lon, "appid": API_KEY, "units": "metric"}

    weather_json = requests.get(weather_url, params=weather_params).json()

    weather = {
        "temp": weather_json["main"]["temp"],
        "humidity": weather_json["main"]["humidity"],
        "wind": weather_json["wind"]["speed"],
        "condition": weather_json["weather"][0]["main"],  # Clear / Clouds / Rain...
        "icon": weather_json["weather"][0]["icon"],        # Icon code
    }

    return pollutants, weather
