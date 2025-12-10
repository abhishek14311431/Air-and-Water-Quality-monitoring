import streamlit as st
import joblib
import pandas as pd
import numpy as np
import os
import plotly.express as px
from utils import get_air_quality_for_city, load_water_dataset


# ---------------------------------------------------------
# PAGE CONFIG & GLOBAL STYLE
# ---------------------------------------------------------
st.set_page_config(
    page_title="Air & Water Quality Monitoring",
    page_icon="🌍",
    layout="wide",
)

st.markdown(
    """
    <style>
        .stApp {
            background-color: #f2f4f7;
            background-image: linear-gradient(140deg, #eef1f5 0%, #dfe3e8 100%);
            font-family: 'Segoe UI', sans-serif;
        }

        .title-main {
            font-size: 46px;
            font-weight: 900;
            text-align: center;
            margin-top: -10px;
            color: #0a0a0a;
        }

        .section-title {
            font-size: 32px;
            font-weight: 800;
            color: #0a2540;
            margin-bottom: 10px;
        }

        .card {
            background: white;
            padding: 30px;
            border-radius: 16px;
            box-shadow: 0 6px 24px rgba(0,0,0,0.15);
            margin-bottom: 25px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# TITLE
# ---------------------------------------------------------
st.markdown("<div class='title-main'>🌍 Air & Water Quality Monitoring</div>", unsafe_allow_html=True)
st.write("View live air pollution levels, analyze water parameters, and use ML predictions.")


# ---------------------------------------------------------
# LOAD MODELS + WATER DATA
# ---------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

air_model = joblib.load(os.path.join(BASE_DIR, "models", "air_quality_model.pkl"))
water_model = joblib.load(os.path.join(BASE_DIR, "models", "water_quality_model.pkl"))

df_water = load_water_dataset()

CITY_ALIASES = {
    "bangalore": "bengaluru",
    "banglore": "bengaluru",
    "bombay": "mumbai",
}


# ---------------------------------------------------------
# THRESHOLD COLOR LOGIC
# ---------------------------------------------------------
def color_icon(value, low, med, high):
    if value <= low:
        return "🟢"
    elif value <= med:
        return "🟡"
    return "🔴"


def air_label(code):
    return {0: "Good", 1: "Moderate", 2: "Poor"}.get(code)


def water_label(code):
    return "Drinkable" if code == 1 else "Not Drinkable"


# =========================================================
# 🌫️ AIR QUALITY SECTION
# =========================================================
st.markdown("<div class='section-title'>🌫️ Air Quality</div>", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    air_city = st.text_input("Enter city name for Air Quality", key="air")

    if st.button("Fetch Air Quality", type="primary"):
        try:
            city = CITY_ALIASES.get(air_city.lower().strip(), air_city)
            air = get_air_quality_for_city(city)

            st.subheader(f"Pollutant Levels — {city.title()}")

            limits_air = {
                "pm2_5": (30, 60, 90),
                "pm10": (50, 100, 150),
                "no2": (40, 80, 180),
                "so2": (20, 80, 380),
                "o3": (50, 100, 200),
                "co": (200, 400, 1000)
            }

            cols = st.columns(3)
            keys = list(air.keys())

            for i, key in enumerate(keys):
                low, med, high = limits_air[key]
                icon = color_icon(air[key], low, med, high)
                cols[i % 3].metric(f"{icon} {key.upper()}", round(air[key], 2))

            pred = air_model.predict([[*air.values()]])[0]
            label = air_label(pred)

            st.subheader(f"Air Quality Category: {label}")

            if label == "Good":
                st.success("🌿 Air is healthy.")
            elif label == "Moderate":
                st.warning("😷 Sensitive people should limit outdoor exposure.")
            else:
                st.error("🚨 Air quality is dangerous.")

        except Exception as e:
            st.error(str(e))

    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# 💧 WATER QUALITY SECTION
# =========================================================
st.markdown("<div class='section-title'>💧 Water Quality</div>", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    water_city = st.text_input("Enter city name for Water Quality", key="water")

    if st.button("Fetch Water Quality", type="secondary"):
        try:
            city2 = CITY_ALIASES.get(water_city.lower().strip(), water_city).title()

            if city2 not in df_water["City"].values:
                st.error("City not found in water dataset.")
            else:
                row = df_water[df_water["City"] == city2].sample(1).iloc[0]

                st.subheader(f"Water Parameters — {city2}")

                params = {
                    "pH": row["ph"],
                    "Hardness": row["Hardness"],
                    "Solids": row["Solids"],
                    "Chloramines": row["Chloramines"],
                    "Sulfate": row["Sulfate"],
                    "Conductivity": row["Conductivity"],
                    "Organic Carbon": row["Organic_carbon"],
                    "Trihalomethanes": row["Trihalomethanes"],
                    "Turbidity": row["Turbidity"],
                }

                limits_water = {
                    "pH": (6.5, 8.5, 10),
                    "Hardness": (150, 300, 500),
                    "Solids": (300, 600, 900),
                    "Chloramines": (2, 4, 8),
                    "Sulfate": (150, 250, 400),
                    "Conductivity": (200, 400, 800),
                    "Organic Carbon": (5, 10, 20),
                    "Trihalomethanes": (40, 80, 150),
                    "Turbidity": (1, 3, 6),
                }

                cols = st.columns(3)
                idx = 0

                for name, val in params.items():
                    low, med, high = limits_water[name]
                    icon = color_icon(val, low, med, high)
                    cols[idx % 3].metric(f"{icon} {name}", round(val, 2))
                    idx += 1

                feature_order = [
                    "ph", "Hardness", "Solids", "Chloramines", "Sulfate",
                    "Conductivity", "Organic_carbon", "Trihalomethanes", "Turbidity"
                ]

                values = [row[v] for v in feature_order]

                pred = water_model.predict([values])[0]
                label = water_label(pred)

                st.subheader(f"Water Quality: {label}")

                if label == "Drinkable":
                    st.success("💧 Water is clean and safe.")
                else:
                    st.error("🚱 Water is NOT safe to drink.")

        except Exception as e:
            st.error(str(e))

    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# 📊 CITY COMPARISON SECTION
# =========================================================
st.markdown("<div class='section-title'>📊 PM2.5 Comparison Between Cities</div>", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    city1 = st.text_input("City 1")
    city2 = st.text_input("City 2")
    city3 = st.text_input("City 3 (optional)")

    if st.button("Compare Cities"):
        try:
            cities = [city1, city2, city3]
            labels = []
            values = []

            for ct in cities:
                if ct.strip():
                    fixed = CITY_ALIASES.get(ct.lower().strip(), ct)
                    pm = get_air_quality_for_city(fixed)["pm2_5"]
                    labels.append(fixed.title())
                    values.append(pm)

            df = pd.DataFrame({"City": labels, "PM2.5": values})
            fig = px.pie(df, names="City", values="PM2.5")

            st.plotly_chart(fig)

        except Exception as e:
            st.error(str(e))

    st.markdown("</div>", unsafe_allow_html=True)
