import streamlit as st
import numpy as np
import joblib
import pandas as pd
import os
from utils import get_air_quality_for_city

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
water_csv_path = os.path.join(BASE_DIR, "data", "water_quality_cities.csv")

df_water = pd.read_csv(water_csv_path)

CITY_ALIASES = {
    "bangalore": "bengaluru",
    "banglore": "bengaluru",
    "bombay": "mumbai"
}

st.set_page_config(page_title="Smart Air & Water Quality", page_icon="🌍", layout="centered")

# Night mode toggle
if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = False

theme = "dark" if st.session_state["dark_mode"] else "light"

# Apply theme
st.markdown(f"""
<style>
body {{ transition: 0.4s; }}
.light .stApp {{ background: linear-gradient(135deg,#4FACFE,#00F2FE); color:#000; }}
.dark .stApp {{ background: radial-gradient(circle,#0f172a,#020617); color:#fff; }}
.card {{ padding:30px; border-radius:20px; background:rgba(255,255,255,0.1); backdrop-filter:blur(10px); margin-top:20px; }}
.title {{ font-size:50px; text-align:center; font-weight:900; color:white; }}
.sub { font-size:34px; text-align:center; font-weight:800; color:#38bdf8; }
</style>
<script>
window.parent.document.querySelector('body').className = '""" + theme + """';
</script>
""", unsafe_allow_html=True)

# Toggle button
if st.button("🌙 Night Mode" if not st.session_state["dark_mode"] else "☀️ Light Mode"):
    st.session_state["dark_mode"] = not st.session_state["dark_mode"]
    st.rerun()

st.markdown('<p class="title">🌍 Smart Air & Water Quality Monitoring</p>', unsafe_allow_html=True)

# Label mappers
def map_air_label(x): return {0:"Good",1:"Moderate",2:"Poor"}.get(x, "Unknown")
def air_color(x): return {"Good":"#16A34A","Moderate":"#EAB308","Poor":"#DC2626"}[x]
def map_water_label(x): return "Drinkable" if x==1 else "Not Drinkable"
def water_color(x): return {"Drinkable":"#16A34A","Not Drinkable":"#DC2626"}[x]

# ---------------- AIR QUALITY SECTION ----------------
st.markdown('<p class="sub">🌬️ Air Quality Check</p>', unsafe_allow_html=True)
st.markdown('<div cl
