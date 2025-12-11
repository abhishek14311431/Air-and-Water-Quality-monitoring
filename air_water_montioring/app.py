import streamlit as st
import joblib
import pandas as pd
import os
import plotly.express as px
from utils import get_air_quality_for_city


# ---------------------------------------------------------
# PAGE CONFIG + GLOBAL STYLE
# ---------------------------------------------------------
st.set_page_config(
    page_title="Air & Water Quality Monitoring",
    page_icon="🌍",
    layout="wide"
)

# Background color (sky blue)
st.markdown("""
<style>
.stApp {
    background-color: #d8ecff;
    font-family: 'Segoe UI', sans-serif;
}

.main-title {
    font-size: 46px;
    text-align: center;
    font-weight: 900;
    color: #003554;
    margin-top: -10px;
}

.section-title {
    font-size: 32px;
    color: #003554;
    font-weight: 800;
    margin-bottom: 5px;
    padding-top: 10px;
}

.card {
    background: white;
    padding: 28px;
    border-radius: 16px;
    box-shadow: 0 4px 18px rgba(0,0,0,0.15);
    margin-bottom: 25px;
}

.tag-box {
    background: rgba(0,0,0,0.05);
    padding: 10px 14px;
    border-radius: 10px;
    font-size: 16px;
    margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)



# ---------------------------------------------------------
# TITLE
# ---------------------------------------------------------
st.markdown("<div class='main-title'>🌍 Air & Water Quality Monitoring</div>", unsafe_allow_html=True)
st.write("Analyze real-time environmental conditions with ML-powered predictions.")



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
    "bombay": "mumbai"
}



# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------
def pollutant_color(value, low, med):
    if value <= low:
        return "🟢 Good", "green"
    elif value <= med:
        return "🟡 Moderate", "yellow"
    return "🔴 Poor", "red"


def weather_icon(cond):
    cond = cond.lower()
    if "rain" in cond:
        return "🌧"
    if "cloud" in cond:
        return "☁️"
    return "☀️"



# =================================================================
# 🌫️ AIR QUALITY SECTION
# =================================================================
st.markdown("<div class='section-title'>🌫️ Air Quality</div>", unsafe_allow_html=True)
st.markdown("<div class='tag-box'>🌬️ Check live pollution levels and weather conditions for your city.</div>", unsafe_allow_html=True)

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
                "no2":  (40, 80),
                "so2":  (20, 80),
                "o3":   (50, 100),
                "co":   (200, 400)
            }

            cols = st.columns(3)

            # pollutant row
            for i, key in enumerate(pollutants):
                low, med = limits[key]
                status, _ = pollutant_color(pollutants[key], low, med)
                emoji = status.split()[0]  # extract 🟢🟡🔴

                with cols[i % 3]:
                    st.write(f"{emoji} **{key.upper()}**: {round(pollutants[key], 2)}")

            # Weather
            st.subheader("🌦 Current Weather")
            wcols = st.columns(3)
            wcols[0].metric(f"{weather_icon(weather['condition'])} Condition", weather["condition"])
            wcols[1].metric("🌡 Temperature (°C)", weather["temp"])
            wcols[2].metric("💧 Humidity (%)", weather["humidity"])

            # Health Advisory
            pm25, pm10, no2 = pollutants["pm2_5"], pollutants["pm10"], pollutants["no2"]
            score = sum([
                pm25 > 60,
                pm10 > 100,
                no2 > 80
            ])

            st.subheader("🏥 Health Advisory")

            if score == 0:
                st.success("💚 Air is safe to breathe.")
            elif score == 1:
                st.warning("🟡 Moderate — sensitive individuals should reduce outdoor activity.")
            else:
                st.error("🔴 Poor — avoid outdoor exposure!")

        except Exception as e:
            st.error(str(e))

    st.markdown("</div>", unsafe_allow_html=True)



# =================================================================
# 💧 WATER QUALITY SECTION
# =================================================================
st.markdown("<div class='section-title'>💧 Water Quality</div>", unsafe_allow_html=True)
st.markdown("<div class='tag-box'>💧 Check drinking water safety for your location.</div>", unsafe_allow_html=True)

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
                    val = row[param]
                    low, med = water_limits[param]
                    status, _ = pollutant_color(val, low, med)
                    emoji = status.split()[0]

                    with cols[i % 3]:
                        st.write(f"{emoji} **{param.replace('_', ' ').title()}**: {round(val, 2)}")

                # ML Prediction
                model = joblib.load(os.path.join(BASE_DIR, "models", "water_quality_model.pkl"))
                pred = model.predict([[row["ph"], row["hardness"], row["solids"]]])[0]

                st.subheader("🚰 Water Safety")

                if pred == 1:
                    st.success("💧 Water is **Drinkable**.")
                else:
                    st.error("🚱 Water is **Not Safe for Drinking**.")

        except Exception as e:
            st.error(str(e))

    st.markdown("</div>", unsafe_allow_html=True)



# =================================================================
# 📊 CITY COMPARISON (PM2.5 Pie Chart)
# =================================================================
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
                    pm = get_air_quality_for_city(fixed)[0]["pm2_5"]
                    labels.append(fixed.title())
                    values.append(pm)

            df = pd.DataFrame({"City": labels, "PM2.5": values})
            fig = px.pie(df, names="City", values="PM2.5", title="PM2.5 Comparison")
            st.plotly_chart(fig)

        except Exception as e:
            st.error(str(e))

    st.markdown("</div>", unsafe_allow_html=True)
