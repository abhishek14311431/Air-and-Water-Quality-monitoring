import streamlit as st
import joblib
import pandas as pd
import numpy as np
import os
import plotly.express as px
from utils import get_air_quality_for_city


# ---------------------------------------------------------
# PAGE CONFIG + GLOBAL STYLING
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
st.write("Analyze real-time environmental conditions with ML-backed predictions.")


# ---------------------------------------------------------
# LOAD WATER QUALITY DATA
# ---------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
water_path = os.path.join(BASE_DIR, "data", "water_quality_cities.csv")
df_water = pd.read_csv(water_path)

# Normalize column names
df_water.columns = df_water.columns.str.lower().str.replace(" ", "_")

CITY_ALIASES = {
    "bangalore": "bengaluru",
    "banglore": "bengaluru",
    "bombay": "mumbai",
}


# ---------------------------------------------------------
# HELPER – FIX CITY MATCHING
# ---------------------------------------------------------
def find_city_match(city_name, df):
    city_name = city_name.lower().strip()

    for c in df["city"]:
        if c.lower().strip() == city_name:
            return c

    return None


# ---------------------------------------------------------
# 🌫️ AIR QUALITY SECTION (REAL AQI LOGIC)
# ---------------------------------------------------------
st.markdown("<div class='section-title'>🌫️ Air Quality</div>", unsafe_allow_html=True)
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    city_air = st.text_input("Enter city name for Air Quality")

    if st.button("Fetch Air Quality", type="primary"):
        try:

            c = CITY_ALIASES.get(city_air.lower().strip(), city_air)
            air = get_air_quality_for_city(c)

            st.subheader(f"Pollutant Levels in {c.title()}")

            # AQI RANGES USING STANDARD BREAKPOINTS
            AQI_BREAKPOINTS = {
                "pm2_5": [(0, 30, "Good"), (31, 60, "Moderate"), (61, 250, "Poor")],
                "pm10": [(0, 50, "Good"), (51, 100, "Moderate"), (101, 430, "Poor")],
                "no2":  [(0, 40, "Good"), (41, 80, "Moderate"), (81, 180, "Poor")],
                "so2":  [(0, 20, "Good"), (21, 80, "Moderate"), (81, 380, "Poor")],
                "o3":   [(0, 50, "Good"), (51, 100, "Moderate"), (101, 200, "Poor")],
                "co":   [(0, 200, "Good"), (201, 400, "Moderate"), (401, 2000, "Poor")],
            }

            def get_status(value, ranges):
                for low, high, category in ranges:
                    if low <= value <= high:
                        return category
                return "Poor"

            def get_icon(category):
                return "🟢" if category == "Good" else "🟡" if category == "Moderate" else "🔴"

            # DISPLAY POLLUTANTS
            cols = st.columns(3)
            statuses = []

            for i, (key, value) in enumerate(air.items()):
                category = get_status(value, AQI_BREAKPOINTS[key])
                icon = get_icon(category)
                statuses.append(category)

                cols[i % 3].metric(f"{icon} {key.upper()}", round(value, 2))

            # FINAL AQI = Worst pollutant result
            if "Poor" in statuses:
                final = "Poor"
            elif "Moderate" in statuses:
                final = "Moderate"
            else:
                final = "Good"

            st.subheader(f"Air Quality Category: {final}")

            if final == "Good":
                st.success("🌿 Air is safe to breathe.")
            elif final == "Moderate":
                st.warning("😷 Moderate air quality — sensitive individuals should take care.")
            else:
                st.error("🚨 Poor air quality. Avoid going outdoors.")

        except Exception as e:
            st.error(str(e))

    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# 💧 WATER QUALITY SECTION (3 FEATURE MODEL)
# ---------------------------------------------------------
st.markdown("<div class='section-title'>💧 Water Quality</div>", unsafe_allow_html=True)
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    city_water = st.text_input("Enter city name for Water Quality")

    if st.button("Fetch Water Quality", type="secondary"):
        try:
            c2 = CITY_ALIASES.get(city_water.lower().strip(), city_water)

            matched_city = find_city_match(c2, df_water)

            if matched_city is None:
                st.error(f"City '{c2}' not found in water dataset.")
            else:
                row = df_water[df_water["city"] == matched_city].iloc[0]

                all_metrics = {
                    "pH": row.get("ph"),
                    "Hardness": row.get("hardness"),
                    "Solids": row.get("solids"),
                    "Chloramines": row.get("chloramines"),
                    "Sulfate": row.get("sulfate"),
                    "Conductivity": row.get("conductivity"),
                    "Organic Carbon": row.get("organic_carbon"),
                    "Trihalomethanes": row.get("trihalomethanes"),
                    "Turbidity": row.get("turbidity"),
                }

                st.subheader(f"Water Parameters — {matched_city.title()}")
                cols = st.columns(3)

                for i, (name, value) in enumerate(all_metrics.items()):
                    if pd.notna(value):
                        cols[i % 3].metric(name, round(value, 2))

                # Only 3 features for model
                X_input = [[row["ph"], row["hardness"], row["solids"]]]

                model_w = joblib.load(os.path.join(BASE_DIR, "models", "water_quality_model.pkl"))
                pred_raw = model_w.predict(X_input)[0]
                pred_label = "Drinkable" if pred_raw == 1 else "Not Drinkable"

                st.subheader(f"Water Quality: {pred_label}")

                if pred_label == "Drinkable":
                    st.success("💧 Water is safe to drink.")
                else:
                    st.error("🚱 Not safe for drinking.")

        except Exception as e:
            st.error(str(e))

    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# 📊 CITY PM2.5 COMPARISON
# ---------------------------------------------------------
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
