import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

# ==============================
# Train AIR model
# ==============================
def train_air_quality_model():
    df = pd.read_csv("data/air_quality_dataset.csv")

    X = df[["pm2_5", "pm10", "no2", "so2", "o3", "co"]]
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(n_estimators=150, random_state=42)
    model.fit(X_train, y_train)

    accuracy = model.score(X_test, y_test)
    print("Air Quality Model Accuracy:", accuracy)

    joblib.dump(model, "models/air_quality_model.pkl")


# ==============================
# Train WATER model (ONLY 3 features)
# ==============================
def train_water_quality_model():
    df = pd.read_csv("data/water_quality_cities.csv")

    # Normalize column names
    df.columns = df.columns.str.lower().str.replace(" ", "_")

    # Fix alternative column names
    df.rename(columns={"tds": "solids"}, inplace=True)

    # Use ONLY these 3 features
    required = ["ph", "hardness", "solids"]

    # Check all required columns exist
    for col in required:
        if col not in df.columns:
            raise Exception(f"Missing column in dataset: {col}")

    X = df[required]
    y = df["potability"]

    # Fill missing values
    X = X.fillna(X.mean())

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)

    accuracy = model.score(X_test, y_test)
    print("Water Quality Model Accuracy:", accuracy)

    joblib.dump(model, "models/water_quality_model.pkl")


# ==============================
# MAIN EXECUTION
# ==============================
if __name__ == "__main__":
    train_air_quality_model()
    train_water_quality_model()
