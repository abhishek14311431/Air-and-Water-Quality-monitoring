import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODEL_DIR = os.path.join(BASE_DIR, "models")


# ==========================================================
#  TRAIN AIR QUALITY MODEL  (6 pollutant features)
# ==========================================================
def train_air_quality_model():
    print("\n==============================")
    print("📌 TRAINING AIR QUALITY MODEL")
    print("==============================")

    air_path = os.path.join(DATA_DIR, "air_quality_dataset.csv")
    df = pd.read_csv(air_path)

    # Keep only pollutant columns
    FEATURES = ["pm2_5", "pm10", "no2", "so2", "o3", "co"]
    LABEL = "label"

    X = df[FEATURES]
    y = df[LABEL]

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Train model
    model = RandomForestClassifier(
        n_estimators=160, max_depth=None, random_state=42
    )
    model.fit(X_train, y_train)

    # Evaluate
    accuracy = model.score(X_test, y_test)
    print(f"✅ Air Model Accuracy: {accuracy:.4f}")

    # Save model
    model_path = os.path.join(MODEL_DIR, "air_quality_model.pkl")
    joblib.dump(model, model_path)
    print(f"💾 Saved: {model_path}")


# ==========================================================
#  TRAIN WATER QUALITY MODEL (ALL 9 FEATURES)
# ==========================================================
def train_water_quality_model():
    print("\n==============================")
    print("💧 TRAINING WATER QUALITY MODEL")
    print("==============================")

    water_path = os.path.join(DATA_DIR, "water_quality_cities.csv")
    df = pd.read_csv(water_path)

    # Remove non-numeric column
    df = df.drop(columns=["City"], errors="ignore")

    # Target
    TARGET = "Potability"

    # Features = everything except target
    X = df.drop(columns=[TARGET])
    y = df[TARGET]

    # Fill missing values automatically
    X = X.fillna(X.mean())

    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Train model
    model = RandomForestClassifier(
        n_estimators=200, max_depth=None, random_state=42
    )
    model.fit(X_train, y_train)

    # Evaluate
    accuracy = model.score(X_test, y_test)
    print(f"✅ Water Model Accuracy: {accuracy:.4f}")

    # Save model
    model_path = os.path.join(MODEL_DIR, "water_quality_model.pkl")
    joblib.dump(model, model_path)
    print(f"💾 Saved: {model_path}")


# ==========================================================
#  MAIN EXECUTION (TRAIN BOTH MODELS)
# ==========================================================
if __name__ == "__main__":
    print("🚀 Starting Training Process...")
    train_air_quality_model()
    train_water_quality_model()
    print("\n🎉 ALL MODELS TRAINED SUCCESSFULLY!")
