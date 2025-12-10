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
# GLOBAL STYLING
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
df_water.columns = df_water.columns.str.lower().str.replace(" ", "_")

CITY_ALIASES = {
    "bangalore": "bengaluru",
    "banglore": "bengaluru",
    "bombay": "mumbai",
}

# ---------------------------------------------------------
# COLOR LOGIC
# ---------------------------------------------------------
def color_icon(value, low, med, high):
    if value <= low:
        return "🟢", "#22c55e"  # green
    elif value <= med:
        return "🟡", "#eab308"  # yellow
    else:
        return "🔴", "#ef4444"  # red


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
                icon, color = color_icon(air[key], low, med, high)

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

            # Air ML prediction
            model_a = joblib.load(os.path.join(BASE_DIR, "models", "air_quality_model.pkl"))
            pred_raw = model_a.predict([[*air.values()]])[0]
            pred_label = {0: "Good", 1: "Moderate", 2: "Poor"}.get(pred_raw)

            st.subheader(f"Air Quality Category: {pred_label}")

            if pred_label == "Good":
                st.success("🌿 Air is safe to breathe.")
            elif pred_label == "Moderate":
                st.warning("😷 Air quality is moderate.")
            else:
                st.error("🚨 Poor air quality. Avoid outdoor exposure.")

        except Exception as e:
            st.error(str(e))

    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 💧 WATER QUALITY SECTION (FIXED)
# =========================================================
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
                    "pH": (6.5, 8.5, 9.5),
                    "Hardness": (150, 300, 450),
                    "Solids": (300, 600, 900),
                    "Chloramines": (2, 4, 8),
                    "Sulfate": (100, 250, 400),
                    "Conductivity": (200, 400, 800),
                    "Organic Carbon": (4, 10, 20),
                    "Trihalomethanes": (30, 60, 80),
                    "Turbidity": (1, 3, 5),
                }

                cols = st.columns(3)

                for i, (name, val) in enumerate(metrics.items()):
                    if pd.notna(val):
                        low, med, high = limits[name]
                        icon, color = color_icon(val, low, med, high)

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
                                <div style="font-size: 22px; margin-top: 4px;">{round(val, 2)}</div>
                            </div>
                        """

                        cols[i % 3].markdown(html, unsafe_allow_html=True)

                # ML on 3 features
                pH = row.get("ph")
                Hardness = row.get("hardness")
                Solids = row.get("solids")

                model_w = joblib.load(os.path.join(BASE_DIR, "models", "water_quality_model.pkl"))
                pred_raw = model_w.predict([[pH, Hardness, Solids]])[0]
                pred_label = "Drinkable" if pred_raw == 1 else "Not Drinkable"

                st.subheader(f"Water Quality: {pred_label}")

                if pred_label == "Drinkable":
                    st.success("💧 Water is safe")
                else:
                    st.error("🚱 Not safe for drinking")

        except Exception as e:
            st.error(str(e))

    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 📊 COMPARISON CHART
# =========================================================
st.markdown("<div class='section-title'>📊 Compare PM2.5 Across Cities</div>", unsafe_allow_html=True)
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    c1 = st.text_input("City 1")
    c2 = st.text_input("City 2")
    c3 = st.text_input("City 3 (optional)")

    if st.button("Compare Cities"):
        try:
            labels = []
            values = []

            for c in [c1, c2, c3]:
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
