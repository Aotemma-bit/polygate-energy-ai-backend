import json
from pathlib import Path
from typing import Any, Dict


METRICS_PATH = (
    Path(__file__).resolve().parent
    / "models"
    / "cross_validation_metrics.json"
)


def get_validation_info() -> Dict[str, Any]:
    if not METRICS_PATH.exists():
        raise FileNotFoundError(
            f"Cross-validation metrics not found at: {METRICS_PATH}"
        )

    with open(
        METRICS_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        metrics = json.load(file)

    return metrics