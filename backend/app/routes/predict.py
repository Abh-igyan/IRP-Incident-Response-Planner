from fastapi import APIRouter, Request

from app.schemas import IncidentRequest, PredictionResponse

router = APIRouter(prefix="", tags=["prediction"])


@router.post("/predict", response_model=PredictionResponse)
def predict_incident(payload: IncidentRequest, request: Request) -> dict:
    return request.app.state.predictor.predict(payload)


@router.get("/options")
def prediction_options(request: Request) -> dict:
    return request.app.state.predictor.options()
