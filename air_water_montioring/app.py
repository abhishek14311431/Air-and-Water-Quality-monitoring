import streamlit as st
import joblib
import pandas as pd
import numpy as np
import os
import plotly.express as px
from utils import get_air_quality_for_city  # returns (pollutants, weather)


# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="Air & Water Quality Monitoring",
    page_icon="🌍",
    layout="wide",
)


# ---------------------------------------------------------
# GLOBAL CSS (Sky Blue Background + Clean UI)
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
    font-weight: 900;
    text-align: center;
    color: #001f33;
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
    font-size: 17px;
    border-left: 5px solid #0077cc;
    margin-bottom: 15px;
}
.metric-large {
    font-size: 28px;
}
.icon-large {
    font-size: 36px;
    font-weight: bold;
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
# EMOJI STATUS FUNCTION
# ---------------------------------------------------------
def emoji_status(value, good, moderate):
    if value <= good:
        return "🟢"
    elif value <= moderate:
        return "🟡"
    return "🔴"


# =========================================================
# 🌫️ AIR QUALITY + WEATHER
# =========================================================
st.markdown("<div class='section-title'>🌫️ Air Quality & Weather</div>", unsafe_allow_html=True)

st.markdown("""
<div class="tagline-box">
🌬️ The air you breathe affects your health. Check real-time pollution levels & stay protected.
</div>
""", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    city_air = st.text_input("Enter City for Air Quality + Weather")

    if st.button("Fetch Air Quality"):
        try:
            city_fixed = CITY_ALIASES.get(city_air.lower().strip(), city_air)
            pollutants, weather = get_air_quality_for_city(city_fixed)

            # ---------------- Weather ----------------
            st.subheader(f"Weather in {city_fixed.title()}")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("🌡️ Temperature", f"{weather['temp']}°C")
            with col2:
                st.metric("💧 Humidity", f"{weather['humidity']}%")
            with col3:
                st.metric("🌬️ Wind Speed", f"{weather['wind']} m/s")

            st.markdown("---")

            # ---------------- Air Pollutants ----------------
            st.subheader(f"Pollutant Levels in {city_fixed.title()}")

            limits = {
                "pm2_5": (30, 60),
                "pm10": (50, 100),
                "no2": (40, 80),
                "so2": (20, 80),
                "o3": (50, 100),
                "co": (200, 400),
            }

            cols = st.columns(3)
            i = 0

            for key, val in pollutants.items():
                good, moderate = limits[key]
                emoji = emoji_status(val, good, moderate)

                with cols[i % 3]:
                    st.markdown(
                        f"<div class='metric-large'><span class='icon-large'>{emoji}</span> "
                        f"{key.upper()}: {round(val, 2)}</div>",
                        unsafe_allow_html=True,
                    )
                i += 1

            st.markdown("---")

            # ---------------- AQI Category ----------------
            pm = pollutants["pm2_5"]
            if pm <= 30:
                st.success("🟢 AQI: Good — Air is safe to breathe.")
            elif pm <= 60:
                st.warning("🟡 AQI: Moderate — Sensitive groups should limit outdoor exposure.")
            else:
                st.error("🔴 AQI: Poor — Avoid outdoor exposure!")

        except Exception as e:
            st.error(str(e))

    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# 💧 WATER QUALITY
# =========================================================
st.markdown("<div class='section-title'>💧 Water Quality</div>", unsafe_allow_html=True)

st.markdown("""
<div class="tagline-box" style="border-left-color:#00aa66;">
💧 Clean water is essential for life. Check if the water in your city is safe to drink.
</div>
""", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    city_water = st.text_input("Enter City for Water Quality")

    if st.button("Fetch Water Quality"):
        try:
            city_fixed = CITY_ALIASES.get(city_water.lower().strip(), city_water)

            if city_fixed not in df_water["city"].str.lower().values:
                st.error("City not found in water dataset.")
            else:
                row = df_water[df_water["city"].str.lower() == city_fixed].iloc[0]
                st.subheader(f"Water Parameters — {row['city'].title()}")

                water_limits = {
                    "ph": (6.5, 8.5),
                    "hardness": (150, 300),
                    "solids": (300, 600),
                    "chloramines": (2, 4),
                    "sulfate": (100, 250),
                    "conductivity": (200, 400),
                    "organic_carbon": (2, 4),
                    "trihalomethanes": (40, 80),
                    "turbidity": (1, 3),
                }

                cols = st.columns(3)
                i = 0

                for key in water_limits.keys():
                    if key in row:
                        val = row[key]
                        good, moderate = water_limits[key]
                        emoji = emoji_status(val, good, moderate)

                        with cols[i % 3]:
                            st.markdown(
                                f"<div class='metric-large'>"
                                f"<span class='icon-large'>{emoji}</span> "
                                f"{key.replace('_',' ').title()}: {round(val,2)}"
                                f"</div>",
                                unsafe_allow_html=True)
                        i += 1

                st.markdown("---")

                # ------ ML Prediction (pH, Hardness, Solids) ------
                model_path = os.path.join(BASE_DIR, "models", "water_quality_model.pkl")
                model = joblib.load(model_path)

                features = [[row["ph"], row["hardness"], row["solids"]]]
                pred = model.predict(features)[0]

                if pred == 1:
                    st.success("🟢 ML Prediction: Water is safe to drink.")
                else:
                    st.error("🔴 ML Prediction: Water is NOT safe to drink.")

        except Exception as e:
            st.error(str(e))

    st.markdown("</div>", unsafe_allow_html=True)



# =========================================================
# 📊 CITY COMPARISON PIE CHART
# =========================================================
st.markdown("<div class='section-title'>📊 Compare PM2.5 Levels Across Cities</div>", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    city_list = st.text_input("Enter up to 3 cities separated by commas")

    if st.button("Compare Cities"):
        try:
            input_cities = [c.strip() for c in city_list.split(",") if c.strip()]
            input_cities = input_cities[:3]  # max 3

            labels, values = [], []

            for c in input_cities:
                fixed = CITY_ALIASES.get(c.lower(), c)
                pollutants, _ = get_air_quality_for_city(fixed)

                if "pm2_5" in pollutants:
                    labels.append(fixed.title())
                    values.append(pollutants["pm2_5"])

            df = pd.DataFrame({"City": labels, "PM2.5": values})

            color_map = {}
            for city, pm in zip(labels, values):
                if pm <= 30:
                    color_map[city] = "green"
                elif pm <= 60:
                    color_map[city] = "orange"
                else:
                    color_map[city] = "red"

            fig = px.pie(
                df,
                names="City",
                values="PM2.5",
                title="PM2.5 Comparison",
                color="City",
                color_discrete_map=color_map,
                hole=0.3
            )

            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(str(e))

    st.markdown("</div>", unsafe_allow_html=True)
