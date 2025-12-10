import streamlit as st
import numpy as np
import joblib
import pandas as pd
import os
from utils import get_air_quality_for_city

st.set_page_config(page_title="Air & Water Quality Monitoring", page_icon="🌍", layout="wide")

# Modern Clean UI
st.markdown(
    """
<style>
.stApp {
    background: #eef5ff;
    font-family: 'Segoe UI', sans-serif;
}

.header {
    text-align: center;
    font-size: 42px;
    font-weight: 900;
    color: #102542;
    margin-bottom: 25px;
}

.card {
    background: white;
    padding: 22px;
    border-radius: 14px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.12);
    margin-bottom: 20px;
}

.metric-circle {
    width: 110px;
    height: 110px;
    border-radius: 50%;
    background: #f0f6ff;
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;
    font-size: 18px;
    font-weight: 700;
    color: #102542;
    border: 3px solid #4f8ef7;
    margin: 10px auto;
}
</style>
""",
    unsafe_allow_html=True
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
water_csv_path = os.path.join(BASE_DIR, "data", "water_quality_cities.csv")
df_water = pd.read_csv(water_csv_path)

CITY_ALIASES = {"bangalore": "bengaluru", "banglore": "bengaluru", "bombay": "mumbai"}

def map_air_label(x): return {0:"Good",1:"Moderate",2:"Poor"}.get(x)
def map_water_label(x): return "Drinkable" if x==1 else "Not Drinkable"

def pollutant_color(x): return "#16a34a" if x<50 else "#eab308" if x<100 else "#dc2626"

def air_color(x): return {"Good":"#16a34a","Moderate":"#eab308","Poor":"#dc2626"}[x]
def water_color(x): return {"Drinkable":"#16a34a","Not Drinkable":"#dc2626"}[x]

st.markdown('<div class="header">🌍 Air & Water Quality Monitoring</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2, gap="large")

# ---------------- AIR QUALITY ----------------
with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🌫️ Air Quality")

    city = st.text_input("City (Air Quality)")

    if st.button("Get AQI", use_container_width=True):
        try:
            c = CITY_ALIASES.get(city.lower().strip(), city)
            data = get_air_quality_for_city(c)
            st.write(f"### Live AQI — {c.title()}")

            cols = st.columns(3)
            items = list(data.items())
            for i in range(0, len(items), 3):
                row = items[i:i+3]
                row_cols = st.columns(len(row))
                for (k, v), col in zip(row, row_cols):
                    col.markdown(f"<div class='metric-circle'>{k.upper()}<br>{v}</div>", unsafe_allow_html=True)

            model = joblib.load(os.path.join(BASE_DIR, "models", "air_quality_model.pkl"))
            pred = map_air_label(model.predict([[*data.values()]])[0])
            st.write(f"### Air Quality: {pred}")

        except Exception as e:
            st.error(str(e))
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- WATER QUALITY ----------------
with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("💧 Water Quality")

    city2 = st.text_input("City (Water Quality)")

    if st.button("Check Water", use_container_width=True):
        try:
            c2 = CITY_ALIASES.get(city2.lower().strip(), city2).title()
            if c2 not in df_water["City"].tolist():
                st.error("City not found in water dataset")
            else:
                row = df_water[df_water["City"] == c2].iloc[0]
                ph, hard, sol = row["pH"], row["Hardness"], row["Solids"]

                st.write("### Water Parameters")
                st.write({"pH":ph, "Hardness":hard, "Solids":sol})

                model = joblib.load(os.path.join(BASE_DIR, "models", "water_quality_model.pkl"))
                pred = map_water_label(model.predict([[ph, hard, sol]])[0])
                st.write(f"### Water Quality: {pred}")

        except Exception as e:
            st.error(str(e))
    st.markdown('</div>', unsafe_allow_html=True)
