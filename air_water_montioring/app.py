import streamlit as st
import joblib
import pandas as pd
import os
import plotly.express as px
from utils import get_air_quality_for_city

# ---------------------------------------------------------
# PAGE CONFIG + GLOBAL STYLE
# ---------------------------------------------------------
st.set_page_config(
    page_title="Air & Water Quality Monitoring",
    page_icon="🌍",
    layout="wide",
)

# ---- CLEAN SKY-BLUE BACKGROUND ----
st.markdown(
    """
    <style>
        .stApp {
            background: linear-gradient(180deg, #c9e8ff, #a8d4ff);
            font-family: 'Segoe UI', sans-serif;
        }

        .main-title {
            font-size: 46px;
            text-align: center;
            font-weight: 900;
            color: #05396b;
            margin-top: -10px;
            margin-bottom: 20px;
        }

        .section-title {
            font-size: 30px;
            color: #05396b;
            font-weight: 800;
            margin-bottom: 10px;
        }

        .tag-box {
            background: #e7f3ff;
            padding: 14px;
            border-radius: 10px;
            border-left: 5px solid #2a7ae2;
            margin-bottom: 15px;
            color: #05396b;
            font-weight: 600;
        }

        .card {
            background: white;
            padding: 25px;
            border-radius: 16px;
            box-shadow: 0 6px 22px rgba(0,0,0,0.15);
            margin-bottom: 25px;
        }

        .metric-good { background:#d5f5d5; padding:10px; border-radius:8px; color:#0c7a0c; font-weight:700; }
        .metric-moderate { background:#fff3cd; padding:10px; border-radius:8px; color:#a67c00; font-weight:700; }
        .metric-poor { background:#f8d7da; padding:10px; border-radius:8px; color:#a80000; font-weight:700; }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# TITLE
# ---------------------------------------------------------
st.markdown("<div class='main-title'>🌍 Air & Water Quality Monitoring</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# LOAD WATER DATA
# ---------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
water_path = os.path.join(BASE_DIR, "data", "water_quality_cities.csv")
df_water = pd.read_csv(water_path)
df_water.columns = df_water.columns.str.lower().str.replace(" ", "_")

CITY_ALIASES = {
    "bangalore": "bengaluru",
    "banglore": "bengaluru",
    "bombay": "mumbai",
}

# AQI category from pollutants
def aqi_category(pm25, pm10, no2):
    if pm25 <= 30 and pm10 <= 50 and no2 <= 40:
        return "Good"
    elif pm25 <= 60 and pm10 <= 100 and no2 <= 80:
        return "Moderate"
    else:
        return "Poor"


# =========================================================
# 🌫️ AIR QUALITY SECTION
# =========================================================
st.markdown("<div class='section-title'>🌫️ Air Quality</div>", unsafe_allow_html=True)

# Tagline box
st.markdown(
    "<div class='tag-box'>🌬️ The air you breathe affects your health. Track pollution levels & stay safe.</div>",
    unsafe_allow_html=True,
)

with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    city_air = st.text_input("Enter city name for Air Quality")

    if st.button("Fetch Air Quality"):
        try:
            city_fixed = CITY_ALIASES.get(city_air.lower().strip(), city_air)
            pollutants, weather, _ = get_air_quality_for_city(city_fixed)

            st.subheader(f"Air Quality in {city_fixed.title()}")

            cols = st.columns(3)
            pollutant_labels = {
                "pm2_5": "PM2.5",
                "pm10": "PM10",
                "no2": "NO₂",
                "so2": "SO₂",
                "o3": "O₃",
                "co": "CO",
            }

            for i, key in enumerate(pollutants.keys()):
                cols[i % 3].metric(
                    pollutant_labels[key],
                    round(pollutants[key], 2)
                )

            category = aqi_category(
                pollutants["pm2_5"], pollutants["pm10"], pollutants["no2"]
            )

            # Category box
            if category == "Good":
                st.markdown("<div class='metric-good'>🌿 Air Quality: GOOD — Safe to breathe</div>", unsafe_allow_html=True)
            elif category == "Moderate":
                st.markdown("<div class='metric-moderate'>😷 Air Quality: MODERATE — Sensitive individuals should be cautious</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='metric-poor'>🚨 Air Quality: POOR — Avoid outdoor exposure</div>", unsafe_allow_html=True)

        except Exception as e:
            st.error(str(e))

    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# 💧 WATER QUALITY SECTION
# =========================================================
st.markdown("<div class='section-title'>💧 Water Quality</div>", unsafe_allow_html=True)

# Tagline box
st.markdown(
    "<div class='tag-box'>💧 Clean water is essential for a healthy life. Check safety levels below.</div>",
    unsafe_allow_html=True,
)

with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    city_water = st.text_input("Enter city name for Water Quality")

    if st.button("Fetch Water Quality"):
        try:
            c2 = CITY_ALIASES.get(city_water.lower().strip(), city_water).title()

            if c2.lower() not in df_water["city"].astype(str).str.lower().values:
                st.error("City not found in water dataset.")
            else:
                row = df_water[df_water["city"].str.lower() == c2.lower()].iloc[0]

                st.subheader(f"Water Quality in {c2}")

                cols = st.columns(3)
                parameters = ["ph", "hardness", "solids"]

                for i, key in enumerate(parameters):
                    cols[i % 3].metric(key.upper(), round(row[key], 2))

                model = joblib.load(os.path.join(BASE_DIR, "models", "water_quality_model.pkl"))
                pred = model.predict([[row["ph"], row["hardness"], row["solids"]]])[0]

                if pred == 1:
                    st.markdown("<div class='metric-good'>💧 Water is SAFE for drinking</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div class='metric-poor'>🚱 Water is NOT SAFE for drinking</div>", unsafe_allow_html=True)

        except Exception as e:
            st.error(str(e))

    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# 📊 COMPARISON BETWEEN TWO CITIES
# =========================================================
st.markdown("<div class='section-title'>📊 Compare PM2.5 Levels Between Cities</div>", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    c1 = st.text_input("City 1")
    c2 = st.text_input("City 2")

    if st.button("Compare"):
        try:
            p1, _, _ = get_air_quality_for_city(c1)
            p2, _, _ = get_air_quality_for_city(c2)

            df = pd.DataFrame({
                "City": [c1.title(), c2.title()],
                "PM2.5": [p1["pm2_5"], p2["pm2_5"]],
            })

            fig = px.bar(df, x="City", y="PM2.5", color="City", title="PM2.5 Comparison")
            st.plotly_chart(fig)

        except Exception as e:
            st.error(str(e))

    st.markdown("</div>", unsafe_allow_html=True)

