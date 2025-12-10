# 🚀 GDUI PREMIUM DASHBOARD — SOLAR SYSTEM EDITION
# -------------------------------------------------------------------
import streamlit as st
import numpy as np
import joblib
import pandas as pd
import os
from utils import get_air_quality_for_city

# NOTE: The 'utils.py' and the model/data files 
# (air_quality_model.pkl, water_quality_model.pkl, water_quality_cities.csv)
# must be present in the correct relative paths for this code to run successfully.
# ------------------ PATHS ------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
water_csv_path = os.path.join(BASE_DIR, "data", "water_quality_cities.csv")
# Placeholder check for file existence
try:
    df_water = pd.read_csv(water_csv_path)
except FileNotFoundError:
    st.error("Data file not found. Ensure 'data/water_quality_cities.csv' exists.")
    st.stop()
except Exception as e:
    st.error(f"Error loading water data: {e}")
    st.stop()


# ------------------ CITY ALIASES ------------------
CITY_ALIASES = {"bangalore":"bengaluru", "banglore":"bengaluru", "bombay":"mumbai"}

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="GDU Premium Dashboard - Solar System Edition", page_icon="🪐", layout="wide")

# =================================================================
# 🪐 SOLAR SYSTEM / NEBULA THEME (REVISED BACKGROUND)
# =================================================================
st.markdown("""
<style>
/* 1. SOLAR SYSTEM BACKGROUND (Deep space purple/blue nebula) */
body {
    background: radial-gradient(circle at 10% 20%, rgba(0, 0, 0, 1) 0%, rgba(17, 24, 39, 1) 40%, rgba(30, 0, 50, 1) 100%);
    background-attachment: fixed;
    background-size: cover;
    overflow: auto;
    color: #f0f4f8; /* Light text for high contrast */
}

/* 2. GLOWING STARFIELD EFFECT */
body::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    /* Simple starfield via CSS gradient */
    background-image: 
        radial-gradient(2px 2px at 20px 30px, #fff, rgba(0,0,0,0)),
        radial-gradient(1px 1px at 70px 110px, #ffd700, rgba(0,0,0,0)), /* Sun-like star */
        radial-gradient(2px 2px at 150px 50px, #eee, rgba(0,0,0,0)),
        radial-gradient(1px 1px at 200px 90px, #fff, rgba(0,0,0,0));
    background-repeat: repeat;
    background-size: 200px 200px;
    opacity: 0.8;
    z-index: -1;
}

/* 3. CARD STYLING - NEBULA EFFECT */
.gdu-card {
    background: rgba(30, 41, 59, 0.75); /* Darker, semi-transparent card */
    border-radius: 15px;
    padding: 20px;
    box-shadow: 0 4px 20px rgba(255, 165, 0, 0.5); /* Orange/Sun glow */
    border: 1px solid rgba(255, 165, 0, 0.3);
    margin-bottom: 20px;
}

/* 4. HEADERS - SOLAR GLOW */
.dashboard-title, .section-title, h2, h3, h4 {
    color: #ffcc66; /* Gold/Yellow for a solar feel */
    text-shadow: 0 0 8px #ff9900; /* Subtle Sun glow */
    border-bottom: 2px solid #ff9900;
    padding-bottom: 5px;
    margin-bottom: 15px;
}

.dashboard-title {
    font-size: 2.5em;
    text-align: center;
    padding: 10px 0;
}

/* 5. INPUTS/BUTTONS */
.stTextInput > div > div > input, .stButton > button {
    background-color: #1f2937; /* Dark input */
    color: #f0f4f8;
    border: 1px solid #ff9900;
    border-radius: 8px;
}

.stButton > button:hover {
    background-color: #ff9900; /* Button hover glow */
    color: #1f2937;
    transition: all 0.3s;
}

/* 6. INDICATORS - VIBRANT POLLUTANT COLORS */
.indicator {
    padding: 10px 15px;
    margin: 5px;
    border-radius: 10px;
    color: #1f2937; /* Dark text for readability on bright indicators */
    font-weight: bold;
    display: inline-block;
}

/* General text and cleanup */
h3 { color: #ffcc66; } 
.stMarkdown { color: #f0f4f8; } 
.stSuccess > div, .stError > div { color: #1f2937; font-weight: bold; }
#planet1, #planet2, #planet3 { display: none !important; }
</style>
""", unsafe_allow_html=True)


# ------------------ HELPERS ------------------
def pollutant_color(v): return "#16a34a" if v<50 else "#eab308" if v<100 else "#dc2626"
def map_air_label(x): return {0:"Good",1:"Moderate",2:"Poor"}.get(x)
def air_color(x): return {"Good":"#16A34A","Moderate":"#EAB308","Poor":"#DC2626"}[x]
def map_water_label(x): return "Drinkable" if x==1 else "Not Drinkable"
def water_color(x): return {"Drinkable":"#16A34A","Not Drinkable":"#DC2626"}[x]

# ------------------ HEADER ------------------
st.markdown('<div class="dashboard-title">☀️ GDU Premium Air + Water Quality Dashboard</div>', unsafe_allow_html=True)

# ================================================================
# SIDE‑BY‑SIDE DASHBOARD LAYOUT
# ================================================================
col_air, col_water = st.columns(2, gap="large")

# ------------------ AIR QUALITY SECTION ------------------
with col_air:
    st.markdown('<div class="gdu-card">', unsafe_allow_html=True)
    st.subheader("🛰️ Air Quality Analysis")

    # City input field for Air Quality
    city = st.text_input("City (Air Quality)", key="air_city_input")

    if st.button("Fetch AQI", key="aqi-btn", use_container_width=True):
        try:
            c = city.lower().strip()
            # Handle aliases
            if c in CITY_ALIASES: c = CITY_ALIASES[c]
            city_display = c.title()

            # Placeholder for the actual API call (assuming 'utils.get_air_quality_for_city' works)
            if 'get_air_quality_for_city' not in globals():
                 data = {"co": 45, "o3": 52, "no2": 35, "so2": 15}
            else:
                 data = get_air_quality_for_city(c)
                 
            st.success(f"Live AQI Data for {city_display}")

            # Display indicators
            for k,v in data.items():
                st.markdown(f"<div class='indicator' style='background:{pollutant_color(v)}'>{k.upper()}: {v}</div>", unsafe_allow_html=True)

            # Predict AQI
            model_path = os.path.join(BASE_DIR, "models", "air_quality_model.pkl")
            if os.path.exists(model_path):
                model = joblib.load(model_path)
                pred = map_air_label(model.predict([[*data.values()]])[0])
                st.markdown(f"<h4 style='text-align:center;color:{air_color(pred)}'>Air Quality: {pred}</h4>", unsafe_allow_html=True)
            else:
                st.warning("Air quality model not found. Cannot predict.")

        except Exception as e:
            st.error(f"API ERROR → {e}")

    st.markdown('</div>', unsafe_allow_html=True)

    

# ------------------ WATER QUALITY SECTION ------------------
with col_water:
    st.markdown('<div class="gdu-card">', unsafe_allow_html=True)
    st.subheader("🪐 Water Quality Prediction")

    # City input field for Water Quality
    city2 = st.text_input("City (Water Quality)", key="water_city_input")

    if st.button("Check Water", key="water-btn", use_container_width=True):
        try:
            c2 = CITY_ALIASES.get(city2.lower().strip(), city2).title()
            
            if c2 not in df_water["City"].tolist(): 
                st.error(f"City '{c2}' not found in the water quality dataset.")
            else:
                row = df_water[df_water["City"] == c2].iloc[0]
                # Assuming the model uses these three features in this order
                ph, hard, sol = row["pH"], row["Hardness"], row["Solids"]

                # Display parameters
                st.table(pd.DataFrame({"Parameter":["pH","Hardness","Solids"],"Value":[ph,hard,sol]}))

                # Predict Water Quality
                model_path = os.path.join(BASE_DIR, "models", "water_quality_model.pkl")
                if os.path.exists(model_path):
                    model = joblib.load(model_path)
                    # Use only the features required by the model
                    pred = map_water_label(model.predict([[ph,hard,sol]])[0])
                    st.markdown(f"<h4 style='text-align:center;color:{water_color(pred)}'>Water Quality: {pred}</h4>", unsafe_allow_html=True)
                else:
                    st.warning("Water quality model not found. Cannot predict.")

        except Exception as e:
            st.error(f"WATER ERROR → {e}")

    st.markdown('</div>', unsafe_allow_html=True)

# =================================================================
# AQI HISTORY TIMELINE
# =================================================================
st.markdown('<div class="section-title">📜 Lunar AQI Timeline</div>', unsafe_allow_html=True)
st.markdown('<div class="gdu-card">', unsafe_allow_html=True)

# Use the city entered in the main Air Quality section for context
hist_city = st.session_state.get('air_city_input', 'City') 

if st.button(f"Show AQI Timeline for {hist_city.title()}", use_container_width=True):
    try:
        # Static mock data for the timeline
        timeline_hours = ["1 AM","3 AM","6 AM","9 AM","12 PM","3 PM","6 PM","9 PM","12 AM"]
        timeline_values = [42, 55, 48, 60, 70, 82, 95, 88, 65]
        df_hist = pd.DataFrame({"Time": timeline_hours, "AQI": timeline_values})
        # Use an area chart with a vibrant solar color
        st.line_chart(df_hist.set_index("Time"), color="#ff9900") 
    except Exception as e:
        st.error(f"TIMELINE ERROR → {e}")

st.markdown('</div>', unsafe_allow_html=True)

# =================================================================
# CITY-WISE AQI COMPARISON (Detailed Report)
st.markdown('<div class="section-title">☄️ Detailed Planet Report</div>', unsafe_allow_html=True)
st.markdown('<div class="gdu-card">', unsafe_allow_html=True)

single_city = st.session_state.get('air_city_input', '')

if st.button("Get City AQI Details", key="details-btn", use_container_width=True):
    try:
        if not single_city:
            st.warning("Please enter a city in the 'Air Quality Analysis' section above first.")
        else:
            c = CITY_ALIASES.get(single_city.lower().strip(), single_city)
            city_display = c.title()
            
            # Placeholder for the actual API call
            if 'get_air_quality_for_city' not in globals():
                 data = {"co": 45, "o3": 52, "no2": 35, "so2": 15}
            else:
                 data = get_air_quality_for_city(c)

            st.markdown(f"<h4 style='text-align:center;'>🌍 Full AQI Report — {city_display}</h4>", unsafe_allow_html=True)

            # Show pollutant indicators
            for k, v in data.items():
                st.markdown(f"<div class='indicator' style='background:{pollutant_color(v)}'>{k.upper()}: {v}</div>", unsafe_allow_html=True)

            # Predict AQI
            model_path = os.path.join(BASE_DIR, "models", "air_quality_model.pkl")
            if os.path.exists(model_path):
                model = joblib.load(model_path)
                pred = map_air_label(model.predict([[*data.values()]])[0])
                st.markdown(f"<h4 style='text-align:center;color:{air_color(pred)}'>Air Quality: {pred}</h4>", unsafe_allow_html=True)
            else:
                 st.warning("Air quality model not found. Cannot predict.")

    except Exception as e:
        st.error(f"DETAILS ERROR → {e}")

st.markdown('</div>', unsafe_allow_html=True)

# ========================= CITY COMPARISON =========================
st.markdown('<div class="section-title">📊 Compare Planetary Cities</div>', unsafe_allow_html=True)
st.markdown('<div class="gdu-card">', unsafe_allow_html=True)

c1 = st.text_input("City 1", key="compare_c1")
c2 = st.text_input("City 2", key="compare_c2")
c3 = st.text_input("City 3 (optional)", key="compare_c3")

if st.button("Compare Cities", key="compare-btn", use_container_width=True):
    try:
        def fetch(city):
            city = CITY_ALIASES.get(city.lower().strip(), city)
            # Use mock data if get_air_quality_for_city is not available
            if 'get_air_quality_for_city' not in globals():
                 return {"co": np.random.randint(20, 80), "o3": np.random.randint(40, 90), "no2": np.random.randint(30, 70), "so2": np.random.randint(10, 40)}
            return get_air_quality_for_city(city)

        vals = {}
        model_path = os.path.join(BASE_DIR, "models", "air_quality_model.pkl")
        
        if not os.path.exists(model_path):
            st.error("Air quality model not found. Comparison failed.")
        else:
            aqi_model = joblib.load(model_path)
            
            for c in [c1, c2, c3]:
                if c and c.strip() != "":
                    data = fetch(c)
                    pred = aqi_model.predict([[*data.values()]])[0] 
                    vals[c.title()] = pred 

            if vals:
                df_compare = pd.DataFrame({"City": list(vals.keys()), "AQI Score": list(vals.values())})
                st.bar_chart(df_compare.set_index("City"), color="#ff7f50") # Coral/Mars red
            else:
                st.warning("Please enter at least two cities to compare.")
                
    except Exception as e:
        st.error(f"COMPARISON ERROR → {e}")

st.markdown('</div>', unsafe_allow_html=True)



# INTERACTIVE HEATMAP FOR INDIA
st.markdown('<div class="section-title">🗺️ Solar AQI Bar Chart</div>', unsafe_allow_html=True)
st.markdown('<div class="gdu-card">', unsafe_allow_html=True)

try:
    # Bar Chart for different cities AQI
    heat_cities = ["Mercury","Venus","Earth","Mars","Jupiter","Saturn"]
    # Random values for demonstration
    heat_values = np.random.randint(50,180,len(heat_cities)) 
    heat_df = pd.DataFrame({"City":heat_cities, "AQI":heat_values}).set_index("City")
    
    # Use a bar chart with a yellow/gold color
    st.bar_chart(heat_df, color="#ffd700") 
except Exception as e:
    st.error(f"HEATMAP ERROR → {e}")

st.markdown('</div>', unsafe_allow_html=True)

# ------------------ FOOTER ------------------
st.markdown("<p style='text-align:center;margin-top:25px;font-size:16px;color:#f0f4f8;'>GDU Solar System Dashboard ✨ | Orbiting Data with Precision ❤️</p>", unsafe_allow_html=True)
