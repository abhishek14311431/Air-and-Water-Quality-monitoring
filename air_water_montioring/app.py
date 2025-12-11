import streamlit as st
import joblib
import pandas as pd
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
# GLOBAL CSS
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
    color: #0a0a0a;
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
    box-shadow: 0px 6px 25px rgba(0,0,0,0.12);
    margin-bottom: 25px;
}
.tagline-box {
    background: white;
    padding: 15px;
    border-left: 5px solid #0077cc;
    border-radius: 10px;
    font-weight: 600;
    margin-bottom: 15px;
}
.big-pollutant {
    font-size: 30px;
    font-weight: 600;
    padding: 10px;
}
.weather-box {
    text-align: center;
    padding: 12px;
}
.weather-box h3 {
    font-size: 28px;
    margin: 0;
}
.weather-box p {
    margin: 0;
    font-size: 16px;
    color: #555;
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
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
water_path = os.path.join(BASE_DIR, "data", "water_quality_cities.csv")

df_water = pd.read_csv(water_path)
df_water.columns = df_water.columns.str.lower().str.replace(" ", "_")

CITY_FIX = {"bangalore": "bengaluru", "banglore": "bengaluru", "bombay": "mumbai"}


# ---------------------------------------------------------
# HELPER FUNCTION – POLLUTANT STATUS
# ---------------------------------------------------------
def pollutant_status(val, good, moderate):
    if val <= good:
        return "🟢", "Good"
    elif val <= moderate:
        return "🟡", "Moderate"
    return "🔴", "Poor"


# ---------------------------------------------------------
# 🌫️ AIR QUALITY + WEATHER SECTION
# ---------------------------------------------------------
st.markdown("<div class='section-title'>🌫️ Air Quality & Weather</div>", unsafe_allow_html=True)

st.markdown("""
<div class="tagline-box">🌬️ The air you breathe affects your daily health. Track pollution levels & stay safe outdoors.</div>
""", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    city_air = st.text_input("Enter city name for Air Quality")

    if st.button("Fetch Air Data"):
        try:
            city = CITY_FIX.get(city_air.lower().strip(), city_air).title()

            # 1️⃣ FETCH REAL WEATHER
            weather = get_weather_for_city(city)

            st.subheader(f"Current Weather in {city}")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"<div class='weather-box'><h3>🌡️ {weather['temperature_c']}°C</h3><p>Temperature</p></div>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<div class='weather-box'><h3>💧 {weather['humidity_percent']}%</h3><p>Humidity</p></div>", unsafe_allow_html=True)
            with col3:
                icon = "☀️" if weather['condition'] == "Clear" else "☁️" if weather['condition'] == "Clouds" else "🌧️"
                st.markdown(f"<div class='weather-box'><h3>{icon}</h3><p>{weather['condition']}</p></div>", unsafe_allow_html=True)

            st.markdown("---")

            # 2️⃣ FETCH REAL AIR POLLUTANTS
            pollutants = get_air_quality_for_city(city)

            st.subheader(f"Pollutant Levels in {city}")

            limits = {
                "pm2_5": (30, 60),
                "pm10": (50, 100),
                "no2":  (40, 80),
                "so2":  (20, 80),
                "o3":   (50, 100),
                "co":   (200, 400)
            }

            cols = st.columns(3)
            i = 0

            for name, value in pollutants.items():
                good, moderate = limits[name]
                emoji, label = pollutant_status(value, good, moderate)

                with cols[i % 3]:
                    st.markdown(f"""
                    <div class='big-pollutant'>
                        {emoji} <b>{name.upper()}</b>: {round(value,2)}
                    </div>
                    """, unsafe_allow_html=True)
                i += 1

            # AQI based on PM2.5
            pm = pollutants["pm2_5"]
            st.markdown("---")

            if pm <= 30:
                st.success("🟢 Air Quality Index: Good — Air is safe to breathe.")
            elif pm <= 60:
                st.warning("🟡 Air Quality Index: Moderate — Sensitive groups should limit outdoor exposure.")
            else:
                st.error("🔴 Air Quality Index: Poor — Avoid outdoor exposure!")

        except Exception as e:
            st.error(str(e))

    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# 💧 WATER QUALITY SECTION
# ---------------------------------------------------------
st.markdown("<div class='section-title'>💧 Water Quality</div>", unsafe_allow_html=True)

st.markdown("""
<div class="tagline-box" style="border-left-color:#00aa66;">
💧 Clean water is essential for health. Check if your city's water is safe to drink.
</div>
""", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    city_water = st.text_input("Enter city name for Water Quality")

    if st.button("Fetch Water Quality"):
        c = CITY_FIX.get(city_water.lower(), city_water).lower()

        if c not in df_water["city"].str.lower().values:
            st.error("City not found in water dataset.")
        else:
            row = df_water[df_water["city"].str.lower() == c].iloc[0]
            st.subheader(f"Water Parameters — {row['city'].title()}")

            water_params = {
                "pH": row["ph"],
                "Hardness": row["hardness"],
                "Solids": row["solids"],
            }

            limits = {
                "pH": (6.5, 8.5),
                "Hardness": (150, 300),
                "Solids": (300, 600),
            }

            cols = st.columns(3)
            i = 0
            for name, value in water_params.items():
                good, moderate = limits[name]
                emoji, label = pollutant_status(value, good, moderate)

                with cols[i % 3]:
                    st.markdown(f"""
                    <div class='big-pollutant'>
                        {emoji} <b>{name}</b>: {round(value,2)}
                    </div>
                    """, unsafe_allow_html=True)
                i += 1

            # ML Prediction
            model_path = os.path.join(BASE_DIR, "models", "water_quality_model.pkl")

            if os.path.exists(model_path):
                model = joblib.load(model_path)
                pred = model.predict([[row["ph"], row["hardness"], row["solids"]]])[0]
                if pred == 1:
                    st.success("🟢 Water is safe to drink.")
                else:
                    st.error("🔴 Water is NOT safe to drink.")
            else:
                st.warning("Water ML model not found.")

    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# 📊 COMPARE PM2.5 ACROSS CITIES
# ---------------------------------------------------------
st.markdown("<div class='section-title'>📊 Compare PM2.5 Across Cities</div>", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    cities_input = st.text_input("Enter cities (comma separated)")

    if st.button("Compare PM2.5"):
        cities = [c.strip() for c in cities_input.split(",") if c.strip()]
        names, values = [], []

        for c in cities[:3]:
            city = CITY_FIX.get(c.lower(), c).title()
            try:
                pollutants = get_air_quality_for_city(city)
                names.append(city)
                values.append(pollutants["pm2_5"])
            except:
                st.warning(f"Could not fetch data for {city}")

        if names:
            df = pd.DataFrame({"City": names, "PM2.5": values})
            fig = px.pie(df, names="City", values="PM2.5",
                         title="PM2.5 Comparison", hole=0.3)
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)
