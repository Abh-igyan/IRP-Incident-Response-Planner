from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import pandas as pd


APP_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = APP_DIR.parent
ROOT_DIR = BACKEND_DIR.parent
MODELS_DIR = ROOT_DIR / "models"
DATASETS_DIR = ROOT_DIR / "datasets"
DATA_DIR = BACKEND_DIR / "data"
DATASET_PATH = DATASETS_DIR / "Astram event data_anonymized - Astram event data_anonymizedb40ac87.csv"
MODEL_PATH = MODELS_DIR / "closure_model.pkl"
METADATA_PATH = MODELS_DIR / "pipeline_metadata.pkl"
GRAPH_PATHS = [
    MODELS_DIR / "bangalore_graph.graphml",
    MODELS_DIR / "bangalore.graphml",
]
GRAPH_DIR = ROOT_DIR / "graphs"

CORRIDOR_GRAPH_MAP = {
    "bannerghata road": list(GRAPH_DIR.glob("Bannerghata_Road_*.pkl")),
    "bellary road 1": list(GRAPH_DIR.glob("Bellary_Road_1_*.pkl")),
    "bellary road 2": list(GRAPH_DIR.glob("Bellary_Road_2_*.pkl")),
    "hosur road": list(GRAPH_DIR.glob("Hosur_Road_*.pkl")),
    "magadi road": list(GRAPH_DIR.glob("Magadi_Road_*.pkl")),
    "mysore road": list(GRAPH_DIR.glob("Mysore_Road_*.pkl")),
    "old madras road": list(GRAPH_DIR.glob("Old_Madras_Road_*.pkl")),
    "orr east 1": list(GRAPH_DIR.glob("ORR_East_1_*.pkl")),
    "orr east 2": list(GRAPH_DIR.glob("ORR_East_2_*.pkl")),
    "orr north 1": list(GRAPH_DIR.glob("ORR_North_1_*.pkl")),
    "orr north 2": list(GRAPH_DIR.glob("ORR_North_2_*.pkl")),
    "orr west 1": list(GRAPH_DIR.glob("ORR_West_1_*.pkl")),
    "tumkur road": list(GRAPH_DIR.glob("Tumkur_Road_*.pkl")),
    "west of chord road": list(GRAPH_DIR.glob("West_of_Chord_Road_*.pkl")),
}

def normalize_text(value: Any, default: str = "unknown") -> str:
    if value is None:
        return default
    text = str(value).strip()
    if not text or text.lower() == "nan":
        return default
    return text.lower()


def display_text(value: str) -> str:
    if not value:
        return "Unknown"
    return value.replace("_", " ").title()


def bool_to_model_value(value: bool) -> int:
    return 1 if value else 0


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius_km = 6371.0088
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )
    return 2 * radius_km * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def get_corridor_graphs(corridor: str):
    return CORRIDOR_GRAPH_MAP.get(corridor.lower(), [])

class LocationResolver:
    def __init__(self, dataset_path: Path = DATASET_PATH) -> None:
        self.dataset_path = dataset_path
        self.records: list[dict[str, Any]] = []
        self.options: dict[str, list[str]] = {}
        self._load()

    def _load(self) -> None:
        df = pd.read_csv(self.dataset_path)
        needed = [
            "latitude",
            "longitude",
            "corridor",
            "zone",
            "police_station",
            "event_type",
            "event_cause",
            "veh_type",
            "priority",
        ]
        df = df[needed].copy()
        df = df.dropna(subset=["latitude", "longitude"])
        df = df[(df["latitude"] != 0) & (df["longitude"] != 0)]

        for col in ["corridor", "zone", "police_station"]:
            df[col] = df[col].fillna("Unknown").map(normalize_text)

        self.records = df[["latitude", "longitude", "corridor", "zone", "police_station"]].to_dict(
            "records"
        )
        self.options = {
            col: sorted(
                {
                    str(v).strip()
                    for v in df[col].dropna().unique()
                    if str(v).strip() and str(v).strip().lower() != "nan"
                }
            )
            for col in ["event_type", "event_cause", "veh_type", "priority"]
        }

    def resolve(self, latitude: float, longitude: float) -> dict[str, str | float]:
        if not self.records:
            return {
                "corridor": "non-corridor",
                "zone": "unknown",
                "police_station": "no police station",
                "nearest_distance_km": 0.0,
            }

        best = min(
            self.records,
            key=lambda row: haversine_km(latitude, longitude, row["latitude"], row["longitude"]),
        )
        return {
            "corridor": best["corridor"],
            "zone": best["zone"],
            "police_station": best["police_station"],
            "nearest_distance_km": round(
                haversine_km(latitude, longitude, best["latitude"], best["longitude"]), 3
            ),
        }


def temporal_features(incident_dt) -> dict[str, int]:
    hour = incident_dt.hour
    dayofweek = incident_dt.weekday()
    month = incident_dt.month
    return {
        "hour": hour,
        "dayofweek": dayofweek,
        "month": month,
        "is_weekend": 1 if dayofweek in (5, 6) else 0,
        "is_peak_hour": 1 if hour in (8, 9, 10, 17, 18, 19) else 0,
    }
