'''import streamlit as st
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

try:
    df_water = pd.read_csv(os.path.join(BASE_DIR, "data", "water_quality_cities.csv"))
    df_water.columns = df_water.columns.str.lower().str.replace(" ", "_")
    water_model = joblib.load(os.path.join(BASE_DIR, "models", "water_quality_model.pkl"))
except FileNotFoundError as e:
    st.error(f"🔴 Critical Error: Required file not found. Ensure 'data/water_quality_cities.csv' and 'models/water_quality_model.pkl' exist. Details: {e}")
    st.stop()
except Exception as e:
    st.error(f"🔴 Critical Error: Failed to load data or model. Details: {e}")
    st.stop()


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

    city_air_input = st.text_input("Enter city name (e.g., Delhi, London, Bangalore)", key="air_input")

    if st.button("Fetch Air Quality"):
        if not city_air_input.strip():
            st.warning("⚠️ Please enter a city name.")
        else:
            city_raw = city_air_input.lower()
            city = CITY_ALIASES.get(city_raw, city_raw)
            
            try:
                pollutants = get_air_quality_for_city(city)
                weather = get_weather_for_city(city)
            except ValueError:
                st.error(f"🔴 Error: Air quality data for **{city_air_input.title()}** not found. Please check spelling or use a supported city (like 'Bangalore' to get 'Bengaluru').")
                st.stop() 

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
            pm = pollutants.get("pm2_5", 999) 
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

    city_water_input = st.text_input("Enter city name for water quality", key="water_input")

    if st.button("Fetch Water Data"):
        if not city_water_input.strip():
            st.warning("⚠️ Please enter city name.")
        else:
            city_raw = city_water_input.lower()
            city = CITY_ALIASES.get(city_raw, city_raw)
            
            filtered_df = df_water[df_water["city"].str.lower() == city]
            
            if filtered_df.empty:
                st.error(f"🔴 City **{city_water_input.title()}** not found in the water quality dataset. Ensure the spelling is correct (e.g., 'Bangalore' or 'Bengaluru') and the data exists in your CSV.")
            else:
                row = filtered_df.iloc[0]
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
                    if k in row:
                        v = row[k]
                        emoji = emoji_status(v, g, m) 
                        cols[i % 3].markdown(
                            f"<div class='metric-large'><b>{emoji}</b> {k.replace('_',' ').title()}: {round(v,2)}</div>",
                            unsafe_allow_html=True
                        )

                st.markdown("---")
                
                try:
                    features = [[row["ph"], row["hardness"], row["solids"]]]
                    pred = water_model.predict(features)[0]

                    if pred == 1:
                        st.success("🟢 Prediction: Water is safe to drink.")
                    else:
                        st.error("🔴 Prediction: Water is NOT safe for drinking. Further testing or treatment is recommended.")
                except Exception as e:
                    st.error(f"🔴 Error during water safety prediction. Details: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 📊 CITY COMPARISON (TWO INPUT BOXES)
# =========================================================
st.markdown("<div class='section-title'>📊 City PM2.5 Comparison</div>", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    city1_in = col1.text_input("City 1 (e.g., London)", key="compare_city1")
    city2_in = col2.text_input("City 2 (e.g., Delhi)", key="compare_city2")

    if st.button("Compare Cities"):
        if not city1_in or not city2_in:
            st.warning("⚠️ Please enter both city names.")
        else:
            c1_raw = city1_in.lower()
            c2_raw = city2_in.lower()
            
            c1 = CITY_ALIASES.get(c1_raw, c1_raw)
            c2 = CITY_ALIASES.get(c2_raw, c2_raw)
            
            try:
                pollutants1 = get_air_quality_for_city(c1)
                pollutants2 = get_air_quality_for_city(c2)
                
                pm1 = pollutants1["pm2_5"]
                pm2 = pollutants2["pm2_5"]
            except ValueError as e:
                st.error(f"🔴 Error fetching data: Air quality data for one or both cities not found. Please check spelling.")
                st.stop()
            except KeyError:
                st.error("🔴 Error: PM2.5 data missing for one or both cities.")
                st.stop()
            
            df = pd.DataFrame({
                "City": [c1.title(), c2.title()],
                "PM2.5": [pm1, pm2]
            })

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
            
            st.markdown("---")
            if pm1 > pm2:
                st.error(f"**{c1.title()}** is the **most polluted** (PM2.5: **{round(pm1, 2)}**) based on PM2.5 levels.")
            elif pm2 > pm1:
                st.error(f"**{c2.title()}** is the **most polluted** (PM2.5: **{round(pm2, 2)}**) based on PM2.5 levels.")
            else:
                st.info("Both cities have a similar PM2.5 level.")


    st.markdown("</div>", unsafe_allow_html=True)''''

