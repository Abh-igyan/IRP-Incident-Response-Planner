from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from typing import Any

from app.schemas import FeedbackRequest
from app.services.utils import DATA_DIR, normalize_text


DB_PATH = DATA_DIR / "feedback.sqlite3"
LEARNING_SCOPES = ("global", "event_type", "event_cause", "corridor", "zone", "police_station")


@dataclass(frozen=True)
class LearningProfile:
    scope: str
    value: str
    samples: int
    closure_events: int
    avg_actual_delay: float | None
    avg_predicted_probability: float | None
    avg_predicted_delay: float | None
    avg_impact_error: float | None

    @property
    def actual_closure_rate(self) -> float | None:
        if self.samples <= 0:
            return None
        return self.closure_events / self.samples


class FeedbackLearningService:
    def __init__(self) -> None:
        self.profiles: dict[tuple[str, str], LearningProfile] = {}

    def init_db(self) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    incident_json TEXT NOT NULL,
                    prediction_json TEXT,
                    actual_road_closure INTEGER,
                    actual_delay_mins REAL,
                    notes TEXT
                )
                """
            )
            self._ensure_feedback_columns(conn)
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS learning_profiles (
                    scope TEXT NOT NULL,
                    value TEXT NOT NULL,
                    samples INTEGER NOT NULL DEFAULT 0,
                    closure_events INTEGER NOT NULL DEFAULT 0,
                    avg_actual_delay REAL,
                    avg_predicted_probability REAL,
                    avg_predicted_delay REAL,
                    avg_impact_error REAL,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (scope, value)
                )
                """
            )

    def refresh(self) -> None:
        self.init_db()
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM learning_profiles").fetchall()

        self.profiles = {
            (row["scope"], row["value"]): LearningProfile(
                scope=row["scope"],
                value=row["value"],
                samples=row["samples"],
                closure_events=row["closure_events"],
                avg_actual_delay=row["avg_actual_delay"],
                avg_predicted_probability=row["avg_predicted_probability"],
                avg_predicted_delay=row["avg_predicted_delay"],
                avg_impact_error=row["avg_impact_error"],
            )
            for row in rows
        }

    def record_feedback(
        self,
        payload: FeedbackRequest,
        predictor,
    ) -> int:
        self.init_db()
        predictor.load()
        predictor._ensure_location_resolver()
        feature_row = predictor.build_feature_row(payload.incident)
        prediction = payload.prediction or predictor.predict(payload.incident)
        scopes = self._profile_keys(feature_row)

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute(
                """
                INSERT INTO feedback (
                    incident_json,
                    prediction_json,
                    actual_road_closure,
                    actual_delay_mins,
                    notes,
                    derived_context_json,
                    predicted_closure_probability,
                    predicted_impact_score,
                    predicted_delay_mins,
                    learning_scopes_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload.incident.model_dump_json(),
                    json.dumps(prediction),
                    None if payload.actual_road_closure is None else int(payload.actual_road_closure),
                    payload.actual_delay_mins,
                    payload.notes,
                    json.dumps({key: feature_row[key] for key in self._context_keys()}),
                    prediction.get("closure_probability"),
                    prediction.get("impact_score"),
                    (prediction.get("traffic_forecast") or {}).get("expected_delay_mins"),
                    json.dumps(scopes),
                ),
            )
            feedback_id = int(cursor.lastrowid)

            if payload.actual_road_closure is not None or payload.actual_delay_mins is not None:
                for scope, value in scopes.items():
                    self._upsert_profile(
                        conn=conn,
                        scope=scope,
                        value=value,
                        actual_road_closure=payload.actual_road_closure,
                        actual_delay_mins=payload.actual_delay_mins,
                        prediction=prediction,
                    )

        self.refresh()
        return feedback_id

    def adjust_closure_probability(self, row: dict[str, Any], base_probability: float) -> tuple[float, dict[str, Any]]:
        adjustments = []
        for weight, profile in self._matching_profiles(row):
            if profile.samples < 3 or profile.actual_closure_rate is None:
                continue
            predicted_rate = profile.avg_predicted_probability
            if predicted_rate is None:
                continue
            confidence = min(1.0, profile.samples / 25)
            adjustments.append(weight * confidence * (profile.actual_closure_rate - predicted_rate))

        raw_adjustment = sum(adjustments)
        capped_adjustment = max(-0.25, min(0.25, raw_adjustment))
        adjusted = max(0.01, min(0.98, base_probability + capped_adjustment))
        return adjusted, {
            "base_closure_probability": round(base_probability, 3),
            "calibration_adjustment": round(capped_adjustment, 3),
            "matched_profiles": self._profile_count(row),
            "learning_samples": self._sample_count(row),
        }

    def adjust_traffic_forecast(self, row: dict[str, Any], forecast: dict[str, Any]) -> dict[str, Any]:
        delay_adjustments = []
        predicted_delay = forecast["expected_delay_mins"]
        for weight, profile in self._matching_profiles(row):
            if profile.samples < 3:
                continue
            if profile.avg_actual_delay is None or profile.avg_predicted_delay is None:
                continue
            confidence = min(1.0, profile.samples / 25)
            delay_adjustments.append(weight * confidence * (profile.avg_actual_delay - profile.avg_predicted_delay))

        adjusted_delay = max(0.0, predicted_delay + max(-20.0, min(20.0, sum(delay_adjustments))))
        if adjusted_delay >= 25:
            severity = "Severe"
        elif adjusted_delay >= 12:
            severity = "Moderate"
        else:
            severity = "Minor"
        return {"severity": severity, "expected_delay_mins": round(adjusted_delay, 1)}

    def summary(self) -> dict[str, Any]:
        self.refresh()
        profiles = sorted(
            self.profiles.values(),
            key=lambda item: (item.samples, item.scope, item.value),
            reverse=True,
        )
        return {
            "profile_count": len(profiles),
            "total_feedback_samples": self.profiles.get(("global", "all"), LearningProfile("global", "all", 0, 0, None, None, None, None)).samples,
            "profiles": [
                {
                    "scope": profile.scope,
                    "value": profile.value,
                    "samples": profile.samples,
                    "actual_closure_rate": None
                    if profile.actual_closure_rate is None
                    else round(profile.actual_closure_rate, 3),
                    "avg_actual_delay": profile.avg_actual_delay,
                    "avg_predicted_probability": profile.avg_predicted_probability,
                    "avg_predicted_delay": profile.avg_predicted_delay,
                    "avg_impact_error": profile.avg_impact_error,
                }
                for profile in profiles[:25]
            ],
        }

    def _matching_profiles(self, row: dict[str, Any]) -> list[tuple[float, LearningProfile]]:
        weighted_keys = [
            (0.18, ("global", "all")),
            (0.16, ("event_type", normalize_text(row.get("event_type")))),
            (0.24, ("event_cause", normalize_text(row.get("event_cause")))),
            (0.20, ("corridor", normalize_text(row.get("corridor")))),
            (0.12, ("zone", normalize_text(row.get("zone")))),
            (0.10, ("police_station", normalize_text(row.get("police_station")))),
        ]
        return [(weight, self.profiles[key]) for weight, key in weighted_keys if key in self.profiles]

    def _profile_count(self, row: dict[str, Any]) -> int:
        return len(self._matching_profiles(row))

    def _sample_count(self, row: dict[str, Any]) -> int:
        return sum(profile.samples for _, profile in self._matching_profiles(row))

    def _upsert_profile(
        self,
        conn: sqlite3.Connection,
        scope: str,
        value: str,
        actual_road_closure: bool | None,
        actual_delay_mins: float | None,
        prediction: dict[str, Any],
    ) -> None:
        existing = conn.execute(
            "SELECT * FROM learning_profiles WHERE scope = ? AND value = ?",
            (scope, value),
        ).fetchone()
        predicted_probability = prediction.get("closure_probability")
        predicted_delay = (prediction.get("traffic_forecast") or {}).get("expected_delay_mins")
        predicted_impact = prediction.get("impact_score")
        actual_impact = self._actual_impact_from_delay(actual_delay_mins)
        impact_error = None
        if actual_impact is not None and predicted_impact is not None:
            impact_error = actual_impact - float(predicted_impact)

        if existing is None:
            conn.execute(
                """
                INSERT INTO learning_profiles (
                    scope, value, samples, closure_events, avg_actual_delay,
                    avg_predicted_probability, avg_predicted_delay, avg_impact_error
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    scope,
                    value,
                    1,
                    1 if actual_road_closure else 0,
                    actual_delay_mins,
                    predicted_probability,
                    predicted_delay,
                    impact_error,
                ),
            )
            return

        samples = int(existing[2]) + 1
        closure_events = int(existing[3]) + (1 if actual_road_closure else 0)
        conn.execute(
            """
            UPDATE learning_profiles
            SET samples = ?,
                closure_events = ?,
                avg_actual_delay = ?,
                avg_predicted_probability = ?,
                avg_predicted_delay = ?,
                avg_impact_error = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE scope = ? AND value = ?
            """,
            (
                samples,
                closure_events,
                self._rolling_average(existing[4], samples, actual_delay_mins),
                self._rolling_average(existing[5], samples, predicted_probability),
                self._rolling_average(existing[6], samples, predicted_delay),
                self._rolling_average(existing[7], samples, impact_error),
                scope,
                value,
            ),
        )

    @staticmethod
    def _rolling_average(current: float | None, new_sample_count: int, value: float | None) -> float | None:
        if value is None:
            return current
        if current is None:
            return float(value)
        previous_count = max(1, new_sample_count - 1)
        return ((float(current) * previous_count) + float(value)) / new_sample_count

    @staticmethod
    def _actual_impact_from_delay(delay: float | None) -> float | None:
        if delay is None:
            return None
        return max(0.0, min(100.0, 25 + float(delay) * 1.8))

    @staticmethod
    def _profile_keys(row: dict[str, Any]) -> dict[str, str]:
        return {
            "global": "all",
            "event_type": normalize_text(row.get("event_type")),
            "event_cause": normalize_text(row.get("event_cause")),
            "corridor": normalize_text(row.get("corridor")),
            "zone": normalize_text(row.get("zone")),
            "police_station": normalize_text(row.get("police_station")),
        }

    @staticmethod
    def _context_keys() -> tuple[str, ...]:
        return (
            "event_type",
            "event_cause",
            "veh_type",
            "priority",
            "corridor",
            "zone",
            "police_station",
            "hour",
            "dayofweek",
            "month",
            "is_weekend",
            "is_peak_hour",
        )

    @staticmethod
    def _ensure_feedback_columns(conn: sqlite3.Connection) -> None:
        existing = {
            row[1]
            for row in conn.execute("PRAGMA table_info(feedback)").fetchall()
        }
        columns = {
            "derived_context_json": "TEXT",
            "predicted_closure_probability": "REAL",
            "predicted_impact_score": "REAL",
            "predicted_delay_mins": "REAL",
            "learning_scopes_json": "TEXT",
        }
        for name, column_type in columns.items():
            if name not in existing:
                conn.execute(f"ALTER TABLE feedback ADD COLUMN {name} {column_type}")
