from __future__ import annotations

import pickle
from typing import Any

import pandas as pd

from app.schemas import IncidentRequest
from app.services.diversion import DiversionService
from app.services.feedback_learning import FeedbackLearningService
from app.services.recommender import (
    diversion_strategy,
    eta_target,
    resource_plan,
    response_priority,
    traffic_forecast,
)
from app.services.utils import (
    METADATA_PATH,
    MODEL_PATH,
    LocationResolver,
    bool_to_model_value,
    normalize_text,
    temporal_features,
)


class IncidentPredictor:
    def __init__(self) -> None:
        self.metadata: dict[str, Any] = {}
        self.model: Any | None = None
        self.model_status = "not_loaded"
        self.location_resolver: LocationResolver | None = None
        self.diversion_service = DiversionService()
        self.learning_service = FeedbackLearningService()
        self._core_loaded = False

    def load(self) -> None:
        if self._core_loaded:
            return

        with open(METADATA_PATH, "rb") as file:
            self.metadata = pickle.load(file)

        try:
            with open(MODEL_PATH, "rb") as file:
                self.model = pickle.load(file)
            self.model_status = "catboost_model_loaded"
        except Exception as exc:
            self.model = None
            self.model_status = f"fallback_metadata_model:{exc.__class__.__name__}"

        self.learning_service.refresh()
        self._core_loaded = True

    def _ensure_location_resolver(self) -> None:
        if self.location_resolver is None:
            self.location_resolver = LocationResolver()
    
    def predict(self, incident: IncidentRequest) -> dict:
        self.load()
        self._ensure_location_resolver()

        row = self.build_feature_row(incident)
        base_probability = self._closure_probability(row)
        row["closure_probability"], learning_insight = self.learning_service.adjust_closure_probability(
            row,
            base_probability,
        )
        row["closure_risk"] = self._closure_risk(row["closure_probability"])
        row["impact_score"] = self._impact_score(row)
        row["impact_class"] = self._impact_class(row["impact_score"])

        priority = response_priority(row)
        strategy = diversion_strategy(row)

        if row["closure_probability"] >= 0.18 and row["corridor"] != "non-corridor":
            diversion_plan = self.diversion_service.get_best_diversion_route(row)
        else:
            diversion_plan = self.diversion_service._empty_plan(
                "Closure probability below threshold or no corridor found."
            )

        forecast = self.learning_service.adjust_traffic_forecast(row, traffic_forecast(row))

        return {
            "impact_score": round(row["impact_score"], 2),
            "impact_class": row["impact_class"],
            "closure_probability": round(row["closure_probability"], 3),
            "resource_plan": resource_plan(row),
            "traffic_forecast": forecast,
            "response_priority": priority,
            "eta_target": eta_target(priority),
            "diversion_strategy": strategy,
            "diversion_plan": diversion_plan,
            "derived_context": {
                "corridor": row["corridor"],
                "zone": row["zone"],
                "police_station": row["police_station"],
                "hour": row["hour"],
                "dayofweek": row["dayofweek"],
                "month": row["month"],
                "is_weekend": row["is_weekend"],
                "is_peak_hour": row["is_peak_hour"],
            },
            "model_status": self.model_status,
            "learning_insight": learning_insight,
        }

    def options(self) -> dict[str, list[str]]:
        self._ensure_location_resolver()
        assert self.location_resolver is not None
        return self.location_resolver.options

    def build_feature_row(self, incident: IncidentRequest) -> dict[str, Any]:
        if self.location_resolver is None:
            raise RuntimeError("Location resolver has not been loaded.")

        resolved = self.location_resolver.resolve(incident.latitude, incident.longitude)
        row = {
            "event_type": normalize_text(incident.event_type),
            "latitude": incident.latitude,
            "longitude": incident.longitude,
            "event_cause": normalize_text(incident.event_cause),
            "authenticated": bool_to_model_value(incident.authenticated),
            "veh_type": normalize_text(incident.veh_type, "unknown"),
            "corridor": normalize_text(resolved["corridor"], "non-corridor"),
            "priority": str(incident.priority or "High").strip().title(),
            "police_station": normalize_text(resolved["police_station"], "no police station"),
            "zone": normalize_text(resolved["zone"], "unknown"),
            "has_end_coords": 0,
        }
        row.update(temporal_features(incident.incident_datetime))
        return row

    def _closure_probability(self, row: dict[str, Any]) -> float:
        features = self.metadata.get("features", [])
        if self.model is not None:
            try:
                sample = pd.DataFrame([{feature: row[feature] for feature in features}])
                return float(self.model.predict_proba(sample)[0][1])
            except Exception as exc:
                self.model_status = f"fallback_after_model_error:{exc.__class__.__name__}"

        event_type_risk = self.metadata.get("event_type_risk", {}).get(
            row["event_type"], self.metadata.get("global_closure_mean", 0.08)
        )
        event_cause_risk = self.metadata.get("event_cause_risk", {}).get(row["event_cause"], 0.5)
        corridor_risk = self._risk_lookup("corridor_risk_map", row["corridor"])
        zone_risk = self._risk_lookup("zone_risk_map", row["zone"])
        station_risk = self._risk_lookup("station_risk_map", row["police_station"])
        score = (
            float(event_type_risk) * 0.18
            + float(event_cause_risk) * 0.24
            + float(corridor_risk) * 1.2
            + float(zone_risk) * 1.0
            + float(station_risk) * 1.0
            + row["is_peak_hour"] * 0.08
            + (1 if row["priority"] == "High" else 0) * 0.04
        )
        return max(0.01, min(0.98, score))

    def _impact_score(self, row: dict[str, Any]) -> float:
        event_type_risk = self.metadata.get("event_type_risk", {}).get(row["event_type"], 0.5)
        event_cause_risk = self.metadata.get("event_cause_risk", {}).get(row["event_cause"], 0.5)
        corridor_risk = self._risk_lookup("corridor_risk_map", row["corridor"])
        zone_risk = self._risk_lookup("zone_risk_map", row["zone"])
        station_risk = self._risk_lookup("station_risk_map", row["police_station"])
        time_risk = 0.2
        if row["is_peak_hour"] == 1:
            time_risk += 0.5
        if row["is_weekend"] == 1:
            time_risk += 0.15
        if row["hour"] >= 21 or row["hour"] <= 6:
            time_risk += 0.15
        endpoint_risk = 0.8 if row.get("has_end_coords", 0) == 1 else 0.2
        score = (
            row["closure_risk"] * 32
            + float(event_type_risk) * 15
            + float(event_cause_risk) * 20
            + float(corridor_risk) * 10
            + float(zone_risk) * 8
            + float(station_risk) * 7
            + time_risk * 5
            + endpoint_risk * 3
        )
        return max(0.0, min(100.0, score))

    def _impact_class(self, score: float) -> str:
        low = float(self.metadata.get("low_thr", 42.68))
        high = float(self.metadata.get("high_thr", 54.81))
        if score <= low:
            return "Low"
        if score <= high:
            return "Medium"
        return "High"

    def _risk_lookup(self, key: str, value: str) -> float:
        return float(
            self.metadata.get(key, {}).get(
                normalize_text(value),
                self.metadata.get("global_closure_mean", 0.0739),
            )
        )

    @staticmethod
    def _closure_risk(probability: float) -> float:
        if probability < 0.20:
            return 0.2
        if probability < 0.40:
            return 0.5
        if probability < 0.60:
            return 0.75
        return 1.0
