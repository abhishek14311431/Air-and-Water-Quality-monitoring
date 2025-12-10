import streamlit as st
import joblib
import pandas as pd
import numpy as np
import plotly.express as px
import os
from utils import get_air_quality_for_city


# ---------------------------------------
# PAGE CONFIG
# ---------------------------------------
st.set_page_config(
    page_title="Air & Water Quality Monitoring",
    page_icon="🌍",
    layout="wide"
)


# ---------------------------------------
# HEADER
# ---------------------------------------
st.title("🌍 Air & Water Quality Monitoring Dashboard")
st.write("Real-time pollutant monitoring + predictions with color-coded safety indicators.")


# ---------------------------------------
# LOAD DATA
# ---------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
water_csv_path = os.path.join(BASE_DIR, "data", "water_quality_cities.csv")
df_water = pd.read_csv(water_csv_path)

CITY_ALIASES = {
    "bangalore": "bengaluru",
    "banglore": "bengaluru",
    "bombay": "mumbai",
}


# ---------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------
def map_air_label(x):
    return {0: "Good", 1: "Moderate", 2: "Poor"}.get(x)


def map_water_label(x):
    return "Drinkable" if x == 1 else "Not Drinkable"


def get_color_icon(val, low, med, high):
    """Returns 🟢 🟡 🔴 based on pollutant severity."""
    if val <= low:
        return "🟢"
    elif val <= med:
        return "🟡"
    else:
        return "🔴"


# ============================================================
# 🌫️ AIR QUALITY SECTION
# ============================================================
st.header("🌫️ Air Quality")

city = st.text_input("Enter a City for Air Quality")

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

        # Display pollutant metrics with color
        for i, (name, value) in enumerate(items):
            low, med, high = pollutant_limits[name]
            icon = get_color_icon(value, low, med, high)

            cols[i % 3].metric(
                label=f"{icon} {name.upper()}",
                value=value
            )

        # Prediction Model
        model = joblib.load(os.path.join(BASE_DIR, "models", "air_quality_model.pkl"))
        pred_label = map_air_label(model.predict([[*data.values()]])[0])

        st.subheader(f"Air Quality Category: {pred_label}")

        if pred_label == "Good":
            st.success("🌿 Air quality is GOOD. Feel free to go outside.")
        elif pred_label == "Moderate":
            st.warning("😷 AIR IS MODERATE. Sensitive groups should wear a mask.")
        else:
            st.error("🚨 AIR IS POOR. Wear a mask and avoid long exposure.")

    except Exception as e:
        st.error(str(e))


# ============================================================
# 💧 WATER QUALITY SECTION
# ============================================================
st.header("💧 Water Quality")

city2 = st.text_input("Enter a City for Water Quality")

if st.button("Fetch Water Quality", type="secondary"):
    try:
        city2_fixed = CITY_ALIASES.get(city2.lower().strip(), city2).title()

        if city2_fixed not in df_water["City"].tolist():
            st.error("City not found in water dataset.")
        else:
            row = df_water[df_water["City"] == city2_fixed].iloc[0]
            ph, hardness, solids = row["pH"], row["Hardness"], row["Solids"]

            st.subheader(f"Water Parameters — {city2_fixed}")

            cols = st.columns(3)

            water_limits = {
                "pH": (6.5, 8.5, 9.5),
                "Hardness": (150, 300, 500),
                "Solids": (300, 600, 900),
            }

            params = [("pH", ph), ("Hardness", hardness), ("Solids", solids)]

            for i, (name, value) in enumerate(params):
                low, med, high = water_limits[name]
                icon = get_color_icon(value, low, med, high)

                cols[i].metric(f"{icon} {name}", value)

            # Water quality model
            model = joblib.load(os.path.join(BASE_DIR, "models", "water_quality_model.pkl"))
            pred = map_water_label(model.predict([[ph, hardness, solids]])[0])

            st.subheader(f"Water Quality Status: {pred}")

            if pred == "Drinkable":
                st.success("💧 Water is safe for drinking.")
            else:
                st.error("🚱 Water is NOT safe. Use filtered or bottled water.")

    except Exception as e:
        st.error(str(e))


# ============================================================
# 📊 CITY COMPARISON — PIE CHART
# ============================================================
st.header("📊 Compare AQI Between Cities (PM2.5 Based)")

c1 = st.text_input("City 1")
c2 = st.text_input("City 2")
c3 = st.text_input("City 3 (Optional)")

if st.button("Compare AQI"):
    try:
        cities = [c1, c2, c3]
        labels = []
        values = []

        for city in cities:
            if city.strip():
                cname = CITY_ALIASES.get(city.lower().strip(), city)
                pollution = get_air_quality_for_city(cname)
                pm25 = pollution["pm2_5"]

                labels.append(cname.title())
                values.append(pm25)

        if len(values) == 0:
            st.warning("Enter at least 1 valid city.")
        else:
            df = pd.DataFrame({"City": labels, "PM2.5": values})

            fig = px.pie(
                df,
                names="City",
                values="PM2.5",
                title="PM2.5 Pollution Comparison (Lower is Better)",
                color="City"
            )

            st.plotly_chart(fig)

    except Exception as e:
        st.error(str(e))
