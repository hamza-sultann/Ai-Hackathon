"""In-memory analysis-job store + a background runner that walks the pipeline
stages the frontend polls for.

The heavy work (feature engineering, training, scoring) already happened at
startup, so a "run" here re-scores against the live model and advances a
progress bar through the same stage names the UI expects.
"""
from __future__ import annotations

import asyncio
import random
from datetime import datetime, timezone

from app.schemas import AnalysisJob, StartAnalysisRequest
from app.services.metrics import context, reset_context

_STAGES: list[tuple[str, int]] = [
    ("validating_data", 15),
    ("calculating_pmt_balance", 35),
    ("scoring_anomalies", 55),
    ("calibrating_risk", 75),
    ("generating_explanations", 92),
    ("completed", 100),
]

_jobs: dict[str, AnalysisJob] = {}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_job(req: StartAnalysisRequest) -> AnalysisJob:
    job_id = f"JOB-{random.randint(1000, 9999)}"
    job = AnalysisJob(
        id=job_id,
        status="queued",
        progress_percentage=5,
        scope=req.scope,
        target_id=req.target_id,
        pipelines=req.pipelines,
        created_at=_now(),
    )
    _jobs[job_id] = job
    return job


def get_job(job_id: str) -> AnalysisJob | None:
    return _jobs.get(job_id)


async def run_job(job_id: str) -> None:
    job = _jobs.get(job_id)
    if job is None:
        return
    try:
        for status, pct in _STAGES:
            await asyncio.sleep(random.uniform(0.6, 1.4))
            job.status = status
            job.progress_percentage = pct
            if status == "scoring_anomalies":
                # refresh cached derivations so the new run is reflected everywhere
                reset_context()
                await asyncio.to_thread(context)
        job.completed_at = _now()
    except Exception as exc:  # pragma: no cover - defensive
        job.status = "failed"
        job.error_message = str(exc)
