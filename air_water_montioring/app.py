import streamlit as st
import joblib
import pandas as pd
import os
import plotly.express as px
from utils import get_air_quality_for_city

# ---------------------------------------------------------
# PAGE CONFIG + GLOBAL STYLE
# ---------------------------------------------------------
st.set_page_config(page_title="Air & Water Quality Monitoring",
                   page_icon="🌍",
                   layout="wide")

st.markdown("""
<style>
.stApp {
    background-color: #dceaff;
    background-image: linear-gradient(135deg, #e8f1ff 0%, #cfe0ff 100%);
    font-family: 'Segoe UI', sans-serif;
}

.main-title {
    font-size: 46px;
    font-weight: 900;
    color: #0a0a0a;
    text-align: center;
}

.section-title {
    font-size: 32px;
    color: #003366;
    font-weight: 800;
    margin-top: 20px;
}

.card {
    background: white;
    padding: 28px;
    border-radius: 16px;
    box-shadow: 0 6px 25px rgba(0,0,0,0.12);
    margin-bottom: 25px;
}

.tag-box {
    background: #fff7cc;
    padding: 14px;
    border-radius: 12px;
    text-align: center;
    font-weight: 700;
    color: #7a6000;
    margin-bottom: 12px;
}

.metric-good {
    background: #d9ffe3;
    padding: 12px;
    border-radius: 10px;
    color: #075e28;
    font-weight: 800;
}

.metric-moderate {
    background: #fff3cd;
    padding: 12px;
    border-radius: 10px;
    color: #7a5c00;
    font-weight: 800;
}

.metric-poor {
    background: #ffd6d6;
    padding: 12px;
    border-radius: 10px;
    color: #7a0000;
    font-weight: 800;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# TITLE
# ---------------------------------------------------------
st.markdown("<div class='main-title'>🌍 Air & Water Quality Monitoring</div>", unsafe_allow_html=True)
st.write("Real-time pollution, weather data & ML predictions for health safety.")

# ---------------------------------------------------------
# LOAD WATER DATA
# ---------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
water_path = os.path.join(BASE_DIR, "data", "water_quality_cities.csv")

df_water = pd.read_csv(water_path)
df_water.columns = df_water.columns.str.lower().str.replace(" ", "_")

CITY_ALIASES = {"bangalore": "bengaluru", "banglore": "bengaluru", "bombay": "mumbai"}


# ---------------------------------------------------------
# AQI CATEGORY CALCULATION
# ---------------------------------------------------------
def aqi_category(pm25, pm10, no2):
    score = 0
    if pm25 > 60: score += 1
    if pm10 > 100: score += 1
    if no2 > 80: score += 1

    return "Good" if score == 0 else "Moderate" if score == 1 else "Poor"


# WEATHER ICONS
def weather_icon(name):
    icons = {
        "Clear": "🌞",
        "Clouds": "☁",
        "Rain": "🌧",
        "Thunderstorm": "⛈",
        "Snow": "❄",
        "Drizzle": "🌦",
        "Mist": "🌫",
        "Haze": "🌫",
        "Fog": "🌫"
    }
    return icons.get(name, "🌍")


# =========================================================
# 🌫 AIR QUALITY SECTION
# =========================================================
st.markdown("<div class='section-title'>🌫️ Air Quality</div>", unsafe_allow_html=True)

st.markdown("<div class='tag-box'>🌬️ Track real-time air pollution and weather to stay protected.</div>",
            unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    city_air = st.text_input("Enter city name for Air Quality")

    if st.button("Fetch Air Quality"):
        try:
            city_fixed = CITY_ALIASES.get(city_air.lower().strip(), city_air)

            pollutants, weather = get_air_quality_for_city(city_fixed)

            st.subheader(f"Air Quality in {city_fixed.title()}")

            cols = st.columns(3)
            labels = {
                "pm2_5": "PM2.5",
                "pm10": "PM10",
                "no2": "NO₂",
                "so2": "SO₂",
                "o3": "O₃",
                "co": "CO"
            }

            for i, key in enumerate(pollutants):
                cols[i % 3].metric(labels[key], round(pollutants[key], 2))

            # WEATHER SECTION
            st.subheader("🌦 Current Weather")
            wcols = st.columns(3)
            wcols[0].metric(f"{weather_icon(weather['condition'])} Condition", weather["condition"])
            wcols[1].metric("🌡 Temperature (°C)", weather["temp"])
            wcols[2].metric("💧 Humidity (%)", weather["humidity"])

            # AQI CATEGORY
            category = aqi_category(pollutants["pm2_5"], pollutants["pm10"], pollutants["no2"])

            if category == "Good":
                st.markdown("<div class='metric-good'>🌿 Good — Air is safe.</div>", unsafe_allow_html=True)
            elif category == "Moderate":
                st.markdown("<div class='metric-moderate'>😷 Moderate — Sensitive individuals should take care.</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='metric-poor'>🚨 Poor — Avoid outdoor exposure!</div>", unsafe_allow_html=True)

        except Exception as e:
            st.error(str(e))

    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# 💧 WATER QUALITY SECTION
# =========================================================
st.markdown("<div class='section-title'>💧 Water Quality</div>", unsafe_allow_html=True)

st.markdown("<div class='tag-box'>💧 Check drinking water safety using ML predictions.</div>",
            unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    city_water = st.text_input("Enter city name for Water Quality")

    if st.button("Fetch Water Quality"):
        try:
            fixed = CITY_ALIASES.get(city_water.lower().strip(), city_water).lower()

            if fixed not in df_water["city"].str.lower().values:
                st.error("City not found in water dataset.")
            else:
                row = df_water[df_water["city"].str.lower() == fixed].iloc[0]

                parameters = {
                    "pH": row["ph"],
                    "Hardness": row["hardness"],
                    "Solids": row["solids"],
                }

                st.subheader(f"Water Parameters — {city_water.title()}")

                cols = st.columns(3)
                for i, (k, v) in enumerate(parameters.items()):
                    cols[i % 3].metric(k, round(v, 2))

                # ML prediction (3 features only)
                model = joblib.load(os.path.join(BASE_DIR, "models", "water_quality_model.pkl"))
                pred = model.predict([[parameters["pH"], parameters["Hardness"], parameters["Solids"]]])[0]
                label = "Drinkable" if pred == 1 else "Not Drinkable"

                if label == "Drinkable":
                    st.markdown("<div class='metric-good'>💧 Water is safe to drink.</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div class='metric-poor'>🚱 Water is NOT safe for drinking.</div>", unsafe_allow_html=True)

        except Exception as e:
            st.error(str(e))

    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# 📊 CITY COMPARISON
# =========================================================
st.markdown("<div class='section-title'>📊 Compare PM2.5 Between Cities</div>", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    c1 = st.text_input("City 1")
    c2 = st.text_input("City 2")
    c3 = st.text_input("City 3 (optional)")

    if st.button("Compare Cities"):
        try:
            cities = [c1, c2, c3]
            labels = []
            values = []

            for city in cities:
                if city.strip():
                    fx = CITY_ALIASES.get(city.lower().strip(), city)
                    pollutants, _ = get_air_quality_for_city(fx)
                    labels.append(fx.title())
                    values.append(pollutants["pm2_5"])

            df = pd.DataFrame({"City": labels, "PM2.5": values})
            fig = px.pie(df, names="City", values="PM2.5", title="PM2.5 Comparison Between Cities")
            st.plotly_chart(fig)

        except Exception as e:
            st.error(str(e))

    st.markdown("</div>", unsafe_allow_html=True)
