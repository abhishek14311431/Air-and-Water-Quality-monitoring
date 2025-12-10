import streamlit as st
import numpy as np
import joblib
import pandas as pd
import os
from utils import get_air_quality_for_city

# ---------------- PAGE SETUP ----------------
st.set_page_config(page_title="Air & Water Quality Monitoring", page_icon="🌍", layout="wide")

# ---------------- CLEAN PREMIUM UI ----------------
st.markdown(
    """
<style>
.stApp {
    background: #e8f1ff;
    font-family: 'Segoe UI', sans-serif;
    color: #0a0a0a;
}
.header {
    text-align: center;
    font-size: 44px;
    font-weight: 900;
    margin-bottom: 25px;
    color: #0a2540;
}
.card {
    background: #ffffff;
    padding: 24px;
    border-radius: 16px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.12);
    margin-bottom: 25px;
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
    color: #0a2540;
    border: 3px solid #4f8ef7;
    margin: 10px auto;
}
.section-title {
    font-size: 28px;
    font-weight: 800;
    color: #0a2540;
    margin: 10px 0 10px;
}
</style>
""",
    unsafe_allow_html=True
)

# ---------------- PATHS ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
water_csv_path = os.path.join(BASE_DIR, "data", "water_quality_cities.csv")
df_water = pd.read_csv(water_csv_path)

CITY_ALIASES = {"bangalore": "bengaluru", "banglore": "bengaluru", "bombay": "mumbai"}

def map_air_label(x): return {0:"Good",1:"Moderate",2:"Poor"}.get(x)
def map_water_label(x): return "Drinkable" if x==1 else "Not Drinkable"

def pollutant_color(x): return "#16a34a" if x<50 else "#eab308" if x<100 else "#dc2626"

def air_color(x): return {"Good":"#16a34a","Moderate":"#eab308","Poor":"#dc2626"}[x]
def water_color(x): return {"Drinkable":"#16a34a","Not Drinkable":"#dc2626"}[x]

# ---------------- HEADER ----------------
st.markdown('<div class="header">🌍 Air & Water Quality Monitoring</div>', unsafe_allow_html=True)

# ---------------- LAYOUT ----------------
col1, col2 = st.columns(2, gap="large")

# ============ AIR QUALITY ============
with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🌫️ Air Quality")

    city = st.text_input("City (Air Quality)")

    if st.button("Get AQI", use_container_width=True):
        try:
            c = CITY_ALIASES.get(city.lower().strip(), city)
            data = get_air_quality_for_city(c)
            st.write(f"### Live AQI — {c.title()}")

            # pollutant circles
            items = list(data.items())
            for i in range(0, len(items), 3):
                cols_sub = st.columns(3)
                for (name, val), box in zip(items[i:i+3], cols_sub):
                    box.markdown(f"<div class='metric-circle'>{name.upper()}<br>{val}</div>", unsafe_allow_html=True)

            model = joblib.load(os.path.join(BASE_DIR, "models", "air_quality_model.pkl"))
            pred = map_air_label(model.predict([[*data.values()]])[0])
            st.write(f"### Air Quality Category: {pred}")

        except Exception as e:
            st.error(str(e))

    st.markdown('</div>', unsafe_allow_html=True)

# ============ WATER QUALITY ============
with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("💧 Water Quality")

    city2 = st.text_input("City (Water Quality)")

    if st.button("Check Water", use_container_width=True):
        try:
            c2 = CITY_ALIASES.get(city2.lower().strip(), city2).title()
            if c2 not in df_water["City"].tolist():
                st.error("City not in database")
            else:
                row = df_water[df_water["City"] == c2].iloc[0]
                ph, hardness, solids = row["pH"], row["Hardness"], row["Solids"]
                background: #f5f9ff;: {pred}")

        except Exception as e:
            st.error(str(e))

    st.markdown('</div>', unsafe_allow_html=True)

# ============ CITY COMPARISON ============
st.markdown('<div class="section-title">📊 Compare AQI Between Cities</div>', unsafe_allow_html=True)
st.markdown('<div class="card">', unsafe_allow_html=True)

c1 = st.text_input("City 1")
c2 = st.text_input("City 2")
c3 = st.text_input("City 3 (optional)")

if st.button("Compare Cities", use_container_width=True):
    try:
        def fetch(city):
            city = CITY_ALIASES.get(city.lower().strip(), city)
            return get_air_quality_for_city(city)

        vals = {}
        for c in [c1, c2, c3]:
            if c and c.strip():
                data = fetch(c)
                model = joblib.load(os.path.join(BASE_DIR, "models", "air_quality_model.pkl"))
                vals[c.title()] = model.predict([[*data.values()]])[0]

        df_compare = pd.DataFrame({"City": list(vals.keys()), "AQI": list(vals.values())}).set_index("City")
        st.bar_chart(df_compare)
    except Exception as e:
        st.error(str(e))

st.markdown('</div>', unsafe_allow_html=True)

# ============ INDIA HEATMAP ============
st.markdown('<div class="section-title">🗺️ India AQI Heatmap</div>', unsafe_allow_html=True)
st.markdown('<div class="card">', unsafe_allow_html=True)

heat_cities = ["Delhi","Mumbai","Kolkata","Chennai","Bengaluru","Hyderabad"]
heat_values = np.random.randint(40, 160, len(heat_cities))
df_heat = pd.DataFrame({"City": heat_cities, "AQI": heat_values}).set_index("City")
st.bar_chart(df_heat)

st.markdown('</div>', unsafe_allow_html=True)
