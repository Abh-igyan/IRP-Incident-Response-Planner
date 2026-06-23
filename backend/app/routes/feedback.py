from __future__ import annotations

from fastapi import APIRouter, Request

from app.schemas import FeedbackRequest, FeedbackResponse
from app.services.feedback_learning import FeedbackLearningService

router = APIRouter(prefix="", tags=["feedback"])
learning_service = FeedbackLearningService()


def init_feedback_db() -> None:
    learning_service.init_db()
    learning_service.refresh()


@router.post("/feedback", response_model=FeedbackResponse)
def save_feedback(payload: FeedbackRequest, request: Request) -> dict:
    feedback_id = learning_service.record_feedback(payload, request.app.state.predictor)
    request.app.state.predictor.learning_service.refresh()
    return {"status": "stored_and_learned", "feedback_id": feedback_id}


@router.get("/feedback/summary")
def feedback_summary() -> dict:
    return learning_service.summary()
