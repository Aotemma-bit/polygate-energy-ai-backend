import json
from pathlib import Path
from typing import Any, Dict


METRICS_PATH = (
    Path(__file__).resolve().parent
    / "models"
    / "machine_failure_metrics.json"
)


def get_model_info() -> Dict[str, Any]:
    if not METRICS_PATH.exists():
        raise FileNotFoundError(
            f"Model metrics not found at: {METRICS_PATH}"
        )

    with open(METRICS_PATH, "r", encoding="utf-8") as file:
        metrics = json.load(file)

    return {
        "model": metrics.get("model"),
        "dataset": metrics.get("dataset"),
        "dataset_rows": metrics.get("dataset_rows"),
        "failure_cases": metrics.get("failure_cases"),
        "non_failure_cases": metrics.get("non_failure_cases"),
        "features": metrics.get("features"),
        "target": metrics.get("target"),
        "metrics": metrics.get("metrics"),
        "confusion_matrix": metrics.get("confusion_matrix"),
        "feature_importance": metrics.get("feature_importance"),
        "model_scope": metrics.get("model_scope"),
    }