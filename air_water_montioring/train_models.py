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

    model = RandomForestClassifier(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)

    accuracy = model.score(X_test, y_test)
    print("Air Quality Model Accuracy:", accuracy)

    joblib.dump(model, "models/air_quality_model.pkl")


# ==============================
# Train WATER model (9 FEATURES)
# ==============================
def train_water_quality_model():
    df = pd.read_csv("data/water_quality_cities.csv")

    # Normalize column names → lower_snake_case
    df.columns = df.columns.str.lower().str.replace(" ", "_")

    # Expected columns (9 features)
    required = [
        "ph",
        "hardness",
        "solids",
        "chloramines",
        "sulfate",
        "conductivity",
        "organic_carbon",
        "trihalomethanes",
        "turbidity",
    ]

    # Fix missing column names from dataset variants
    rename_map = {
        "trihalo_methanes": "trihalomethanes",
        "organiccarbon": "organic_carbon",
        "tds": "solids",
    }

    df.rename(columns=rename_map, inplace=True)

    # Check all columns exist
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing column in dataset: {col}")

    # Feature & Target
    X = df[required]
    y = df["potability"]

    # Fill missing values
    X = X.fillna(X.mean())

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Train model
    model = RandomForestClassifier(n_estimators=300, random_state=42)
    model.fit(X_train, y_train)

    accuracy = model.score(X_test, y_test)
    print("Water Quality Model Accuracy:", accuracy)

    joblib.dump(model, "models/water_quality_model.pkl")


if __name__ == "__main__":
    train_air_quality_model()
    train_water_quality_model()
