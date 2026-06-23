from __future__ import annotations

import os
import pickle
from typing import Any

import networkx as nx
import requests

from app.services.graph_registry import GraphMetadata, GraphRegistry
from app.services.utils import haversine_km


class DiversionService:
    def __init__(self) -> None:
        self.graph: Any | None = None
        self.graph_metadata: GraphMetadata | None = None
        self.registry = GraphRegistry()
        self.status = "graph_not_loaded"

    def load(self, graph_metadata: GraphMetadata) -> None:
        if self.graph_metadata and self.graph_metadata.graph_path == graph_metadata.graph_path:
            return
        try:
            with open(graph_metadata.graph_path, "rb") as f:
                self.graph = pickle.load(f)
            self.graph_metadata = graph_metadata
            self.status = f"nearest_graph:{graph_metadata.graph_name}"
        except Exception:
            self.graph = None
            self.graph_metadata = None
            self.status = "graph_load_failed"

    def get_best_diversion_route(self, row: dict) -> dict:
        graph_candidates = self.registry.get_nearest_graphs(
            row["latitude"],
            row["longitude"],
            limit=3,
        )

        for graph_metadata in graph_candidates:
            self.load(graph_metadata)
            if self.graph is None:
                continue
            route = self._route_from_loaded_graph(row)
            if route["route_coords"]:
                route["routing_status"] = self.status
                route["routing_graph"] = {
                    "graph_name": graph_metadata.graph_name,
                    "corridor_name": graph_metadata.corridor_name,
                    "distance_km": graph_metadata.distance_km,
                    "selection": "nearest_graph",
                }
                return route

        return self._empty_plan("No graph route found, monitoring traffic")

    def _route_from_loaded_graph(self, row: dict) -> dict:
        if self.graph is None:
            return self._empty_plan("Routing graph unavailable")

        source_node = self._nearest_node(row["latitude"], row["longitude"])
        if source_node is None:
            return self._empty_plan("No nearby road node found")

        blocked_radius_km = (
            1.1 if row["closure_probability"] > 0.8
            else 0.7 if row["closure_probability"] > 0.5
            else 0.35
        )

        major_nodes = [
            node for node in self.graph.nodes
            if self.graph.degree(node) >= 3
        ]

        candidates = []
        for node in major_nodes:
            if node == source_node:
                continue

            data = self.graph.nodes[node]
            lat, lon = float(data["y"]), float(data["x"])
            dist = haversine_km(row["latitude"], row["longitude"], lat, lon)

            if dist > blocked_radius_km:
                candidates.append((node, dist))

        candidates = sorted(candidates, key=lambda x: x[1])[:50]

        best_route = None
        best_distance = float("inf")

        for target_node, _ in candidates:
            try:
                route = nx.shortest_path(
                    self.graph,
                    source_node,
                    target_node,
                    weight="length",
                )

                distance = nx.shortest_path_length(
                    self.graph,
                    source_node,
                    target_node,
                    weight="length",
                )
            except Exception:
                continue

            if 500 <= distance <= 6000 and distance < best_distance:
                best_route = route
                best_distance = distance

        if not best_route:
            return self._empty_plan("No diversion route found")

        coords = []
        for node in best_route:
            data = self.graph.nodes[node]
            coords.append([float(data["y"]), float(data["x"])])

        roads = self._extract_road_names(best_route)

        validated = self._validate_with_mappls(
            row["latitude"],
            row["longitude"],
            coords[-1][0],
            coords[-1][1],
        )

        if validated:
            best_distance = validated["distance_m"]
            eta_min = validated["eta_min"]
            roads = validated["roads"] or roads
        else:
            eta_min = (best_distance / 1000) / 25 * 60

        return {
            "best_diversion_distance_km": round(best_distance / 1000, 2),
            "best_diversion_eta_mins": round(eta_min, 2),
            "diversion_road_name": roads[0] if roads else None,
            "alternate_roads": roads[1:4] if len(roads) > 1 else [],
            "route_coords": coords,
            "geometry": validated.get("geometry") if validated else None,
            "routing_status": self.status,
        }

    def _nearest_node(self, latitude: float, longitude: float):
        if self.graph is None:
            return None
        return self._nearest_node_in_graph(self.graph, latitude, longitude)

    def _nearest_node_in_graph(self, graph, latitude: float, longitude: float):
        best_node = None
        best_distance = float("inf")

        for node, data in graph.nodes(data=True):
            try:
                lat = float(data["y"])
                lon = float(data["x"])
            except Exception:
                continue

            dist = haversine_km(latitude, longitude, lat, lon)

            if dist < best_distance:
                best_distance = dist
                best_node = node

        return best_node

    def _extract_road_names(self, route_nodes: list[Any]) -> list[str]:
        roads = []

        for i in range(len(route_nodes) - 1):
            edge_data = self.graph.get_edge_data(route_nodes[i], route_nodes[i + 1])

            if not edge_data:
                continue

            for edge in edge_data.values():
                name = edge.get("name")

                if isinstance(name, list):
                    roads.extend(name)
                elif name:
                    roads.append(name)

        return list(dict.fromkeys(roads))

    @staticmethod
    def _validate_with_mappls(source_lat, source_lon, dest_lat, dest_lon):
        api_key = os.getenv("MAPPLS_ACCESS_TOKEN", "").strip()
        if not api_key:
            return None

        url = (
            "https://route.mappls.com/route/direction/route_traffic/driving/"
            f"{source_lon},{source_lat};{dest_lon},{dest_lat}"
        )

        try:
            response = requests.get(
                url,
                params={
                    "rtype": 0,
                    "steps": True,
                    "access_token": api_key,
                },
                timeout=8,
            )

            data = response.json()

            if data.get("code") != "Ok":
                return None

            route = data["routes"][0]

            roads = []
            for leg in route.get("legs", []):
                for step in leg.get("steps", []):
                    if step.get("name"):
                        roads.append(step["name"])

            return {
                "distance_m": route["distance"],
                "eta_min": route["duration"] / 60,
                "geometry": route.get("geometry"),
                "roads": list(dict.fromkeys(roads)),
            }

        except Exception as e:
            print("MAPPLS ERROR:", e)
            return None

    @staticmethod
    def _empty_plan(reason: str) -> dict:
        return {
            "best_diversion_distance_km": None,
            "best_diversion_eta_mins": None,
            "diversion_road_name": None,
            "alternate_roads": [],
            "route_coords": [],
            "geometry": None,
            "routing_status": reason,
            "routing_graph": None,
            "diversion_strategy": "Traffic Monitoring Only",
        }
