from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import admin, analyses, comparison, field, grid, investigations, job_cards, overview

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-7s %(name)s: %(message)s")
log = logging.getLogger("istikshaf")


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.data.loader import get_data
    from app.db import init_db
    from app.ml.scorer import get_scorer
    from app.services.metrics import context
    from app.services.seed import seed_if_empty

    settings = get_settings()
    log.info("Data dir: %s", settings.data_dir)
    init_db()
    get_data()                # load CSVs
    get_scorer()              # train or load the risk model
    context()                 # warm cached aggregates
    seed_if_empty()           # demo job cards + audit trail
    log.info("Startup complete — API ready on /api")
    yield


app = FastAPI(title="Istikshaf Grid Loss API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for r in (overview, grid, investigations, analyses, comparison, job_cards, field, admin):
    app.include_router(r.router, prefix="/api")


@app.get("/api/health", tags=["meta"])
def health() -> dict:
    from app.services.metrics import context

    ctx = context()
    return {
        "status": "ok",
        "analysis_month": ctx.month_str,
        "flagged_consumers": int(ctx.latest["priority_flag"].sum()),
        "risk_threshold": ctx.threshold,
    }


@app.get("/", tags=["meta"])
def root() -> dict:
    return {"service": "istikshaf-backend", "docs": "/docs", "health": "/api/health"}
