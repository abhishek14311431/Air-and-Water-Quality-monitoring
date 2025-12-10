import streamlit as st
import numpy as np
import joblib
import pandas as pd
import os
from utils import get_air_quality_for_city

# Page Setup
st.set_page_config(page_title="Air & Water Quality Monitoring", page_icon="🌍", layout="wide")

# Clean Light Blue Background
st.markdown(
    """
<style>
.stApp {
    background: linear-gradient(to bottom right, #a8d8ff, #dff3ff);
    font-family: 'Segoe UI', sans-serif;
    color: #000000;
}

.dashboard-title {
    text-align: center;
    font-size: 42px;
    font-weight: 900;
    color: #000000;
    margin-bottom: 10px;
}

.section-title {
    font-size: 26px;
    font-weight: 700;
    color: #000000;
    margin: 20px 0 10px;
}

.gdu-card {
    background: rgba(255,255,255,0.75);
    padding: 20px;
    border-radius: 14px;
    margin-bottom: 15px;
    color: #000000;
    box-shadow: none;
    border: none;
}

.indicator {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    background: rgba(255,255,255,0.75);
    display: flex;
    justify-content: center;
    align-items: center;
    margin: 10px auto;
    font-size: 20px;
    font-weight: 700;
    color: #000000;
    border: none;
    box-shadow: none;
}
</style>
""",
    unsafe_allow_html=True
)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
water_csv_path = os.path.join(BASE_DIR, "data", "water_quality_cities.csv")
df_water = pd.read_csv(water_csv_path)

CITY_ALIASES = {"bangalore": "bengaluru", "banglore": "bengaluru", "bombay": "mumbai"}

def pollutant_color(v): return "#16a34a" if v < 50 else "#eab308" if v < 100 else "#dc2626"
def map_air_label(x): return {0:"Good",1:"Moderate",2:"Poor"}.get(x)
def air_color(x): return {"Good":"#16a34a","Moderate":"#eab308","Poor":"#dc2626"}[x]
def map_water_label(x): return "Drinkable" if x==1 else "Not Drinkable"
def water_color(x): return {"Drinkable":"#16a34a","Not Drinkable":"#dc2626"}[x]

st.markdown('<div class="dashboard-title">🌍 Air & Water Quality Monitoring</div>', unsafe_allow_html=True)

col_air, col_water = st.columns(2, gap="large")

# --- AIR QUALITY ---
with col_air:
    st.markdown('<div class="gdu-card">', unsafe_allow_html=True)
    st.subheader("🌫️ Air Quality")

    city = st.text_input("City (Air Quality)")

    if st.button("Fetch AQI", use_container_width=True):
        try:
            c = CITY_ALIASES.get(city.lower().strip(), city)
            data = get_air_quality_for_city(c)

            st.write(f"### Live AQI for {c.title()}")

            for k, v in data.items():
                st.markdown(f"<div class='indicator'>{k.upper()}<br>{v}</div>", unsafe_allow_html=True)

            model = joblib.load(os.path.join(BASE_DIR, "models", "air_quality_model.pkl"))
            pred = map_air_label(model.predict([[*data.values()]])[0])

            st.write(f"### Air Quality: {pred}")

        except Exception as e:
            st.error(str(e))

    st.markdown('</div>', unsafe_allow_html=True)

# --- WATER QUALITY ---
with col_water:
    st.markdown('<div class="gdu-card">', unsafe_allow_html=True)
    st.subheader("💧 Water Quality")

    city2 = st.text_input("City (Water Quality)")

    if st.button("Check Water", use_container_width=True):
        try:
            c2 = CITY_ALIASES.get(city2.lower().strip(), city2).title()
            if c2 not in df_water["City"].tolist():
                st.error("City not in dataset")
            else:
                row = df_water[df_water["City"] == c2].iloc[0]
                ph, hard, sol = row["pH"], row["Hardness"], row["Solids"]

                st.write({"pH": ph, "Hardness": hard, "Solids": sol})

                model = joblib.load(os.path.join(BASE_DIR, "models", "water_quality_model.pkl"))
                pred = map_water_label(model.predict([[ph, hard, sol]])[0])

                st.write(f"### Water Quality: {pred}")

        except Exception as e:
            st.error(str(e))

    st.markdown('</div>', unsafe_allow_html=True)
