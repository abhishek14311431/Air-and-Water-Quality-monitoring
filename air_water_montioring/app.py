# 🚀 GDUI PREMIUM DASHBOARD — CLEAN, COMPACT, SIDE-BY-SIDE LAYOUT
# -------------------------------------------------------------------
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

# ------------------ CITY ALIASES ------------------
CITY_ALIASES = {"bangalore":"bengaluru", "banglore":"bengaluru", "bombay":"mumbai"}

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="GDU Premium Dashboard", page_icon="🌍", layout="wide")

# ------------------ NIGHT MODE ------------------
if "dark" not in st.session_state:
    st.session_state.dark = False

st.session_state.dark = st.toggle("🌙 Night Mode", value=st.session_state.dark)
mode = "dark" if st.session_state.dark else "light"

# ------------------ PREMIUM GDU CSS ------------------
st.markdown(f"""
<style>
body {{ transition:0.4s; }}

.light .main-bg {{ background:#eef2ff; color:#1e293b; }}
.dark .main-bg  {{ background:#0f172a; color:white; }}

.dashboard-title {{ text-align:center; font-size:38px; font-weight:900; margin-bottom:15px; }}

.gdu-card {{
    background:rgba(255,255,255,0.12);
    border-radius:18px;
    padding:22px;
    backdrop-filter:blur(12px);
    box-shadow:0 4px 20px rgba(0,0,0,0.25);
    animation:fadeIn .7s ease;
}}

@keyframes fadeIn {{ from {{opacity:0; transform:translateY(10px);}} to {{opacity:1; transform:translateY(0);}} }}

.indicator {{
    border-radius:12px;
    padding:12px;
    margin:6px 0;
    text-align:center;
    font-size:20px;
    font-weight:700;
    animation:pulse 1.6s infinite;
}}

@keyframes pulse {{ 0%{{transform:scale(1);}} 50%{{transform:scale(1.05);}} 100%{{transform:scale(1);}} }}
</style>
<script> window.parent.document.body.className = '{mode} main-bg'; </script>
""", unsafe_allow_html=True)

# ------------------ HELPERS ------------------
def pollutant_color(v): return "#16a34a" if v<50 else "#eab308" if v<100 else "#dc2626"
def map_air_label(x): return {0:"Good",1:"Moderate",2:"Poor"}.get(x)
def air_color(x): return {"Good":"#16A34A","Moderate":"#EAB308","Poor":"#DC2626"}[x]
def map_water_label(x): return "Drinkable" if x==1 else "Not Drinkable"
def water_color(x): return {"Drinkable":"#16A34A","Not Drinkable":"#DC2626"}[x]

# ------------------ HEADER ------------------
st.markdown('<div class="dashboard-title">🌍 GDU Premium Air + Water Quality Dashboard</div>', unsafe_allow_html=True)

# ================================================================
# SIDE-BY-SIDE DASHBOARD LAYOUT
# ================================================================
col_air, col_water = st.columns(2, gap="large")

# ------------------ AIR QUALITY SECTION ------------------
with col_air:
    st.markdown('<div class="gdu-card">', unsafe_allow_html=True)
    st.subheader("🌫️ Air Quality")

    city = st.text_input("City (Air Quality)")

    if st.button("Fetch AQI", key="aqi-btn", use_container_width=True):
        try:
            c = city.lower().strip()
            if c in CITY_ALIASES: city = CITY_ALIASES[c]

            data = get_air_quality_for_city(city)
            st.success(f"Live AQI Data for {city.title()}")

            for k,v in data.items():
                st.markdown(f"<div class='indicator' style='background:{pollutant_color(v)}'>{k.upper()}: {v}</div>", unsafe_allow_html=True)

            model = joblib.load(os.path.join(BASE_DIR, "models", "air_quality_model.pkl"))
            pred = map_air_label(model.predict([[*data.values()]])[0])

            st.markdown(f"<h4 style='text-align:center;color:{air_color(pred)}'>Air Quality: {pred}</h4>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"API ERROR → {e}")

    st.markdown('</div>', unsafe_allow_html=True)

    # ---- Tomorrow AQI ----
    st.markdown('<div class="gdu-card">', unsafe_allow_html=True)
    st.subheader("📈 Tomorrow AQI Forecast")
    today = st.number_input("Today's AQI", min_value=0.0)
    yesterday = st.number_input("Yesterday's AQI", min_value=0.0)

    if st.button("Predict Tomorrow", key="aqi-predict", use_container_width=True):
        tmr = today*0.6 + yesterday*0.4
        df = pd.DataFrame({"Day":["Yesterday","Today","Tomorrow"], "AQI":[yesterday,today,tmr]})
        st.line_chart(df.set_index("Day"))

        if tmr > 150: st.error("⚠️ HIGH pollution! Mask required.")
        elif tmr > 100: st.warning("😷 Moderate pollution.")
        else: st.success("🌱 Good air quality.")

    st.markdown('</div>', unsafe_allow_html=True)

# ------------------ WATER QUALITY SECTION ------------------
with col_water:
    st.markdown('<div class="gdu-card">', unsafe_allow_html=True)
    st.subheader("💧 Water Quality")

    city2 = st.text_input("City (Water Quality)")

    if st.button("Check Water", key="water-btn", use_container_width=True):
        try:
            c2 = CITY_ALIASES.get(city2.lower().strip(), city2).title()
            if c2 not in df_water["City"].tolist(): st.error("City not in dataset")
            else:
                row = df_water[df_water["City"] == c2].iloc[0]
                ph, hard, sol = row["pH"], row["Hardness"], row["Solids"]

                st.table(pd.DataFrame({"Parameter":["pH","Hardness","Solids"],"Value":[ph,hard,sol]}))

                model = joblib.load(os.path.join(BASE_DIR, "models", "water_quality_model.pkl"))
                pred = map_water_label(model.predict([[ph,hard,sol]])[0])

                st.markdown(f"<h4 style='text-align:center;color:{water_color(pred)}'>Water Quality: {pred}</h4>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"WATER ERROR → {e}")

    st.markdown('</div>', unsafe_allow_html=True)

# ------------------ FOOTER ------------------
st.markdown("<p style='text-align:center;margin-top:25px;font-size:16px;'>GDU Premium Dashboard ✨ | Built with ❤️</p>", unsafe_allow_html=True)
