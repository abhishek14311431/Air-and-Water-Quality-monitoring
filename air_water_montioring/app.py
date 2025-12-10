import streamlit as st
import numpy as np
import joblib
import pandas as pd
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
st.write("Real-time pollutant monitoring with predictions and safety indicators.")

# ---------------- PATHS ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
water_csv_path = os.path.join(BASE_DIR, "data", "water_quality_cities.csv")
df_water = pd.read_csv(water_csv_path)

CITY_ALIASES = {"bangalore": "bengaluru", "banglore": "bengaluru", "bombay": "mumbai"}

# ---------------- LABEL MAPS ----------------
def map_air_label(x):
    return {0: "Good", 1: "Moderate", 2: "Poor"}.get(x)

def map_water_label(x):
    return "Drinkable" if x == 1 else "Not Drinkable"

# ---------------- COLOR RULES ----------------
def get_color_for_value(val, low, med, high):
    """
    low  = green threshold max
    med  = yellow threshold max
    high = red threshold max
    """
    if val <= low:
        return "🟢"
    elif val <= med:
        return "🟡"
    else:
        return "🔴"


# ---------------------------------------------------------
# 🟦 AIR QUALITY SECTION
# ---------------------------------------------------------
st.header("🌫️ Air Quality")

city = st.text_input("Enter a city for Air Quality")

if st.button("Fetch Air Quality", type="primary"):
    try:
        city_fixed = CITY_ALIASES.get(city.lower().strip(), city)
        data = get_air_quality_for_city(city_fixed)

        st.subheader(f"Live AQI Pollutants — {city_fixed.title()}")

        cols = st.columns(3)
        items = list(data.items())

        # pollutant thresholds (approx WHO standards)
        pollutant_limits = {
            "pm2_5": (30, 60, 90),
            "pm10": (50, 100, 150),
            "no2": (40, 80, 180),
            "so2": (20, 80, 380),
            "o3": (50, 100, 200),
            "co": (200, 400, 1000),
        }

        # Display pollutants with circle color indicator
        for i, (name, value) in enumerate(items):
            low, med, high = pollutant_limits[name]
            color = get_color_for_value(value, low, med, high)

            cols[i % 3].metric(
                label=f"{color} {name.upper()}",
                value=value
            )

        # Prediction
        model_path = os.path.join(BASE_DIR, "models", "air_quality_model.pkl")
        model = joblib.load(model_path)
        pred_label = map_air_label(model.predict([[*data.values()]])[0])

        st.subheader(f"Predicted Air Quality: {pred_label}")

        if pred_label == "Good":
            st.success("🌿 Air quality is GOOD. Safe to go outside!")
        elif pred_label == "Moderate":
            st.warning("😷 Air is MODERATE. Sensitive groups should wear a mask.")
        else:
            st.error("🚨 AIR IS POOR. Wear a mask and limit exposure.")

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

            st.subheader(f"Water Parameters — {city2_fixed}")

            colw = st.columns(3)

            # Thresholds for color coding
            water_limits = {
                "pH": (6.5, 8.5, 9.5),
                "Hardness": (150, 300, 500),
                "Solids": (300, 600, 900)
            }

            params = [("pH", ph), ("Hardness", hardness), ("Solids", solids)]

            for i, (name, value) in enumerate(params):
                low, med, high = water_limits[name]
                color = get_color_for_value(value, low, med, high)

                colw[i].metric(
                    label=f"{color} {name}",
                    value=value
                )

            # Prediction
            model_path = os.path.join(BASE_DIR, "models", "water_quality_model.pkl")
            model = joblib.load(model_path)
            pred = map_water_label(model.predict([[ph, hardness, solids]])[0])

            st.subheader(f"Predicted Water Quality: {pred}")

            if pred == "Drinkable":
                st.success("💧 Water is safe for drinking.")
            else:
                st.error("🚱 Water is NOT safe — use filtered or bottled water.")

    except Exception as e:
        st.error(str(e))


# ---------------------------------------------------------
# 📊 CITY COMPARISON (NO HEATMAP)
# ---------------------------------------------------------
st.header("📊 Compare AQI Between Cities")

c1 = st.text_input("City 1")
c2 = st.text_input("City 2")
c3 = st.text_input("City 3 (optional)")

if st.button("Compare AQI"):
    try:
        def fetch(city):
            fixed = CITY_ALIASES.get(city.lower().strip(), city)
            return get_air_quality_for_city(fixed)

        cities = [c1, c2, c3]
        aqi_vals = {}
        model = joblib.load(os.path.join(BASE_DIR, "models", "air_quality_model.pkl"))

        for ct in cities:
            if ct.strip():
                data = fetch(ct)
                pred = model.predict([[*data.values()]])[0]
                aqi_vals[ct.title()] = pred

        if aqi_vals:
            df = pd.DataFrame({"City": list(aqi_vals.keys()), "AQI": list(aqi_vals.values())})
            df = df.set_index("City")
            st.bar_chart(df)
        else:
            st.warning("Enter at least two cities.")

    except Exception as e:
        st.error(str(e))
