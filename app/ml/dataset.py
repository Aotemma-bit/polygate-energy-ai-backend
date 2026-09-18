from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd


DATA_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "ml"
    / "ai4i2020.csv"
)


FEATURE_COLUMNS: List[str] = [
    "Air temperature [K]",
    "Process temperature [K]",
    "Rotational speed [rpm]",
    "Torque [Nm]",
    "Tool wear [min]",
]


TARGET_COLUMN = "Machine failure"


def load_dataset() -> pd.DataFrame:
    """
    Load the UCI AI4I 2020 predictive-maintenance dataset.

    Returns:
        Raw pandas DataFrame.

    Raises:
        FileNotFoundError: If the dataset is not present.
    """

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found at: {DATA_PATH}"
        )

    return pd.read_csv(DATA_PATH)


def prepare_dataset() -> Tuple[pd.DataFrame, pd.Series]:
    """
    Prepare feature matrix X and target vector y.

    Features:
        Operating and sensor variables documented in the dataset.

    Target:
        Machine failure.

    UDI and Product ID are excluded because they are identifiers,
    not operating measurements.
    """

    df = load_dataset()

    missing_columns = [
        column
        for column in FEATURE_COLUMNS + [TARGET_COLUMN]
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    X = df[FEATURE_COLUMNS].copy()
    y = df[TARGET_COLUMN].copy()

    return X, y


def dataset_summary() -> Dict[str, object]:
    """
    Return basic dataset information for inspection.
    """

    df = load_dataset()

    return {
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "feature_columns": FEATURE_COLUMNS,
        "target_column": TARGET_COLUMN,
        "failure_count": int(
            df[TARGET_COLUMN].sum()
        ),
        "non_failure_count": int(
            (df[TARGET_COLUMN] == 0).sum()
        ),
        "failure_rate_percent": round(
            float(df[TARGET_COLUMN].mean() * 100),
            2,
        ),
    }