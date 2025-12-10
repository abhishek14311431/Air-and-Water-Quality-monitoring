import streamlit as st
import joblib
import pandas as pd
import numpy as np
import os
import requests
import plotly.express as px
from utils import get_air_quality_for_city
from streamlit.components.v1 import html


# -----------------------------------------------------
# PAGE CONFIG
# -----------------------------------------------------
st.set_page_config(
    page_title="Air & Water Quality Monitoring",
    page_icon="🌍",
    layout="wide"
)

# -----------------------------------------------------
# FUNCTION TO RENDER LOTTIE FROM URL (HTML METHOD)
# -----------------------------------------------------
def st_lottie(url: str, height: int = 200):
    html(
        f"""
        <script src="https://unpkg.com/@lottiefiles/lottie-player@latest/dist/lottie-player.js"></script>
        <lottie-player 
            src="{url}" 
            background="transparent" 
            speed="1" 
            style="width: 100%; height: {height}px;" 
            loop 
            autoplay>
        </lottie-player>
        """,
        height=height,
    )


# -----------------------------------------------------
# LOTTIE ANIMATION URLS
# -----------------------------------------------------
solar_url = "https://lottie.host/e0e7c9d9-ae3f-4b4a-b566-5ad240b40858/4oWjXLkb44.json"
air_url = "https://lottie.host/597ad4e2-202d-4cff-bf9d-8fbfeba2aede/1QWohG7m3E.json"
water_url = "https://lottie.host/df96b6ac-292b-4525-b315-36f3e30dbd38/gTxKN3U5UD.json"


# -----------------------------------------------------
# HEADER WITH SOLAR ANIMATION
# -----------------------------------------------------
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st_lottie(solar_url, height=220)

st.title("🌍 Air & Water Quality Monitoring Dashboard")
st.write("Real-time environmental monitoring with predictions, indicators and animations.")


# -----------------------------------------------------
# LOAD WATER DATA
# -----------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
water_data_path = os.path.join(BASE_DIR, "data", "water_quality_cities.csv")
df_water = pd.read_csv(water_data_path)

CITY_ALIASES = {
    "bangalore": "bengaluru",
    "banglore": "bengaluru",
    "bombay": "mumbai"
}


# -----------------------------------------------------
# HELPER FUNCTIONS
# -----------------------------------------------------
def map_air_label(x):
    return {0: "Good", 1: "Moderate", 2: "Poor"}.get(x)

def map_water_label(x):
    return "Drinkable" if x == 1 else "Not Drinkable"

def get_color_icon(val, low, med, high):
    if val <= low:
        return "🟢"
    elif val <= med:
        return "🟡"
    else:
        return "🔴"


# =====================================================
# 🌫️ AIR QUALITY SECTION
# =====================================================
st.header("🌫️ Air Quality")

air_c1, air_c2 = st.columns([1, 5])
with air_c1:
    st_lottie(air_url, height=130)

with air_c2:
    city_air = st.text_input("Enter a city for Air Quality")

if st.button("Fetch Air Quality", type="primary"):
    try:
        fixed_city = CITY_ALIASES.get(city_air.lower().strip(), city_air)
        data = get_air_quality_for_city(fixed_city)

        st.subheader(f"Pollutant Levels in {fixed_city.title()}")

        limits = {
            "pm2_5": (30, 60, 90),
            "pm10": (50, 100, 150),
            "no2": (40, 80, 180),
            "so2": (20, 80, 380),
            "o3": (50, 100, 200),
            "co": (200, 400, 1000),
        }

        cols = st.columns(3)
        keys = list(data.keys())

        for i in range(len(keys)):
            pollutant = keys[i]
            value = data[pollutant]

            low, med, high = limits[pollutant]
            icon = get_color_icon(value, low, med, high)
            cols[i % 3].metric(f"{icon} {pollutant.upper()}", value)

        # Model prediction
        model_air = joblib.load(os.path.join(BASE_DIR, "models", "air_quality_model.pkl"))
        prediction_raw = model_air.predict([[*data.values()]])[0]
        prediction_label = map_air_label(prediction_raw)

        st.subheader(f"Air Quality Category: {prediction_label}")

        if prediction_label == "Good":
            st.success("🌿 Air is safe to breathe.")
        elif prediction_label == "Moderate":
            st.warning("😷 Moderate air — sensitive groups should use a mask.")
        else:
            st.error("🚨 Poor air quality — avoid going outside.")

    except Exception as e:
        st.error(str(e))


# =====================================================
# 💧 WATER QUALITY SECTION
# =====================================================
st.header("💧 Water Quality")

water_c1, water_c2 = st.columns([1, 5])
with water_c1:
    st_lottie(water_url, height=130)

with water_c2:
    city_water = st.text_input("Enter a city for Water Quality")

if st.button("Fetch Water Quality", type="secondary"):
    try:
        fixed_city2 = CITY_ALIASES.get(city_water.lower().strip(), city_water).title()

        if fixed_city2 not in df_water["City"].values:
            st.error("City not found in water dataset.")
        else:
            row = df_water[df_water["City"] == fixed_city2].iloc[0]
            ph, hardness, solids = row["pH"], row["Hardness"], row["Solids"]

            st.subheader(f"Water Parameters — {fixed_city2}")

            limits = {
                "pH": (6.5, 8.5, 9.5),
                "Hardness": (150, 300, 500),
                "Solids": (300, 600, 900),
            }

            params = [("pH", ph), ("Hardness", hardness), ("Solids", solids)]
            cols = st.columns(3)

            for i, (name, value) in enumerate(params):
                low, med, high = limits[name]
                icon = get_color_icon(value, low, med, high)
                cols[i].metric(f"{icon} {name}", value)

            model_water = joblib.load(os.path.join(BASE_DIR, "models", "water_quality_model.pkl"))
            pred_raw = model_water.predict([[ph, hardness, solids]])[0]
            pred_label = map_water_label(pred_raw)

            st.subheader(f"Water Quality: {pred_label}")

            if pred_label == "Drinkable":
                st.success("💧 Water is safe to drink.")
            else:
                st.error("🚱 Not safe — use filtered or bottled water.")

    except Exception as e:
        st.error(str(e))


# =====================================================
# 📊 CITY COMPARISON PIE CHART
# =====================================================
st.header("📊 Compare PM2.5 Across Cities")

city1 = st.text_input("City 1")
city2 = st.text_input("City 2")
city3 = st.text_input("City 3 (optional)")

if st.button("Compare Cities", type="primary"):
    try:
        cities = [city1, city2, city3]
        labels, values = [], []

        for c in cities:
            if c.strip():
                fixed = CITY_ALIASES.get(c.lower().strip(), c)
                pm = get_air_quality_for_city(fixed)["pm2_5"]
                labels.append(fixed.title())
                values.append(pm)

        df = pd.DataFrame({"City": labels, "PM2.5": values})
        fig = px.pie(df, names="City", values="PM2.5", title="City PM2.5 Comparison")
        st.plotly_chart(fig)

    except Exception as e:
        st.error(str(e))
