import streamlit as st
import joblib
import pandas as pd
import numpy as np
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

# ---- CLEAN BACKGROUND ----
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
            margin-top: -20px;
        }

        .section-title {
            font-size: 32px;
            color: #0a2540;
            font-weight: 800;
            margin-bottom: 10px;
            padding-top: 10px;
        }

        .card {
            background: white;
            padding: 28px;
            border-radius: 16px;
            box-shadow: 0 6px 25px rgba(0,0,0,0.12);
            margin-bottom: 25px;
        }

        .metric-box {
            background: #f7f9fc;
            padding: 18px;
            border-radius: 10px;
            text-align: center;
            box-shadow: inset 0 0 10px rgba(0,0,0,0.06);
        }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# TITLE
# ---------------------------------------------------------
st.markdown("<div class='main-title'>🌍 Air & Water Quality Monitoring</div>", unsafe_allow_html=True)
st.write("Analyze real-time environmental conditions with ML-based predictions.")


# ---------------------------------------------------------
# LOAD WATER DATA
# ---------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
water_path = os.path.join(BASE_DIR, "data", "water_quality_cities.csv")
df_water = pd.read_csv(water_path)

CITY_ALIASES = {
    "bangalore": "bengaluru",
    "banglore": "bengaluru",
    "bombay": "mumbai",
}


# Utility functions
def map_air(x):
    return {0: "Good", 1: "Moderate", 2: "Poor"}.get(x)


def map_water(x):
    return "Drinkable" if x == 1 else "Not Drinkable"


def color_icon(value, low, med, high):
    if value <= low:
        return "🟢"
    elif value <= med:
        return "🟡"
    return "🔴"


# =========================================================
# 🌫️ AIR QUALITY SECTION
# =========================================================
st.markdown("<div class='section-title'>🌫️ Air Quality</div>", unsafe_allow_html=True)
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    city_air = st.text_input("Enter city name for Air Quality")

    if st.button("Fetch Air Quality", type="primary"):
        try:
            c = CITY_ALIASES.get(city_air.lower().strip(), city_air)
            air = get_air_quality_for_city(c)

            st.subheader(f"Pollutant Levels in {c.title()}")

            # Thresholds
            limits = {
                "pm2_5": (30, 60, 90),
                "pm10": (50, 100, 150),
                "no2": (40, 80, 180),
                "so2": (20, 80, 380),
                "o3": (50, 100, 200),
                "co": (200, 400, 1000),
            }

            cols = st.columns(3)
            for i, key in enumerate(air.keys()):
                low, med, high = limits[key]
                icon = color_icon(air[key], low, med, high)

                with cols[i % 3]:
                    st.metric(f"{icon} {key.upper()}", round(air[key], 2))

            # Predict category
            model_a = joblib.load(os.path.join(BASE_DIR, "models", "air_quality_model.pkl"))
            pred_raw = model_a.predict([[*air.values()]])[0]
            pred_label = map_air(pred_raw)

            st.subheader(f"Air Quality Category: {pred_label}")

            if pred_label == "Good":
                st.success("🌿 Air is safe to breathe.")
            elif pred_label == "Moderate":
                st.warning("😷 Air quality is moderate.")
            else:
                st.error("🚨 Air quality is poor. Avoid outdoor exposure.")

        except Exception as e:
            st.error(str(e))

    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# 💧 WATER QUALITY SECTION (9 FEATURES)
# =========================================================
st.markdown("<div class='section-title'>💧 Water Quality</div>", unsafe_allow_html=True)
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    city_water = st.text_input("Enter city name for Water Quality")

    if st.button("Fetch Water Quality", type="secondary"):
        try:
            c2 = CITY_ALIASES.get(city_water.lower().strip(), city_water).title()

            if c2 not in df_water["City"].values:
                st.error("City not found in water dataset.")
            else:

                row = df_water[df_water["City"] == c2].iloc[0]

                st.subheader(f"Water Parameters — {c2}")

                features = [
                    ("pH", row["pH"]),
                    ("Hardness", row["Hardness"]),
                    ("Solids", row["Solids"]),
                    ("Chloramines", row["Chloramines"]),
                    ("Sulfate", row["Sulfate"]),
                    ("Conductivity", row["Conductivity"]),
                    ("Organic Carbon", row["Organic_carbon"]),
                    ("Trihalomethanes", row["Trihalomethanes"]),
                    ("Turbidity", row["Turbidity"]),
                ]

                cols = st.columns(3)
                for i, (name, value) in enumerate(features):
                    cols[i % 3].metric(name, round(value, 2))

                # Load model
                model_w = joblib.load(os.path.join(BASE_DIR, "models", "water_quality_model.pkl"))

                # Predict using ALL 9 features
                X_input = [[
                    row["pH"], row["Hardness"], row["Solids"],
                    row["Chloramines"], row["Sulfate"], row["Conductivity"],
                    row["Organic_carbon"], row["Trihalomethanes"], row["Turbidity"]
                ]]

                pred_raw = model_w.predict(X_input)[0]
                pred_label = map_water(pred_raw)

                st.subheader(f"Water Quality: {pred_label}")

                if pred_label == "Drinkable":
                    st.success("💧 Water is safe to drink.")
                else:
                    st.error("🚱 Water is not safe for drinking.")

        except Exception as e:
            st.error(str(e))

    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# 📊 CITY COMPARISON (PM2.5 PIE CHART)
# =========================================================
st.markdown("<div class='section-title'>📊 Compare PM2.5 Across Cities</div>", unsafe_allow_html=True)
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

            for c in cities:
                if c.strip():
                    fixed = CITY_ALIASES.get(c.lower().strip(), c)
                    pm = get_air_quality_for_city(fixed)["pm2_5"]
                    labels.append(fixed.title())
                    values.append(pm)

            df = pd.DataFrame({"City": labels, "PM2.5": values})
            fig = px.pie(df, names="City", values="PM2.5", title="PM2.5 Comparison")
            st.plotly_chart(fig)

        except Exception as e:
            st.error(str(e))

    st.markdown("</div>", unsafe_allow_html=True)
