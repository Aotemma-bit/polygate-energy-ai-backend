from pathlib import Path
from typing import Any, Dict

import joblib
import pandas as pd


MODEL_PATH = (
    Path(__file__).resolve().parent
    / "models"
    / "machine_failure_random_forest.joblib"
)


FEATURE_COLUMNS = [
    "Air temperature [K]",
    "Process temperature [K]",
    "Rotational speed [rpm]",
    "Torque [Nm]",
    "Tool wear [min]",
]


def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Trained model not found at: {MODEL_PATH}"
        )

    return joblib.load(MODEL_PATH)


def predict_machine_failure(
    air_temperature: float,
    process_temperature: float,
    rotational_speed: float,
    torque: float,
    tool_wear: float,
) -> Dict[str, Any]:

    model = load_model()

    input_data = pd.DataFrame(
        [
            {
                "Air temperature [K]": air_temperature,
                "Process temperature [K]": process_temperature,
                "Rotational speed [rpm]": rotational_speed,
                "Torque [Nm]": torque,
                "Tool wear [min]": tool_wear,
            }
        ]
    )

    prediction = int(model.predict(input_data)[0])

    probability = float(
        model.predict_proba(input_data)[0][1]
    )

    return {
        "prediction": prediction,
        "failure_probability_percent": round(
            probability * 100,
            2,
        ),
        "model": "Random Forest",
        "model_dataset": "UCI AI4I 2020 Predictive Maintenance Dataset",
        "model_scope": (
            "Benchmark prediction based on the synthetic UCI AI4I "
            "dataset. Not validated for real-world field deployment."
        ),
        "input_features": {
            "air_temperature_K": air_temperature,
            "process_temperature_K": process_temperature,
            "rotational_speed_rpm": rotational_speed,
            "torque_Nm": torque,
            "tool_wear_min": tool_wear,
        },
    }