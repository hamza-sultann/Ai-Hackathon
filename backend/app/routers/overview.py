from fastapi import APIRouter

from app.schemas import SystemOverview
from app.services.grid_service import system_overview

router = APIRouter(tags=["overview"])


@router.get("/overview", response_model=SystemOverview)
def get_overview() -> SystemOverview:
    return system_overview()
