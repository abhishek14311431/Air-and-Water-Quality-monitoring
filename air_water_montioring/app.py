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

# Normalize column names
df_water.columns = df_water.columns.str.lower().str.replace(" ", "_")

# Ensure city column is lowercase
df_water["city"] = df_water["city"].str.lower().str.strip()

CITY_ALIASES = {
    "bangalore": "bengaluru",
    "banglore": "bengaluru",
    "bombay": "mumbai",
}

# ---------------------------------------------------------
# FLEXIBLE CITY MATCHING
# ---------------------------------------------------------
def find_city_match(city_name, df):
    city_name = city_name.lower().strip()

    for c in df["city"]:
        if c.lower().strip() == city_name:
            return c

    return None

# ---------------------------------------------------------
# ICON + COLOR LOGIC
# ---------------------------------------------------------
def classify_pollutant(value, low, high):
    if value <= low:
        return "Good", "🟢", "#32CD32"
    if value <= high:
        return "Moderate", "🟡", "#FFD700"
    return "Poor", "🔴", "#FF4C4C"

# =========================================================
# 🌫️ AIR QUALITY SECTION
# =========================================================
st.markdown("<div class='section-title'>🌫️ Air Quality</div>", unsafe_allow_html=True)
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    city_air = st.text_input("Enter city name for Air Quality")

    if st.button("Fetch Air Quality"):
        try:
            c = CITY_ALIASES.get(city_air.lower().strip(), city_air)
            air = get_air_quality_for_city(c)

            st.subheader(f"Pollutant Levels in {c.title()}")

            thresholds = {
                "pm2_5": (30, 60),
                "pm10": (50, 100),
                "no2": (40, 80),
                "so2": (20, 80),
                "o3": (50, 100),
                "co": (200, 400),
            }

            cols = st.columns(3)
            statuses = []

            for i, key in enumerate(air.keys()):
                low, high = thresholds[key]
                status, icon, color = classify_pollutant(air[key], low, high)
                statuses.append(status)

                html = f"""
                    <div style="
                        background: #ffffff;
                        padding: 18px;
                        border-radius: 14px;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
                        text-align: center;
                        border-left: 6px solid {color};
                    ">
                        <div style="font-size: 42px;">{icon}</div>
                        <div style="font-size: 20px; font-weight: 700; color: #0a2540;">{key.upper()}</div>
                        <div style="font-size: 22px; margin-top: 4px;">{round(air[key], 2)}</div>
                    </div>
                """
                cols[i % 3].markdown(html, unsafe_allow_html=True)

            # Final AQI
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
                st.warning("😷 Moderate air quality. Sensitive individuals should be cautious.")
            else:
                st.error("🚨 Poor air quality. Avoid outdoor exposure.")

        except Exception as e:
            st.error(str(e))

    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# 💧 WATER QUALITY SECTION (FULL UI)
# =========================================================
st.markdown("<div class='section-title'>💧 Water Quality</div>", unsafe_allow_html=True)
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    city_water = st.text_input("Enter city name for Water Quality")

    if st.button("Fetch Water Quality"):
        try:
            c2 = CITY_ALIASES.get(city_water.lower().strip(), city_water)

            matched_city = find_city_match(c2, df_water)

            if matched_city is None:
                st.error(f"City '{c2}' not found in water dataset.")
            else:
                row = df_water[df_water["city"] == matched_city].iloc[0]

                metrics = {
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

                limits = {
                    "pH": (6.5, 8.5),
                    "Hardness": (150, 300),
                    "Solids": (300, 600),
                    "Chloramines": (2, 4),
                    "Sulfate": (100, 250),
                    "Conductivity": (200, 500),
                    "Organic Carbon": (3, 10),
                    "Trihalomethanes": (30, 60),
                    "Turbidity": (1, 3),
                }

                st.subheader(f"Water Parameters — {matched_city.title()}")

                cols = st.columns(3)

                for i, (name, value) in enumerate(metrics.items()):
                    if pd.notna(value):
                        low, high = limits[name]
                        status, icon, color = classify_pollutant(value, low, high)

                        html = f"""
                            <div style="
                                background: #ffffff;
                                padding: 18px;
                                border-radius: 14px;
                                box-shadow: 0 4px 12px rgba(0,0,0,0.12);
                                text-align: center;
                                border-left: 6px solid {color};
                            ">
                                <div style="font-size: 42px;">{icon}</div>
                                <div style="font-size: 20px; font-weight: 700; color: #0a2540;">{name}</div>
                                <div style="font-size: 22px; margin-top: 4px;">{round(value, 2)}</div>
                            </div>
                        """
                        cols[i % 3].markdown(html, unsafe_allow_html=True)

                # ML Prediction
                model_w = joblib.load(os.path.join(BASE_DIR, "models", "water_quality_model.pkl"))
                X_in = [[row["ph"], row["hardness"], row["solids"]]]
                pred = model_w.predict(X_in)[0]

                water_status = "Drinkable" if pred == 1 else "Not Drinkable"

                st.subheader(f"Water Quality: {water_status}")

                if water_status == "Drinkable":
                    st.success("💧 Water is safe for drinking.")
                else:
                    st.error("🚱 Water is NOT safe for drinking.")

        except Exception as e:
            st.error(str(e))

    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# 📊 CITY COMPARISON PIE CHART
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
            labels, values = [], []

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
