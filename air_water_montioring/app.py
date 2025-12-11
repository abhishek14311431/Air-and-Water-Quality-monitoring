import streamlit as st
import joblib
import pandas as pd
import os
import plotly.express as px
from utils import get_air_quality_for_city

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="Air & Water Quality Monitoring",
    page_icon="🌍",
    layout="wide",
)

# ---------------------------------------------------------
# SKY BLUE BACKGROUND + CENTERED CONTENT
# ---------------------------------------------------------
st.markdown("""
<style>

.stApp {
    background-color: #cfe8ff;
    background-image: linear-gradient(135deg, #d7edff, #b5dbff);
    font-family: 'Segoe UI', sans-serif;
}

/* Center-column layout */
.centered {
    max-width: 850px;
    margin: auto;
}

/* Cards */
.card {
    background: white;
    padding: 25px;
    border-radius: 18px;
    box-shadow: 0 6px 25px rgba(0,0,0,0.12);
    margin-top: 20px;
}

/* Result boxes */
.air-box-good {
    background: #d4f8d4;
    padding: 15px; border-radius: 10px;
    border-left: 5px solid #2ecc71; font-weight: 700;
}
.air-box-moderate {
    background: #fff5cc;
    padding: 15px; border-radius: 10px;
    border-left: 5px solid #f1c40f; font-weight: 700;
}
.air-box-poor {
    background: #ffd6d6;
    padding: 15px; border-radius: 10px;
    border-left: 5px solid #e74c3c; font-weight: 700;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# TITLE (CENTERED)
# ---------------------------------------------------------
st.markdown("<h1 style='text-align:center; color:#05396b;'>🌍 Air & Water Quality Monitoring</h1>", unsafe_allow_html=True)

# ---------------------------------------------------------
# LOAD WATER DATA
# ---------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
df_water = pd.read_csv(os.path.join(BASE_DIR, "data", "water_quality_cities.csv"))
df_water.columns = df_water.columns.str.lower().str.replace(" ", "_")

CITY_ALIASES = {
    "bangalore": "bengaluru",
    "banglore": "bengaluru",
    "bombay": "mumbai",
}

# ---------------------------------------------------------
# AIR QUALITY CLASSIFICATION
# ---------------------------------------------------------
def classify_air(pm25, pm10, no2):
    if pm25 <= 30 and pm10 <= 50 and no2 <= 40:
        return "Good"
    elif pm25 <= 60 and pm10 <= 100 and no2 <= 80:
        return "Moderate"
    return "Poor"

def weather_icon(temp, humidity):
    if temp > 30:
        return f"☀️ Hot ({temp}°C)"
    elif humidity > 80:
        return f"🌧️ Humid ({humidity}%)"
    elif 20 <= temp <= 30:
        return f"⛅ Pleasant ({temp}°C)"
    return f"☁️ Cool ({temp}°C)"

# ---------------------------------------------------------
# WATER PARAMETER SAFETY LIMITS
# ---------------------------------------------------------
water_limits = {
    "pH": (6.5, 8.5),
    "Hardness": (150, 300),
    "Solids": (300, 1200),
    "Chloramines": (2, 4),
    "Organic Carbon": (2, 4),
    "Sulfate": (100, 250),
    "Conductivity": (250, 750),
    "Trihalomethanes": (40, 80),
    "Turbidity": (1, 5),
}

def water_icon(val, low, high):
    if val <= low:
        return "🟢"
    elif val <= high:
        return "🟡"
    return "🔴"


# ---------------------------------------------------------
# 🌫️ AIR QUALITY SECTION
# ---------------------------------------------------------
st.markdown("<div class='centered'>", unsafe_allow_html=True)

st.subheader("🌫️ Air Quality")

# ⭐ AIR TAGLINE BOX
st.markdown("""
<div style="
    background:#e8f4ff;
    padding:15px;
    border-radius:10px;
    border-left:5px solid #2980b9;
    font-weight:600;
    margin-top:10px;
    margin-bottom:15px;">
🌬️ The air you breathe shapes your health.  
Track live pollution levels & stay protected outdoors.
</div>
""", unsafe_allow_html=True)

st.markdown("<div class='card'>", unsafe_allow_html=True)

city_air = st.text_input("Enter city name for Air Quality")

if st.button("Fetch Air Quality"):
    try:
        c = CITY_ALIASES.get(city_air.lower().strip(), city_air)
        data = get_air_quality_for_city(c)

        st.markdown(f"### Live Air Quality — {c.title()}")

        # Weather icon
        st.metric("Weather", weather_icon(data["temp"], data["humidity"]))

        pollutants = {
            "PM2.5": data["pm2_5"],
            "PM10": data["pm10"],
            "NO₂": data["no2"],
            "SO₂": data["so2"],
            "O₃": data["o3"],
            "CO": data["co"],
        }

        limits = {
            "PM2.5": (30, 60),
            "PM10": (50, 100),
            "NO₂": (40, 80),
            "SO₂": (20, 80),
            "O₃": (50, 100),
            "CO": (200, 400),
        }

        def air_icon(val, low, mid):
            if val <= low: return "🟢"
            if val <= mid: return "🟡"
            return "🔴"

        cols = st.columns(3)
        for i, (name, value) in enumerate(pollutants.items()):
            low, mid = limits[name]
            symbol = air_icon(value, low, mid)
            cols[i % 3].metric(f"{symbol} {name}", round(value, 2))

        # Category box
        category = classify_air(data["pm2_5"], data["pm10"], data["no2"])

        if category == "Good":
            st.markdown("<div class='air-box-good'>🌿 Good Air — Safe to breathe.</div>", unsafe_allow_html=True)
        elif category == "Moderate":
            st.markdown("<div class='air-box-moderate'>😐 Moderate — Sensitive individuals limit outdoor time.</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='air-box-poor'>🚨 Poor — Avoid heavy outdoor activity.</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(str(e))

st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# 💧 WATER QUALITY SECTION
# ---------------------------------------------------------
st.subheader("💧 Water Quality")

# ⭐ WATER TAGLINE BOX
st.markdown("""
<div style="
    background:#e8fff1;
    padding:15px;
    border-radius:10px;
    border-left:5px solid #27ae60;
    font-weight:600;
    margin-top:10px;
    margin-bottom:15px;">
💧 Clean water is essential for a healthy life.  
Check purity levels & ensure safe drinking water.
</div>
""", unsafe_allow_html=True)

st.markdown("<div class='card'>", unsafe_allow_html=True)

city_water = st.text_input("Enter city name for Water Quality")

if st.button("Fetch Water Quality"):
    try:
        c2 = CITY_ALIASES.get(city_water.lower().strip(), city_water).title()

        if c2.lower() not in df_water["city"].astype(str).str.lower().values:
            st.error("City not found in water dataset.")
        else:
            row = df_water[df_water["city"].str.lower() == c2.lower()].iloc[0]
            st.markdown(f"### Water Quality — {c2}")

            metrics = {
                "pH": row["ph"],
                "Hardness": row["hardness"],
                "Solids": row["solids"],
                "Chloramines": row["chloramines"],
                "Organic Carbon": row["organic_carbon"],
                "Sulfate": row["sulfate"],
                "Conductivity": row["conductivity"],
                "Trihalomethanes": row["trihalomethanes"],
                "Turbidity": row["turbidity"],
            }

            cols = st.columns(3)
            for i, (name, value) in enumerate(metrics.items()):
                if pd.notna(value):
                    low, high = water_limits[name]
                    symbol = water_icon(value, low, high)
                    cols[i % 3].metric(f"{symbol} {name}", round(value, 2))

            # ML PREDICTION
            model_w = joblib.load(os.path.join(BASE_DIR, "models", "water_quality_model.pkl"))
            X = [[row["ph"], row["hardness"], row["solids"]]]
            pred = model_w.predict(X)[0]
            label = "Drinkable" if pred == 1 else "Not Drinkable"

            if label == "Drinkable":
                st.success("💧 Water is SAFE to drink.")
            else:
                st.error("🚱 Water is NOT safe to drink.")

    except Exception as e:
        st.error(str(e))

st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# 📊 CITY COMPARISON
# ---------------------------------------------------------
st.subheader("📊 Compare Air Quality Between Cities")
st.markdown("<div class='card'>", unsafe_allow_html=True)

c1 = st.text_input("City 1")
c2 = st.text_input("City 2")
c3 = st.text_input("City 3 (optional)")

if st.button("Compare Cities"):
    try:
        labels, pm_values = [], []

        for city in [c1, c2, c3]:
            if city.strip():
                fixed = CITY_ALIASES.get(city.lower().strip(), city)
                aq = get_air_quality_for_city(fixed)
                labels.append(fixed.title())
                pm_values.append(aq["pm2_5"])

        df = pd.DataFrame({"City": labels, "PM2.5": pm_values})
        fig = px.bar(df, x="City", y="PM2.5", color="City", 
                     title="PM2.5 Comparison Between Cities")
        st.plotly_chart(fig)

    except Exception as e:
        st.error(str(e))

st.markdown("</div>", unsafe_allow_html=True)
