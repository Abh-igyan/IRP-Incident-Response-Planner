from fastapi import APIRouter, Request

router = APIRouter(prefix="", tags=["analytics"])


@router.get("/analytics")
def get_all_analytics(request: Request) -> dict:
    return request.app.state.analytics_service.get_full_analytics_bundle()


@router.get("/analytics/summary")
def get_summary(request: Request) -> dict:
    return request.app.state.analytics_service.get_summary()


@router.get("/analytics/heatmap")
def get_heatmap(request: Request) -> dict:
    return {"heatmap": request.app.state.analytics_service.get_heatmap_data()}
