# Istikshaf Backend

FastAPI service that connects the **frontend** (`Ai-Hackathon-frontend`) to the
**agentic / ML layer** (`Ai-Hackathon-agentic`). It serves the grid data,
runs the risk model, produces explainability payloads, and exposes the
analysis-job + job-card + field-finding workflow the UI expects.

```
frontend (React/Vite)  ──HTTP /api──▶  this service  ──▶  scikit-learn risk model
                                                     └──▶  agentic dispatcher (safeguards / alerts)
                                                     └──▶  CSV grid data (pandas)
```

## Requirements

* **Python 3.12** (the repo's `py -3.12`). 3.14 has no `pip`/packages here.
* Packages in `requirements.txt` — all already available in the 3.12 site-packages
  except nothing (FastAPI, pandas, scikit-learn, pyarrow, joblib, uvicorn are present).

```bash
py -3.12 -m pip install -r requirements.txt   # if starting from a clean env
```

## Run

```bash
cd backend
py -3.12 run.py            # or: py -3.12 -m uvicorn app.main:app --reload --port 8000
```

First boot trains the risk model (~2 min) and caches it to `.cache/risk_model.joblib`;
later boots load the cache in a second. Force a retrain with `ISTIKSHAF_FORCE_RETRAIN=true`
or `py -3.12 scripts/train.py`.

* API root: `http://localhost:8000/api`
* Interactive docs: `http://localhost:8000/docs`
* Health: `http://localhost:8000/api/health`
* Smoke test every endpoint: `py -3.12 scripts/smoke.py`

## Configuration (`.env`, see `.env.example`)

| Var | Default | Meaning |
|---|---|---|
| `ISTIKSHAF_DATA_DIR` | `./data` | folder holding the 5 CSVs |
| `ISTIKSHAF_CACHE_DIR` | `./.cache` | model artifact + SQLite DB |
| `ISTIKSHAF_ALLOWED_ORIGINS` | `http://localhost:5173,...` | CORS allow-list |
| `ISTIKSHAF_RISK_THRESHOLD` | `0.55` | calibrated prob. above which a consumer enters the investigation queue |
| `ISTIKSHAF_FORCE_RETRAIN` | `false` | retrain on startup |
| `ISTIKSHAF_ANALYSIS_MONTH` | latest in data | month the dashboard treats as "now" |

## Data

`backend/data/` holds a copy of the v3 dataset from `Ai-Hackathon-agentic`
(10,000 consumers, 300 PMTs, 30 feeders, 36 months, 2,000 AMI consumers):
`consumers.csv`, `feeder_monthly.csv`, `pmt_monthly.csv`, `monthly_readings.csv`,
`track2_features.csv`.

## What's real vs. modelled

| Real (from CSV) | Modelled / reconstructed |
|---|---|
| Consumer/PMT/feeder topology, monthly billed kWh, injected energy, uptime, arrears, prosumer flag, AMI flag, theft ground truth | Technical-vs-non-technical split of the metering gap (`NTL_SHARE_OF_GAP = 0.55`) |
| Track-2 aggregate load-shape features for AMI consumers | 24-hour interval curves (raw AMI stream isn't in the repo — rebuilt from monthly total + Track-2 features) |
| Isolation Forest + gradient-boosted classifier + sigmoid calibration, trained on the real labels | Feature *contributions* use a logistic surrogate, not TreeSHAP (no `shap` installed) |
| Safeguard / confounder logic ported from `agents/agent_dispatcher.py` | Cosmetic labels: feeder names, substations, addresses, meter IDs, tariff codes |

### Upgrading to the real XGBoost + TreeSHAP pipeline

`pip install xgboost shap`, add `app/ml/xgb_scorer.py` implementing the same
`RiskScorer` surface (`score_panel`, `latest_scores`, `explain`) backed by the
artifacts from `Ai-Hackathon-agentic/run_pipeline.py`, and point `get_scorer()`
at it. Nothing else changes.

## Endpoints (all under `/api`)

| Method | Path | Frontend service |
|---|---|---|
| GET | `/overview` | `overviewApi` |
| GET | `/grid/feeders`, `/grid/feeders/{id}`, `/grid/feeders/{id}/pmts`, `/grid/pmts/{id}`, `/grid/pmts/{id}/consumers` | `gridApi` |
| GET | `/investigations`, `/investigations/{id}`, `/investigations/{id}/explanation`, `/investigations/{id}/monthly`, `/investigations/{id}/hourly` | `investigationApi` |
| POST/GET | `/analyses`, `/analyses/{jobId}` | `analysisApi` |
| GET | `/comparison/pipeline` | `comparisonApi` |
| GET/POST | `/job-cards`, `/job-cards/{id}` (GET, PATCH) | `jobCardsApi` |
| GET | `/field/overview`, `/field/jobs`; GET/POST `/field/jobs/{id}/findings` | `fieldApi` |
| GET | `/admin/data-sources`, `/admin/model-services`, `/admin/audit` | `adminApi` |

## Wiring the frontend

Two changes in `Ai-Hackathon-frontend/frontend`:

1. The API stubs are at `src/routes/api/` but the services import `../lib/api/`.
   Move them: `src/routes/api/client.ts` → `src/lib/api/client.ts`,
   `src/routes/api/endpoints.ts` → `src/lib/api/endpoints.ts`.
2. `.env`:
   ```
   VITE_API_BASE_URL=http://localhost:8000/api
   VITE_USE_MOCK_API=false
   ```

`fetchWithMockFallback` still falls back to mock data per-call if the backend is
down, so the UI degrades gracefully.
