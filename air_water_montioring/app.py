# FULL REWRITTEN STREAMLIT APP – CLEAN, STABLE & ERROR-FREE

import streamlit as st
import numpy as np
import joblib
import pandas as pd
import os
from utils import get_air_quality_for_city

# ------------------------------------------------------
# PATHS
# ------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
water_csv_path = os.path.join(BASE_DIR, "data", "water_quality_cities.csv")

df_water = pd.read_csv(water_csv_path)

CITY_ALIASES = {
    "bangalore": "bengaluru",
    "banglore": "bengaluru",
    "bombay": "mumbai"
}

# ------------------------------------------------------
# PAGE SETUP
# ------------------------------------------------------
st.set_page_config(page_title="Smart Air & Water Quality", page_icon="🌍", layout="centered")

# Dark mode toggle
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

theme = "dark" if st.session_state.dark_mode else "light"

# ------------------------------------------------------
# SAFE & CLEAN CSS
# ------------------------------------------------------
st.markdown(
    f"""
    <style>
    body {{ transition: 0.4s; }}

    .light .stApp {{
        background: linear-gradient(135deg,#4FACFE,#00F2FE);
        color: #000;
    }}
    .dark .stApp {{
        background: radial-gradient(circle,#0f172a,#020617);
        color: #fff;
    }}

    .card {{
        padding: 30px;
        border-radius: 20px;
        background: rgba(255,255,255,0.08);
        backdrop-filter: blur(10px);
        margin-top: 22px;
    }}

    .title {{ text-align:center; font-size:50px; font-weight:900; color:white; }}
    .sub   {{ text-align:center; font-size:34px; font-weight:800; color:#38bdf8; }}
    </style>

    <script>
    window.parent.document.querySelector('body').className = '{theme}';
    </script>
    """,
    unsafe_allow_html=True
)

# Toggle button
if st.button("🌙 Night Mode" if not st.session_state.dark_mode else "☀️ Light Mode"):
    st.session_state.dark_mode = not st.session_state.dark_mode
    st.rerun()

# ------------------------------------------------------
# HEADER
# ------------------------------------------------------
st.markdown('<p class="title">🌍 Smart Air & Water Quality Monitoring</p>', unsafe_allow_html=True)

# Label/Color Helpers
def map_air_label(x): return {0:"Good",1:"Moderate",2:"Poor"}.get(x, "Unknown")
def air_color(x): return {"Good":"#16A34A","Moderate":"#EAB308","Poor":"#DC2626"}[x]
def map_water_label(x): return "Drinkable" if x==1 else "Not Drinkable"
def water_color(x): return {"Drinkable":"#16A34A","Not Drinkable":"#DC2626"}[x]

# ------------------------------------------------------
# AIR QUALITY SECTION
# ------------------------------------------------------
st.markdown('<p class="sub">🌬️ Air Quality Check</p>', unsafe_allow_html=True)
st.markdown('<div class="card">', unsafe_allow_html=True)

city = st.text_input("Enter City (Air Quality)")

if st.button("Get Air Quality", use_container_width=True):
    try:
        c = city.strip().lower()
        if c in CITY_ALIASES:
            city = CITY_ALIASES[c]

        data = get_air_quality_for_city(city)
        st.write(data)

        model = joblib.load(os.path.join(BASE_DIR, "models", "air_quality_model.pkl"))
        X = np.array([[data[i] for i in data]])
        pred = model.predict(X)[0]

        label = map_air_label(pred)
        color = air_color(label)

        st.markdown(f'<div style="background:{color};padding:20px;border-radius:12px;text-align:center;font-size:28px;color:white;">{label} Air Quality</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"API ERROR → {e}")

st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------------------
# AIR TOMORROW PREDICTION
# ------------------------------------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("<h3>Predict Tomorrow's Air Quality</h3>", unsafe_allow_html=True)

today = st.number_input("Today's AQI", min_value=0.0)
yesterday = st.number_input("Yesterday's AQI", min_value=0.0)

if st.button("Predict Tomorrow AQI", use_container_width=True):
    tomorrow = today * 0.6 + yesterday * 0.4
    df = pd.DataFrame({"Day":["Yesterday","Today","Tomorrow"],"AQI":[yesterday,today,tomorrow]})
    st.line_chart(df.set_index("Day"))

    if tomorrow > 150:
        st.error("⚠️ HIGH pollution! Mask is compulsory.")
    elif tomorrow > 100:
        st.warning("😷 Moderate pollution. Mask recommended.")
    else:
        st.success("🌱 Air Quality is good.")

st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------------------
# WATER QUALITY SECTION
# ------------------------------------------------------
st.markdown('<p class="sub">💧 Water Quality Prediction</p>', unsafe_allow_html=True)
st.markdown('<div class="card">', unsafe_allow_html=True)

city2 = st.text_input("Enter City (Water Quality)")

if st.button("Check Water Quality", use_container_width=True):
    try:
        c2 = city2.strip().lower()
        c2 = CITY_ALIASES.get(c2, c2).title()

        if c2 not in df_water["City"].tolist():
            st.error("City not found in water dataset")
        else:
            row = df_water[df_water["City"] == c2].iloc[0]
            ph, hard, sol = row["pH"], row["Hardness"], row["Solids"]
            st.write({"pH":ph, "Hardness":hard, "Solids":sol})

            model = joblib.load(os.path.join(BASE_DIR, "models", "water_quality_model.pkl"))
            pred = model.predict([[ph, hard, sol]])[0]

            label = map_water_label(pred)
            color = water_color(label)

            st.markdown(f'<div style="background:{color};padding:20px;border-radius:12px;text-align:center;font-size:28px;color:white;">{label}</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"WATER ERROR → {e}")

st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------------------
# WATER TOMORROW PREDICTION
# ------------------------------------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("<h3>Predict Tomorrow's Water Quality</h3>", unsafe_allow_html=True)

today_w = st.number_input("Today's WQI", min_value=0.0)
yesterday_w = st.number_input("Yesterday's WQI", min_value=0.0)

if st.button("Predict Tomorrow WQI", use_container_width=True):
    tomorrow_w = (today_w + yesterday_w) / 2

    df_w = pd.DataFrame({"Day":["Yesterday","Today","Tomorrow"],"WQI":[yesterday_w,today_w,tomorrow_w]})
    st.line_chart(df_w.set_index("Day"))

    if tomorrow_w < 50:
        st.error("🚱 Water unsafe! Do NOT drink.")
    elif tomorrow_w < 80:
        st.warning("⚠️ Water quality moderate.")
    else:
        st.success("💧 Water is safe.")

st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------------------
# FOOTER
# ------------------------------------------------------
st.markdown("<p style='text-align:center;color:white;font-size:18px;margin-top:25px;'>Designed with ❤️ for Academic Project</p>", unsafe_allow_html=True)
