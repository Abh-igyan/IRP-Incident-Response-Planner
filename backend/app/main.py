from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.routes.analytics import router as analytics_router
from app.routes.feedback import init_feedback_db, router as feedback_router
from app.routes.predict import router as predict_router
from app.services.predictor import IncidentPredictor
from app.services.analytics_service import AnalyticsService
from app.services.utils import APP_DIR


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.predictor = IncidentPredictor()
    app.state.analytics_service = AnalyticsService()
    init_feedback_db()
    yield


app = FastAPI(
    title="Traffic Incident Response Planning",
    description="AI-assisted traffic closure, impact, resources, and diversion planning for Bengaluru incidents.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = APP_DIR / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.include_router(analytics_router)
app.include_router(predict_router)
app.include_router(feedback_router)

analytics_static_dir = APP_DIR.parent.parent / "analytics"
if analytics_static_dir.exists():
    app.mount("/analytics", StaticFiles(directory=analytics_static_dir, html=True), name="analytics_files")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(static_dir / "index.html")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
