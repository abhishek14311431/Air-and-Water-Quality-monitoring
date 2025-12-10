# 🚀 GDUI PREMIUM DASHBOARD — CLEAN, COMPACT, SIDE‑BY‑SIDE LAYOUT
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
# Placeholder check for file existence (assuming you have created these files)
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
st.set_page_config(page_title="GDU Premium Dashboard - Universe Edition", page_icon="🌌", layout="wide")

# ------------------ DARK UNIVERSE / SOLAR SYSTEM THEME (REVISED) ------------------
st.markdown("""
<style>
/* 1. DARK UNIVERSE BACKGROUND */
body {
    background: #0d1117; /* Dark space background */
    background-attachment: fixed;
    background-size: cover;
    overflow: auto;
    color: #e6e6e6; /* Light text for contrast */
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
        radial-gradient(2px 2px at 20px 30px, #eee, rgba(0,0,0,0)),
        radial-gradient(2px 2px at 40px 70px, #fff, rgba(0,0,0,0)),
        radial-gradient(1px 1px at 90px 40px, #ddd, rgba(0,0,0,0)),
        radial-gradient(2px 2px at 130px 100px, #eee, rgba(0,0,0,0)),
        radial-gradient(1px 1px at 180px 50px, #fff, rgba(0,0,0,0));
    background-repeat: repeat;
    background-size: 200px 200px;
    opacity: 0.7;
    z-index: -1;
}

/* 3. CARD STYLING - NEBULA EFFECT */
.gdu-card {
    background: rgba(30, 41, 59, 0.7); /* Darker, semi-transparent card */
    border-radius: 15px;
    padding: 20px;
    box-shadow: 0 4px 15px rgba(0, 150, 255, 0.5); /* Blue/Nebula glow */
    border: 1px solid rgba(0, 150, 255, 0.3);
    margin-bottom: 20px;
}

/* 4. HEADERS - COSMIC GLOW */
.dashboard-title, .section-title, h2, h3, h4 {
    color: #93c5fd; /* Light Blue for a cosmic feel */
    text-shadow: 0 0 5px #0ea5e9; /* Subtle glow */
    border-bottom: 2px solid #0ea5e9;
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
    background-color: #0f172a; /* Even darker input */
    color: #e6e6e6;
    border: 1px solid #0ea5e9;
    border-radius: 8px;
}

.stButton > button:hover {
    background-color: #0ea5e9; /* Button hover glow */
    color: #0f172a;
    transition: all 0.3s;
}

/* 6. INDICATORS - VIBRANT POLLUTANT COLORS */
.indicator {
    padding: 10px 15px;
    margin: 5px;
    border-radius: 10px;
    color: #0d1117; /* Dark text for readability on bright indicators */
    font-weight: bold;
    display: inline-block;
}

/* Override Streamlit's default subheader color for the dark theme */
h3 {
    color: #93c5fd; 
}

/* Set the default color for all text in the main content */
.stMarkdown {
    color: #e6e6e6; 
}

/* Ensure the success/error messages are visible against the dark background */
.stSuccess > div, .stError > div {
    color: #0d1117;
    font-weight: bold;
}

/* Remove unused planet elements */
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
# Updated header emoji to reflect the theme
st.markdown('<div class="dashboard-title">🌌 GDU Premium Air + Water Quality Dashboard</div>', unsafe_allow_html=True)

# ================================================================
# SIDE‑BY‑SIDE DASHBOARD LAYOUT
# ================================================================
col_air, col_water = st.columns(2, gap="large")

# ------------------ AIR QUALITY SECTION ------------------
with col_air:
    st.markdown('<div class="gdu-card">', unsafe_allow_html=True)
    st.subheader("🪐 Air Quality Analysis")

    # City input field for Air Quality
    city = st.text_input("City (Air Quality)", key="air_city_input")

    if st.button("Fetch AQI", key="aqi-btn", use_container_width=True):
        try:
            c = city.lower().strip()
            # Handle aliases
            if c in CITY_ALIASES: c = CITY_ALIASES[c]
            city_display = c.title()

            # Placeholder for the actual API call (assuming 'utils.get_air_quality_for_city' works)
            # data = get_air_quality_for_city(c) 
            
            # Mock data for demonstration if utils is not available
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
    st.subheader("💧 Water Quality Prediction")

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
st.markdown('<div class="section-title">📜 Cosmic AQI Timeline</div>', unsafe_allow_html=True)
st.markdown('<div class="gdu-card">', unsafe_allow_html=True)

# Use the city entered in the main Air Quality section for context
hist_city = st.session_state.get('air_city_input', 'City') 

if st.button(f"Show AQI Timeline for {hist_city.title()}", use_container_width=True):
    try:
        # Static mock data for the timeline
        timeline_hours = ["1 AM","3 AM","6 AM","9 AM","12 PM","3 PM","6 PM","9 PM","12 AM"]
        timeline_values = [42, 55, 48, 60, 70, 82, 95, 88, 65]
        df_hist = pd.DataFrame({"Time": timeline_hours, "AQI": timeline_values})
        # Use an area chart with a vibrant color (e.g., #0ea5e9 for cosmic blue)
        st.line_chart(df_hist.set_index("Time"), color="#0ea5e9") 
    except Exception as e:
        st.error(f"TIMELINE ERROR → {e}")

st.markdown('</div>', unsafe_allow_html=True)

# =================================================================
# CITY-WISE AQI COMPARISON (Detailed Report)
st.markdown('<div class="section-title">☄️ Detailed City AQI Report</div>', unsafe_allow_html=True)
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
            # data = get_air_quality_for_city(c)
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
                    # The prediction is just a number (0, 1, or 2) representing the category
                    pred = aqi_model.predict([[*data.values()]])[0] 
                    vals[c.title()] = pred # Store the numerical category for the bar chart

            if vals:
                df_compare = pd.DataFrame({"City": list(vals.keys()), "AQI Score": list(vals.values())})
                st.bar_chart(df_compare.set_index("City"), color="#5b21b6") # Deep purple cosmic color
            else:
                st.warning("Please enter at least two cities to compare.")
                
    except Exception as e:
        st.error(f"COMPARISON ERROR → {e}")

st.markdown('</div>', unsafe_allow_html=True)



# INTERACTIVE HEATMAP FOR INDIA
st.markdown('<div class="section-title">🗺️ Galactic AQI Bar Chart</div>', unsafe_allow_html=True)
st.markdown('<div class="gdu-card">', unsafe_allow_html=True)

try:
    # Bar Chart for different cities AQI
    heat_cities = ["Alderaan","Coruscant","Tatooine","Krypton","Vulcan","Mars Colony"]
    # Random values for demonstration
    heat_values = np.random.randint(50,180,len(heat_cities)) 
    heat_df = pd.DataFrame({"City":heat_cities, "AQI":heat_values}).set_index("City")
    
    # Use a bar chart to simulate a heatmap effect on a region
    st.bar_chart(heat_df, color="#fde047") # Star/Sun yellow
except Exception as e:
    st.error(f"HEATMAP ERROR → {e}")

st.markdown('</div>', unsafe_allow_html=True)

# ------------------ FOOTER ------------------
st.markdown("<p style='text-align:center;margin-top:25px;font-size:16px;color:#94a3b8;'>GDU Universe Dashboard ✨ | Built with Cosmic Dust and Streamlit ❤️</p>", unsafe_allow_html=True)
