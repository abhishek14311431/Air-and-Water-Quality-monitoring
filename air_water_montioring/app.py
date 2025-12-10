import streamlit as st
import numpy as np
import joblib
import pandas as pd
import os
from utils import get_air_quality_for_city

# ---------------- PAGE SETUP ----------------
st.set_page_config(page_title="Air & Water Quality Monitoring", page_icon="🌍", layout="wide")

# ---------------- UPDATED PREMIUM UI (GLOW + ADVICE BOXES) ----------------
st.markdown(
    """
<style>

.stApp {
    background: #e8f1ff;
    font-family: 'Segoe UI', sans-serif;
    color: #0a0a0a;
}

.header {
    text-align: center;
    font-size: 44px;
    font-weight: 900;
    margin-bottom: 25px;
    color: #0a2540;
}

.card {
    background: #ffffff;
    padding: 24px;
    border-radius: 18px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.18);
    margin-bottom: 25px;
}

.section-title {
    font-size: 28px;
    font-weight: 800;
    color: #0a2540;
    margin: 10px 0 14px;
}

/* ------------------- METRIC CIRCLES ------------------- */
.metric-circle {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    background: #eef4ff;
    border: 3px solid #4f8ef7;
    color: #0a2540;
    font-size: 18px;
    font-weight: 700;
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;
    margin: 12px auto;
    box-shadow: 0 0 18px rgba(79,142,247,0.35);
}

/* ------------------- GLOW ADVICE BOXES ------------------- */
.advice-good {
    padding: 14px;
    border-radius: 14px;
    background: rgba(0, 255, 120, 0.18);
    border: 2px solid rgba(0, 255, 120, 0.45);
    box-shadow: 0 0 18px rgba(0,255,120,0.35);
    color: #065f46;
    font-weight: 700;
    margin-top: 10px;
}

.advice-warning {
    padding: 14px;
    border-radius: 14px;
    background: rgba(255, 200, 0, 0.18);
    border: 2px solid rgba(255, 200, 0, 0.45);
    box-shadow: 0 0 18px rgba(255,200,0,0.35);
    color: #7c5800;
    font-weight: 700;
    margin-top: 10px;
}

.advice-danger {
    padding: 14px;
    border-radius: 14px;
    background: rgba(255, 60, 60, 0.18);
    border: 2px solid rgba(255, 60, 60, 0.45);
    box-shadow: 0 0 18px rgba(255,60,60,0.35);
    color: #7f1d1d;
    font-weight: 700;
    margin-top: 10px;
}

</style>
""",
    unsafe_allow_html=True
)

# ---------------- PATHS ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
water_csv_path = os.path.join(BASE_DIR, "data", "water_quality_cities.csv")
df_water = pd.read_csv(water_csv_path)

CITY_ALIASES = {"bangalore": "bengaluru", "banglore": "bengaluru", "bombay": "mumbai"}

def map_air_label(x): return {0: "Good", 1: "Moderate", 2: "Poor"}.get(x)
def map_water_label(x): return "Drinkable" if x == 1 else "Not Drinkable"

# ---------------- HEADER ----------------
st.markdown('<div class="header">🌍 Air & Water Quality Monitoring</div>', unsafe_allow_html=True)

# ---------------- LAYOUT ----------------
col1, col2 = st.columns(2, gap="large")

# ============ AIR QUALITY SECTION ============
with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🌫️ Air Quality</div>', unsafe_allow_html=True)

    city = st.text_input("City (Air Quality)")

    if st.button("Get AQI", use_container_width=True):
        try:
            c = CITY_ALIASES.get(city.lower().strip(), city)
            data = get_air_quality_for_city(c)

            st.write(f"### Live AQI — {c.title()}")

            items = list(data.items())
            for i in range(0, len(items), 3):
                cols_sub = st.columns(3)
                for (name, val), box in zip(items[i:i+3], cols_sub):
                    box.markdown(
                        f"<div class='metric-circle'>{name.upper()}<br>{val}</div>",
                        unsafe_allow_html=True
                    )

            model = joblib.load(os.path.join(BASE_DIR, "models", "air_quality_model.pkl"))
            pred = map_air_label(model.predict([[*data.values()]])[0])
            st.write(f"### Air Quality Category: {pred}")

            # ---------- Advice ----------
            if pred == "Good":
                st.markdown("<div class='advice-good'>🌿 Good Air Quality — No mask required.</div>",
                            unsafe_allow_html=True)

            elif pred == "Moderate":
                st.markdown("<div class='advice-warning'>😷 Moderate Air Quality — Sensitive people should consider wearing a mask.</div>",
                            unsafe_allow_html=True)

            else:
                st.markdown("<div class='advice-danger'>🚨 Poor Air Quality — Mask is strongly recommended!</div>",
                            unsafe_allow_html=True)

        except Exception as e:
            st.error(str(e))

    st.markdown('</div>', unsafe_allow_html=True)

# ============ WATER QUALITY SECTION ============
with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">💧 Water Quality</div>', unsafe_allow_html=True)

    city2 = st.text_input("City (Water Quality)")

    if st.button("Check Water", use_container_width=True):
        try:
            c2 = CITY_ALIASES.get(city2.lower().strip(), city2).title()

            if c2 not in df_water["City"].tolist():
                st.error("City not in water dataset")
            else:
                row = df_water[df_water["City"] == c2].iloc[0]
                ph, hardness, solids = row["pH"], row["Hardness"], row["Solids"]

                st.write("### Water Parameters")

                params = [("pH", ph), ("Hardness", hardness), ("Solids", solids)]
                for i in range(0, len(params), 3):
                    cols_w = st.columns(3)
                    for (n, v), wc in zip(params[i:i+3], cols_w):
                        wc.markdown(
                            f"<div class='metric-circle'>{n}<br>{v}</div>",
                            unsafe_allow_html=True
                        )

                # Predict
                model = joblib.load(os.path.join(BASE_DIR, "models", "water_quality_model.pkl"))
                pred = map_water_label(model.predict([[ph, hardness, solids]])[0])
                st.write(f"### Water Quality: {pred}")

                # ---------- Advice ----------
                if pred == "Drinkable":
                    st.markdown("<div class='advice-good'>💧 Safe for drinking.</div>",
                                unsafe_allow_html=True)
                else:
                    st.markdown("<div class='advice-danger'>🚱 Not safe — Use filtered or bottled water.</div>",
                                unsafe_allow_html=True)

        except Exception as e:
            st.error(str(e))

    st.markdown('</div>', unsafe_allow_html=True)

# ============ CITY COMPARISON ============
st.markdown('<div class="section-title">📊 Compare AQI Between Cities</div>', unsafe_allow_html=True)
st.markdown('<div class="card">', unsafe_allow_html=True)

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
            if c and c.strip():
                data = fetch(c)
                model = joblib.load(os.path.join(BASE_DIR, "models", "air_quality_model.pkl"))
                vals[c.title()] = model.predict([[*data.values()]])[0]

        df_compare = pd.DataFrame({"City": list(vals.keys()), "AQI": list(vals.values())}).set_index("City")
        st.bar_chart(df_compare)

    except Exception as e:
        st.error(str(e))

st.markdown('</div>', unsafe_allow_html=True)

# ============ INDIA HEATMAP ============
st.markdown('<div class="section-title">🗺️ India AQI Heatmap</div>', unsafe_allow_html=True)
st.markdown('<div class="card">', unsafe_allow_html=True)

heat_cities = ["Delhi","Mumbai","Kolkata","Chennai","Bengaluru","Hyderabad"]
heat_values = np.random.randint(40, 160, len(heat_cities))
df_heat = pd.DataFrame({"City": heat_cities, "AQI": heat_values}).set_index("City")
st.bar_chart(df_heat)

st.markdown('</div>', unsafe_allow_html=True)
