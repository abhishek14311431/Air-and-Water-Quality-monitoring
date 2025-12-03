import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib

def train_air_quality_model():
    df = pd.read_csv("data/air_quality_dataset.csv")

    X = df[["pm2_5", "pm10", "no2", "so2", "o3", "co"]]
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    accuracy = model.score(X_test, y_test)
    print("Air Quality Model Accuracy:", accuracy)

    joblib.dump(model, "models/air_quality_model.pkl")


def train_water_quality_model():
    df = pd.read_csv("data/water_quality_dataset.csv")

    X = df.drop(columns=["Potability"])
    y = df["Potability"]

    X = X.fillna(X.mean())

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    accuracy = model.score(X_test, y_test)
    print("Water Quality Model Accuracy:", accuracy)

    joblib.dump(model, "models/water_quality_model.pkl")


if __name__ == "__main__":
    train_air_quality_model()
    train_water_quality_model()

