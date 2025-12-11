# =========================================================
# 🌫️ AIR QUALITY SECTION — AQI BASED ONLY ON PM2.5, PM10, NO2
# =========================================================
st.markdown("<div class='section-title'>🌫️ Air Quality</div>", unsafe_allow_html=True)
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    city_air = st.text_input("Enter city name for Air Quality")

    if st.button("Fetch Air Quality", type="primary"):
        try:
            c = CITY_ALIASES.get(city_air.lower().strip(), city_air)
            air = get_air_quality_for_city(c)

            st.subheader(f"Pollutant Levels in {c.title()}")

            # AQI RANGES (PM2.5, PM10, NO2 ONLY)
            AQI_RANGES = {
                "pm2_5": [(0, 30, "Good"), (31, 60, "Moderate"), (61, 9999, "Poor")],
                "pm10": [(0, 50, "Good"), (51, 100, "Moderate"), (101, 9999, "Poor")],
                "no2":  [(0, 40, "Good"), (41, 80, "Moderate"), (81, 9999, "Poor")],
            }

            def classify(value, rules):
                for low, high, label in rules:
                    if low <= value <= high:
                        return label
                return "Poor"

            def icon(category):
                return "🟢" if category == "Good" else "🟡" if category == "Moderate" else "🔴"

            cols = st.columns(3)
            statuses = []

            # Display ALL pollutants but classify only key 3
            for i, (key, value) in enumerate(air.items()):
                if key in AQI_RANGES:
                    category = classify(value, AQI_RANGES[key])
                    statuses.append(category)
                else:
                    category = "Info"

                cols[i % 3].metric(f"{icon(category)} {key.upper()}", round(value, 2))

            # FINAL AQI BASED ONLY ON PM2.5, PM10, NO2
            if "Poor" in statuses:
                final = "Poor"
            elif "Moderate" in statuses:
                final = "Moderate"
            else:
                final = "Good"

            st.subheader(f"Air Quality Category: {final}")

            if final == "Good":
                st.success("🌿 Air is safe to breathe.")
            elif final == "Moderate":
                st.warning("😷 Moderate air quality — Sensitive groups should be careful.")
            else:
                st.error("🚨 Poor air quality — Avoid outdoor exposure.")

        except Exception as e:
            st.error(str(e))

    st.markdown("</div>", unsafe_allow_html=True)
