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
st.set_page_config(page_title="GDU Premium Dashboard", page_icon="🌍", layout="wide")

# ------------------ REMOVE NIGHT MODE — ALWAYS ENABLE SPACE THEME
# Force space galaxy theme as default

st.markdown("""
<style>
body {
    background: linear-gradient(to bottom right, #b3e5ff, #e0f7ff);
    background-attachment: fixed;
    background-size: cover;
    overflow: auto;
    color: black;
}

/* Remove starfield and planets */
body::before, body::after, .planet { display: none !important; }
</style>

<div id="planet1" class="planet"></div>
<div id="planet2" class="planet"></div>
<div id="planet3" class="planet"></div>

""", unsafe_allow_html=True)

# ------------------ HELPERS ------------------
def pollutant_color(v): return "#16a34a" if v<50 else "#eab308" if v<100 else "#dc2626"
def map_air_label(x): return {0:"Good",1:"Moderate",2:"Poor"}.get(x)
def air_color(x): return {"Good":"#16A34A","Moderate":"#EAB308","Poor":"#DC2626"}[x]
def map_water_label(x): return "Drinkable" if x==1 else "Not Drinkable"
def water_color(x): return {"Drinkable":"#16A34A","Not Drinkable":"#DC2626"}[x]

# ------------------ HEADER ------------------
st.markdown('<div class="dashboard-title">🌍 GDU Premium Air + Water Quality Dashboard</div>', unsafe_allow_html=True)

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

# =================================================================
# AQI HISTORY TIMELINE
# =================================================================
st.markdown('<div class="section-title">📜 AQI History Timeline</div>', unsafe_allow_html=True)
st.markdown('<div class="gdu-card">', unsafe_allow_html=True)

hist_city = city

if st.button("Show AQI Timeline", use_container_width=True):
    try:
        timeline_hours = ["1 AM","3 AM","6 AM","9 AM","12 PM","3 PM","6 PM","9 PM","12 AM"]
        timeline_values = [42, 55, 48, 60, 70, 82, 95, 88, 65]
        df_hist = pd.DataFrame({"Time": timeline_hours, "AQI": timeline_values})
        st.line_chart(df_hist.set_index("Time"))
    except Exception as e:
        st.error(f"TIMELINE ERROR → {e}")

st.markdown('</div>', unsafe_allow_html=True)

# =================================================================
# CITY-WISE AQI COMPARISON
st.markdown('<div class="section-title">🏙️ City-wise AQI Details</div>', unsafe_allow_html=True)
st.markdown('<div class="gdu-card">', unsafe_allow_html=True)

single_city = city

if st.button("Get City AQI Details", use_container_width=True):
    try:
        c = CITY_ALIASES.get(single_city.lower().strip(), single_city)
        data = get_air_quality_for_city(c)

        st.markdown(f"<h4 style='text-align:center;'>🌍 Full AQI Report — {c.title()}</h4>", unsafe_allow_html=True)

        # Show pollutant indicators
        for k, v in data.items():
            st.markdown(f"<div class='indicator' style='background:{pollutant_color(v)}'>{k.upper()}: {v}</div>", unsafe_allow_html=True)

        # Predict AQI
        model = joblib.load(os.path.join(BASE_DIR, "models", "air_quality_model.pkl"))
        pred = map_air_label(model.predict([[*data.values()]])[0])
        st.markdown(f"<h4 style='text-align:center;color:{air_color(pred)}'>Air Quality: {pred}</h4>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"DETAILS ERROR → {e}")

# ========================= CITY COMPARISON =========================
st.markdown('<div class="section-title">📊 Compare Multiple Cities</div>', unsafe_allow_html=True)
st.markdown('<div class="gdu-card">', unsafe_allow_html=True)

c1 = st.text_input("City 1")
c2 = st.text_input("City 2")
c3 = st.text_input("City 3 (optional)")

if st.button("Compare Cities", use_container_width=True):
    try:
        def fetch(city):
            city = CITY_ALIASES.get(city.lower().strip(), city)
            return get_air_quality_for_city(city)

        vals = {}
        for c in [c1, c2, c3]:
            if c.strip() != "":
                data = fetch(c)
                aqi_model = joblib.load(os.path.join(BASE_DIR, "models", "air_quality_model.pkl"))
                pred = aqi_model.predict([[*data.values()]])[0]
                vals[c.title()] = pred

        df_compare = pd.DataFrame({"City": list(vals.keys()), "AQI Score": list(vals.values())})
        st.bar_chart(df_compare.set_index("City"))
    except Exception as e:
        st.error(f"COMPARISON ERROR → {e}")

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

# ------------------ FOOTER ------------------
st.markdown("<p style='text-align:center;margin-top:25px;font-size:16px;'>GDU Premium Dashboard ✨ | Built with ❤️</p>", unsafe_allow_html=True)
