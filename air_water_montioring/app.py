import streamlit as st
import numpy as np
import joblib
import pandas as pd
import os
from utils import get_air_quality_for_city

# ---------------------- BASIC SETUP ----------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
water_csv_path = os.path.join(BASE_DIR, "data", "water_quality_cities.csv")
air_csv_path = os.path.join(BASE_DIR, "data", "air_quality_dataset.csv")

df_water = pd.read_csv(water_csv_path)

CITY_ALIASES = {
    "bangalore": "bengaluru",
    "banglore": "bengaluru",
    "bombay": "mumbai"
}

st.set_page_config(
    page_title="Smart Air & Water Quality",
    page_icon="🌍",
    layout="centered",
)

# ---------------------- NIGHT MODE TOGGLE ----------------------
if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = False

theme_class = "dark" if st.session_state["dark_mode"] else "light"

st.markdown(f"""
<style>
body {{
    transition: background 0.6s ease-in-out, color 0.4s;
}}

.light .stApp {{
    background: linear-gradient(135deg, #4FACFE 0%, #00F2FE 100%);
    color: #000;
}}
.dark .stApp {{
    background: radial-gradient(circle at top, #0f172a, #020617);
    color: #FFF;
}}

div.card {{
    width: 80%;
    margin: 0 auto;
    background: rgba(255,255,255,0.10);
    backdrop-filter: blur(12px);
    padding: 40px;
    border-radius: 25px;
    box-shadow: 0 0 25px rgba(0,0,0,0.45);
    margin-top: 18px;
    animation: fadeIn 1s ease;
}}

@keyframes fadeIn {{
  0% {{ opacity:0; transform: translateY(15px); }}
  100% {{ opacity:1; transform: translateY(0px); }}
}}

.title {{
    font-size: 60px;
    text-align:center;
    font-weight: 900;
    margin-bottom: 10px;
    color: white;
    animation: glow 2s infinite alternate;
}}

@keyframes glow {{
  from {{ text-shadow: 0 0 8px #ffffff; }}
  to {{ text-shadow: 0 0 18px #00eaff; }}
}}

.sub {{
    font-size: 38px;
    text-align:center;
    font-weight: 900;
    margin-top: 35px;
    color: #38bdf8;
}}

.result-box {{
    padding: 20px;
    border-radius: 16px;
    text-align:center;
    font-size: 32px;
    font-weight: 900;
    margin-top: 25px;
    color:white;
    animation: fadeIn 1s ease;
}}

</style>
<script>
const body = window.parent.document.querySelector('body');
body.className = '""" + theme_class + """';
</script>
""", unsafe_allow_html=True)

# Toggle Button
if st.button("🌙 Switch to Night Mode" if not st.session_state["dark_mode"] else "☀️ Switch to Light Mode"):
    st.session_state["dark_mode"] = not st.session_state["dark_mode"]
    st.rerun()

# ---------------------- HEADER ----------------------
st.markdown('<p class="title">🌍 Smart Air & Water Quality Monitoring</p>', unsafe_allow_html=True)

# ---------------------- MAPPERS ----------------------
def map_air_label(x): return {0: "Good", 1: "Moderate", 2: "Poor"}.get(x, "Unknown")
def air_color(x): return {"Good": "#16A34A", "Moderate": "#EAB308", "Poor": "#DC2626"}.get(x, "#1E3A8A")
def map_water_label(x): return "Drinkable" if x == 1 else "Not Drinkable"
def water_color(x): return {"Drinkable": "#16A34A", "Not Drinkable": "#DC2626"}.get(x, "#1E3A8A")

# ---------------------- AIR QUALITY SECTION ----------------------
st.markdown('<p class="sub">🌬️ Air Quality Check</p>', unsafe_allow_html=True)
st.markdown('<div class="card">', unsafe_allow_html=True)

city = st.text_input("Enter City (Air Quality)")

if st.button("Get Air Quality", use_container_width=True):
    try:
        c = city.strip().lower()
        if c in CITY_ALIASES:
            city = CITY_ALIASES[c]

        data = get_air_quality_for_city(city)
        st.markdown(f"<h3>Live Pollutants in {city.title()}</h3>", unsafe_allow_html=True)
        st.write(data)

        model = joblib.load(os.path.join(BASE_DIR, "models", "air_quality_model.pkl"))
        X = np.array([[data[i] for i in data]])
        pred = model.predict(X)[0]

        label = map_air_label(pred)
        color = air_color(label)

        st.markdown(
            f'<div class="result-box" style="background:{color};">{label} Air Quality</div>',
            unsafe_allow_html=True
        )

    except Exception:
        st.error("Invalid City or API Error")

st.markdown('</div>', unsafe_allow_html=True)

# ---------------------- WATER QUALITY SECTION ----------------------
st.markdown('<p class="sub">💧 Water Quality Prediction</p>', unsafe_allow_html=True)
st.markdown('<div class="card">', unsafe_allow_html=True)

city2 = st.text_input("Enter City (Water Quality)")

if st.button("Check Water Quality", use_container_width=True):
    c2 = city2.strip().lower()
    c2 = CITY_ALIASES.get(c2, city2).title()

    if c2 not in df_water["City"].tolist():
        st.error("City not found in water dataset")
    else:
        row = df_water[df_water["City"] == c2].iloc[0]

        st.markdown("<h3>Measured Water Parameters</h3>", unsafe_allow_html=True)
        st.write({"pH": row["pH"], "Hardness": row["Hardness"], "Solids": row["Solids"]})

        model = joblib.load(os.path.join(BASE_DIR, "models", "water_quality_model.pkl"))
        pred = model.predict([[row["pH"], row["Hardness"], row["Solids"]]])[0]

        label = map_water_label(pred)
        color = water_color(label)

        st.markdown(
            f'<div class="result-box" style="background:{color};">{label} Water Quality</div>',
            unsafe_allow_html=True
        )

st.markdown('</div>', unsafe_allow_html=True)

# ---------------------- FOOTER ----------------------
st.markdown(
    "<p style='text-align:center;color:white;font-weight:700;margin-top:25px;font-size:20px;'>Designed with ❤️ for Academic Project</p>",
    unsafe_allow_html=True)
