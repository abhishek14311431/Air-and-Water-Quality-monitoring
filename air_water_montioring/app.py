import streamlit as st
import joblib
import pandas as pd
import numpy as np
import plotly.express as px
import os
from utils import get_air_quality_for_city

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Air & Water Monitoring",
    page_icon="🌍",
    layout="wide",
)

# ---------------- HEADER ----------------
st.title("🌍 Air & Water Quality Monitoring Dashboard")
st.write("Real-time pollutant monitoring with predictions and color-coded safety indicators.")

# ---------------- PATHS ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
water_csv_path = os.path.join(BASE_DIR, "data", "water_quality_cities.csv")
df_water = pd.read_csv(water_csv_path)

CITY_ALIASES = {
    "bangalore": "bengaluru",
    "banglore": "bengaluru",
    "bombay": "mumbai"
}

def map_air_label(x):
    return {0: "Good", 1: "Moderate", 2: "Poor"}.get(x)

def map_water_label(x):
    return "Drinkable" if x == 1 else "Not Drinkable"

# ---------------- COLOR RULES ----------------
def get_color_icon(val, low, med, high):
    if val <= low:
        return "🟢"
    elif val <= med:
        return "🟡"
    else:
        return "🔴"


# ---------------------------------------------------------
# 🌫️ AIR QUALITY SECTION
# ---------------------------------------------------------
st.header("🌫️ Air Quality")

city = st.text_input("Enter a city for Air Quality")

if st.button("Fetch Air Quality", type="primary"):
    try:
        city_fixed = CITY_ALIASES.get(city.lower().strip(), city)
        data = get_air_quality_for_city(city_fixed)

        st.subheader(f"Live Pollutant Levels — {city_fixed.title()}")

        cols = st.columns(3)
        items = list(data.items())

        pollutant_limits = {
            "pm2_5": (30, 60, 90),
            "pm10": (50, 100, 150),
            "no2": (40, 80, 180),
            "so2": (20, 80, 380),
            "o3": (50, 100, 200),
            "co": (200, 400, 1000),
        }

        # Display metrics
        for i, (name, value) in enumerate(items):
            low, med, high = pollutant_limits[name]
            color_icon = get_color_icon(value, low, med, high)
            cols[i % 3].metric(f"{color_icon} {name.upper()}", value)

        # Prediction
        model = joblib.load(os.path.join(BASE_DIR, "models", "air_quality_model.pkl"))
        pred_label = map_air_label(model.predict([[*data.values()]])[0])

        st.subheader(f"Air Quality Category: {pred_label}")

        if pred_label == "Good":
            st.success("🌿 Air quality is GOOD. Safe to go outside!")
        elif pred_label == "Moderate":
            st.warning("😷 MODERATE air. Sensitive groups should wear masks.")
        else:
            st.error("🚨 POOR air quality — Wear a mask!")

    except Exception as e:
        st.error(str(e))


# ---------------------------------------------------------
# 💧 WATER QUALITY SECTION
# ---------------------------------------------------------
st.header("💧 Water Quality")

city2 = st.text_input("Enter a city for Water Quality")

if st.button("Fetch Water Quality", type="secondary"):
    try:
        city2_fixed = CITY_ALIASES.get(city2.lower().strip(), city2).title()

        if city2_fixed not in df_water["City"].tolist():
            st.error("City not found in water dataset.")
        else:
            row = df_water[df_water["City"] == city2_fixed].iloc[0]
            ph, hardness, solids = row["pH"], row["Hardness"], row["Solids"]

            st.subheader(f"Parameters — {city2_fixed}")

            colw = st.columns(3)

            water_limits = {
                "pH": (6.5, 8.5, 9.5),
                "Hardness": (150, 300, 500),
                "Solids": (300, 600, 900)
            }

            params = [("pH", ph), ("Hardness", hardness), ("Solids", solids)]

            for i, (name, value) in enumerate(params):
                low, med, high = water_limits[name]
                color_icon = get_color_icon(value, low, med, high)
                colw[i].metric(f"{color_icon} {name}", value)

            # Prediction
            model = joblib.load(os.path.join(BASE_DIR, "models", "water_quality_model.pkl"))
            pred = map_water_label(model.predict([[ph, hardness, solids]])[0])

            st.subheader(f"Water Quality Status: {pred}")

            if pred == "Drinkable":
                st.success("💧 Water is safe for drinking.")
            else:
                st.error("🚱 Water is NOT safe for drinking.")

    except Exception as e:
        st.error(str(e))


# ---------------------------------------------------------
# 📊 CITY COMPARISON — PIE CHART
# ---------------------------------------------------------
st.header("📊 Compare AQI Between Cities")

ci1 = st.text_input("City 1")
ci2 = st.text_input("City 2")
ci3 = st.text_input("City 3 (optional)")

if st.button("Compare AQI"):
    try:
        cities = [ci1, ci2, ci3]
        values = []
        labels = []

        model = joblib.load(os.path.join(BASE_DIR, "models", "air_quality_model.pkl"))

        for c in cities:
            if c.strip():
                cname = CITY_ALIASES.get(c.lower().strip(), c)
                data = get_air_quality_for_city(cname)
                pred = model.predict([[*data.values()]])[0]

                labels.append(cname.title())
                values.append(pred)

        if values:
            df = pd.DataFrame({"City": labels, "AQI": values})
            fig = px.pie(df, names="City", values="AQI", title="AQI Comparison")
            st.plotly_chart(fig)

        else:
            st.warning("Enter at least 1 valid city.")

    except Exception as e:
        st.error(str(e))
