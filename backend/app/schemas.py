from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class IncidentRequest(BaseModel):
    event_type: str
    event_cause: str
    veh_type: str = "Unknown"
    priority: str = "High"
    authenticated: bool = True
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    incident_datetime: datetime


class ResourcePlan(BaseModel):
    officers: int
    barricades: int
    patrol_vehicles: int
    ambulance_required: bool
    crane_required: bool


class TrafficForecast(BaseModel):
    severity: str
    expected_delay_mins: float


class DerivedContext(BaseModel):
    corridor: str
    zone: str
    police_station: str
    hour: int
    dayofweek: int
    month: int
    is_weekend: int
    is_peak_hour: int


class PredictionResponse(BaseModel):
    impact_score: float
    impact_class: str
    closure_probability: float
    resource_plan: ResourcePlan
    traffic_forecast: TrafficForecast
    response_priority: str
    eta_target: str
    diversion_strategy: str
    diversion_plan: dict[str, Any]
    derived_context: DerivedContext
    model_status: str
    learning_insight: dict[str, Any]


class FeedbackRequest(BaseModel):
    incident: IncidentRequest
    prediction: dict[str, Any] | None = None
    actual_road_closure: bool | None = None
    actual_delay_mins: float | None = None
    notes: str | None = None


class FeedbackResponse(BaseModel):
    status: str
    feedback_id: int
