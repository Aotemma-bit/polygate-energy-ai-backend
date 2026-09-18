from pathlib import Path
from typing import Any, Dict

import joblib
import pandas as pd
import shap


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


def explain_machine_prediction(
    air_temperature: float,
    process_temperature: float,
    rotational_speed: float,
    torque: float,
    tool_wear: float,
) -> Dict[str, Any]:

    model = load_model()

    input_data = pd.DataFrame(
        [{
            "Air temperature [K]": air_temperature,
            "Process temperature [K]": process_temperature,
            "Rotational speed [rpm]": rotational_speed,
            "Torque [Nm]": torque,
            "Tool wear [min]": tool_wear,
        }]
    )

    prediction = int(model.predict(input_data)[0])

    probability = float(
        model.predict_proba(input_data)[0][1]
    )

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(input_data)

    if shap_values.ndim == 3:
        values = shap_values[0, :, 1]
    elif shap_values.ndim == 2:
        values = shap_values[0]
    else:
        raise ValueError(
            f"Unexpected SHAP output shape: {shap_values.shape}"
        )

    contributions = []

    for feature, value, contribution in zip(
        FEATURE_COLUMNS,
        input_data.iloc[0].tolist(),
        values,
    ):
        contribution_value = float(
            contribution.item()
            if hasattr(contribution, "item")
            else contribution
        )

        contributions.append(
            {
                "feature": feature,
                "input_value": float(value),
                "shap_value": round(
                    contribution_value,
                    6,
                ),
                "direction": (
                    "increases_failure_score"
                    if contribution_value > 0
                    else "decreases_failure_score"
                    if contribution_value < 0
                    else "neutral"
                ),
            }
        )

    contributions.sort(
        key=lambda item: abs(item["shap_value"]),
        reverse=True,
    )

    return {
        "prediction": prediction,
        "failure_probability_percent": round(
            probability * 100,
            2,
        ),
        "model": "Random Forest",
        "explanation_method": "SHAP TreeExplainer",
        "feature_contributions": contributions,
        "scope": (
            "Feature-attribution explanation for the benchmark "
            "Random Forest model trained on the synthetic UCI "
            "AI4I 2020 Predictive Maintenance Dataset. "
            "SHAP contributions describe model behavior and "
            "do not establish causal engineering relationships "
            "or field performance."
        ),
    }
