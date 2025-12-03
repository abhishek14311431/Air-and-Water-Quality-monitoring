import streamlit as st
import numpy as np
import joblib
import pandas as pd
import os
from utils import get_air_quality_for_city

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

st.markdown("""
<style>
html, body, [class*="css"] { font-size: 20px; }
.stApp {
    background: linear-gradient(135deg, #4FACFE 0%, #00F2FE 100%);
    background-attachment: fixed;
    font-family: "Segoe UI";
}
.title {
    font-size: 60px;
    text-align:center;
    font-weight: 900;
    margin-bottom: 10px;
    color: white;
}
.sub {
    font-size: 38px;
    font-weight: 900;
    margin-top: 35px;
    text-align:center;
    color: #051B33;
}
.card {
    width: 80%;
    margin: 0 auto;
    background: rgba(255,255,255,0.75);
    backdrop-filter: blur(8px);
    padding: 40px;
    border-radius: 25px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.32);
    margin-top: 18px;
}
.result-box {
    padding: 20px;
    border-radius: 16px;
    text-align:center;
    font-size: 32px;
    font-weight: 900;
    margin-top: 25px;
    color:white;
}
input, textarea, .stNumberInput, .stTextInput { font-size: 22px !important; }
div.stButton > button {
    font-size: 22px;
    padding: 12px 25px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

def map_air_label(x):
    return {0:"Good",1:"Moderate",2:"Poor"}.get(x,"Unknown")

def air_color(x):
    return {"Good":"#16A34A","Moderate":"#EAB308","Poor":"#DC2626"}.get(x,"#1E3A8A")

def map_water_label(x):
    return "Drinkable" if x == 1 else "Not Drinkable"

def water_color(x):
    return {"Drinkable":"#16A34A","Not Drinkable":"#DC2626"}.get(x,"#1E3A8A")

st.markdown('<p class="title">🌍 Smart Air & Water Quality Monitoring</p>', unsafe_allow_html=True)

# AIR SECTION
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

        model = joblib.load(os.path.join(BASE_DIR,"models","air_quality_model.pkl"))
        X = np.array([[data[i] for i in data]])
        pred = model.predict(X)[0]

        label = map_air_label(pred)
        color = air_color(label)

        st.markdown(
            f'<div class="result-box" style="background:{color};">{label} Air Quality</div>',
            unsafe_allow_html=True
        )

    except Exception as e:
        st.error("Invalid City or API Error")

st.markdown('</div>', unsafe_allow_html=True)

# WATER SECTION
st.markdown('<p class="sub">💧 Water Quality Prediction</p>', unsafe_allow_html=True)
st.markdown('<div class="card">', unsafe_allow_html=True)

city2 = st.text_input("Enter City (Water Quality)")

if st.button("Check Water Quality", use_container_width=True):
    c2 = city2.strip().lower()
    if c2 in CITY_ALIASES:
        c2 = CITY_ALIASES[c2].title()
    else:
        c2 = city2.strip().title()

    if c2 not in list(df_water["City"]):
        st.error("City not found in water dataset")
    else:
        row = df_water[df_water["City"] == c2].iloc[0]
        ph = row["pH"]
        hardness = row["Hardness"]
        solids = row["Solids"]

        st.markdown("<h3>Measured Water Parameters</h3>", unsafe_allow_html=True)
        st.write({"pH": ph, "Hardness": hardness, "Solids": solids})

        model = joblib.load(os.path.join(BASE_DIR,"models","water_quality_model.pkl"))
        Xw = np.array([[ph, hardness, solids]])
        pred = model.predict(Xw)[0]

        label = map_water_label(pred)
        color = water_color(label)

        st.markdown(
            f'<div class="result-box" style="background:{color};">{label} Water Quality</div>',
            unsafe_allow_html=True
        )

st.markdown('</div>', unsafe_allow_html=True)

st.markdown(
    "<p style='text-align:center;color:white;font-weight:700;margin-top:25px;font-size:20px;'>Designed with ❤️ for Academic Project</p>",
    unsafe_allow_html=True
)
