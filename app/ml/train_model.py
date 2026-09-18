from pathlib import Path
import json

import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split

from app.ml.dataset import prepare_dataset


MODEL_DIR = Path(__file__).resolve().parent / "models"
MODEL_PATH = MODEL_DIR / "machine_failure_random_forest.joblib"
METRICS_PATH = MODEL_DIR / "machine_failure_metrics.json"


def train_model():
    print("Loading dataset...")

    X, y = prepare_dataset()

    print(f"Dataset rows: {len(X)}")
    print(f"Failure cases: {int(y.sum())}")
    print(f"Non-failure cases: {int((y == 0).sum())}")

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    print(f"Training rows: {len(X_train)}")
    print(f"Test rows: {len(X_test)}")

    print("Training Random Forest model...")

    model = RandomForestClassifier(
        n_estimators=300,
        random_state=42,
        class_weight="balanced",
        n_jobs=-1,
        min_samples_leaf=2,
    )

    model.fit(X_train, y_train)

    print("Generating predictions...")

    y_pred = model.predict(X_test)
    y_probability = model.predict_proba(X_test)[:, 1]

    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    roc_auc = roc_auc_score(y_test, y_probability)

    matrix = confusion_matrix(y_test, y_pred)

    print("\n===== MODEL RESULTS =====")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1 Score:  {f1:.4f}")
    print(f"ROC-AUC:   {roc_auc:.4f}")

    print("\n===== CONFUSION MATRIX =====")
    print(matrix)

    print("\n===== CLASSIFICATION REPORT =====")
    print(classification_report(y_test, y_pred, zero_division=0))

    print("\n===== FEATURE IMPORTANCE =====")

    feature_importance = {}

    for feature, importance in zip(
        X.columns,
        model.feature_importances_,
    ):
        feature_importance[feature] = round(float(importance), 6)
        print(f"{feature}: {importance:.4f}")

    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    joblib.dump(model, MODEL_PATH)

    metrics = {
        "model": "RandomForestClassifier",
        "dataset": "UCI AI4I 2020 Predictive Maintenance Dataset",
        "dataset_rows": int(len(X)),
        "failure_cases": int(y.sum()),
        "non_failure_cases": int((y == 0).sum()),
        "test_size": 0.20,
        "random_state": 42,
        "features": list(X.columns),
        "target": "Machine failure",
        "metrics": {
            "precision": round(float(precision), 4),
            "recall": round(float(recall), 4),
            "f1": round(float(f1), 4),
            "roc_auc": round(float(roc_auc), 4),
        },
        "confusion_matrix": matrix.tolist(),
        "feature_importance": feature_importance,
        "model_scope": (
            "Benchmark model trained on the synthetic UCI AI4I dataset. "
            "This is not a validated field failure predictor."
        ),
    }

    with open(METRICS_PATH, "w", encoding="utf-8") as file:
        json.dump(metrics, file, indent=2)

    print("\n===== SAVED =====")
    print(f"Model:   {MODEL_PATH}")
    print(f"Metrics: {METRICS_PATH}")


if __name__ == "__main__":
    train_model()