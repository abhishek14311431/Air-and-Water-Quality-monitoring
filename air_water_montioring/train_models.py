import pandas as pd
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib


# BASE DIRECTORY
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODEL_DIR = os.path.join(BASE_DIR, "models")


# --------------------------------------------------------
#                 AIR QUALITY MODEL TRAINING
# --------------------------------------------------------
def train_air_quality_model():
    air_path = os.path.join(DATA_DIR, "air_quality_cities.csv")
    df = pd.read_csv(air_path)

    X = df[["pm2_5", "pm10", "no2", "so2", "o3", "co"]]
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(n_estimators=150, random_state=42)
    model.fit(X_train, y_train)

    accuracy = model.score(X_test, y_test)
    print("Air Quality Model Accuracy:", accuracy)

    save_path = os.path.join(MODEL_DIR, "air_quality_model.pkl")
    joblib.dump(model, save_path)


# --------------------------------------------------------
#               WATER QUALITY MODEL TRAINING
# --------------------------------------------------------
def train_water_quality_model():
    water_path = os.path.join(DATA_DIR, "water_quality_cities.csv")
    df = pd.read_csv(water_path)

    feature_cols = [
        "ph", "Hardness", "Solids", "Chloramines", "Sulfate",
        "Conductivity", "Organic_carbon", "Trihalomethanes", "Turbidity"
    ]

    X = df[feature_cols]
    y = df["Potability"]

    X = X.fillna(X.mean())

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)

    accuracy = model.score(X_test, y_test)
    print("Water Quality Model Accuracy:", accuracy)

    save_path = os.path.join(MODEL_DIR, "water_quality_model.pkl")
    joblib.dump(model, save_path)


# --------------------------------------------------------
#                        MAIN RUN
# --------------------------------------------------------
if __name__ == "__main__":
    train_air_quality_model()
    train_water_quality_model()
