# Integration Session Status — 2026-09-04

**Branch**: `integrate/full-stack`
**Scope**: Wiring the three items requested (real pipeline, unified model, Urdu alert display), plus two regressions found and partially fixed along the way. This document is the honest state of that work — what's done, what's broken, what's still disconnected.

---

## 1. What was fixed and verified

### 1.1 `POST /api/analyses` now runs the real pipeline
- `backend/app/services/analysis_jobs.py` no longer fakes progress with `asyncio.sleep()`.
- A run now: drops the cached scorer/context → re-scores the full panel through the live model → walks the real agentic dispatch layer (`app/agents/dispatcher.py: run_dispatch`) over up to 40 flagged consumers, respecting the requested scope (Entire Grid / Feeder / PMT) → writes agent decisions into SQLite `audit_events` → advances progress on real stage completion.
- `AnalysisJob` gained `modelScored`, `flaggedCount`, `agentDecisions`, `auditEventsWritten`, `analysisMonth`; `AnalysisDrawer.tsx` shows them on completion.
- Verified via `backend/scripts/smoke.py` and manual round-trips.

### 1.2 Backend unified onto the real XGBoost + TreeSHAP pipeline
- New `backend/app/ml/xgb_scorer.py` loads the artifacts produced by root `run_pipeline.py` (`xgboost_model.json`, `final_calibrator.joblib`, `isolation_forest_final.joblib`, `iso_forest_imputer.joblib`), reuses the root `features.py` / `data_assembly.py` (not the backend's trimmed port), and computes real TreeSHAP per consumer.
- `app/ml/scorer.py: get_scorer()` auto-selects the real pipeline when artifacts + `xgboost`/`shap` are installed, else falls back to the original scikit-learn scorer (`ISTIKSHAF_SCORER=on|off|auto`).
- Had to retune priority tiers because the real calibrator's probabilities are compressed (max ~0.73 vs the old model's ~1.0): `investigation_service.HIGH_TIER=0.62`, `MEDIUM_TIER=0.50`, default `risk_threshold` 0.55→0.50.
- Caches the scored panel to `backend/.cache/xgb_scored.parquet`, invalidated by artifact/data-file mtime fingerprint.

### 1.3 `fieldAlertUrdu` now reaches the UI
- Added `fieldAlert`/`fieldAlertUrdu` to `RiskExplanation` and `JobCard` (backend schema + frontend TS types), plumbed through `CreateJobCardRequest` → `JobCardForm` → job-card creation → seed data.
- Rendered: bilingual card on `ConsumerInvestigationPage`, bilingual section on the printable `JobCardDetailPage`, Urdu-first box on `FieldJobDetailPage`.
- Verified end-to-end: explanation → job card → field jobs list all carry the Urdu text.

### 1.4 Regression found (by unifying the model) and fixed: "Smart Meter Only" was structurally impossible
- **Root cause**: unifying to one Track-1 model made `monthly_probability = probability` always, so for AMI consumers `smart_meter_probability` (a copy of `probability`) and `monthly_probability` became numerically identical — `smartMeterOnlyCount` on the Pipeline Comparison page could never be anything but `0`, and `pipelineAgreement`/`evidenceSource` could never show "Smart Meter Only" / "Smart Meter" at all. This was **introduced by this session's work** (item 1.2 above), not pre-existing in that absolute form.
- **Fix**: built `train_track2_model.py` (repo root) — a *servable* version of `uplift_evaluation.py`'s existing "Model 2" (Track-1 + Track-2 features). It reuses their exact feature lists and XGBoost hyperparameters verbatim, adds calibration via the existing `calibrate.calibrate_model()` (same function Track-1 already uses), and persists `xgboost_model_track2.json` / `final_calibrator_track2.joblib` / `isolation_forest_track2.joblib`. One deliberate correction (not a modeling change): `uplift_evaluation.py` computes its iso-forest feature with an inconsistent sign between train and eval; this script fits one isolation forest and scores everyone the same way.
- `xgb_scorer.py` now loads this second model when present and serves a genuinely independent `smart_meter_probability` for the ~2,000 AMI consumers. Verified: `smartMeterOnlyCount` is now non-zero (7 in the current run) and real divergent cases exist, e.g. consumer C-008761 shows 73.1% monthly risk vs 1.4% smart-meter risk.
- The Track-2 model is **optional** — if its artifacts aren't present, the backend silently falls back to the old (broken) behavior. Nothing else changes.

---

## 2. Known unresolved issue

### 2.1 Dedup guard / recidivism checker still don't work correctly — mid-fix, NOT verified working
- **Original bug found**: `case_dedup_guard` / `recidivism_checker` (in `backend/app/agents/dispatcher.py`) only read a frozen CLI-era file, `audit_log.jsonl`, which the live pipeline never writes to. So these safeguards were blind to the real pipeline's own decisions — running the exact same analysis twice in a row never triggered "Consolidated - Alert Active" even though it obviously should have.
- **Attempted fix**: redirected both functions to query the live SQLite `audit_events` table instead (`db.list_audit_events_for_object`, new function in `app/db.py`).
- **Current state**: when called directly/manually against a populated database, the functions return the correct answer (`True`/dedup detected). But when exercised through the actual `POST /api/analyses` → `analysis_jobs._execute()` flow — running the same analysis twice back-to-back — `consolidatedDuplicate` and `recidivist` still come back `0` both times, even though the exact same 40 consumers are processed in both runs and their audit rows are confirmed present in the database in between. This was reproduced with async `BackgroundTasks` **and** with a fully synchronous direct call to `_execute()` (no threading involved at all), so it is not a threading/async timing artifact — something else is preventing `case_dedup_guard`/`recidivism_checker` from seeing the rows during the actual dispatch loop, even though calling them standalone against the same database state works.
- **This needs further debugging before it can be called fixed.** Do not assume `_execute()`'s dedup/recidivism counts are trustworthy yet.

---

## 3. Disconnections still open (from the original two audit docs)

Everything below is **unchanged from before this session** unless noted.

| # | Disconnect | Status |
|---|---|---|
| Confounder suppression doesn't remove cases from the main queue | Still open — `list_investigations()` doesn't filter out `cancelled=True` cases; no "Actionable vs Suppressed" tab in the UI. |
| 51.8M real hourly AMI readings ignored | Still open — `investigation_service.get_hourly_readings()` still synthesizes a fake Gaussian diurnal curve. `interval_readings.parquet` (51.8M rows) doesn't exist locally and would need `generate_intervals.py` (~6 min) to produce it; `track2_features.csv` (the aggregate derived from it) is already committed and real. |
| Pipeline Comparison page hardcoded "68.4%" text | Still open — `frontend/src/views/PipelineComparisonPage.tsx` has a hardcoded string contradicting the real ~20% AMI coverage; not touched this session. |
| 3D Grid Topology is decorative | Still open — `GridMeshCanvas.tsx` still renders random sine-wave particles, not real feeder/PMT topology. |
| Admin "Run Inference" test endpoint | Still open — `POST /api/admin/model-services/{id}/test` still returns hardcoded `0.912` regardless of input. |
| Admin Config Page doesn't persist | Still open — `PATCH /api/admin/config` still just echoes the payload back. |
| Field inspection findings never feed back into ground truth / retraining | Still open — `POST /api/field/jobs/{id}/findings` updates the job-card status only. |
| Backend `features.py` (sklearn-fallback path) still only carries 3 of 7 Track-2 features | Still open for the **fallback** scorer. The real `xgb_scorer.py` path now merges all 7 (needed for the new Track-2 model), but `app/ml/features.py`'s `TRACK2_FEATURES` list (used only when `ISTIKSHAF_SCORER=off`) still has 3. |
| Two of the ML team's own scripts fight over `output/eval.parquet` | **Newly identified this session**, not fixed in the scripts themselves. `run_pipeline.py`'s last step overwrites `output/eval.parquet` with the feature-engineered version "so agent_loop.py can find the required columns" — but `uplift_evaluation.py` and the new `train_track2_model.py` both expect the *pristine* (pre-feature-engineering) version and crash with a `pmt_loss_rank_x`/`_y` merge-suffix collision otherwise. Current workaround: run `python data_assembly.py --input_dir data --output_dir output` immediately before running either evaluation script, then `python run_pipeline.py` again afterward if you need `agents/agent_loop.py`'s CLI to keep working. This conflict will recur every time both flows are used back-to-back — worth the ML side deciding on one canonical `eval.parquet` shape rather than two scripts overwriting each other's expectations. |

---

## 4. Artifacts this session produced (all gitignored, regenerate locally)

- `output/{train,calibrate,eval}.parquet` — via `python data_assembly.py --input_dir data --output_dir output`
- `xgboost_model.json`, `final_calibrator.joblib`, `isolation_forest_final.joblib`, `iso_forest_imputer.joblib` — via `python run_pipeline.py`
- `ami_consumer_ids.csv` — derived from `track2_features.csv` (already committed), not a new random selection
- `xgboost_model_track2.json`, `final_calibrator_track2.joblib`, `isolation_forest_track2.joblib` — via `python train_track2_model.py` (new script, needs the above two done first)
- Python env note: the backend runs on **Python 3.12** (`py -3.12`), not the default `python` (3.14, has nothing installed). `xgboost`, `shap`, `deep-translator` were installed into the 3.12 environment.

## 5. New file added this session

- `train_track2_model.py` (repo root) — see §1.4. Reuses `uplift_evaluation.py`'s exact Model 2 recipe + `calibrate.py`'s calibration function; adds persistence only.
