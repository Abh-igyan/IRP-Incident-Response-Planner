from __future__ import annotations

import json
import sqlite3

from fastapi import APIRouter

from app.schemas import FeedbackRequest, FeedbackResponse
from app.services.utils import DATA_DIR

router = APIRouter(prefix="", tags=["feedback"])


def init_feedback_db() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DATA_DIR / "feedback.sqlite3") as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                incident_json TEXT NOT NULL,
                prediction_json TEXT,
                actual_road_closure INTEGER,
                actual_delay_mins REAL,
                notes TEXT
            )
            """
        )


@router.post("/feedback", response_model=FeedbackResponse)
def save_feedback(payload: FeedbackRequest) -> dict:
    init_feedback_db()
    with sqlite3.connect(DATA_DIR / "feedback.sqlite3") as conn:
        cursor = conn.execute(
            """
            INSERT INTO feedback (
                incident_json,
                prediction_json,
                actual_road_closure,
                actual_delay_mins,
                notes
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                payload.incident.model_dump_json(),
                json.dumps(payload.prediction) if payload.prediction is not None else None,
                None if payload.actual_road_closure is None else int(payload.actual_road_closure),
                payload.actual_delay_mins,
                payload.notes,
            ),
        )
        feedback_id = int(cursor.lastrowid)
    return {"status": "stored", "feedback_id": feedback_id}
