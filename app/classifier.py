"""
Academic defect-probability classifier.

The model is trained on fictional sample data. It does NOT predict real
manufacturing defects and must not be used as evidence of causation.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = ROOT / "ml" / "model.pkl"
METRICS_PATH = ROOT / "ml" / "metrics.json"

FEATURE_COLUMNS = [
    "machine_code",
    "product_code",
    "temperature",
    "pressure",
    "operating_hours",
    "shift_code",
    "previous_defects",
    "maintenance_overdue",
]

SHIFT_MAP = {"Morning": 0, "Afternoon": 1, "Night": 2}
MAINT_MAP = {"COMPLETED": 0, "SCHEDULED": 1, "OVERDUE": 2, "MAINTENANCE_REQUIRED": 2}


class DefectAnalyzer:
    def __init__(self) -> None:
        self.bundle: Optional[dict] = None
        self.load_error: Optional[str] = None
        self._load()

    def _load(self) -> None:
        if not MODEL_PATH.exists():
            self.load_error = (
                "Model file ml/model.pkl was not found. Run: python ml/train_model.py"
            )
            return
        try:
            self.bundle = joblib.load(MODEL_PATH)
            self.load_error = None
        except Exception as exc:  # noqa: BLE001
            self.load_error = f"Could not load the academic model: {exc}"
            self.bundle = None

    def ready(self) -> bool:
        return self.bundle is not None

    def _encode(self, features: Dict[str, Any]) -> np.ndarray:
        machine = str(features.get("machine_id", "M01"))
        product = str(features.get("product_id", "P01"))
        shift = str(features.get("shift", "Morning"))
        maint = str(features.get("maintenance_status", "COMPLETED"))
        machine_code = int("".join(ch for ch in machine if ch.isdigit()) or "1")
        product_code = int("".join(ch for ch in product if ch.isdigit()) or "1")
        row = [
            machine_code,
            product_code,
            float(features.get("temperature", 0)),
            float(features.get("pressure", 0)),
            float(features.get("operating_hours", 0)),
            SHIFT_MAP.get(shift, 0),
            float(features.get("previous_defects", 0)),
            1 if MAINT_MAP.get(maint, 0) == 2 else 0,
        ]
        return np.array(row, dtype=float).reshape(1, -1)

    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        if not self.ready():
            return {
                "ok": False,
                "error": self.load_error or "Classifier is not available.",
            }
        try:
            x = self._encode(features)
        except (TypeError, ValueError):
            return {
                "ok": False,
                "error": "Prediction inputs must be valid numbers and selected lists.",
            }

        model = self.bundle["model"]
        names = self.bundle.get("feature_names") or FEATURE_COLUMNS
        frame = pd.DataFrame(x, columns=names)
        proba = float(model.predict_proba(frame)[0][1])
        percent = round(proba * 100, 1)
        if percent >= 70:
            risk = "HIGH"
        elif percent >= 40:
            risk = "MEDIUM"
        else:
            risk = "LOW"

        reasons = self._reasons(features, percent)
        return {
            "ok": True,
            "probability": percent,
            "risk_level": risk,
            "reasons": reasons,
            "disclaimer": (
                "Academic demonstration only. Trained on fictional sample data. "
                "This probability is not a real-world diagnosis and does not prove "
                "that a machine caused a defect."
            ),
            "metrics": self.bundle.get("metrics", {}),
        }

    def _reasons(self, features: Dict[str, Any], percent: float) -> List[str]:
        reasons: List[str] = []
        prev = float(features.get("previous_defects") or 0)
        hours = float(features.get("operating_hours") or 0)
        temp = float(features.get("temperature") or 0)
        pressure = float(features.get("pressure") or 0)
        maint = str(features.get("maintenance_status") or "")
        if prev >= 8:
            reasons.append("High previous defect count on similar runs")
        if hours >= 4000:
            reasons.append("Long machine operating hours")
        if maint in {"OVERDUE", "MAINTENANCE_REQUIRED"}:
            reasons.append("Maintenance overdue / required")
        if temp >= 90:
            reasons.append("High recorded operating temperature")
        if pressure >= 8:
            reasons.append("High recorded pressure")
        if str(features.get("shift")) == "Night":
            reasons.append("Night shift (associated with higher sample defect rate)")
        if not reasons:
            reasons.append("No strong risk flags in the submitted sample inputs")
        if percent < 40:
            reasons.append("Overall encoded features resemble lower-risk sample rows")
        return reasons[:5]


classifier = DefectAnalyzer()
