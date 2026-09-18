from pathlib import Path
import json

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_validate

from app.ml.dataset import prepare_dataset


OUTPUT_PATH = (
    Path(__file__).resolve().parent
    / "models"
    / "cross_validation_metrics.json"
)


def evaluate_model():
    print("Loading dataset...")

    X, y = prepare_dataset()

    print(f"Dataset rows: {len(X)}")
    print(f"Failure cases: {int(y.sum())}")
    print(f"Non-failure cases: {int((y == 0).sum())}")

    model = RandomForestClassifier(
        n_estimators=300,
        random_state=42,
        class_weight="balanced",
        n_jobs=-1,
        min_samples_leaf=2,
    )

    cv = StratifiedKFold(
        n_splits=5,
        shuffle=True,
        random_state=42,
    )

    scoring = {
        "roc_auc": "roc_auc",
        "precision": "precision",
        "recall": "recall",
        "f1": "f1",
    }

    print("\nRunning 5-fold stratified cross-validation...")

    results = cross_validate(
        model,
        X,
        y,
        cv=cv,
        scoring=scoring,
        n_jobs=-1,
        return_train_score=False,
    )

    fold_metrics = []

    for index in range(5):
        fold_number = index + 1

        roc_auc = results["test_roc_auc"][index]
        precision = results["test_precision"][index]
        recall = results["test_recall"][index]
        f1 = results["test_f1"][index]

        fold_result = {
            "fold": fold_number,
            "roc_auc": round(float(roc_auc), 4),
            "precision": round(float(precision), 4),
            "recall": round(float(recall), 4),
            "f1": round(float(f1), 4),
        }

        fold_metrics.append(fold_result)

        print(
            f"Fold {fold_number}: "
            f"ROC-AUC={roc_auc:.4f}, "
            f"Precision={precision:.4f}, "
            f"Recall={recall:.4f}, "
            f"F1={f1:.4f}"
        )

    summary = {}

    for metric in scoring:
        values = results[f"test_{metric}"]

        summary[metric] = {
            "mean": round(float(values.mean()), 4),
            "std": round(float(values.std()), 4),
        }

    output = {
        "model": "RandomForestClassifier",
        "dataset": "UCI AI4I 2020 Predictive Maintenance Dataset",
        "dataset_rows": int(len(X)),
        "failure_cases": int(y.sum()),
        "non_failure_cases": int((y == 0).sum()),
        "cross_validation": {
            "method": "5-fold StratifiedKFold",
            "shuffle": True,
            "random_state": 42,
            "folds": fold_metrics,
            "summary": summary,
        },
        "scope": (
            "Cross-validation benchmark on the synthetic UCI AI4I "
            "dataset. Results do not establish field performance."
        ),
    }

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            output,
            file,
            indent=2,
        )

    print("\n===== CROSS-VALIDATION SUMMARY =====")

    for metric, values in summary.items():
        print(
            f"{metric.upper()}: "
            f"{values['mean']:.4f} "
            f"+/- {values['std']:.4f}"
        )

    print("\n===== SAVED =====")
    print(f"Metrics: {OUTPUT_PATH}")


if __name__ == "__main__":
    evaluate_model()