import streamlit as st
import joblib
import pandas as pd
import numpy as np
import os
import plotly.express as px
from utils import get_air_quality_for_city

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="Air & Water Quality Monitoring",
    page_icon="🌍",
    layout="wide",
)

# ---------------------------------------------------------
# GLOBAL CSS + BACKGROUND
# ---------------------------------------------------------
st.markdown("""
<style>
.stApp {
    background-color: #d9eefe;
    background-image: linear-gradient(135deg, #e9f4ff 0%, #cfe4fa 100%);
    font-family: 'Segoe UI', sans-serif;
}
.main-title {
    font-size: 46px;
    text-align: center;
    font-weight: 900;
    color: #0a0a0a;
}
.section-title {
    font-size: 32px;
    color: #003366;
    font-weight: 800;
    margin-bottom: 4px;
}
.card {
    background: white;
    padding: 26px;
    border-radius: 16px;
    box-shadow: 0px 6px 25px rgba(0,0,0,0.12);
    margin-bottom: 20px;
}
.tagline-box {
    background: white;
    padding: 16px;
    border-radius: 12px;
    font-weight: 600;
    border-left: 5px solid #0077cc;
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)

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

# ---------------------------------------------------------
# HELPER — Status + Emoji
# ---------------------------------------------------------
def emoji_status(value, low, med):
    if value <= low:
        return "🟢 Good"
    elif value <= med:
        return "🟡 Moderate"
    return "🔴 Poor"

# ---------------------------------------------------------
# 🌫️ AIR QUALITY SECTION
# ---------------------------------------------------------
st.markdown("<div class='section-title'>🌫️ Air Quality</div>", unsafe_allow_html=True)

st.markdown("""
<div class="tagline-box">
🌬️ The air you breathe affects your daily health. Track pollution levels & stay safe outdoors.
</div>
""", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    city_air = st.text_input("Enter city name for Air Quality")

    if st.button("Fetch Air Quality"):
        try:
            c = CITY_ALIASES.get(city_air.lower().strip(), city_air)
            
            # ❗ Fetch Air API (dict of pollutant values)
            pollutants = get_air_quality_for_city(c)

            st.subheader(f"Pollutant Levels in {c.title()}")

            limits = {
                "pm2_5": (30, 60),
                "pm10": (50, 100),
                "no2":  (40, 80),
                "so2":  (20, 80),
                "o3":   (50, 100),
                "co":   (200, 400)
            }

            cols = st.columns(3)

            for i, key in enumerate(pollutants.keys()):
                low, med = limits[key]
                status = emoji_status(pollutants[key], low, med)
                emoji = status.split()[0]

                with cols[i % 3]:
                    st.markdown(f"""
                        <div style='font-size:24px;'>
                            <b style='font-size:32px'>{emoji}</b>
                            <b>{key.upper()}</b>: {round(pollutants[key], 2)}
                        </div>
                    """, unsafe_allow_html=True)

            # ------- AI Category -------
            pm = pollutants["pm2_5"]

            if pm <= 30:
                st.success("🟢 Good — Air is safe to breathe.")
            elif pm <= 60:
                st.warning("🟡 Moderate — Sensitive people should limit outdoor exposure.")
            else:
                st.error("🔴 Poor — Avoid outdoor exposure!")

        except Exception as e:
            st.error(str(e))

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 💧 WATER QUALITY SECTION
# ---------------------------------------------------------
st.markdown("<div class='section-title'>💧 Water Quality</div>", unsafe_allow_html=True)

st.markdown("""
<div class="tagline-box" style="border-left-color:#00aa66;">
💧 Clean water is essential for health. Check if your city's water is safe to drink.
</div>
""", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    city_water = st.text_input("Enter city name for Water Quality")

    if st.button("Fetch Water Quality"):
        try:
            c2 = CITY_ALIASES.get(city_water.lower().strip(), city_water)

            if c2.lower() not in df_water["city"].str.lower().values:
                st.error("City not found in water dataset.")
            else:
                row = df_water[df_water["city"].str.lower() == c2.lower()].iloc[0]

                st.subheader(f"Water Parameters — {c2.title()}")

                water_limits = {
                    "ph": (6.5, 8.5),
                    "hardness": (150, 300),
                    "solids": (300, 600),
                    "chloramines": (2, 4),
                    "sulfate": (100, 250),
                    "conductivity": (200, 400),
                    "organic_carbon": (2, 4),
                    "trihalomethanes": (40, 80),
                    "turbidity": (1, 3)
                }

                cols = st.columns(3)

                for i, key in enumerate(water_limits.keys()):
                    val = row[key]
                    low, med = water_limits[key]
                    status = emoji_status(val, low, med)
                    emoji = status.split()[0]

                    with cols[i % 3]:
                        st.markdown(f"""
                        <div style='font-size:24px;'>
                            <b style='font-size:32px'>{emoji}</b>
                            <b>{key.replace('_',' ').title()}</b>: {round(val, 2)}
                        </div>
                        """, unsafe_allow_html=True)

                # ------- ML prediction -------
                model_w = joblib.load(os.path.join(BASE_DIR, "models", "water_quality_model.pkl"))
                pred_raw = model_w.predict([[row["ph"], row["hardness"], row["solids"]]])[0]

                if pred_raw == 1:
                    st.success("🟢 Water is safe to drink.")
                else:
                    st.error("🔴 Not safe for drinking.")

        except Exception as e:
            st.error(str(e))

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 📊 CITY COMPARISON (PM2.5)
# ---------------------------------------------------------
st.markdown("<div class='section-title'>📊 Compare PM2.5 Across Cities</div>", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    cities_input = st.text_input("Enter up to 3 cities (comma separated)")

    if st.button("Compare Cities"):
        try:
            cities = [c.strip() for c in cities_input.split(",") if c.strip()]
            names, values = [], []

            for c in cities:
                fixed = CITY_ALIASES.get(c.lower(), c)
                pm = get_air_quality_for_city(fixed)["pm2_5"]
                names.append(fixed.title())
                values.append(pm)

            df = pd.DataFrame({"City": names, "PM2.5": values})
            fig = px.pie(df, names="City", values="PM2.5", title="PM2.5 Comparison")
            st.plotly_chart(fig)

        except Exception as e:
            st.error(str(e))

    st.markdown("</div>", unsafe_allow_html=True)
