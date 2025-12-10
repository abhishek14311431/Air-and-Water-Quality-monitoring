# 🚀 GDUI PREMIUM DASHBOARD — CLEAN, COMPACT, SIDE‑BY‑SIDE LAYOUT
# -------------------------------------------------------------------
import streamlit as st
import numpy as np
import joblib
import pandas as pd
import os
from utils import get_air_quality_for_city

# ------------------ PATHS ------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
water_csv_path = os.path.join(BASE_DIR, "data", "water_quality_cities.csv")
df_water = pd.read_csv(water_csv_path)

# ------------------ CITY ALIASES ------------------
CITY_ALIASES = {"bangalore":"bengaluru", "banglore":"bengaluru", "bombay":"mumbai"}

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Air & Water Quality Monitoring", page_icon="🌍", layout="wide")

# ------------------ REMOVE NIGHT MODE — ALWAYS ENABLE SPACE THEME
# Force space galaxy theme as default

st.markdown("""
<style>
.stApp {
    background: linear-gradient(to bottom right, #a8d8ff, #dff3ff); /* light blue background */
    background-size: cover;
    background-repeat: no-repeat;
    background-attachment: fixed;
    color: #000000;
    font-family: "Segoe UI", sans-serif;
}

.dashboard-title {
    text-align: center;
    font-size: 40px;
    font-weight: 800;
    margin-bottom: 5px;
}

.section-title {
    font-size: 26px;
    font-weight: 700;
    margin: 20px 0 10px 0;
}

.gdu-card {
    background: rgba(255, 255, 255, 0.55);
    border-radius: 16px;
    padding: 18px;
    margin-bottom: 15px;
    color: black;
    border: 2px solid #00eaff;
    box-shadow: 0 0 12px #00eaff, 0 0 24px #00eaff;
}

.indicator {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    display: flex;
    justify-content: center;
    align-items: center;
    margin: 15px auto;
    font-size: 20px;
    font-weight: 700;
    color: #00eaff;
    background: rgba(0, 0, 0, 0.35);
    border: 4px solid #00eaff;
    box-shadow: 0 0 15px #00eaff, 0 0 30px #00eaff, inset 0 0 20px #00eaff;
    animation: neonPulse 2s infinite ease-in-out;
}

@keyframes neonPulse {
    0% { box-shadow: 0 0 10px #00eaff, 0 0 20px #00eaff, inset 0 0 10px #00eaff; }
    50% { box-shadow: 0 0 20px #00eaff, 0 0 40px #00eaff, inset 0 0 20px #00eaff; }
    100% { box-shadow: 0 0 10px #00eaff, 0 0 20px #00eaff, inset 0 0 10px #00eaff; }
}
</style>



""", unsafe_allow_html=True)

# ------------------ HELPERS ------------------
def pollutant_color(v): return "#16a34a" if v<50 else "#eab308" if v<100 else "#dc2626"
def map_air_label(x): return {0:"Good",1:"Moderate",2:"Poor"}.get(x)
def air_color(x): return {"Good":"#16A34A","Moderate":"#EAB308","Poor":"#DC2626"}[x]
def map_water_label(x): return "Drinkable" if x==1 else "Not Drinkable"
def water_color(x): return {"Drinkable":"#16A34A","Not Drinkable":"#DC2626"}[x]

# ------------------ HEADER ------------------
st.markdown('<div class="dashboard-title">🌍 Air & Water Quality Monitoring</div>', unsafe_allow_html=True)

# ================================================================
# SIDE‑BY‑SIDE DASHBOARD LAYOUT
# ================================================================
col_air, col_water = st.columns(2, gap="large")

# ------------------ AIR QUALITY SECTION ------------------
with col_air:
    st.markdown('<div class="gdu-card">', unsafe_allow_html=True)
    st.subheader("🌫️ Air Quality")

    city = st.text_input("City (Air Quality)")

    if st.button("Fetch AQI", key="aqi-btn", use_container_width=True):
        try:
            c = city.lower().strip()
            if c in CITY_ALIASES: city = CITY_ALIASES[c]

            data = get_air_quality_for_city(city)
            st.success(f"Live AQI Data for {city.title()}")

            for k,v in data.items():
                st.markdown(f"<div class='indicator' style='background:{pollutant_color(v)}'>{k.upper()}: {v}</div>", unsafe_allow_html=True)

            model = joblib.load(os.path.join(BASE_DIR, "models", "air_quality_model.pkl"))
            pred = map_air_label(model.predict([[*data.values()]])[0])

            st.markdown(f"<h4 style='text-align:center;color:{air_color(pred)}'>Air Quality: {pred}</h4>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"API ERROR → {e}")

    st.markdown('</div>', unsafe_allow_html=True)

    

# ------------------ WATER QUALITY SECTION ------------------
with col_water:
    st.markdown('<div class="gdu-card">', unsafe_allow_html=True)
    st.subheader("💧 Water Quality")

    city2 = st.text_input("City (Water Quality)")

    if st.button("Check Water", key="water-btn", use_container_width=True):
        try:
            c2 = CITY_ALIASES.get(city2.lower().strip(), city2).title()
            if c2 not in df_water["City"].tolist(): st.error("City not in dataset")
            else:
                row = df_water[df_water["City"] == c2].iloc[0]
                ph, hard, sol = row["pH"], row["Hardness"], row["Solids"]

                st.table(pd.DataFrame({"Parameter":["pH","Hardness","Solids"],"Value":[ph,hard,sol]}))

                model = joblib.load(os.path.join(BASE_DIR, "models", "water_quality_model.pkl"))
                pred = map_water_label(model.predict([[ph,hard,sol]])[0])

                st.markdown(f"<h4 style='text-align:center;color:{water_color(pred)}'>Water Quality: {pred}</h4>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"WATER ERROR → {e}")

    st.markdown('</div>', unsafe_allow_html=True)







# INTERACTIVE HEATMAP FOR INDIA
st.markdown('<div class="section-title">🗺️ India AQI Heatmap</div>', unsafe_allow_html=True)
st.markdown('<div class="gdu-card">', unsafe_allow_html=True)

try:
    heat_cities = ["Delhi","Mumbai","Chennai","Kolkata","Bengaluru","Hyderabad"]
    heat_values = np.random.randint(50,180,len(heat_cities))
    heat_df = pd.DataFrame({"City":heat_cities, "AQI":heat_values}).set_index("City")
    st.bar_chart(heat_df)
except Exception as e:
    st.error(f"HEATMAP ERROR → {e}")

st.markdown('</div>', unsafe_allow_html=True)

# ========================= CITY COMPARISON (ADDED) =========================
st.markdown('<div class="section-title">📊 Compare AQI Between Cities</div>', unsafe_allow_html=True)
st.markdown('<div class="gdu-card">', unsafe_allow_html=True)

city_a = st.text_input("City A")
city_b = st.text_input("City B")
city_c = st.text_input("City C (optional)")

if st.button("Compare City AQI", use_container_width=True):
    try:
        def fetch(city):
            city = CITY_ALIASES.get(city.lower().strip(), city)
            return get_air_quality_for_city(city)

        vals = {}
        for c in [city_a, city_b, city_c]:
            if c and c.strip() != "":
                data = fetch(c)
                model = joblib.load(os.path.join(BASE_DIR, "models", "air_quality_model.pkl"))
                pred = model.predict([[*data.values()]])[0]
                vals[c.title()] = pred

        if vals:
            df_compare = pd.DataFrame({"City": list(vals.keys()), "AQI": list(vals.values())}).set_index("City")
            st.bar_chart(df_compare)
        else:
            st.warning("Enter at least 2 cities to compare.")

    except Exception as e:
        st.error(f"COMPARISON ERROR → {e}")

st.markdown('</div>', unsafe_allow_html=True)

# ------------------ FOOTER ------------------
st.markdown("<p style='text-align:center;margin-top:25px;font-size:16px;'>Air & Water Quality Monitoring ✨ | Built with ❤️</p>", unsafe_allow_html=True)
