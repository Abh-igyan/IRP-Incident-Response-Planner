from __future__ import annotations

from typing import Any

import pandas as pd

from app.services.utils import DATASET_PATH, normalize_text


class AnalyticsService:
    """Builds operational analytics bundles from the historical incident dataset."""

    def __init__(self, dataset_path=DATASET_PATH) -> None:
        self.dataset_path = dataset_path
        self.df = self._preprocess(pd.read_csv(self.dataset_path))

    def _preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        for col in ["start_datetime", "created_date", "modified_datetime", "closed_datetime", "end_datetime"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")

        if "incident_datetime" in df.columns:
            df["incident_datetime"] = pd.to_datetime(df["incident_datetime"], errors="coerce")
        elif "start_datetime" in df.columns:
            df["incident_datetime"] = df["start_datetime"]

        for col in ["event_type", "event_cause", "veh_type", "corridor", "priority", "police_station", "zone"]:
            if col in df.columns:
                df[col] = df[col].fillna("unknown").map(normalize_text)

        if "authenticated" in df.columns:
            df["authenticated"] = df["authenticated"].fillna("no").map(normalize_text)

        if "latitude" in df.columns and "longitude" in df.columns:
            df = df.dropna(subset=["latitude", "longitude"])

        if "requires_road_closure" in df.columns:
            df["requires_road_closure"] = df["requires_road_closure"].fillna(False).astype(int)
        else:
            df["requires_road_closure"] = 0

        df = df.dropna(subset=["incident_datetime"])
        df["hour"] = df["incident_datetime"].dt.hour
        df["dayofweek"] = df["incident_datetime"].dt.dayofweek
        df["month"] = df["incident_datetime"].dt.month
        df["is_weekend"] = df["dayofweek"].isin([5, 6]).astype(int)
        df["is_peak_hour"] = df["hour"].isin([8, 9, 10, 17, 18, 19]).astype(int)

        return df

    def get_summary(self) -> dict[str, Any]:
        total_incidents = int(len(self.df))
        total_closures = int(self.df["requires_road_closure"].sum())
        closure_rate = round(total_closures / total_incidents, 3) if total_incidents else 0.0

        corridor_stats = self.df.groupby("corridor")["requires_road_closure"].mean().sort_values(ascending=False)
        cause_stats = self.df.groupby("event_cause")["requires_road_closure"].mean().sort_values(ascending=False)

        return {
            "total_incidents": total_incidents,
            "total_closures": total_closures,
            "closure_rate": closure_rate,
            "highest_risk_corridor": corridor_stats.index[0] if not corridor_stats.empty else None,
            "highest_risk_event_cause": cause_stats.index[0] if not cause_stats.empty else None,
        }

    def get_heatmap_data(self, limit: int = 500) -> list[dict[str, Any]]:
        if self.df.empty:
            return []

        sample = (
            self.df[[
                "latitude",
                "longitude",
                "event_type",
                "event_cause",
                "veh_type",
                "requires_road_closure",
            ]]
            .copy()
            .assign(
                intensity=lambda frame: frame["requires_road_closure"].astype(float) * 0.8 + 0.2,
                incident_category=lambda frame: frame["event_cause"].where(
                    frame["event_cause"].ne("unknown"),
                    frame["event_type"],
                ),
            )
        )
        sample = sample.sort_values(by=["requires_road_closure", "intensity"], ascending=False).head(limit)
        return sample[
            [
                "latitude",
                "longitude",
                "event_type",
                "event_cause",
                "veh_type",
                "incident_category",
                "intensity",
            ]
        ].to_dict(orient="records")

    def get_corridor_analytics(self) -> dict[str, Any]:
        incidents = self.df["corridor"].value_counts().head(10).to_dict()
        closure_rate = (
            self.df.groupby("corridor")["requires_road_closure"]
            .mean()
            .sort_values(ascending=False)
            .head(10)
            .to_dict()
        )
        return {
            "incidents_by_corridor": incidents,
            "closure_rate_by_corridor": closure_rate,
            "top_risky_corridors": list(closure_rate.keys())[:5],
        }

    def get_hourly_distribution(self) -> dict[str, int]:
        return self.df["hour"].value_counts().sort_index().astype(int).to_dict()

    def get_event_cause_distribution(self) -> dict[str, int]:
        return self.df["event_cause"].value_counts().head(12).astype(int).to_dict()

    def get_vehicle_type_distribution(self) -> dict[str, int]:
        return self.df["veh_type"].value_counts().head(12).astype(int).to_dict()

    def get_closure_risk_analytics(self) -> dict[str, Any]:
        risky = (
            self.df.groupby(["event_cause", "veh_type"])["requires_road_closure"]
            .mean()
            .sort_values(ascending=False)
            .head(10)
        )
        return {
            "top_risky_pairs": [
                {
                    "event_cause": event_cause,
                    "veh_type": veh_type,
                    "closure_rate": round(rate, 3),
                }
                for (event_cause, veh_type), rate in risky.items()
            ]
        }

    def get_full_analytics_bundle(self) -> dict[str, Any]:
        return {
            "summary": self.get_summary(),
            "heatmap": self.get_heatmap_data(),
            "corridors": self.get_corridor_analytics(),
            "hourly": self.get_hourly_distribution(),
            "event_causes": self.get_event_cause_distribution(),
            "vehicle_types": self.get_vehicle_type_distribution(),
            "closure_risk": self.get_closure_risk_analytics(),
        }
