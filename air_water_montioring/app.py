import streamlit as st
import joblib
import pandas as pd
import numpy as np
import os
import plotly.express as px
from utils import get_air_quality_for_city # Assumes this function is defined in utils.py

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="Air & Water Quality Monitoring",
    page_icon="🌍",
    layout="wide",
)

# ---------------------------------------------------------
# GLOBAL CSS + BACKGROUND
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
    background: white;
    padding: 16px;
    border-radius: 12px;
    font-weight: 600;
    border-left: 5px solid #0077cc;
    margin-bottom: 15px;
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
# NOTE: Ensure the 'data' and 'models' folders exist in the same directory as this script.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
water_path = os.path.join(BASE_DIR, "data", "water_quality_cities.csv")
# Fallback for running locally without __file__ attribute (e.g., in some IDEs)
if not os.path.exists(water_path):
    water_path = os.path.join(os.getcwd(), "data", "water_quality_cities.csv") 

try:
    df_water = pd.read_csv(water_path)
    df_water.columns = df_water.columns.str.lower().str.replace(" ", "_")
except FileNotFoundError:
    st.error("Error: water_quality_cities.csv not found. Please ensure it's in the 'data' folder.")
    df_water = pd.DataFrame({"city": [], "ph": [], "hardness": [], "solids": [], 
                             "chloramines": [], "sulfate": [], "conductivity": [], 
                             "organic_carbon": [], "trihalomethanes": [], "turbidity": []})
    
CITY_ALIASES = {
    "bangalore": "bengaluru",
    "banglore": "bengaluru",
    "bombay": "mumbai",
}

# ---------------------------------------------------------
# HELPER — Status + Emoji
# ---------------------------------------------------------
def emoji_status(value, low, med):
    """Returns status based on value relative to low (Good limit) and med (Moderate limit)."""
    # Note: For pH, the logic might need adjustment if it's based on an acceptable range (e.g., 6.5-8.5).
    # This function assumes 'low' is the good threshold and 'med' is the moderate threshold (i.e., less is better).
    if value <= low:
        return "🟢 Good"
    elif value <= med:
        return "🟡 Moderate"
    return "🔴 Poor"

# ---------------------------------------------------------
# 🌫️ AIR QUALITY SECTION (FIXED)
# ---------------------------------------------------------
st.markdown("<div class='section-title'>🌫️ Air Quality</div>", unsafe_allow_html=True)

st.markdown("""
<div class="tagline-box">
🌬️ The air you breathe affects your daily health. Track pollution levels & stay safe outdoors.
</div>
""", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    city_air = st.text_input("Enter city name for Air Quality")

    if st.button("Fetch Air Quality"):
        try:
            c = CITY_ALIASES.get(city_air.lower().strip(), city_air).title() # Title case for display
            
            # ❗ Fetch Air API (dict of pollutant values)
            pollutants = get_air_quality_for_city(c)

            # --- CRITICAL FIX: Check if pollutants is a dictionary ---
            if not isinstance(pollutants, dict) or not pollutants:
                st.error(f"❌ Could not retrieve air quality data for **{c}**. Please check the city name or verify the `get_air_quality_for_city` function.")
            else:
                st.subheader(f"Pollutant Levels in {c}")

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
                for key in pollutants.keys():
                    if key in limits: # Only display pollutants we have limits for
                        low, med = limits[key]
                        status = emoji_status(pollutants[key], low, med)
                        emoji = status.split()[0]

                        with cols[i % 3]:
                            st.markdown(f"""
                                <div style='font-size:24px;'>
                                    <b style='font-size:32px'>{emoji}</b>
                                    <b>{key.upper()}</b>: {round(pollutants[key], 2)}
                                </div>
                            """, unsafe_allow_html=True)
                        i += 1

                # ------- AI Category (based on PM2.5) -------
                if "pm2_5" in pollutants:
                    pm = pollutants["pm2_5"]

                    st.markdown("---") # Separator for AQI category

                    if pm <= 30:
                        st.success("🟢 **Air Quality Index: Good** — Air is safe to breathe.")
                    elif pm <= 60:
                        st.warning("🟡 **Air Quality Index: Moderate** — Sensitive people should limit outdoor exposure.")
                    else:
                        st.error("🔴 **Air Quality Index: Poor** — Avoid outdoor exposure!")
                else:
                    st.info("ℹ️ PM2.5 data not available for general air quality assessment.")


        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")

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
        try:
            c2 = CITY_ALIASES.get(city_water.lower().strip(), city_water)

            if c2.lower() not in df_water["city"].str.lower().values:
                st.error(f"City **{city_water.title()}** not found in water dataset.")
            else:
                row = df_water[df_water["city"].str.lower() == c2.lower()].iloc[0]

                st.subheader(f"Water Parameters — {c2.title()}")

                # Note: These limits are simple comparisons, not strict ranges for acceptability.
                # 'low' here means a value up to the 'low' threshold is 'Good'.
                water_limits = {
                    "ph": (6.5, 8.5), # pH is better handled as a range, but using existing helper logic
                    "hardness": (150, 300),
                    "solids": (300, 600),
                    "chloramines": (2, 4),
                    "sulfate": (100, 250),
                    "conductivity": (200, 400),
                    "organic_carbon": (2, 4),
                    "trihalomethanes": (40, 80),
                    "turbidity": (1, 3)
                }

                cols = st.columns(3)

                for i, key in enumerate(water_limits.keys()):
                    if key in row: # Ensure the column exists
                        val = row[key]
                        low, med = water_limits[key]
                        
                        # Simplified status check (not ideal for pH, but keeps consistent with emoji_status)
                        status = emoji_status(val, low, med) 
                        emoji = status.split()[0]

                        with cols[i % 3]:
                            st.markdown(f"""
                                <div style='font-size:24px;'>
                                    <b style='font-size:32px'>{emoji}</b>
                                    <b>{key.replace('_',' ').title()}</b>: {round(val, 2)}
                                </div>
                            """, unsafe_allow_html=True)

                # ------- ML prediction -------
                st.markdown("---")
                
                # Check for model file existence
                model_path = os.path.join(BASE_DIR, "models", "water_quality_model.pkl")
                if not os.path.exists(model_path):
                     st.warning("⚠️ ML Model file 'water_quality_model.pkl' not found in 'models' directory. Cannot make prediction.")
                elif "ph" not in row or "hardness" not in row or "solids" not in row:
                     st.warning("⚠️ Missing critical water parameters (pH, Hardness, Solids) for ML prediction.")
                else:
                    model_w = joblib.load(model_path)
                    
                    # NOTE: Input array must match training features (ph, hardness, solids)
                    # We are passing a 2D array: [[feature_1, feature_2, feature_3]]
                    pred_raw = model_w.predict([[row["ph"], row["hardness"], row["solids"]]])[0]

                    if pred_raw == 1:
                        st.success("🟢 **ML Prediction:** Water is safe to drink.")
                    else:
                        st.error("🔴 **ML Prediction:** Not safe for drinking.")

        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 📊 CITY COMPARISON (PM2.5) (FIXED)
# ---------------------------------------------------------
st.markdown("<div class='section-title'>📊 Compare PM2.5 Across Cities</div>", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    cities_input = st.text_input("Enter up to 3 cities (comma separated)")

    if st.button("Compare Cities"):
        try:
            input_cities = [c.strip() for c in cities_input.split(",") if c.strip()]
            
            if not input_cities:
                st.warning("Please enter at least one city name.")
            else:
                names, values = [], []
                
                # Limit to 3 cities
                cities_to_compare = input_cities[:3]

                for c in cities_to_compare:
                    fixed_city = CITY_ALIASES.get(c.lower(), c).title()
                    
                    # --- CRITICAL FIX: Check if pollutants is a dictionary and has pm2_5 ---
                    pollutants = get_air_quality_for_city(fixed_city)
                    
                    if isinstance(pollutants, dict) and "pm2_5" in pollutants:
                        pm = pollutants["pm2_5"]
                        names.append(fixed_city)
                        values.append(pm)
                    else:
                        st.warning(f"⚠️ Could not get PM2.5 data for **{fixed_city}**.")

                if names:
                    df = pd.DataFrame({"City": names, "PM2.5": values})
                    
                    # Set color scale based on PM2.5 limits for better visualization
                    color_map = {}
                    for i in df.index:
                        pm_val = df.loc[i, 'PM2.5']
                        if pm_val <= 30:
                            color_map[df.loc[i, 'City']] = 'green'
                        elif pm_val <= 60:
                            color_map[df.loc[i, 'City']] = 'orange'
                        else:
                            color_map[df.loc[i, 'City']] = 'red'

                    fig = px.pie(
                        df, 
                        names="City", 
                        values="PM2.5", 
                        title="PM2.5 Comparison (Micrograms per cubic meter)",
                        color="City",
                        color_discrete_map=color_map,
                        hole=0.3 # Add a hole for a donut chart look
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No valid PM2.5 data retrieved for comparison.")

        except Exception as e:
            st.error(f"An unexpected error occurred during comparison: {str(e)}")

    st.markdown("</div>", unsafe_allow_html=True)
