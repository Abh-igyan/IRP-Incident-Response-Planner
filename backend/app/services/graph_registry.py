from __future__ import annotations

import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.services.utils import GRAPH_DIR, haversine_km


@dataclass(frozen=True)
class GraphMetadata:
    graph_name: str
    center_lat: float
    center_lon: float
    graph_path: Path
    corridor_name: str | None = None
    distance_km: float | None = None


class GraphRegistry:
    def __init__(self, graph_dir: Path = GRAPH_DIR, threshold_km: float = 8.0) -> None:
        self.graph_dir = graph_dir
        self.threshold_km = threshold_km
        self._graphs: list[GraphMetadata] | None = None

    def load(self) -> None:
        if self._graphs is not None:
            return

        graphs: list[GraphMetadata] = []
        for path in sorted(self.graph_dir.glob("*.pkl")):
            metadata = self._metadata_for_graph(path)
            if metadata is not None:
                graphs.append(metadata)
        self._graphs = graphs

    def get_nearest_graph(self, latitude: float, longitude: float) -> GraphMetadata | None:
        graphs = self.get_nearest_graphs(latitude, longitude, limit=1)
        return graphs[0] if graphs else None

    def get_nearest_graphs(self, latitude: float, longitude: float, limit: int = 3) -> list[GraphMetadata]:
        self.load()
        assert self._graphs is not None
        ranked = []
        for graph in self._graphs:
            distance = haversine_km(latitude, longitude, graph.center_lat, graph.center_lon)
            if distance <= self.threshold_km:
                ranked.append(
                    GraphMetadata(
                        graph_name=graph.graph_name,
                        center_lat=graph.center_lat,
                        center_lon=graph.center_lon,
                        graph_path=graph.graph_path,
                        corridor_name=graph.corridor_name,
                        distance_km=round(distance, 3),
                    )
                )
        return sorted(ranked, key=lambda item: item.distance_km or 0)[:limit]

    @staticmethod
    def _metadata_for_graph(path: Path) -> GraphMetadata | None:
        try:
            with open(path, "rb") as file:
                graph = pickle.load(file)
            coords = [
                (float(data["y"]), float(data["x"]))
                for _, data in graph.nodes(data=True)
                if "y" in data and "x" in data
            ]
        except Exception:
            return None

        if not coords:
            return None

        return GraphMetadata(
            graph_name=path.stem,
            center_lat=sum(lat for lat, _ in coords) / len(coords),
            center_lon=sum(lon for _, lon in coords) / len(coords),
            graph_path=path,
            corridor_name=_corridor_from_graph_name(path.stem),
        )


def _corridor_from_graph_name(name: str) -> str:
    parts = name.split("_")
    if parts and parts[-1].isdigit():
        parts = parts[:-1]
    return " ".join(parts).lower()
