import requests
import streamlit as st


def get_air_quality_for_city(city_name: str):
    """
    Fetches:
      - Latitude & Longitude of the city
      - Air pollutant levels (PM2.5, PM10, NO2, SO2, O3, CO)
      - Weather data (Temperature, Humidity, Wind Speed)
    """

    # Load API key from Streamlit Secrets
    API_KEY = st.secrets.get("openweather_api_key")

    if not API_KEY:
        raise Exception("API Key not found. Please add `openweather_api_key` in secrets.toml")

    # ----------------------------------------------------
    # 1) GET LATITUDE & LONGITUDE OF CITY
    # ----------------------------------------------------
    geo_url = "https://api.openweathermap.org/geo/1.0/direct"
    geo_params = {"q": city_name, "limit": 1, "appid": API_KEY}

    geo_resp = requests.get(geo_url, params=geo_params)

    if geo_resp.status_code != 200:
        raise Exception("Failed to fetch city coordinates")

    geo_data = geo_resp.json()

    if not geo_data:
        raise ValueError(f"City '{city_name}' not found")

    lat = geo_data[0]["lat"]
    lon = geo_data[0]["lon"]

    # ----------------------------------------------------
    # 2) GET AIR POLLUTION DATA
    # ----------------------------------------------------
    air_url = "https://api.openweathermap.org/data/2.5/air_pollution"
    air_params = {"lat": lat, "lon": lon, "appid": API_KEY}

    air_resp = requests.get(air_url, params=air_params)

    if air_resp.status_code != 200:
        raise Exception("Failed to fetch air pollution data")

    air_data = air_resp.json()

    comp = air_data["list"][0]["components"]

    # ----------------------------------------------------
    # 3) GET WEATHER DATA (Temperature, Humidity, Wind)
    # ----------------------------------------------------
    weather_url = "https://api.openweathermap.org/data/2.5/weather"
    weather_params = {"lat": lat, "lon": lon, "appid": API_KEY, "units": "metric"}

    weather_resp = requests.get(weather_url, params=weather_params)

    if weather_resp.status_code != 200:
        raise Exception("Failed to fetch weather data")

    weather = weather_resp.json()

    temperature = weather["main"]["temp"]
    humidity = weather["main"]["humidity"]
    wind_speed = weather["wind"]["speed"]

    # ----------------------------------------------------
    # 4) RETURN ALL VALUES
    # ----------------------------------------------------
    return {
        "pm2_5": comp.get("pm2_5", 0),
        "pm10": comp.get("pm10", 0),
        "no2": comp.get("no2", 0),
        "so2": comp.get("so2", 0),
        "o3": comp.get("o3", 0),
        "co": comp.get("co", 0),
        "temp": temperature,
        "humidity": humidity,
        "wind": wind_speed,
    }
