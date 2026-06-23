from __future__ import annotations


def recommend_officers(row: dict) -> int:
    officers = 2 if row["impact_class"] == "Low" else 4 if row["impact_class"] == "Medium" else 6
    if row["is_peak_hour"] == 1:
        officers += 2
    if row["event_cause"] in ["accident", "vehicle_breakdown", "tree_fall"]:
        officers += 2
    if row["event_cause"] in ["public_event", "procession", "protest"]:
        officers += 4
    if row["closure_probability"] > 0.7:
        officers += 2
    if row.get("has_end_coords", 0) == 1:
        officers += 1
    return int(officers)


def recommend_barricades(row: dict) -> int:
    barricades = 1 if row["impact_score"] < 45 else 3 if row["impact_score"] < 58 else 5
    if row["closure_probability"] > 0.75:
        barricades += 2
    if row.get("has_end_coords", 0) == 1:
        barricades += 1
    return int(barricades)


def response_priority(row: dict) -> str:
    if row["impact_class"] == "High":
        return "Immediate"
    if row["impact_class"] == "Medium":
        return "High"
    return "Normal"


def diversion_strategy(row: dict) -> str:
    prob = row["closure_probability"]
    if prob > 0.75:
        return "Full Diversion Required"
    if prob > 0.4:
        return "Partial Diversion Recommended"
    return "Traffic Monitoring Only"

def eta_target(priority: str) -> str:
    if priority == "Immediate":
        return "5 mins"
    if priority == "High":
        return "15 mins"
    return "30 mins"


def resource_plan(row: dict) -> dict:
    officers = recommend_officers(row)
    barricades = recommend_barricades(row)
    return {
        "officers": officers,
        "barricades": barricades,
        "patrol_vehicles": max(1, officers // 4),
        "ambulance_required": row["event_cause"] == "accident",
        "crane_required": row["event_cause"] in ["vehicle_breakdown", "tree_fall"],
    }
