import streamlit as st
import joblib
import pandas as pd
import numpy as np
import json
import os
import plotly.express as px
from streamlit_lottie import st_lottie
from utils import get_air_quality_for_city

# -----------------------------------------------------
# PAGE SETTINGS
# -----------------------------------------------------
st.set_page_config(
    page_title="Air & Water Quality Monitoring",
    page_icon="🌍",
    layout="wide",
)

# -----------------------------------------------------
# LOAD LOTTIE ANIMATIONS
# -----------------------------------------------------
def load_lottie(path):
    with open(path, "r") as f:
        return json.load(f)

solar_anim = load_lottie("animations/solar.json")
air_anim = load_lottie("animations/air.json")
water_anim = load_lottie("animations/water.json")

# -----------------------------------------------------
# HEADER WITH SOLAR ANIMATION
# -----------------------------------------------------
colA, colB, colC = st.columns([1, 2, 1])
with colB:
    st_lottie(solar_anim, height=230)

st.title("🌍 Air & Water Quality Monitoring Dashboard")
st.write("Real-time monitoring with predictions, animations, and pollutant indicators.")


# -----------------------------------------------------
# LOAD WATER DATA
# -----------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
water_path = os.path.join(BASE_DIR, "data", "water_quality_cities.csv")
df_water = pd.read_csv(water_path)

CITY_ALIASES = {"bangalore": "bengaluru", "banglore": "bengaluru", "bombay": "mumbai"}


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

col_icon, col_text = st.columns([1, 5])
with col_icon:
    st_lottie(air_anim, height=120)
with col_text:
    city = st.text_input("Enter a City for Air Quality")

if st.button("Fetch Air Quality", type="primary"):
    try:
        c = CITY_ALIASES.get(city.lower().strip(), city)
        data = get_air_quality_for_city(c)

        st.subheader(f"Pollutant Levels in {c.title()}")

        limits = {
            "pm2_5": (30, 60, 90),
            "pm10": (50, 100, 150),
            "no2": (40, 80, 180),
            "so2": (20, 80, 380),
            "o3": (50, 100, 200),
            "co": (200, 400, 1000),
        }

        cols = st.columns(3)
        for i, (name, val) in enumerate(data.items()):
            low, med, high = limits[name]
            icon = get_color_icon(val, low, med, high)
            cols[i % 3].metric(f"{icon} {name.upper()}", val)

        model = joblib.load(os.path.join(BASE_DIR, "models", "air_quality_model.pkl"))
        pred = map_air_label(model.predict([[*data.values()]])[0])

        st.subheader(f"Air Quality Category: {pred}")

        if pred == "Good":
            st.success("🌿 Air quality is GOOD.")
        elif pred == "Moderate":
            st.warning("😷 Moderate air — sensitive groups should wear a mask.")
        else:
            st.error("🚨 Poor air quality — avoid exposure.")

    except Exception as e:
        st.error(str(e))


# =====================================================
# 💧 WATER QUALITY SECTION
# =====================================================
st.header("💧 Water Quality")

col_w_icon, col_w_text = st.columns([1, 5])
with col_w_icon:
    st_lottie(water_anim, height=120)
with col_w_text:
    city2 = st.text_input("Enter a City for Water Quality")

if st.button("Fetch Water Quality", type="secondary"):
    try:
        c2 = CITY_ALIASES.get(city2.lower().strip(), city2).title()

        if c2 not in df_water["City"].tolist():
            st.error("City not found in dataset.")
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

            model = joblib.load(os.path.join(BASE_DIR, "models", "water_quality_model.pkl"))
            pred = map_water_label(model.predict([[ph, hardness, solids]])[0])

            st.subheader(f"Water Quality: {pred}")

            if pred == "Drinkable":
                st.success("💧 Water is safe to drink.")
            else:
                st.error("🚱 Not safe — use filtered/bottled water.")

    except Exception as e:
        st.error(str(e))


# =====================================================
# 📊 CITY COMPARISON — PIE CHART
# =====================================================
st.header("📊 Compare AQI Between Cities (PM2.5 Levels)")

cityA = st.text_input("City 1")
cityB = st.text_input("City 2")
cityC = st.text_input("City 3 (optional)")

if st.button("Compare AQI"):
    try:
        cities = [cityA, cityB, cityC]
        labels = []
        pm_values = []

        for c in cities:
            if c.strip():
                cname = CITY_ALIASES.get(c.lower().strip(), c)
                pm = get_air_quality_for_city(cname)["pm2_5"]
                labels.append(cname.title())
                pm_values.append(pm)

        df = pd.DataFrame({"City": labels, "PM2.5": pm_values})
        fig = px.pie(df, names="City", values="PM2.5")
        st.plotly_chart(fig)

    except Exception as e:
        st.error(str(e))
