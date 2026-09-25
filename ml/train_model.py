"""
Train a Decision Tree classifier on the fictional MDTPS dataset.

Run after generating data:
    python ml/train_model.py
"""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "ml" / "dataset.csv"
MODEL = ROOT / "ml" / "model.pkl"
METRICS = ROOT / "ml" / "metrics.json"

SHIFT_MAP = {"Morning": 0, "Afternoon": 1, "Night": 2}


def encode(frame: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame()
    out["machine_code"] = frame["machine_id"].astype(str).str.extract(r"(\d+)").astype(int)
    out["product_code"] = frame["product_id"].astype(str).str.extract(r"(\d+)").astype(int)
    out["temperature"] = frame["temperature"].astype(float)
    out["pressure"] = frame["pressure"].astype(float)
    out["operating_hours"] = frame["operating_hours"].astype(float)
    out["shift_code"] = frame["shift"].map(SHIFT_MAP).fillna(0)
    out["previous_defects"] = frame["previous_defects"].astype(float)
    out["maintenance_overdue"] = frame["maintenance_status"].isin(["OVERDUE", "MAINTENANCE_REQUIRED"]).astype(int)
    return out


def main() -> None:
    if not DATA.exists():
        raise SystemExit("ml/dataset.csv missing. Run: python scripts/generate_sample_data.py")
    df = pd.read_csv(DATA)
    x = encode(df)
    y = df["is_defective"].astype(int)
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.25, random_state=42, stratify=y
    )
    model = DecisionTreeClassifier(max_depth=5, min_samples_leaf=8, random_state=42)
    model.fit(x_train, y_train)
    pred = model.predict(x_test)
    acc = accuracy_score(y_test, pred)
    matrix = confusion_matrix(y_test, pred).tolist()
    report = classification_report(y_test, pred, output_dict=True)
    payload = {
        "model": model,
        "feature_names": list(x.columns),
        "metrics": {
            "algorithm": "Decision Tree (max_depth=5)",
            "accuracy": round(float(acc), 4),
            "confusion_matrix": matrix,
            "n_train": int(len(x_train)),
            "n_test": int(len(x_test)),
            "disclaimer": "Fictional sample data. Academic demonstration only.",
        },
        "report": report,
    }
    joblib.dump(payload, MODEL)
    METRICS.write_text(json.dumps(payload["metrics"], indent=2), encoding="utf-8")
    print(f"Saved {MODEL}")
    print(f"Test accuracy: {acc:.3f}")
    print("Confusion matrix:", matrix)


if __name__ == "__main__":
    main()
