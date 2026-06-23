from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from app.services.utils import DATASET_PATH, normalize_text


CONFIDENCE_FIELDS = ("event_type", "event_cause", "veh_type", "police_station", "corridor")


@dataclass(frozen=True)
class FieldConfidence:
    field: str
    value: str
    count: int
    score: float


class FeatureConfidenceScorer:
    def __init__(self, dataset_path: Path = DATASET_PATH) -> None:
        self.dataset_path = dataset_path
        self.counts: dict[str, dict[str, int]] = {}
        self.thresholds = {
            "event_type": 100,
            "event_cause": 75,
            "veh_type": 50,
            "police_station": 30,
            "corridor": 30,
        }
        self.weights = {
            "event_type": 0.15,
            "event_cause": 0.25,
            "veh_type": 0.15,
            "police_station": 0.20,
            "corridor": 0.25,
        }
        self._load()

    def _load(self) -> None:
        df = pd.read_csv(self.dataset_path, usecols=list(CONFIDENCE_FIELDS))
        for field in CONFIDENCE_FIELDS:
            normalized = df[field].fillna("unknown").map(normalize_text)
            self.counts[field] = normalized.value_counts().to_dict()

    def score(self, row: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
        details = []
        notes = []
        total = 0.0
        for field in CONFIDENCE_FIELDS:
            value = normalize_text(row.get(field))
            count = int(self.counts.get(field, {}).get(value, 0))
            threshold = self.thresholds[field]
            field_score = max(0.0, min(1.0, count / threshold))
            total += self.weights[field] * field_score
            details.append(
                FieldConfidence(
                    field=field,
                    value=value,
                    count=count,
                    score=round(field_score, 3),
                )
            )
            if count == 0:
                notes.append(f"Unseen {field}: {value}")
            elif field_score < 0.5:
                notes.append(f"Rare {field}: {value} ({count} training samples)")

        score = round(max(0.0, min(1.0, total)), 3)
        if score >= 0.75:
            label = "High"
        elif score >= 0.45:
            label = "Medium"
        else:
            label = "Low"
            notes.append("Low-confidence prediction: smoothing applied")

        return {
            "score": score,
            "label": label,
            "feature_support": [item.__dict__ for item in details],
        }, notes
