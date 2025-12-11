import streamlit as st
import joblib
import pandas as pd
import numpy as np
import os
import plotly.express as px

from utils import get_air_quality_for_city, get_weather_for_city

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="Air & Water Quality Monitoring",
    page_icon="🌍",
    layout="wide",
)

# ---------------------------------------------------------
# GLOBAL CSS — SKY BLUE THEME + CLEAN UI
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
    color: #003366;
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
    background: #ffffff;
    padding: 15px;
    border-radius: 12px;
    border-left: 5px solid #0077cc;
    font-weight: 600;
    margin-bottom: 10px;
}

.metric-large {
    font-size: 26px;
    padding: 10px;
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
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()
water_path = os.path.join(BASE_DIR, "data", "water_quality_cities.csv")

df_water = pd.read_csv(water_path)
df_water.columns = df_water.columns.str.lower().str.replace(" ", "_")

CITY_ALIASES = {
    "bangalore": "bengaluru",
    "banglore": "bengaluru",
    "bombay": "mumbai",
}

# ---------------------------------------------------------
# HELPER FUNCTION: Get emoji category
# ---------------------------------------------------------
def emoji_status(value, low, med):
    if value <= low:
        return "🟢 Good"
    elif value <= med:
        return "🟡 Moderate"
    return "🔴 Poor"

# ---------------------------------------------------------
# 🌫️ AIR QUALITY + WEATHER SECTION
# ---------------------------------------------------------
st.markdown("<div class='section-title'>🌫️ Air Quality & Weather</div>", unsafe_allow_html=True)
st.markdown("""
<div class="tagline-box">
🌬️ The air you breathe affects your daily health. Track pollution levels & stay safe outdoors.
</div>
""", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    city_air = st.text_input("Enter city name")

    if st.button("Fetch Air Quality"):
        try:
            c = CITY_ALIASES.get(city_air.lower(), city_air)

            # ---- Fetch real API data ----
            pollutants = get_air_quality_for_city(c)
            weather = get_weather_for_city(c)

            st.subheader(f"Current Weather in {c.title()}")
            w1, w2, w3 = st.columns(3)

            w1.metric("🌡️ Temperature", f"{weather['temperature_c']}°C")
            w2.metric("💧 Humidity", f"{weather['humidity_percent']}%")
            w3.metric("🌬️ Wind Speed", f"{weather['wind_speed']} m/s")

            st.markdown("---")
            st.subheader(f"Pollutant Levels in {c.title()}")

            limits = {
                "pm2_5": (30, 60), "pm10": (50, 100), "no2": (40, 80),
                "so2": (20, 80), "o3": (50, 100), "co": (200, 400)
            }

            cols = st.columns(3)
            i = 0

            for pollutant, value in pollutants.items():
                low, med = limits[pollutant]
                status = emoji_status(value, low, med)
                emoji = status.split()[0]

                with cols[i % 3]:
                    st.markdown(
                        f"<div class='metric-large'><b style='font-size:32px'>{emoji}</b> "
                        f"{pollutant.upper()}: {round(value, 2)}</div>",
                        unsafe_allow_html=True
                    )
                i += 1

            # AQI Category (Based on PM2.5 Only)
            pm = pollutants["pm2_5"]
            st.markdown("---")

            if pm <= 30:
                st.success("🟢 **Air Quality Index: Good** — Air is safe to breathe.")
            elif pm <= 60:
                st.warning("🟡 **Air Quality Index: Moderate** — Sensitive people should limit exposure.")
            else:
                st.error("🔴 **Air Quality Index: Poor** — Avoid outdoor activities.")

        except Exception as e:
            st.error(str(e))

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 💧 WATER QUALITY SECTION
# ---------------------------------------------------------
st.markdown("<div class='section-title'>💧 Water Quality</div>", unsafe_allow_html=True)
st.markdown("""
<div class="tagline-box" style="border-left-color:#00aa66;">
💧 Clean water is essential for good health. Check if your city's water is safe to drink.
</div>
""", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    city_water = st.text_input("Enter city name for water quality")

    if st.button("Fetch Water Quality"):
        try:
            c2 = CITY_ALIASES.get(city_water.lower(), city_water).lower()

            if c2 not in df_water["city"].str.lower().values:
                st.error("City not found in water dataset.")
            else:
                row = df_water[df_water["city"].str.lower() == c2].iloc[0]
                st.subheader(f"Water Parameters — {row['city'].title()}")

                water_limits = {
                    "ph": (6.5, 8.5), "hardness": (150, 300),
                    "solids": (300, 600)
                }

                cols = st.columns(3)
                i = 0

                for key, (low, med) in water_limits.items():
                    val = row[key]
                    status = emoji_status(val, low, med)
                    emoji = status.split()[0]

                    with cols[i % 3]:
                        st.markdown(
                            f"<div class='metric-large'><b style='font-size:32px'>{emoji}</b> "
                            f"{key.upper()}: {round(val, 2)}</div>",
                            unsafe_allow_html=True
                        )
                    i += 1

                st.markdown("---")

                model_path = os.path.join(BASE_DIR, "models", "water_quality_model.pkl")

                if os.path.exists(model_path):
                    model = joblib.load(model_path)
                    pred = model.predict([[row["ph"], row["hardness"], row["solids"]]])[0]

                    if pred == 1:
                        st.success("🟢 Water is safe to drink.")
                    else:
                        st.error("🔴 Water is NOT safe for drinking.")
                else:
                    st.warning("ML model missing — cannot classify water.")

        except Exception as e:
            st.error(str(e))

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 📊 CITY COMPARISON PIE CHART
# ---------------------------------------------------------
st.markdown("<div class='section-title'>📊 Compare PM2.5 Across Cities</div>", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    city_input = st.text_input("Enter up to 3 cities (comma-separated)")

    if st.button("Compare"):
        try:
            city_list = [c.strip() for c in city_input.split(",") if c.strip()]
            names, values = [], []

            for c in city_list[:3]:
                fixed = CITY_ALIASES.get(c.lower(), c)
                data = get_air_quality_for_city(fixed)

                if "pm2_5" in data:
                    names.append(fixed.title())
                    values.append(data["pm2_5"])

            if names:
                df = pd.DataFrame({"City": names, "PM2.5": values})
                fig = px.pie(df, names="City", values="PM2.5",
                             title="PM2.5 Comparison",
                             hole=0.3)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No valid data to compare.")

        except Exception as e:
            st.error(str(e))

    st.markdown("</div>", unsafe_allow_html=True)
