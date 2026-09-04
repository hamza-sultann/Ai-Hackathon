# Unified Stack Integration Walkthrough

**Repository**: `hamza-sultann/Ai-Hackathon`  
**Branch**: `integrate/full-stack`  
**Stack**: XGBoost + Isolation Forest + Multi-Agent Orchestration + FastAPI + React 18 / Vite / TailwindCSS

---

## 1. Executive Summary

This repository integrates all four core layers of the **Istikshaf (استکشاف) Grid Loss Intelligence System**:
1. **Machine Learning Core**: Track 1 (Monthly billing + PMT mass balance with XGBoost, Isolation Forest, and Isotonic Calibration) & Track 2 (Hourly interval feature generation and AMI prosumer analysis).
2. **Agentic Layer**: Multi-agent decision framework with confounder checking (solar, load shedding, zero-consumption), seasonal adjustments, audit logging, and automated deduplication guards.
3. **FastAPI Backend**: High-performance RESTful API exposing grid topology, investigation queues, automated job cards, model explanations, and on-demand localized field alerts.
4. **React / Vite Frontend**: Operations dashboard providing real-time telemetry, 3D grid topological explorer, TreeSHAP contribution breakdowns, bilingual Urdu/English field inspection cards, and pipeline comparison tools.

All components have been unified on branch `integrate/full-stack` with zero merge conflicts and 100% passing test suites across frontend and backend.

---

## 2. Branch Topology & Integration History

### Source Branches
- `origin/data-v2`: Core ML pipeline, dataset generation, feature engineering, probability calibration, and diagnostics.
- `origin/feature/agentic-layer`: Multi-agent orchestration loop (`agents/agent_dispatcher.py`, `agents/agent_loop.py`), case deduplication, and Urdu localization.
- `origin/Frontend`: React UI mockups and client components.
- `origin/feature/backend`: FastAPI backend (`backend/`), and connected frontend with Axios client and UI adjustments.

### Unified Integration Branch
- Branch `integrate/full-stack` was created from `origin/feature/agentic-layer` and cleanly merged with `origin/feature/backend`.
- Source branches (`data-v2`, `feature/agentic-layer`, `feature/backend`, and `Frontend`) remain intact and untouched on remote.

```
       origin/data-v2 ──┐
                        ▼
            feature/agentic-layer ──────────┐
                                            ▼
                                   integrate/full-stack (Unified Stack)
                                            ▲
            feature/backend ────────────────┘
                   ▲
            origin/Frontend
```

---

## 3. Architecture & Repository Layout

```
Ai-Hackathon/
├── agents/                             # Agentic loop & multi-agent routing
│   ├── agent_dispatcher.py             # Confounder checks, deduplication guard, Urdu translator
│   └── agent_loop.py                   # Batch dispatch loop, evaluation metrics, audit log
├── backend/                            # FastAPI REST API & analytics engine
│   ├── app/
│   │   ├── main.py                     # Application entrypoint & CORS middleware
│   │   ├── config.py                   # Automatic dataset discovery (backend/data vs data/)
│   │   ├── schemas.py                  # Pydantic models (with fieldAlertUrdu & safeguards)
│   │   ├── agents/dispatcher.py        # Backend agent dispatcher with LRU caching
│   │   ├── ml/scorer.py                # Cached model scoring & TreeSHAP driver
│   │   └── services/                   # Grid, comparison, and investigation services
│   ├── scripts/smoke.py                # 11-endpoint automated smoke test suite
│   └── requirements.txt                # Python backend dependencies (including deep-translator)
├── frontend/                           # React 18 + Vite + Tailwind UI
│   ├── src/
│   │   ├── lib/api/client.ts           # Axios client with mock fallback safeguards
│   │   ├── views/                      # Overview, Grid Explorer, Queue, Admin, Field
│   │   ├── components/                 # ECharts, Three.js 3D grid, dialogs, status badges
│   │   └── test/                       # Vitest test suite & mock setup
│   └── package.json                    # Frontend dependencies & scripts
├── data/                               # Synthetic grid CSV datasets (consumers, billing, feeders)
├── calibrate.py                        # Model probability calibration
├── features.py                         # Monthly & PMT feature engineering
├── run_pipeline.py                     # End-to-end ML training and calibration runner
├── audit_log.jsonl                     # Multi-agent audit records
└── README.md                           # Quick start guide
```

---

## 4. Key Technical Enhancements

### A. Dynamic Urdu Localization & Field Alerts
- Integrated `urdu_localization_agent` into [`backend/app/agents/dispatcher.py`](backend/app/agents/dispatcher.py).
- Uses `deep-translator` with an `@functools.lru_cache(maxsize=128)` and resilient local fallback dictionaries.
- Generates natural, action-oriented Urdu instructions for field squads (e.g., direct inspection steps for hook connections, meter bypassing, or CT/PT tampering).
- Populates `field_alert` (English) and `field_alert_urdu` (Urdu) in `RiskExplanationResponse` schemas in [`backend/app/schemas.py`](backend/app/schemas.py).

### B. Anti-Recidivism & Case Deduplication Safeguard (`sg-7`)
- Added `case_dedup_guard` and `recidivism_checker` to [`backend/app/agents/dispatcher.py`](backend/app/agents/dispatcher.py).
- Prevents redundant alerts and harassment by checking for open job cards within the last 30 days.
- Appends `sg-7: Case Deduplication Guard` to the pre-inspection safeguard checklist in the UI.

### C. Cross-Platform Windows UTF-8 Support
- Standardized `sys.stdout.reconfigure(encoding='utf-8')` across `agents/agent_dispatcher.py` and `agents/agent_loop.py` to ensure Urdu text streams cleanly on Windows consoles without `cp1252` encoding errors.

### D. Headless Frontend Testing Mocks
- Configured realistic mock responses in [`frontend/src/test/setup.ts`](frontend/src/test/setup.ts) for `apiClient.get` and mutating methods, allowing Vitest to validate components without requiring a running backend daemon.

---

## 5. Verification & Test Results

### 1. Frontend Test Suite (`npm test -- --run`)
```
 RUN  v3.2.7 D:/hackathon/Ai-Hackathon/frontend

 ✓ src/test/App.test.tsx (5 tests) 401ms

 Test Files  1 passed (1)
      Tests  5 passed (5)
   Start at  11:20:50
   Duration  4.25s
```

### 2. Frontend Production Build (`npm run build`)
```
vite v6.4.3 building for production...
transforming...
✓ 2745 modules transformed.
dist/index.html                     0.47 kB │ gzip:   0.30 kB
dist/assets/index-BfpUtMKS.css     49.83 kB │ gzip:   9.53 kB
dist/assets/index-CsSNf_lw.js   1,799.13 kB │ gzip: 561.42 kB
✓ built in 15.90s
```

### 3. Backend Smoke Test Suite (`python backend/scripts/smoke.py`)
```
200  GET  /api/health                              items=-
200  GET  /api/overview                            items=-
200  GET  /api/grid/feeders                        items=30
200  GET  /api/comparison/pipeline                 items=-
200  GET  /api/investigations                      items=200
200  GET  /api/job-cards                           items=10
200  GET  /api/field/overview                      items=-
200  GET  /api/field/jobs                          items=10
200  GET  /api/admin/data-sources                  items=5
200  GET  /api/admin/model-services                items=4
200  GET  /api/admin/audit                         items=16
      feeder F-07 -> 10 pmts
      pmt PMT-0061 -> 39 consumers
      investigations: 200
      200  /investigations/C-006421
      200  /investigations/C-006421/explanation
      200  /investigations/C-006421/monthly
      200  /investigations/C-006421/hourly
      top driver: CUSUM Structural Break
      created job JOB-2503 status=queued
      created card JC-2026-823
      finding submitted: {'success': True, 'message': 'Inspection findings recorded and queued for supervisor review.'}

ALL SMOKE CHECKS PASSED
```

### 4. Python ML Tests (`pytest test_features.py test_merge.py`)
```
============================= test session starts =============================
collected 4 items

test_features.py .                                                       [ 25%]
test_merge.py ...                                                        [100%]

============================== 4 passed in 4.20s ==============================
```

### 5. ML Pipeline Execution (`python run_pipeline.py`)
- Loaded 360,000 monthly billing records across 10,000 consumers.
- Computed physics mass balance against 100 PMTs and 30 Feeders.
- Trained XGBoost with out-of-fold Isolation Forest feature representations.
- Generated `output/eval.parquet` and calibrated decision surface in `final_calibrator.joblib`.

---

## 6. How to Run the Stack

### Step 1: Install Dependencies
```bash
# Python dependencies
pip install -r backend/requirements.txt
pip install xgboost shap pytest deep-translator

# Frontend dependencies
cd frontend
npm install --legacy-peer-deps
cd ..
```

### Step 2: Run Backend Server
```bash
cd backend
python run.py
# Server running at http://localhost:8000 (Swagger docs at http://localhost:8000/docs)
```

### Step 3: Run Frontend Application
```bash
cd frontend
npm run dev
# Application running at http://localhost:5173
```

### Step 4: Run Multi-Agent Decision Loop
```bash
python agents/agent_loop.py
```
