import streamlit as st
import joblib
import pandas as pd
import os
import plotly.express as px
from utils import get_air_quality_for_city

# ---------------------------------------------------------
# PAGE CONFIG + STYLE
# ---------------------------------------------------------
st.set_page_config(
    page_title="Air & Water Quality Monitoring",
    page_icon="🌍",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background-color: #d6eaff;
    background-image: linear-gradient(135deg, #e8f1ff 0%, #cfe0ff 100%);
    font-family: 'Segoe UI', sans-serif;
}
.main-title {
    font-size: 46px;
    font-weight: 900;
    text-align: center;
    color: #003366;
}
.section-title {
    font-size: 32px;
    color: #003366;
    font-weight: 800;
}
.card {
    background: white;
    padding: 28px;
    border-radius: 16px;
    box-shadow: 0 6px 25px rgba(0,0,0,0.12);
    margin-bottom: 25px;
}
.tag-box {
    background: #fff4c4;
    padding: 12px;
    border-radius: 10px;
    font-weight: 700;
    text-align: center;
    color: #795c00;
    margin-bottom: 15px;
}
.metric-good {
    background: #d9ffe3;
    padding: 14px;
    border-radius: 10px;
    font-weight: 700;
    color: #075e28;
}
.metric-moderate {
    background: #fff3cd;
    padding: 14px;
    border-radius: 10px;
    font-weight: 700;
    color: #7a5c00;
}
.metric-poor {
    background: #ffd6d6;
    padding: 14px;
    border-radius: 10px;
    font-weight: 700;
    color: #7a0000;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# TITLE
# ---------------------------------------------------------
st.markdown("<div class='main-title'>🌍 Air & Water Quality Monitoring</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# WATER DATA LOAD
# ---------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
water_path = os.path.join(BASE_DIR, "data", "water_quality_cities.csv")

df_water = pd.read_csv(water_path)
df_water.columns = df_water.columns.str.lower().str.replace(" ", "_")

CITY_ALIASES = {"bangalore": "bengaluru", "banglore": "bengaluru", "bombay": "mumbai"}


# ---------------------------------------------------------
# ICON & COLOR LOGIC
# ---------------------------------------------------------
def pollutant_color(value, low, med):
    """Return emoji + CSS class."""
    if value <= low:
        return "🟢 Good", "metric-good"
    elif value <= med:
        return "🟡 Moderate", "metric-moderate"
    else:
        return "🔴 Poor", "metric-poor"


def weather_icon(cond):
    icons = {
        "Clear": "🌞",
        "Clouds": "☁",
        "Rain": "🌧",
        "Snow": "❄",
        "Haze": "🌫",
        "Mist": "🌫",
        "Fog": "🌫"
    }
    return icons.get(cond, "🌍")


# ---------------------------------------------------------
# AIR QUALITY SECTION
# ---------------------------------------------------------
st.markdown("<div class='section-title'>🌫️ Air Quality</div>", unsafe_allow_html=True)
st.markdown("<div class='tag-box'>🌬️ Track real-time air pollution, weather and safety alerts.</div>", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    city_air = st.text_input("Enter city name for Air Quality")

    if st.button("Fetch Air Quality"):
        try:
            city_fixed = CITY_ALIASES.get(city_air.lower().strip(), city_air)
            pollutants, weather = get_air_quality_for_city(city_fixed)

            st.subheader(f"Air Quality in {city_fixed.title()}")

            limits = {
                "pm2_5": (30, 60),
                "pm10": (50, 100),
                "no2": (40, 80),
                "so2": (20, 80),
                "o3":  (50, 100),
                "co":  (200, 400)
            }

            cols = st.columns(3)
            for i, key in enumerate(pollutants):
                low, med = limits[key]
                status, css = pollutant_color(pollutants[key], low, med)

                with cols[i % 3]:
                    st.markdown(
                        f"<div class='{css}'>{status} — {key.upper()}: {round(pollutants[key],2)}</div>",
                        unsafe_allow_html=True
                    )

            # Weather
            st.subheader("🌦 Current Weather")
            wcols = st.columns(3)
            wcols[0].metric(f"{weather_icon(weather['condition'])} Condition", weather["condition"])
            wcols[1].metric("🌡 Temperature (°C)", weather["temp"])
            wcols[2].metric("💧 Humidity (%)", weather["humidity"])

        except Exception as e:
            st.error(str(e))

    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# WATER QUALITY SECTION
# ---------------------------------------------------------
st.markdown("<div class='section-title'>💧 Water Quality</div>", unsafe_allow_html=True)
st.markdown("<div class='tag-box'>💧 Check potability and safety levels for drinking water.</div>", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    city_water = st.text_input("Enter city name for Water Quality")

    if st.button("Fetch Water Quality"):
        try:
            fixed = CITY_ALIASES.get(city_water.lower().strip(), city_water).lower()

            if fixed not in df_water["city"].str.lower().values:
                st.error("City not found in dataset.")
            else:
                row = df_water[df_water["city"].str.lower() == fixed].iloc[0]
                st.subheader(f"Water Parameters — {city_water.title()}")

                water_limits = {
                    "ph": (6.5, 8.5),
                    "hardness": (150, 300),
                    "solids": (300, 600),
                    "chloramines": (2, 4),
                    "sulfate": (100, 250),
                    "organic_carbon": (2, 5),
                    "conductivity": (250, 400),
                    "trihalomethanes": (40, 80),
                    "turbidity": (1, 3)
                }

                cols = st.columns(3)
                for i, param in enumerate(water_limits):
                    value = row[param]
                    low, med = water_limits[param]
                    status, css = pollutant_color(value, low, med)
                    with cols[i % 3]:
                        st.markdown(
                            f"<div class='{css}'>{status} — {param.replace('_',' ').title()}: {round(value,2)}</div>",
                            unsafe_allow_html=True
                        )

                # ML MODEL PREDICTION
                model = joblib.load(os.path.join(BASE_DIR, "models", "water_quality_model.pkl"))
                pred = model.predict([[row["ph"], row["hardness"], row["solids"]]])[0]
                label = "Drinkable" if pred == 1 else "Not Drinkable"

                if label == "Drinkable":
                    st.markdown("<div class='metric-good'>💧 Water is safe for drinking.</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div class='metric-poor'>🚱 Water is NOT safe for drinking.</div>", unsafe_allow_html=True)

        except Exception as e:
            st.error(str(e))

    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# CITY COMPARISON (PM2.5)
# ---------------------------------------------------------
st.markdown("<div class='section-title'>📊 Compare PM2.5 Between Cities</div>", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    c1 = st.text_input("City 1")
    c2 = st.text_input("City 2")
    c3 = st.text_input("City 3 (optional)")

    if st.button("Compare Cities"):
        try:
            labels, values = [], []

            for city in [c1, c2, c3]:
                if city.strip():
                    fx = CITY_ALIASES.get(city.lower().strip(), city)
                    pol, _ = get_air_quality_for_city(fx)
                    labels.append(fx.title())
                    values.append(pol["pm2_5"])

            df = pd.DataFrame({"City": labels, "PM2.5": values})

            fig = px.pie(df, names="City", values="PM2.5",
                         title="PM2.5 Comparison Between Cities")
            st.plotly_chart(fig)

        except Exception as e:
            st.error(str(e))

    st.markdown("</div>", unsafe_allow_html=True)
