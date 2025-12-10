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
st.write("Get real-time air & water quality insights with prediction and comparison features.")

# ---------------- PATHS ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
water_csv_path = os.path.join(BASE_DIR, "data", "water_quality_cities.csv")
df_water = pd.read_csv(water_csv_path)

CITY_ALIASES = {"bangalore": "bengaluru", "banglore": "bengaluru", "bombay": "mumbai"}

def map_air_label(x): 
    return {0: "Good", 1: "Moderate", 2: "Poor"}.get(x)

def map_water_label(x): 
    return "Drinkable" if x == 1 else "Not Drinkable"


# ---------------------------------------------------------
# 🟦 AIR QUALITY SECTION
# ---------------------------------------------------------
air_container = st.container()
air_container.header("🌫️ Air Quality")

city = air_container.text_input("Enter a City for Air Quality")

if air_container.button("Get Air Quality"):
    try:
        c = CITY_ALIASES.get(city.lower().strip(), city)
        data = get_air_quality_for_city(c)

        air_container.subheader(f"Live AQI Data — {c.title()}")

        # Display pollutants as metrics
        cols = air_container.columns(3)
        items = list(data.items())

        for i, (name, val) in enumerate(items):
            cols[i % 3].metric(label=name.upper(), value=f"{val}")

        # Prediction model
        model_path = os.path.join(BASE_DIR, "models", "air_quality_model.pkl")
        model = joblib.load(model_path)
        pred = map_air_label(model.predict([[*data.values()]])[0])

        air_container.subheader(f"Air Quality Category: {pred}")

        # Advice (pure streamlit)
        if pred == "Good":
            air_container.success("🌿 Good Air Quality — Safe to go outside.")
        elif pred == "Moderate":
            air_container.warning("😷 Moderate Air Quality — Sensitive people should consider wearing masks.")
        else:
            air_container.error("🚨 Poor Air Quality — Mask strongly recommended!")

    except Exception as e:
        air_container.error(str(e))


# ---------------------------------------------------------
# 💧 WATER QUALITY SECTION
# ---------------------------------------------------------
water_container = st.container()
water_container.header("💧 Water Quality")

city2 = water_container.text_input("Enter a City for Water Quality")

if water_container.button("Check Water Quality"):
    try:
        c2 = CITY_ALIASES.get(city2.lower().strip(), city2).title()

        if c2 not in df_water["City"].tolist():
            water_container.error("City not found in water dataset.")
        else:
            row = df_water[df_water["City"] == c2].iloc[0]
            ph, hardness, solids = row["pH"], row["Hardness"], row["Solids"]

            param_cols = water_container.columns(3)
            param_cols[0].metric("pH", ph)
            param_cols[1].metric("Hardness", hardness)
            param_cols[2].metric("Solids", solids)

            # Predict water quality
            model_path = os.path.join(BASE_DIR, "models", "water_quality_model.pkl")
            model = joblib.load(model_path)
            pred = map_water_label(model.predict([[ph, hardness, solids]])[0])

            water_container.subheader(f"Water Quality Status: {pred}")

            if pred == "Drinkable":
                water_container.success("💧 Safe for drinking.")
            else:
                water_container.error("🚱 Not safe — Use filtered or bottled water.")

    except Exception as e:
        water_container.error(str(e))


# ---------------------------------------------------------
# 📊 CITY COMPARISON SECTION
# ---------------------------------------------------------
st.header("📊 Compare AQI Between Multiple Cities")

c1 = st.text_input("City 1")
c2 = st.text_input("City 2")
c3 = st.text_input("City 3 (optional)")

if st.button("Compare Air Quality"):
    try:
        def fetch(city):
            city = CITY_ALIASES.get(city.lower().strip(), city)
            return get_air_quality_for_city(city)

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
            st.warning("Please enter at least two cities.")

    except Exception as e:
        st.error(str(e))


# ---------------------------------------------------------
# 🗺️ INDIA AQI SAMPLE HEATMAP (Demo)
# ---------------------------------------------------------
st.header("🗺️ India AQI Heatmap (Sample Data)")

heat_cities = ["Delhi", "Mumbai", "Kolkata", "Chennai", "Bengaluru", "Hyderabad"]
heat_values = np.random.randint(40, 180, len(heat_cities))
df_heat = pd.DataFrame({"City": heat_cities, "AQI": heat_values}).set_index("City")

st.bar_chart(df_heat)
