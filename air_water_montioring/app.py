# =========================================================
# 💧 WATER QUALITY SECTION (BEAUTIFUL UI + COLOR RANGES)
# =========================================================
st.markdown("<div class='section-title'>💧 Water Quality</div>", unsafe_allow_html=True)
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    city_water = st.text_input("Enter city name for Water Quality")

    if st.button("Fetch Water Quality"):
        try:
            c2 = CITY_ALIASES.get(city_water.lower().strip(), city_water).title()

            if c2.lower() not in df_water["city"].astype(str).str.lower().values:
                st.error("City not found in water dataset.")
            else:
                row = df_water[df_water["city"].str.lower() == c2.lower()].iloc[0]

                # All 9 visual water metrics
                metrics = {
                    "pH": row.get("ph"),
                    "Hardness": row.get("hardness"),
                    "Solids": row.get("solids"),
                    "Chloramines": row.get("chloramines"),
                    "Sulfate": row.get("sulfate"),
                    "Conductivity": row.get("conductivity"),
                    "Organic Carbon": row.get("organic_carbon"),
                    "Trihalomethanes": row.get("trihalomethanes"),
                    "Turbidity": row.get("turbidity"),
                }

                # Water safety ranges
                limits = {
                    "pH": (6.5, 8.5, 9.5),
                    "Hardness": (150, 300, 450),
                    "Solids": (300, 600, 900),
                    "Chloramines": (2, 4, 8),
                    "Sulfate": (100, 250, 400),
                    "Conductivity": (200, 400, 800),
                    "Organic Carbon": (4, 10, 20),
                    "Trihalomethanes": (30, 60, 80),
                    "Turbidity": (1, 3, 5),
                }

                st.subheader(f"Water Parameters — {c2}")

                cols = st.columns(3)

                # Generate pollutant-style cards for each water parameter
                for i, (name, value) in enumerate(metrics.items()):
                    if pd.notna(value):
                        low, med, high = limits[name]
                        icon, color = color_icon(value, low, med, high)

                        html = f"""
                            <div style="
                                background: #ffffff;
                                padding: 18px;
                                border-radius: 14px;
                                box-shadow: 0 4px 12px rgba(0,0,0,0.12);
                                text-align: center;
                                border-left: 6px solid {color};
                            ">
                                <div style="font-size: 42px;">{icon}</div>
                                <div style="font-size: 20px; font-weight: 700; color: #0a2540;">{name}</div>
                                <div style="font-size: 22px; margin-top: 4px;">{round(value, 2)}</div>
                            </div>
                        """
                        cols[i % 3].markdown(html, unsafe_allow_html=True)

                # ML prediction using ONLY 3 features
                pH = row.get("ph")
                Hardness = row.get("hardness")
                Solids = row.get("solids")

                model_w = joblib.load(os.path.join(BASE_DIR, "models", "water_quality_model.pkl"))
                X_input = [[pH, Hardness, Solids]]

                pred_raw = model_w.predict(X_input)[0]
                pred_label = "Drinkable" if pred_raw == 1 else "Not Drinkable"

                st.subheader(f"Water Quality: {pred_label}")

                if pred_label == "Drinkable":
                    st.success("💧 Water is safe for drinking.")
                else:
                    st.error("🚱 Water is NOT safe for drinking.")

        except Exception as e:
            st.error(str(e))

    st.markdown("</div>", unsafe_allow_html=True)
