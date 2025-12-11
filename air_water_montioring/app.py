import streamlit as st
import joblib
import pandas as pd
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
# SKY BLUE BACKGROUND + CENTERED CONTENT
# ---------------------------------------------------------
st.markdown("""
<style>

.stApp {
    background-color: #cfe8ff;
    background-image: linear-gradient(135deg, #d7edff, #b5dbff);
    font-family: 'Segoe UI', sans-serif;
}

/* Center-column layout */
.centered {
    max-width: 850px;
    margin: auto;
}

/* Cards */
.card {
    background: white;
    padding: 25px;
    border-radius: 18px;
    box-shadow: 0 6px 25px rgba(0,0,0,0.12);
    margin-top: 20px;
}

/* Result boxes */
.air-box-good {
    background: #d4f8d4;
    padding: 15px; border-radius: 10px;
    border-left: 5px solid #2ecc71; font-weight: 700;
}
.air-box-moderate {
    background: #fff5cc;
    padding: 15px; border-radius: 10px;
    border-left: 5px solid #f1c40f; font-weight: 700;
}
.air-box-poor {
    background: #ffd6d6;
    padding: 15px; border-radius: 10px;
    border-left: 5px solid #e74c3c; font-weight: 700;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# TITLE (CENTERED)
# ---------------------------------------------------------
st.markdown("<h1 style='text-align:center; color:#05396b;'>🌍 Air & Water Quality Monitoring</h1>", unsafe_allow_html=True)


# ---------------------------------------------------------
# LOAD WATER DATA
# ---------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
df_water = pd.read_csv(os.path.join(BASE_DIR, "data", "water_quality_cities.csv"))
df_water.columns = df_water.columns.str.lower().str.replace(" ", "_")

CITY_ALIASES = {
    "bangalore": "bengaluru",
    "banglore": "bengaluru",
    "bombay": "mumbai",
}

# ---------------------------------------------------------
# AIR QUALITY CATEGORY
# ---------------------------------------------------------
def classify_air(pm25, pm10, no2):
    if pm25 <= 30 and pm10 <= 50 and no2 <= 40:
        return "Good"
    elif pm25 <= 60 and pm10 <= 100 and no2 <= 80:
        return "Moderate"
    return "Poor"


def weather_icon(temp, humidity):
    if temp > 30:
        return "☀️ Hot"
    elif humidity > 80:
        return "🌧️ Humid/Rainy"
    elif 20 <= temp <= 30:
        return "⛅ Pleasant"
    return "☁️ Cool/Cloudy"


# ---------------------------------------------------------
# 🌫️ AIR QUALITY SECTION
# ---------------------------------------------------------
st.markdown("<div class='centered'>", unsafe_allow_html=True)

st.subheader("🌫️ Air Quality")
st.markdown("<div class='card'>", unsafe_allow_html=True)

city_air = st.text_input("Enter city name for Air Quality")

if st.button("Fetch Air Quality"):
    try:
        c = CITY_ALIASES.get(city_air.lower().strip(), city_air)
        data = get_air_quality_for_city(c)

        st.markdown(f"### Live Air Quality — {c.title()}")

        # Weather icon
        w_icon = weather_icon(data["temp"], data["humidity"])
        st.metric("Weather", w_icon)

        pollutants = {
            "PM2.5": data["pm2_5"],
            "PM10": data["pm10"],
            "NO₂": data["no2"],
            "SO₂": data["so2"],
            "O₃": data["o3"],
            "CO": data["co"],
        }

        limits = {
            "PM2.5": (30, 60),
            "PM10": (50, 100),
            "NO₂": (40, 80),
            "SO₂": (20, 80),
            "O₃": (50, 100),
            "CO": (200, 400),
        }

        def icon(val, low, mid):
            if val <= low: return "🟢"
            if val <= mid: return "🟡"
            return "🔴"

        cols = st.columns(3)
        for i, (name, value) in enumerate(pollutants.items()):
            low, mid = limits[name]
            symbol = icon(value, low, mid)
            cols[i % 3].metric(f"{symbol} {name}", round(value, 2))

        # Category box
        category = classify_air(data["pm2_5"], data["pm10"], data["no2"])

        if category == "Good":
            st.markdown("<div class='air-box-good'>🌿 Good Air — Safe to breathe.</div>", unsafe_allow_html=True)
        elif category == "Moderate":
            st.markdown("<div class='air-box-moderate'>😐 Moderate — Sensitive people limit outdoors.</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='air-box-poor'>🚨 Poor — Avoid outdoor activities.</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(str(e))

st.markdown("</div>", unsafe_allow_html=True)  # close card


# ---------------------------------------------------------
# 💧 WATER QUALITY SECTION (CENTER)
# ---------------------------------------------------------
st.subheader("💧 Water Quality")
st.markdown("<div class='card'>", unsafe_allow_html=True)

city_water = st.text_input("Enter city name for Water Quality")

if st.button("Fetch Water Quality"):
    try:
        c2 = CITY_ALIASES.get(city_water.lower().strip(), city_water).title()

        if c2.lower() not in df_water["city"].astype(str).str.lower().values:
            st.error("City not found in water dataset.")
        else:
            row = df_water[df_water["city"].str.lower() == c2.lower()].iloc[0]

            st.markdown(f"### Water Quality — {c2}")

            metrics = {
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
            for i, (name, value) in enumerate(metrics.items()):
                if pd.notna(value):
                    cols[i % 3].metric(name, round(value, 2))

            model_w = joblib.load(os.path.join(BASE_DIR, "models", "water_quality_model.pkl"))
            X = [[row["ph"], row["hardness"], row["solids"]]]
            pred = model_w.predict(X)[0]
            label = "Drinkable" if pred == 1 else "Not Drinkable"

            if label == "Drinkable":
                st.success("💧 Water is SAFE to drink.")
            else:
                st.error("🚱 Water is NOT safe to drink.")

    except Exception as e:
        st.error(str(e))

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)  # centered end
