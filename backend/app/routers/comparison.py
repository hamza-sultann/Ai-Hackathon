from fastapi import APIRouter

from app.schemas import PipelineComparison
from app.services.comparison_service import pipeline_comparison

router = APIRouter(prefix="/comparison", tags=["comparison"])


@router.get("/pipeline", response_model=PipelineComparison)
def get_pipeline_comparison() -> PipelineComparison:
    return pipeline_comparison()
