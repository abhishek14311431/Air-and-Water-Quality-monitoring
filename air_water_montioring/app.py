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
# GLOBAL UI STYLE
# ---------------------------------------------------------
st.markdown(
    """
    <style>
        .stApp {
            background-color: #eef1f5;
            background-image: linear-gradient(145deg, #f7f9fc 0%, #dfe3ea 100%);
            font-family: 'Segoe UI', sans-serif;
        }
        .main-title {
            font-size: 46px;
            text-align: center;
            font-weight: 900;
            color: #0a0a0a;
            margin-top: -10px;
        }
        .section-title {
            font-size: 32px;
            color: #0a2540;
            font-weight: 800;
            margin-bottom: 10px;
        }
        .card {
            background: white;
            padding: 28px;
            border-radius: 16px;
            box-shadow: 0 6px 25px rgba(0,0,0,0.12);
            margin-bottom: 25px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# TITLE
# ---------------------------------------------------------
st.markdown("<div class='main-title'>🌍 Air & Water Quality Monitoring</div>", unsafe_allow_html=True)
st.write("Real-time Air & Water analysis using API data + Machine Learning.")

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
# AIR QUALITY CLASSIFICATION (Based on PM2.5, PM10, NO2)
# ---------------------------------------------------------
def classify_air(pm25, pm10, no2):
    if pm25 <= 30 and pm10 <= 50 and no2 <= 40:
        return "Good"
    elif pm25 <= 60 and pm10 <= 100 and no2 <= 80:
        return "Moderate"
    else:
        return "Poor"

# ---------------------------------------------------------
# 🌫️ AIR QUALITY SECTION
# ---------------------------------------------------------
st.markdown("<div class='section-title'>🌫️ Air Quality</div>", unsafe_allow_html=True)
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    city_air = st.text_input("Enter city name for Air Quality")

    if st.button("Fetch Air Quality"):
        try:
            c = CITY_ALIASES.get(city_air.lower().strip(), city_air)
            data = get_air_quality_for_city(c)

            st.subheader(f"Air Quality Details — {c.title()}")

            pollutants = {
                "PM 2.5": data["pm2_5"],
                "PM 10": data["pm10"],
                "NO₂": data["no2"],
                "SO₂": data["so2"],
                "O₃": data["o3"],
                "CO": data["co"],
            }

            weather = {
                "Temperature (°C)": data["temp"],
                "Humidity (%)": data["humidity"],
                "Wind Speed (m/s)": data["wind"],
            }

            # Show pollutants
            cols = st.columns(3)
            for i, (name, value) in enumerate(pollutants.items()):
                cols[i % 3].metric(name, round(value, 2))

            # Show weather
            st.subheader("Weather Conditions")
            cols2 = st.columns(3)
            for i, (name, value) in enumerate(weather.items()):
                cols2[i % 3].metric(name, round(value, 2))

            # Classification based on main 3 parameters
            category = classify_air(data["pm2_5"], data["pm10"], data["no2"])

            st.subheader(f"Air Quality Category: {category}")

            if category == "Good":
                st.success("🌿 Air quality is GOOD.")
            elif category == "Moderate":
                st.warning("😐 Air quality is MODERATE.")
            else:
                st.error("🚨 AIR QUALITY IS POOR! Avoid outdoor activities.")

        except Exception as e:
            st.error(str(e))

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 💧 WATER QUALITY SECTION
# ---------------------------------------------------------
st.markdown("<div class='section-title'>💧 Water Quality</div>", unsafe_allow_html=True)
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

                st.subheader(f"Water Parameters — {c2}")

                parameters = {
                    "pH": row["ph"],
                    "Hardness": row["hardness"],
                    "Solids": row["solids"],
                    "Chloramines": row["chloramines"],
                    "Organic Carbon": row["organic_carbon"],
                    "Sulfate": row["sulfate"],
                    "Conductivity": row["conductivity"],
                    "Trihalomethanes": row["trihalomethanes"],
                    "Turbidity": row["turbidity"],
                }

                cols = st.columns(3)
                for i, (name, value) in enumerate(parameters.items()):
                    if pd.notna(value):
                        cols[i % 3].metric(name, round(value, 2))

                # ML Prediction
                model_w = joblib.load(os.path.join(BASE_DIR, "models", "water_quality_model.pkl"))
                X = [[row["ph"], row["hardness"], row["solids"]]]
                pred = model_w.predict(X)[0]

                result = "Drinkable" if pred == 1 else "Not Drinkable"

                st.subheader(f"Water Status: {result}")

                if result == "Drinkable":
                    st.success("💧 Water is safe to drink.")
                else:
                    st.error("🚱 Water is NOT safe for drinking.")

        except Exception as e:
            st.error(str(e))

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 📊 CITY COMPARISON PIE CHART
# ---------------------------------------------------------
st.markdown("<div class='section-title'>📊 Compare PM2.5 Across Cities</div>", unsafe_allow_html=True)
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    a = st.text_input("City 1")
    b = st.text_input("City 2")
    c = st.text_input("City 3 (optional)")

    if st.button("Compare Cities"):
        try:
            cities = [a, b, c]
            labels, values = [], []

            for city in cities:
                if city.strip():
                    fixed = CITY_ALIASES.get(city.lower().strip(), city)
                    pm = get_air_quality_for_city(fixed)["pm2_5"]
                    labels.append(fixed.title())
                    values.append(pm)

            df = pd.DataFrame({"City": labels, "PM2.5": values})

            fig = px.pie(df, names="City", values="PM2.5", title="PM2.5 Levels Comparison")
            st.plotly_chart(fig)

        except Exception as e:
            st.error(str(e))

    st.markdown("</div>", unsafe_allow_html=True)
