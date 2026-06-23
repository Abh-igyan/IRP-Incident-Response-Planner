from __future__ import annotations

from app.services.utils import normalize_text


HEAVY_VEHICLES = {"heavy_vehicle", "truck", "private_bus", "ksrtc_bus", "bmtc_bus", "bus", "lcv"}
HIGH_RISK_CAUSES = {"accident", "fire", "protest", "procession", "public_event", "vip_movement"}
LOW_RISK_CAUSES = {"pot_holes", "road_conditions", "vehicle_breakdown", "others", "debris"}
SMALL_VEHICLES = {"private_car", "taxi", "auto", "two_wheeler", "car"}


class SanityRuleEngine:
    def apply(
        self,
        row: dict,
        probability: float,
        global_mean_probability: float,
    ) -> tuple[float, list[str]]:
        adjusted = probability
        notes: list[str] = []
        event_cause = normalize_text(row.get("event_cause"))
        veh_type = normalize_text(row.get("veh_type"))
        priority = str(row.get("priority") or "").strip().lower()

        if priority == "high" and adjusted < global_mean_probability:
            adjusted += 0.02
            notes.append("Sanity check: high priority should not suppress closure risk")

        if row.get("authenticated") == 1 and adjusted < global_mean_probability * 0.8:
            adjusted += 0.015
            notes.append("Sanity check: authenticated reports kept from reducing risk too far")

        if event_cause == "accident" and veh_type in HEAVY_VEHICLES:
            adjusted += 0.06
            notes.append("Sanity check: accident with heavy vehicle increases closure likelihood")

        if veh_type in HEAVY_VEHICLES and event_cause not in {"pot_holes", "road_conditions"}:
            adjusted += 0.015
            notes.append("Sanity check: heavy vehicle presence slightly increases closure risk")

        if event_cause in HIGH_RISK_CAUSES:
            adjusted += 0.035
            notes.append("Sanity check: high-risk event cause increases closure risk")

        if event_cause in {"debris", "tree_fall"} and veh_type in HEAVY_VEHICLES and adjusted < 0.18:
            adjusted = min(0.32, adjusted + 0.05)
            notes.append("Sanity check: debris or obstruction with large vehicle needs moderate risk")

        if (
            event_cause in LOW_RISK_CAUSES
            and veh_type in SMALL_VEHICLES
            and row.get("is_peak_hour") != 1
            and adjusted > global_mean_probability
        ):
            adjusted -= 0.02
            notes.append("Sanity check: minor non-peak incident reduced toward monitoring risk")

        if event_cause in {"pot_holes", "road_conditions"} and adjusted > 0.55:
            adjusted -= 0.04
            notes.append("Sanity check: road-condition events capped from extreme closure risk")

        return max(0.01, min(0.98, adjusted)), notes
