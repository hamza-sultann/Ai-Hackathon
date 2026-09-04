# End-to-End System Analysis: Connecting the Agentic Layer, Backend, and Frontend

**Repository**: `hamza-sultann/Ai-Hackathon`  
**Branch**: `integrate/full-stack`  
**Scope**: Technical Audit of Connections, Disconnects, and Missing Links across ML, Agentic Layer, FastAPI Backend, and React Frontend.

---

## 1. Executive Summary & Root Problem

When inspecting each branch before the merge:
- `data-v2` built an offline Python data science pipeline (`run_pipeline.py`, `features.py`, XGBoost + SHAP).
- `feature/agentic-layer` built an offline CLI agent loop (`agents/agent_loop.py`, `agents/agent_dispatcher.py`) reading static Parquet/JSON and printing to stdout / appending to `audit_log.jsonl`.
- `feature/backend` created a standalone FastAPI server that re-implemented a lightweight Scikit-Learn model (`HistGradientBoosting` + logistic surrogate) inside `backend/app/ml/` so it could run without XGBoost/SHAP dependencies.
- `Frontend` created a React 18 / Tailwind dashboard designed around mock and REST contracts that did not incorporate the agentic layer's dynamic outputs (such as Urdu localization, agent routing states, or audit streams).

While the branches have been merged into `integrate/full-stack` without git syntax conflicts, **the system currently behaves as three semi-isolated silos**. 

This document details:
1. Exactly what each component does today.
2. The specific broken/missing connections between them.
3. How an operator or field worker actually experiences the system today vs. how they should.
4. A concrete architectural plan to truly wire the Agentic Layer into the Backend and Frontend.

---

## 2. Component-by-Component Reality Check

### Layer 1: Machine Learning & Feature Engineering
| File | Current Implementation | Is It Used by the Web App? |
| :--- | :--- | :--- |
| `run_pipeline.py` | Trains XGBoost, evaluates with Isolation Forest OOF scores, saves `xgboost_model.json` and `final_calibrator.joblib`. | **NO**. Completely disconnected from backend API. |
| `features.py` | Builds Track-1 monthly features and CUSUM structural break metrics. | **NO**. Backend has a duplicate port in `backend/app/ml/features.py`. |
| `backend/app/ml/scorer.py` | Trains an in-memory `HistGradientBoostingClassifier` and a linear surrogate at startup; caches to `.cache/risk_model.joblib`. | **YES**. This is what powers `/api/investigations`. |

> **Disconnect #1**: Any ML work or model retraining done via `run_pipeline.py` has **zero impact** on the FastAPI backend or the UI dashboard because the backend trains its own separate Scikit-Learn model.

---

### Layer 2: Agentic Decision Layer
| File / Agent | Current Implementation | Connection Status |
| :--- | :--- | :--- |
| `agents/agent_loop.py` | CLI batch script that iterates over `output/eval.parquet`, computes SHAP values, and calls `dispatch_agent()`. | **DISCONNECTED**. Never invoked by FastAPI, background workers, or the UI. |
| `agents/agent_dispatcher.py` | CLI dispatcher printing `--- ANALYST VIEW ---` and `--- FIELD ALERT ---` to terminal and writing to `audit_log.jsonl`. | **DISCONNECTED**. CLI only. |
| `backend/app/agents/dispatcher.py` | In-process Python functions (`run_dispatch`, `urdu_localization_agent`, `case_dedup_guard`, `recidivism_checker`). | **PARTIALLY CONNECTED**. Called on-demand when `/api/investigations/{id}/explanation` is requested. |
| `Confounder Agent` (`check_confound`) | Returns `cancelled = True` if solar prosumer or feeder uptime < 20%. | **INCOMPLETE LOGIC**. In backend, cancelled cases are still listed in the main `/api/investigations` queue. |
| `Seasonal Agent` (`seasonal_agent`) | Shifts probability threshold by $\pm 0.05$ based on summer/winter. | **NOT EXPOSED**. Hardcoded in CLI loop; backend queue uses static priority flags. |
| `Urdu Localization Agent` | Translates field alert text into Urdu via `deep-translator` with fallback. | **BACKEND ONLY**. Generates `field_alert_urdu`, but frontend does not render it anywhere. |
| `Audit Logger` | Appends JSON records to `audit_log.jsonl`. | **DISCONNECTED**. The web UI reads SQLite `audit_events`, not `audit_log.jsonl`. |

---

### Layer 3: FastAPI Backend & API Contracts
| Endpoint | What It Does | Gap / Issue |
| :--- | :--- | :--- |
| `POST /api/analyses` | Starts a new AI grid analysis job. | **MOCK SIMULATION**. `backend/app/services/analysis_jobs.py` runs a loop with `asyncio.sleep()` that fakes progress percentages. It does not invoke ML models or agents. |
| `GET /api/investigations` | Returns top 200 flagged consumers. | Flags are statically derived at startup. Does not filter out cases cancelled by the Confounder Agent. |
| `GET /api/investigations/{id}/explanation` | Returns SHAP contributions, safeguards, `fieldAlert`, and `fieldAlertUrdu`. | **WORKING ON API**, but frontend types and views ignore `fieldAlert` and `fieldAlertUrdu`. |
| `POST /api/job-cards` | Creates a new inspection job card in SQLite. | Does not store or transfer `fieldAlertUrdu` into the job card. |
| `GET /api/field/jobs/{id}` | Returns job card for field inspectors. | Contains only English `evidenceSummary`; no Urdu text available to field workers. |
| `GET /api/admin/audit` | Returns audit events from SQLite table. | Does not contain agent decisions (confound cancellations, soft warnings, repeat offender flags). |

---

### Layer 4: Frontend UI Views & User Workflows
| View | Intended User Flow | Actual Reality |
| :--- | :--- | :--- |
| `AnalysisDrawer.tsx` | Operator starts AI analysis with scope & pipeline options. | Connects to `POST /api/analyses`, which is just a fake progress bar. No actual model or agent runs. |
| `ConsumerInvestigationPage.tsx` | Analyst reviews AI findings, safeguards, and issues a job card. | Displays English summary and safeguards. **Does not display the generated field alert or Urdu alert**. Job card modal uses hardcoded placeholder defaults. |
| `JobCardDetailPage.tsx` | Printable official job card for field squad. | English-only. Contains hardcoded strings ("All 6 safeguards verified") rather than dynamic data. |
| `FieldJobDetailPage.tsx` | Field worker on mobile/tablet records findings. | Field worker cannot see the Urdu guidance generated by the Urdu localization agent. |
| `AdminAuditPage.tsx` | System admin reviews automated model and agent decisions. | Shows seed user logins and UI clicks; zero visibility into agentic loop decisions or audit log entries. |

---

## 3. Deep-Dive Analysis of the 5 Core Disconnects

### Disconnect 1: The "Dual Brain" Problem (Root ML vs Backend Scorer)
- **Root Cause**: The data team developed in the root directory with XGBoost, TreeSHAP, and Parquet. The backend team developed in `backend/` with Scikit-Learn `HistGradientBoostingClassifier` and Logistic Regression to avoid XGBoost C++ binary dependencies.
- **Symptom**: When a developer runs `python run_pipeline.py`, it generates `output/eval.parquet` and `xgboost_model.json`. But when `backend/run.py` starts, it reads `data/consumers.csv` and fits a completely different `HistGradientBoosting` model into `backend/.cache/risk_model.joblib`.
- **Consequence**: The frontend never sees the output of the Track 1 XGBoost model or true TreeSHAP values. It sees the Scikit-Learn surrogate model.

### Disconnect 2: The Agentic Loop is Offline CLI Only
- **Root Cause**: `agents/agent_loop.py` was created to be executed via `python agents/agent_loop.py` in a terminal. It writes to `temp_flagged_input.json`, prints formatted reports to stdout, and appends to `audit_log.jsonl`.
- **Symptom**: Neither the FastAPI backend nor the React frontend has any mechanism to trigger `agents/agent_loop.py`, query its state, or stream its output.
- **Consequence**: In production or demo, if someone clicks "Run AI Grid Analysis" in the UI, `agent_loop.py` is completely untouched.

### Disconnect 3: The Urdu Field Alert is Lost Between Backend and Field Inspector
- **Root Cause**: The backend API added `field_alert_urdu` to `RiskExplanation` in `backend/app/schemas.py`. However:
  1. In `frontend/src/types/index.ts`, `fieldAlert` and `fieldAlertUrdu` were never declared in the TypeScript interface.
  2. `ConsumerInvestigationPage.tsx` does not display `explanation.fieldAlertUrdu`.
  3. When an analyst clicks "Create Inspection Job-Card", the form (`JobCardForm.tsx`) only passes `explanation.summaryText` (English).
  4. The `JobCard` entity (both in backend `schemas.py` and frontend `types/index.ts`) has no field for Urdu alerts.
- **Consequence**: The Urdu translation agent—designed specifically for Pakistani field crews—never reaches the field crew screen (`FieldJobDetailPage.tsx`) or the printed job card (`JobCardDetailPage.tsx`).

### Disconnect 4: Confounder "Cancellation" Does Not Actually Suppress Alerts
- **Root Cause**: In `agents/agent_dispatcher.py`, `check_confound()` prints `"Alert was Cancelled by Confound Agent"` and skips dispatching to the field.
- **Symptom in Backend**: In `backend/app/agents/dispatcher.py`, `run_dispatch()` sets `cancelled = True` and writes an analyst summary explaining the cancellation. But `backend/app/services/investigation_service.py` still returns this consumer in `list_investigations()`.
- **Consequence**: An analyst viewing `/analyst/investigations` still sees the consumer in the queue with a High/Medium priority badge, rather than seeing the case filtered out, marked as "Suppressed by Confound Agent", or moved to a separate "Suppressed" tab.

### Disconnect 5: Two Isolated Audit Logs
- **Root Cause**: `agents/agent_dispatcher.py` logs to `audit_log.jsonl` with schema:
  `{ timestamp, consumer_id, calibrated_probability, shap_rationale, routing_decision }`.
  Meanwhile, FastAPI logs to SQLite `audit_events` with schema:
  `{ id, actor, timestamp, action, object_id, result }`.
- **Consequence**: The frontend Admin Audit Trail (`AdminAuditPage.tsx`) only reads SQLite `audit_events`. None of the agent actions (`Cancelled by Confound Agent`, `Sent Soft Warning SMS`, `Consolidated - Alert Active`) appear on the Admin Audit screen.

---

## 4. Operational Walkthrough: What Happens Today vs What Should Happen

### Scenario: An anomalous drop occurs on consumer C-006421 (Registered Solar Prosumer)

#### What Happens Today:
1. **Model Scoring**: Backend scores C-006421 as High Risk (probability 100%) due to consumption drop.
2. **Investigation Queue**: C-006421 appears in the UI Investigation Queue as a top priority target.
3. **Analyst Inspection**: Analyst clicks C-006421. The backend calls `run_dispatch()`, which identifies that `is_registered_solar_prosumer == True` and sets `cancelled = True`.
4. **UI Display**: The UI displays the case with `Safeguards: Action Required` (because solar is flagged). The analyst sees the TreeSHAP chart showing the drop.
5. **Job Card Creation**: The analyst can still click "Create Job Card", which creates a job card with generic English text.
6. **Field View**: The field squad receives the job card in English with no Urdu translation and no notice that this was cancelled by the confounder agent.
7. **Audit Trail**: Nothing is logged to the Admin Audit Trail.

#### What Should Happen:
1. **Agent Pipeline Execution**: During analysis, the **Confounder Agent** evaluates C-006421 before it enters the active queue.
2. **Auto-Suppression**: Because legitimate net-metering is verified, the Confounder Agent suppresses the alert and transitions status to `Suppressed - Confound Factor (Solar Prosumer)`.
3. **Queue Segmentation**: In the UI, the Investigation Queue shows:
   - Tab 1: **Actionable Queue** (Clean, unconfounded theft targets).
   - Tab 2: **Suppressed / Confounded** (Transparently showing why the agent cancelled them).
4. **Field Alert Delivery**: For non-suppressed cases, the **Urdu Localization Agent** generates the exact Urdu operational warning.
5. **Job Card Sync**: The job card automatically inherits both English and Urdu field alerts, printing bilingual job orders.
6. **Unified Audit**: The Confounder Agent's suppression rationale is logged directly into the system audit trail visible on the Admin screen.

---

## 5. Architectural Remediation Plan (Future Implementation)

To transform these four branches into a cohesive, production-grade system, the following 5 integration bridges must be established:

### Bridge 1: Unified ML Pipeline Engine
- Standardize the backend scorer (`backend/app/ml/scorer.py`) to directly load the production artifacts (`xgboost_model.json`, `final_calibrator.joblib`, and `iso_forest_imputer.joblib`).
- When a user clicks "Run Analysis" in the frontend, the backend should run the unified feature scoring pipeline rather than a mock delay.

### Bridge 2: Real Agent Loop Integration via Background Tasks
- Replace `backend/app/services/analysis_jobs.py`'s `asyncio.sleep()` mock with an asynchronous execution of the agent loop:
  - Stage 1: Feature engineering & mass balance calculation.
  - Stage 2: Isolation Forest & XGBoost calibrated scoring.
  - Stage 3: Confounder Agent check (auto-suppress solar & low uptime).
  - Stage 4: Deduplication & Recidivism Agent check (check against open job cards).
  - Stage 5: Urdu Localization Agent generation for all approved flags.
  - Stage 6: Audit logging into SQLite `audit_events`.

### Bridge 3: Full-Stack Urdu Support
- Update `frontend/src/types/index.ts`:
  - Add `fieldAlert?: string` and `fieldAlertUrdu?: string` to `RiskExplanation`.
  - Add `fieldAlertUrdu?: string` to `JobCard`.
- Update `ConsumerInvestigationPage.tsx`:
  - Add a "Field Warning (Urdu / English)" card displaying the generated bilingual alert.
- Update `JobCardForm.tsx` & `backend/app/schemas.py`:
  - Include `fieldAlertUrdu` in the job card creation schema so field squads see Urdu on their mobile screens and PDF printouts.

### Bridge 4: Queue Status Filtering (Actionable vs Suppressed)
- In `backend/app/services/investigation_service.py`, partition investigations into:
  - `Actionable`: Verified flags passed by Confounder and Deduplication agents.
  - `Suppressed`: Cases auto-cancelled by Confounder Agent (prosumer solar, grid blackout).
- In `frontend/src/views/AnalystOverviewPage.tsx` & `InvestigationsQueuePage.tsx`, provide quick filter tabs (`Actionable`, `Suppressed by Agent`, `All`).

### Bridge 5: Unified Audit Stream
- In `backend/app/agents/dispatcher.py`, whenever an agent takes an action (Confounder cancels, Soft Warning SMS sent, Duplicate alert consolidated, Recidivist flagged), write directly to `db.add_audit_event()`.
- This immediately surfaces all automated agent decisions inside the frontend's `AdminAuditPage.tsx`.

---

## 6. Summary Matrix

| Integration Aspect | Current State | Target Connected State |
| :--- | :--- | :--- |
| **Model Serving** | Backend trains its own Scikit-Learn model; ignores XGBoost artifacts. | Backend loads and serves the calibrated XGBoost + TreeSHAP pipeline. |
| **Agent Execution** | Offline CLI script (`agents/agent_loop.py`) printing to terminal. | Asynchronous service triggered by backend API & UI drawer. |
| **Urdu Localization** | Backend computes Urdu string; Frontend ignores and discards it. | Rendered in Investigation View, Job Card, and Field Inspector UI. |
| **Confounder Decisions** | Flags `cancelled=True` internally, but still leaves case in queue. | Automatically routes cases to "Suppressed by Confounder" queue tab. |
| **Audit Logging** | Written to disconnected `audit_log.jsonl`. | Written to SQLite and displayed live in Admin Audit Trail. |
