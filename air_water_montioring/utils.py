import requests
import json

def load_api_key(service_name: str) -> str:
    with open("api_keys.json", "r") as f:
        keys = json.load(f)
    return keys[service_name]

def get_air_quality_for_city(city_name: str):
    api_key = load_api_key("openweather_api_key")
    
    geo_url = "https://api.openweathermap.org/geo/1.0/direct"
    geo_params = {
        "q": city_name,
        "limit": 1,
        "appid": api_key
    }

    geo_resp = requests.get(geo_url, params=geo_params)
    geo_data = geo_resp.json()

    if not geo_data:
        raise ValueError(f"City '{city_name}' not found")

    lat = geo_data[0]["lat"]
    lon = geo_data[0]["lon"]

    air_url = "https://api.openweathermap.org/data/2.5/air_pollution"
    air_params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key
    }

    air_resp = requests.get(air_url, params=air_params)
    air_data = air_resp.json()

    comp = air_data["list"][0]["components"]

    return {
        "pm2_5": comp["pm2_5"],
        "pm10": comp["pm10"],
        "no2": comp["no2"],
        "so2": comp["so2"],
        "o3": comp["o3"],
        "co": comp["co"]
    }

