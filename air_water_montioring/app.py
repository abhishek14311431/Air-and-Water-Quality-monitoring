import streamlit as st
import joblib
import pandas as pd
import os
import plotly.express as px

from utils import get_air_quality_for_city, get_weather_for_city

st.set_page_config(
    page_title="Air & Water Quality Monitoring",
    page_icon="🌍",
    layout="wide",
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #e9f4ff, #cfe4fa);
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
}
.card {
    background: white;
    padding: 26px;
    border-radius: 16px;
    box-shadow: 0 6px 25px rgba(0,0,0,0.12);
    margin-bottom: 20px;
}
.tagline-box {
    background: white;
    padding: 15px;
    border-radius: 12px;
    border-left: 5px solid #0077cc;
    font-weight: 600;
    margin-bottom: 10px;
}
.metric-large {
    font-size: 26px;
}
</style>
""", unsafe_allow_html=True)


st.markdown("<div class='main-title'>🌍 Air & Water Quality Monitoring</div>", unsafe_allow_html=True)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
df_water = pd.read_csv(os.path.join(BASE_DIR, "data", "water_quality_cities.csv"))
df_water.columns = df_water.columns.str.lower().str.replace(" ", "_")

CITY_ALIASES = {
    "bangalore": "bengaluru",
    "bombay": "mumbai",
}

def emoji_status(val, good, moderate):
    if val <= good:
        return "🟢"
    elif val <= moderate:
        return "🟡"
    return "🔴"

# =========================================================
# 🌫️ AIR QUALITY + WEATHER
# =========================================================
st.markdown("<div class='section-title'>🌫️ Air Quality & Weather</div>", unsafe_allow_html=True)
st.markdown("<div class='tagline-box'>🌬️ Track real-time air quality and stay safe outdoors.</div>", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    city_air = st.text_input("Enter city name")

    if st.button("Fetch Air Quality"):
        if not city_air.strip():
            st.warning("⚠️ Please enter a city name.")
        else:
            city = CITY_ALIASES.get(city_air.lower(), city_air)
            pollutants = get_air_quality_for_city(city)
            weather = get_weather_for_city(city)

            st.subheader(f"Weather in {city.title()}")
            c1, c2, c3 = st.columns(3)
            c1.metric("🌡️ Temperature", f"{weather['temperature_c']} °C")
            c2.metric("💧 Humidity", f"{weather['humidity_percent']} %")
            c3.metric("🌬️ Wind", f"{weather['wind_speed']} m/s")

            st.markdown("---")
            st.subheader("Pollutants")

            limits = {
                "pm2_5": (30, 60),
                "pm10": (50, 100),
                "no2": (40, 80),
                "so2": (20, 80),
                "o3": (50, 100),
                "co": (200, 400),
            }

            cols = st.columns(3)
            for i, (k, v) in enumerate(pollutants.items()):
                emoji = emoji_status(v, *limits[k])
                cols[i % 3].markdown(
                    f"<div class='metric-large'><b>{emoji}</b> {k.upper()}: {round(v,2)}</div>",
                    unsafe_allow_html=True
                )

            st.markdown("---")
            pm = pollutants["pm2_5"]
            if pm <= 30:
                st.success("🟢 AQI Good — Safe to breathe.")
            elif pm <= 60:
                st.warning("🟡 AQI Moderate — Limit outdoor exposure.")
            else:
                st.error("🔴 AQI Poor — Avoid outdoor activities.")

    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 💧 WATER QUALITY (ALL POLLUTANTS)
# =========================================================
st.markdown("<div class='section-title'>💧 Water Quality</div>", unsafe_allow_html=True)
st.markdown("<div class='tagline-box' style='border-left-color:#00aa66;'>💧 Check drinking water safety.</div>", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    city_water = st.text_input("Enter city name for water quality")

    if st.button("Fetch Water Data"):
        if not city_water.strip():
            st.warning("⚠️ Please enter city name.")
        else:
            city = CITY_ALIASES.get(city_water.lower(), city_water)
            if city not in df_water["city"].str.lower().values:
                st.error("City not found in dataset.")
            else:
                row = df_water[df_water["city"].str.lower() == city].iloc[0]
                st.subheader(f"Water Parameters — {row['city'].title()}")

                water_limits = {
                    "ph": (6.5, 8.5),
                    "hardness": (150, 300),
                    "solids": (300, 600),
                    "chloramines": (2, 4),
                    "sulfate": (100, 250),
                    "conductivity": (200, 400),
                    "organic_carbon": (2, 4),
                    "trihalomethanes": (40, 80),
                    "turbidity": (1, 3),
                }

                cols = st.columns(3)
                for i, (k, (g, m)) in enumerate(water_limits.items()):
                    v = row[k]
                    emoji = emoji_status(v, g, m)
                    cols[i % 3].markdown(
                        f"<div class='metric-large'><b>{emoji}</b> {k.replace('_',' ').title()}: {round(v,2)}</div>",
                        unsafe_allow_html=True
                    )

                st.markdown("---")
                model = joblib.load(os.path.join(BASE_DIR, "models", "water_quality_model.pkl"))
                pred = model.predict([[row["ph"], row["hardness"], row["solids"]]])[0]

                if pred == 1:
                    st.success("🟢 Water is safe to drink.")
                else:
                    st.error("🔴 Water is NOT safe for drinking.")

    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 📊 CITY COMPARISON (TWO INPUT BOXES)
# =========================================================
st.markdown("<div class='section-title'>📊 City PM2.5 Comparison</div>", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    city1 = col1.text_input("City 1")
    city2 = col2.text_input("City 2")

    if st.button("Compare Cities"):
        if not city1 or not city2:
            st.warning("⚠️ Please enter both city names.")
        else:
            c1 = CITY_ALIASES.get(city1.lower(), city1)
            c2 = CITY_ALIASES.get(city2.lower(), city2)

            pm1 = get_air_quality_for_city(c1)["pm2_5"]
            pm2 = get_air_quality_for_city(c2)["pm2_5"]

            df = pd.DataFrame({
                "City": [c1.title(), c2.title()],
                "PM2.5": [pm1, pm2]
            })

            colors = {
                c1.title(): "green" if pm1 < pm2 else "red",
                c2.title(): "green" if pm2 < pm1 else "red"
            }

            fig = px.pie(df, names="City", values="PM2.5",
                         color="City", color_discrete_map=colors,
                         title="PM2.5 Comparison")

            st.plotly_chart(fig, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)
