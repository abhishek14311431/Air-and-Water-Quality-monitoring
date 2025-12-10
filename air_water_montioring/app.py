import streamlit as st
import joblib
import pandas as pd
import numpy as np
import os
import requests
import plotly.express as px
from utils import get_air_quality_for_city
from streamlit_lottie import st_lottie


# -----------------------------------------------------
# PAGE SETTINGS
# -----------------------------------------------------
st.set_page_config(
    page_title="Air & Water Quality Monitoring",
    page_icon="🌍",
    layout="wide",
)


# -----------------------------------------------------
# FUNCTION TO LOAD LOTTIE ANIMATIONS FROM URL
# -----------------------------------------------------
def load_lottie_url(url: str):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
        else:
            return None
    except:
        return None


# -----------------------------------------------------
# LOTTIE ANIMATIONS (URL BASED)
# -----------------------------------------------------
solar_anim = load_lottie_url(
    "https://lottie.host/e0e7c9d9-ae3f-4b4a-b566-5ad240b40858/4oWjXLkb44.json"
)

air_anim = load_lottie_url(
    "https://lottie.host/597ad4e2-202d-4cff-bf9d-8fbfeba2aede/1QWohG7m3E.json"
)

water_anim = load_lottie_url(
    "https://lottie.host/df96b6ac-292b-4525-b315-36f3e30dbd38/gTxKN3U5UD.json"
)


# -----------------------------------------------------
# HEADER WITH SOLAR ANIMATION
# -----------------------------------------------------
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st_lottie(solar_anim, height=220)

st.title("🌍 Air & Water Quality Monitoring Dashboard")
st.write("Real-time environmental monitoring with predictions and indicators.")


# -----------------------------------------------------
# LOAD WATER DATA
# -----------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
water_csv_path = os.path.join(BASE_DIR, "data", "water_quality_cities.csv")
df_water = pd.read_csv(water_csv_path)

CITY_ALIASES = {
    "bangalore": "bengaluru",
    "banglore": "bengaluru",
    "bombay": "mumbai",
}


# -----------------------------------------------------
# HELPERS
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

left, right = st.columns([1, 5])
with left:
    st_lottie(air_anim, height=130)
with right:
    city = st.text_input("Enter a city name for Air Quality")

if st.button("Fetch Air Quality", type="primary"):
    try:
        proper_city = CITY_ALIASES.get(city.lower().strip(), city)
        data = get_air_quality_for_city(proper_city)

        st.subheader(f"Pollutant Levels in {proper_city.title()}")

        # thresholds
        limits = {
            "pm2_5": (30, 60, 90),
            "pm10": (50, 100, 150),
            "no2": (40, 80, 180),
            "so2": (20, 80, 380),
            "o3": (50, 100, 200),
            "co": (200, 400, 1000),
        }

        cols = st.columns(3)
        for i, (name, value) in enumerate(data.items()):
            low, med, high = limits[name]
            icon = get_color_icon(value, low, med, high)
            cols[i % 3].metric(f"{icon} {name.upper()}", value)

        # prediction
        model = joblib.load(os.path.join(BASE_DIR, "models", "air_quality_model.pkl"))
        pred_raw = model.predict([[*data.values()]])[0]
        pred_label = map_air_label(pred_raw)

        st.subheader(f"Air Quality Category: {pred_label}")

        if pred_label == "Good":
            st.success("🌿 Air quality is good.")
        elif pred_label == "Moderate":
            st.warning("😷 Air quality is moderate.")
        else:
            st.error("🚨 Poor air quality! Avoid going outside.")

    except Exception as e:
        st.error(str(e))


# =====================================================
# 💧 WATER QUALITY SECTION
# =====================================================
st.header("💧 Water Quality")

left2, right2 = st.columns([1, 5])
with left2:
    st_lottie(water_anim, height=130)
with right2:
    city2 = st.text_input("Enter a city name for Water Quality")

if st.button("Fetch Water Quality", type="secondary"):
    try:
        c2 = CITY_ALIASES.get(city2.lower().strip(), city2).title()

        if c2 not in df_water["City"].values:
            st.error("City not found in water dataset.")
        else:
            row = df_water[df_water["City"] == c2].iloc[0]
            ph, hardness, solids = row["pH"], row["Hardness"], row["Solids"]

            st.subheader(f"Water Parameters — {c2}")

            limits = {
                "pH": (6.5, 8.5, 9.5),
                "Hardness": (150, 300, 500),
                "Solids": (300, 600, 900),
            }

            params = [("pH", ph), ("Hardness", hardness), ("Solids", solids)]
            cols = st.columns(3)

            for i, (name, val) in enumerate(params):
                low, med, high = limits[name]
                icon = get_color_icon(val, low, med, high)
                cols[i].metric(f"{icon} {name}", val)

            model_w = joblib.load(os.path.join(BASE_DIR, "models", "water_quality_model.pkl"))
            pred_raw = model_w.predict([[ph, hardness, solids]])[0]
            pred_label = map_water_label(pred_raw)

            st.subheader(f"Water Quality: {pred_label}")

            if pred_label == "Drinkable":
                st.success("💧 The water is safe to drink.")
            else:
                st.error("🚱 Not safe. Use filtered or bottled water.")

    except Exception as e:
        st.error(str(e))


# =====================================================
# 📊 CITY COMPARISON
# =====================================================
st.header("📊 Compare PM2.5 Across Cities")

cityA = st.text_input("City 1")
cityB = st.text_input("City 2")
cityC = st.text_input("City 3 (optional)")

if st.button("Compare"):
    try:
        cities = [cityA, cityB, cityC]
        valid_labels = []
        pm_values = []

        for c in cities:
            if c.strip():
                fixed = CITY_ALIASES.get(c.lower().strip(), c)
                pm = get_air_quality_for_city(fixed)["pm2_5"]
                valid_labels.append(fixed.title())
                pm_values.append(pm)

        df = pd.DataFrame({"City": valid_labels, "PM2.5": pm_values})
        fig = px.pie(df, names="City", values="PM2.5")
        st.plotly_chart(fig)

    except Exception as e:
        st.error(str(e))
