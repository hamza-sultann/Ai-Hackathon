from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.schemas import AnalysisJob, StartAnalysisRequest
from app.services import analysis_jobs

router = APIRouter(prefix="/analyses", tags=["analyses"])


@router.post("", response_model=AnalysisJob)
async def start_analysis(req: StartAnalysisRequest, background: BackgroundTasks) -> AnalysisJob:
    job = analysis_jobs.create_job(req)
    background.add_task(analysis_jobs.run_job, job.id)
    return job


@router.get("/{job_id}", response_model=AnalysisJob)
def get_analysis(job_id: str) -> AnalysisJob:
    job = analysis_jobs.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return job
