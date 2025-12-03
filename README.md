<p align="center">
  <img src="https://img.shields.io/badge/Status-Live%20✔-22c55e?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Framework-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" />
  <img src="https://img.shields.io/badge/Machine%20Learning-RandomForest-0ea5e9?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Language-Python%203.12-blue?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Hosted%20on-Streamlit%20Cloud-f97316?style=for-the-badge&logo=streamlit&logoColor=white" />
  <img src="https://img.shields.io/badge/API-OpenWeatherMap-3b82f6?style=for-the-badge&logo=openweather&logoColor=white" />
</p>

<h1 align="center">🌍 Air & Water Quality Monitoring System</h1>

🌍 Air & Water Quality Monitoring System

A Machine Learning–powered monitoring and prediction system that evaluates environmental health through live air pollution values and city-based water drinkability predictions.

This project integrates:

Real-time OpenWeather API data,

ML classification models,

CSV-driven water sampling dataset, and

Fully interactive Streamlit UI.

It is deployed publicly and accessible online for demonstrations, viva presentation, or portfolio display.

🚀 Live Demo

🔗 Hosted Application:
https://air-and-water-quality-monitoring-wywuuyhzxfzfrwyqeatgay.streamlit.app/

🧠 Objective

To design a smart monitoring system that:

Fetches LIVE Air Quality Index metrics from API

Predicts pollutant severity using trained ML model

Reads city water parameters from dataset

Predicts drinkability using RandomForest

The system helps users determine whether a state's environment is:

Safe

Moderate

Critical

✨ Key Features

✔ Live pollutant extraction using API
✔ City-based water drinkability prediction
✔ Fully interactive Streamlit UI
✔ Gradient-glass cards & result banners
✔ Classification color indicators (Green/Yellow/Red)
✔ Data-driven ML model training
✔ Secure API secret integration
✔ Cloud hosted dashboard
✔ Alias-based city correction (e.g., “Bangalore → Bengaluru”)

🧪 Technologies Used
Category	Technology
Language	Python
Frontend	Streamlit
ML Models	Scikit-Learn (RandomForest)
API	OpenWeather Air Pollution API
Data Source	CSV (Water & Air datasets)
Deployment	Streamlit Cloud
Storage	Joblib Serialized Models
📂 Project Structure
air_water_montioring/
│
├─ .streamlit/
│   └─ secrets.toml                # Secure API Key
│
├─ data/
│   ├─ air_quality_dataset.csv     # Air quality model training dataset
│   └─ water_quality_cities.csv    # City-level water properties
│
├─ models/
│   ├─ air_quality_model.pkl       # Trained Air model
│   └─ water_quality_model.pkl     # Trained Water model
│
├─ app.py                          # Streamlit application file
├─ utils.py                        # API call logic
├─ train_models.py                 # Model builder script
└─ requirements.txt                # Package dependencies

🔐 API Key Setup

A secure .streamlit/secrets.toml file must be present:

✔ Location:

air_water_montioring/.streamlit/secrets.toml


✔ Content:

openweather_api_key = "YOUR_API_KEY"


⚠ Do NOT upload your key directly into GitHub
⚠ Streamlit Secrets protects it automatically

🌬️ Air Quality Prediction Model
Input Features from API

PM2.5

PM10

NO₂

SO₂

O₃

CO

Output Classes
Label	Meaning
0	Good
1	Moderate
2	Poor

Classifier: RandomForestClassifier

💧 Water Quality Prediction Model
Input Features

pH level

Hardness

Solids

Output Classes
Label	Water Status
1	Drinkable
0	Not Drinkable

Classifier: RandomForestClassifier

🔁 City Alias Mapping

User-friendly name conversion:

CITY_ALIASES = {
    "bangalore": "bengaluru",
    "banglore": "bengaluru",
    "bombay": "mumbai"
}


So even if users enter:

Banglore
Mumbai
Bangalore


The API safely queries:

Bengaluru
Mumbai

⚙️ Training the ML Models

Run locally:

python train_models.py


Outputs:

models/
 ├─ air_quality_model.pkl
 └─ water_quality_model.pkl

▶️ Run Locally

Install dependencies:

pip install -r requirements.txt


Run dashboard:

streamlit run app.py


Access at:

http://localhost:8501

🌍 Deployment Process (Streamlit Cloud)

Push repo to GitHub

Go to Streamlit Cloud

Select “Deploy app”

Fill details:

Repository: abhishek14311431/Air-and-Water-Quality-monitoring
Branch: main
Main file: air_water_montioring/app.py


Deploy

App builds and launches live 🎉

🧪 Test Cities
Air Quality (Works worldwide)
Mumbai
Delhi
Bengaluru
New York
Dubai
Tokyo
Paris

Water Quality (Dataset supported)
Delhi
Mumbai
Bengaluru
Chennai
Hyderabad
Pune

📊 Sample Output
City: Bengaluru
PM2.5: 16.3
PM10: 32.1
SO2: 5.4
O3: 12.8
CO: 392

Prediction: Moderate Air (Yellow)

City: Mumbai
pH: 7.5
Hardness: 110
Solids: 15000

Prediction: Drinkable (Green)

🌈 UI Highlights

✔ Blurred glass effect cards
✔ Blue gradient background
✔ Large readable fonts
✔ Colored result banners
✔ Minimalistic, clean layout

📜 Future Enhancements

🔹 AQI Score gauge meters
🔹 Multi-city comparison graphs
🔹 Email alerts for unsafe levels
🔹 Uploadable water sample testing
🔹 Heatmaps of pollution zones
🔹 AQI forecasting with timeseries models

👤 Author
Abhishek

🎓 Academic Mini Project
🧠 ML | Python | Deployment

🙌 Acknowledgements

OpenWeather API

Scikit-Learn

Streamlit Framework

Dataset sources for water parameters

If this project helped you, consider giving the repository a ⭐
And feel free to open issues or contribute!

🎉 Conclusion

This system integrates:

Machine Learning

Real APIs

Data Models

Deployment

UI Engineering

It’s feature-rich, academically strong, and production-ready!

Your Air & Water Quality Monitoring System is successfully deployed and fully functional.
