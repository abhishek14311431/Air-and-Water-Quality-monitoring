import streamlit as st
import joblib
import pandas as pd
import os
import plotly.express as px

# Ensure you have a 'utils.py' file with these functions implemented
# (These functions need to handle API errors and return data or raise ValueError)
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

# --- Load Data and Model ---
try:
    df_water = pd.read_csv(os.path.join(BASE_DIR, "data", "water_quality_cities.csv"))
    df_water.columns = df_water.columns.str.lower().str.replace(" ", "_")
    water_model = joblib.load(os.path.join(BASE_DIR, "models", "water_quality_model.pkl"))
except FileNotFoundError as e:
    st.error(f"🔴 Critical Error: Required file not found. Ensure 'data/water_quality_cities.csv' and 'models/water_quality_model.pkl' exist. Details: {e}")
    st.stop()


CITY_ALIASES = {
    "bangalore": "bengaluru",
    "bombay": "mumbai",
}

def emoji_status(val, good, moderate):
    """Returns an emoji based on the value's position relative to 'good' and 'moderate' limits."""
    # This assumes 'good' is less than 'moderate'
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

    city_air = st.text_input("Enter city name", key="air_input")

    if st.button("Fetch Air Quality"):
        if not city_air.strip():
            st.warning("⚠️ Please enter a city name.")
        else:
            city = CITY_ALIASES.get(city_air.lower(), city_air)
            
            # --- FIX: Added try-except to handle ValueError from get_air_quality_for_city ---
            try:
                pollutants = get_air_quality_for_city(city)
                weather = get_weather_for_city(city)
            except ValueError:
                # Assuming ValueError is raised when city data is not available (as per your traceback)
                st.error(f"🔴 Error: Real-time air quality data for **{city.title()}** not found. Please try another city.")
                st.stop() # Stop further execution in this block

            st.subheader(f"Weather in {city.title()}")
            c1, c2, c3 = st.columns(3)
            c1.metric("🌡️ Temperature", f"{weather['temperature_c']} °C")
            c2.metric("💧 Humidity", f"{weather['humidity_percent']} %")
            c3.metric("🌬️ Wind", f"{weather['wind_speed']} m/s")

            st.markdown("---")
            st.subheader("Pollutants")

            limits = {
                "pm2_5": (30, 60),  # Example limits (Good, Moderate)
                "pm10": (50, 100),
                "no2": (40, 80),
                "so2": (20, 80),
                "o3": (50, 100),
                "co": (200, 400),
            }

            cols = st.columns(3)
            for i, (k, v) in enumerate(pollutants.items()):
                # Ensure the pollutant key exists in the limits dictionary to prevent KeyError
                if k in limits:
                    emoji = emoji_status(v, *limits[k])
                    cols[i % 3].markdown(
                        f"<div class='metric-large'><b>{emoji}</b> {k.upper()}: {round(v,2)}</div>",
                        unsafe_allow_html=True
                    )
                else:
                    cols[i % 3].markdown(
                        f"<div class='metric-large'> {k.upper()}: {round(v,2)}</div>",
                        unsafe_allow_html=True
                    )


            st.markdown("---")
            # Overall AQI based on PM2.5 (a common indicator)
            pm = pollutants.get("pm2_5", 999) # Use a high default if key is missing
            if pm <= 30:
                st.success("🟢 AQI Good — Safe to breathe.")
            elif pm <= 60:
                st.warning("🟡 AQI Moderate — Limit outdoor exposure.")
            else:
                st.error("🔴 AQI Poor — Avoid outdoor activities. ")

    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 💧 WATER QUALITY (ALL POLLUTANTS)
# =========================================================
st.markdown("<div class='section-title'>💧 Water Quality</div>", unsafe_allow_html=True)
st.markdown("<div class='tagline-box' style='border-left-color:#00aa66;'>💧 Check drinking water safety.</div>", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    city_water = st.text_input("Enter city name for water quality", key="water_input")

    if st.button("Fetch Water Data"):
        if not city_water.strip():
            st.warning("⚠️ Please enter city name.")
        else:
            city = CITY_ALIASES.get(city_water.lower(), city_water)
            
            # Use .str.contains for a more flexible check (though .values is fine)
            if not df_water["city"].str.lower().str.contains(city, case=False, regex=False).any():
                st.error(f"🔴 City **{city.title()}** not found in the water quality dataset.")
            else:
                row = df_water[df_water["city"].str.lower() == city].iloc[0]
                st.subheader(f"Water Parameters — {row['city'].title()}")

                # Limits for water quality parameters (Example limits)
                water_limits = {
                    "ph": (6.5, 8.5),        # Optimal pH range
                    "hardness": (150, 300),  # Unit: mg/L, often Ca/Mg concentration
                    "solids": (300, 600),    # Total Dissolved Solids (TDS), Unit: mg/L
                    "chloramines": (2, 4),   # Unit: mg/L
                    "sulfate": (100, 250),   # Unit: mg/L
                    "conductivity": (200, 400), # Unit: µS/cm (microsiemens per centimeter)
                    "organic_carbon": (2, 4), # Total Organic Carbon (TOC), Unit: mg/L
                    "trihalomethanes": (40, 80), # THMs, Unit: µg/L (micrograms per liter)
                    "turbidity": (1, 3),     # Unit: NTU (Nephelometric Turbidity Units)
                }

                cols = st.columns(3)
                for i, (k, (g, m)) in enumerate(water_limits.items()):
                    if k in row:
                        v = row[k]
                        # For water parameters, often a value *outside* the (g, m) range is bad. 
                        # We'll stick to the original emoji_status logic for consistency (low=good). 
                        # A more accurate function would check for being within the optimal range.
                        emoji = emoji_status(v, g, m) 
                        cols[i % 3].markdown(
                            f"<div class='metric-large'><b>{emoji}</b> {k.replace('_',' ').title()}: {round(v,2)}</div>",
                            unsafe_allow_html=True
                        )

                st.markdown("---")
                
                # Predict water safety using the loaded model
                try:
                    # Model expects a list of features: [ph, hardness, solids]
                    features = [[row["ph"], row["hardness"], row["solids"]]]
                    pred = water_model.predict(features)[0]

                    if pred == 1:
                        st.success("🟢 Prediction: Water is safe to drink.")
                    else:
                        st.error("🔴 Prediction: Water is NOT safe for drinking. Further testing or treatment is recommended.")
                except Exception:
                    st.error("🔴 Error during water safety prediction. Check model feature consistency.")

    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 📊 CITY COMPARISON (TWO INPUT BOXES)
# =========================================================
st.markdown("<div class='section-title'>📊 City PM2.5 Comparison</div>", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    city1_in = col1.text_input("City 1", key="compare_city1")
    city2_in = col2.text_input("City 2", key="compare_city2")

    if st.button("Compare Cities"):
        if not city1_in or not city2_in:
            st.warning("⚠️ Please enter both city names.")
        else:
            c1 = CITY_ALIASES.get(city1_in.lower(), city1_in)
            c2 = CITY_ALIASES.get(city2_in.lower(), city2_in)
            
            # --- FIX: Added try-except for comparison ---
            try:
                # Fetch data for both cities
                pollutants1 = get_air_quality_for_city(c1)
                pollutants2 = get_air_quality_for_city(c2)
                
                pm1 = pollutants1["pm2_5"]
                pm2 = pollutants2["pm2_5"]
            except ValueError as e:
                # Handle cases where one or both cities are not found
                st.error(f"🔴 Error fetching data: {e}. Please ensure both cities are valid.")
                st.stop()
            except KeyError:
                st.error("🔴 Error: PM2.5 data missing for one or both cities.")
                st.stop()
            
            # --- Create Comparison Data and Chart ---
            df = pd.DataFrame({
                "City": [c1.title(), c2.title()],
                "PM2.5": [pm1, pm2]
            })

            # Color logic: give 'red' to the city with the higher PM2.5 value
            colors = {}
            if pm1 > pm2:
                 colors = {c1.title(): "#cc3333", c2.title(): "#3399ff"}
            elif pm2 > pm1:
                colors = {c1.title(): "#3399ff", c2.title(): "#cc3333"}
            else:
                colors = {c1.title(): "#3399ff", c2.title(): "#3399ff"}

            fig = px.pie(df, names="City", values="PM2.5",
                         color="City", color_discrete_map=colors,
                         title="PM2.5 Comparison (Higher PM2.5 = Larger Slice)")

            st.plotly_chart(fig, use_container_width=True)
            
            # --- Explicitly state the most polluted city ---
            st.markdown("---")
            if pm1 > pm2:
                st.error(f"**{c1.title()}** is the **most polluted** (PM2.5: **{round(pm1, 2)}**) based on PM2.5 levels.")
            elif pm2 > pm1:
                st.error(f"**{c2.title()}** is the **most polluted** (PM2.5: **{round(pm2, 2)}**) based on PM2.5 levels.")
            else:
                st.info("Both cities have a similar PM2.5 level.")


    st.markdown("</div>", unsafe_allow_html=True)
