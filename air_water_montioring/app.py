# PREMIUM THEME + ANIMATED POLLUTANT INDICATORS ✨
# --------------------------------------------------------------
# Streamlit Clean + Professional Dashboard

import streamlit as st
import numpy as np
import joblib
import pandas as pd
import os
from utils import get_air_quality_for_city

# ------------------ PATHS ------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
water_csv_path = os.path.join(BASE_DIR, "data", "water_quality_cities.csv")

df_water = pd.read_csv(water_csv_path)

CITY_ALIASES = {
    "bangalore": "bengaluru",
    "banglore": "bengaluru",
    "bombay": "mumbai"
}

# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="Pro AQI Dashboard",
    page_icon="🌍",
    layout="wide"
)

# ------------------ DARK MODE TOGGLE ------------------
if "dark" not in st.session_state:
    st.session_state.dark = False

if st.toggle("🌙 Night Mode", value=st.session_state.dark):
    st.session_state.dark = True
else:
    st.session_state.dark = False

mode = "dark" if st.session_state.dark else "light"

# ------------------ PREMIUM CSS THEME ------------------
st.markdown(
    f"""
    <style>
    body {{ transition: all .4s ease-in-out; }}

    .light .main-bg {{
        background: linear-gradient(to bottom right, #e0f7fa, #80deea);
        color: #000;
    }}

    .dark .main-bg {{
        background: linear-gradient(to bottom right, #0a0f24, #112344);
        color: white;
    }}

    .glass-card {{
        background: rgba(255,255,255,0.10);
        border-radius: 20px;
        padding: 30px;
        backdrop-filter: blur(12px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.25);
        animation: fadeIn 0.8s ease;
    }}

    @keyframes fadeIn {{
        from {{ opacity:0; transform: translateY(15px); }}
        to   {{ opacity:1; transform: translateY(0px); }}
    }}

    .indicator {{
        border-radius: 18px;
        padding: 18px;
        font-size: 22px;
        font-weight: 700;
        margin: 8px 0;
        animation: pulse 1.5s infinite;
        text-align: center;
    }}

    @keyframes pulse {{
        0% {{ transform: scale(1); }}
        50% {{ transform: scale(1.05); }}
        100% {{ transform: scale(1); }}
    }}

    .title {{ text-align:center; font-size:50px; font-weight:900; margin-bottom:20px; }}
    .section-title {{ font-size:34px; font-weight:800; margin-top:15px; text-align:center; }}
    </style>

    <script>
    window.parent.document.body.className = '{mode} main-bg';
    </script>
    """,
    unsafe_allow_html=True
)

# ------------------ HEADER ------------------
st.markdown('<div class="title">🌍 Premium Air & Water Quality Dashboard</div>', unsafe_allow_html=True)

# ------------------ HELPERS ------------------
def pollutant_color(value):
    if value < 50: return "#16A34A"   # Good
    if value < 100: return "#EAB308"  # Moderate
    return "#DC2626"                 # Poor

def map_air_label(x): return {0:"Good",1:"Moderate",2:"Poor"}.get(x, "Unknown")
def air_color(x): return {"Good":"#16A34A","Moderate":"#EAB308","Poor":"#DC2626"}.get(x)
def map_water_label(x): return "Drinkable" if x==1 else "Not Drinkable"
def water_color(x): return {"Drinkable":"#16A34A","Not Drinkable":"#DC2626"}.get(x)

# =================================================================
# AIR QUALITY SECTION
# =================================================================
st.markdown('<div class="section-title">🌬️ Real-Time Air Quality</div>', unsafe_allow_html=True)
st.markdown('<div class="glass-card">', unsafe_allow_html=True)

city = st.text_input("Enter City for AQI Data")

if st.button("Fetch AQI", use_container_width=True):
    try:
        c = city.lower().strip()
        if c in CITY_ALIASES: city = CITY_ALIASES[c]

        data = get_air_quality_for_city(city)

        cols = st.columns(3)
        keys = list(data.keys())

        for i, (k,v) in enumerate(data.items()):
            with cols[i % 3]:
                st.markdown(f"<div class='indicator' style='background:{pollutant_color(v)};'> {k.upper()}: {v} </div>", unsafe_allow_html=True)

        model = joblib.load(os.path.join(BASE_DIR, "models", "air_quality_model.pkl"))
        pred = map_air_label(model.predict([[x for x in data.values()]])[0])

        st.markdown(f'<h3 style="text-align:center;margin-top:20px;color:{air_color(pred)}">🌫️ Air Quality: {pred}</h3>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"API ERROR → {e}")

st.markdown('</div>', unsafe_allow_html=True)

# =================================================================
# TOMORROW AQI PREDICTION
# =================================================================
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">📈 Tomorrow AQI Prediction</div>', unsafe_allow_html=True)

today = st.number_input("Today's AQI", min_value=0.0)
yesterday = st.number_input("Yesterday's AQI", min_value=0.0)

if st.button("Predict Tomorrow", use_container_width=True):
    tmr = today*0.6 + yesterday*0.4

    df = pd.DataFrame({"Day":["Yesterday","Today","Tomorrow"], "AQI":[yesterday,today,tmr]})
    st.line_chart(df.set_index("Day"))

    if tmr > 150:
        st.error("⚠️ HIGH pollution! MASK COMPULSORY.")
    elif tmr > 100:
        st.warning("😷 Moderate pollution. Mask recommended.")
    else:
        st.success("🌱 Air quality good.")

st.markdown('</div>', unsafe_allow_html=True)

# =================================================================
# WATER QUALITY SECTION
# =================================================================
st.markdown('<div class="section-title">💧 Water Quality Check</div>', unsafe_allow_html=True)
st.markdown('<div class="glass-card">', unsafe_allow_html=True)

city2 = st.text_input("Enter City for Water Quality")

if st.button("Check Water", use_container_width=True):
    try:
        c2 = CITY_ALIASES.get(city2.lower().strip(), city2).title()
        if c2 not in df_water["City"].tolist():
            st.error("City not found in dataset")
        else:
            row = df_water[df_water["City"] == c2].iloc[0]
            ph, hard, sol = row["pH"], row["Hardness"], row["Solids"]

            st.table(pd.DataFrame({"Parameter":["pH", "Hardness", "Solids"], "Value":[ph, hard, sol]}))

            model = joblib.load(os.path.join(BASE_DIR, "models", "water_quality_model.pkl"))
            pred = map_water_label(model.predict([[ph, hard, sol]])[0])

            st.markdown(f'<h3 style="text-align:center;margin-top:20px;color:{water_color(pred)}">💧 Water Quality: {pred}</h3>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"WATER ERROR → {e}")

st.markdown('</div>', unsafe_allow_html=True)

# =================================================================
# FOOTER
# =================================================================
st.markdown("<p style='text-align:center;margin-top:30px;font-size:16px;'>Premium Dashboard ✨ | Built with ❤️</p>", unsafe_allow_html=True)
