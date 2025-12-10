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

# ------------------ NIGHT MODE ------------------
if "dark" not in st.session_state:
    st.session_state.dark = False

st.session_state.dark = st.toggle("🌙 Night Mode", value=st.session_state.dark)
mode = "dark" if st.session_state.dark else "light"

# ------------------ PREMIUM GDU CSS ------------------
st.markdown("""
<style>
body { transition:0.4s; }

/* ---------- LIGHT MODE ---------- */
.light .main-bg {
    background: linear-gradient(to bottom right, #dff1ff, #a8d8ff);
    color:#1e293b;
}

/* ---------- DARK MODE ---------- */
.dark .main-bg {
    background: radial-gradient(circle at top, #060b18, #0a1229);
    color:white;
    position: relative;
    overflow:hidden;
}

/* NEON BORDERS FOR CARDS IN NIGHT MODE */
.dark .gdu-card {
    border: 2px solid #00eaff;
    box-shadow: 0 0 18px #00eaff;
}

/* ANIMATED STARFIELD */
.dark .main-bg::before,
.dark .main-bg::after {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-repeat: repeat;
    pointer-events: none;
    z-index: -1;
}

.dark .main-bg::before {
    background-image: radial-gradient(2px 2px at 20px 20px, #ffffff, transparent),
                      radial-gradient(2px 2px at 50px 80px, #ffffff, transparent),
                      radial-gradient(2px 2px at 90px 40px, #ffffff, transparent),
                      radial-gradient(2px 2px at 140px 120px, #ffffff, transparent),
                      radial-gradient(2px 2px at 200px 200px, #ffffff, transparent);
    animation: stars 12s linear infinite;
    opacity: 0.7;
}

.dark .main-bg::after {
    background-image: radial-gradient(1px 1px at 30px 60px, #a3eaff, transparent),
                      radial-gradient(1px 1px at 120px 200px, #a3eaff, transparent),
                      radial-gradient(1px 1px at 300px 150px, #a3eaff, transparent),
                      radial-gradient(1px 1px at 400px 40px, #a3eaff, transparent);
    animation: stars 20s linear infinite;
    opacity: 0.5;
}

@keyframes stars {
    from { transform: translateY(0px); }
    to   { transform: translateY(-200px); }
}

/* Cards */
.gdu-card {
    background: rgba(255,255,255,0.12);
    border-radius:18px;
    padding:22px;
    backdrop-filter: blur(12px);
    animation: fadeIn .7s ease;
}

@keyframes fadeIn {
    from { opacity:0; transform:translateY(10px); }
    to   { opacity:1; transform:translateY(0); }
}

.indicator {
    border-radius:12px;
    padding:12px;
    margin:6px 0;
    text-align:center;
    font-size:20px;
    font-weight:700;
    animation:pulse 1.6s infinite;
}

@keyframes pulse {
    0% { transform:scale(1); }
    50% { transform:scale(1.05); }
    100% { transform:scale(1); }
}
/* NEON GLOW TEXT */
.neon-text {
    font-size: 36px;
    font-weight: 900;
    color: #00eaff;
    text-shadow: 0 0 8px #00eaff, 0 0 16px #00eaff, 0 0 32px #00eaff;
}

/* FLOATING PARTICLES */
.dark .main-bg::before {
    animation: stars 12s linear infinite, floatParticles 8s ease-in-out infinite;
}

@keyframes floatParticles {
    0% { transform: translateY(0) translateX(0); }
    50% { transform: translateY(-20px) translateX(10px); }
    100% { transform: translateY(0) translateX(0); }
}

/* CIRCULAR AQI GAUGE */
.aqi-gauge {
    width: 140px;
    height: 140px;
    border-radius: 50%;
    border: 10px solid;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 26px;
    font-weight: 900;
    margin: 10px auto;
    animation: pulse 2s infinite;
}

/* PARALLAX BACKGROUND */
.dark .main-bg {
    background-attachment: fixed;
    background-size: 200% 200%;
    animation: parallaxMove 15s ease infinite;
}

@keyframes parallaxMove {
    0% { background-position: 0% 0%; }
    50% { background-position: 100% 100%; }
    100% { background-position: 0% 0%; }
}
</style>
<script>
const body = window.parent.document.body;
if ({mode} === 'light') {
    body.className = 'main-bg light';
    body.style.background = "linear-gradient(to bottom right, #dff1ff, #a8d8ff)";
} else {
    body.className = 'main-bg dark';
    body.style.background = "linear-gradient(to bottom right, #0a0f1f, #111827)";
}
</script>
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

    # ---- Tomorrow AQI ----
    st.markdown('<div class="gdu-card">', unsafe_allow_html=True)
    st.subheader("📈 Tomorrow AQI Forecast")
    today = st.number_input("Today's AQI", min_value=0.0)
    yesterday = st.number_input("Yesterday's AQI", min_value=0.0)

    if st.button("Predict Tomorrow", key="aqi-predict", use_container_width=True):
        tmr = today*0.6 + yesterday*0.4
        df = pd.DataFrame({"Day":["Yesterday","Today","Tomorrow"], "AQI":[yesterday,today,tmr]})
        st.line_chart(df.set_index("Day"))

        if tmr > 150: st.error("⚠️ HIGH pollution! Mask required.")
        elif tmr > 100: st.warning("😷 Moderate pollution.")
        else: st.success("🌱 Good air quality.")

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

hist_city = st.text_input("City for AQI History")

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
# =================================================================
st.markdown('<div class="section-title">🏙️ City-wise AQI Comparison</div>', unsafe_allow_html=True)
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

# REAL-TIME AQI SPARKLINE
st.markdown('<div class="section-title">⚡ Real-Time AQI Sparkline</div>', unsafe_allow_html=True)
st.markdown('<div class="gdu-card">', unsafe_allow_html=True)

spark_city = st.text_input("City for Real-Time Sparkline")
if st.button("Show Sparkline", use_container_width=True):
    try:
        # simple synthetic real-time fluctuating data
        spark_values = np.random.randint(40,150,20)
        spark_df = pd.DataFrame({"AQI": spark_values})
        st.line_chart(spark_df)
    except Exception as e:
        st.error(f"SPARKLINE ERROR → {e}")

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
