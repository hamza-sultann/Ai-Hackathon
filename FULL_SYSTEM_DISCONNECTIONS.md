# Complete System Audit: All Areas of Disconnection Across the Entire Stack

**Repository**: `hamza-sultann/Ai-Hackathon`  
**Branch**: `integrate/full-stack`  
**Scope**: In-depth audit of **all non-agentic disconnections** across Data, ML, Backend Services, and Frontend UI Views.

---

## 1. Executive Summary

Beyond the agentic layer disconnects (detailed in `AGENTIC_INTEGRATION_ISSUES.md`), a thorough audit of the entire repository reveals **9 additional major areas of disconnection**. 

These range from **51.8 million real hourly smart-meter readings being completely ignored** in favor of hardcoded mathematical curves, to **mocked admin inference endpoints**, **transient configurations**, **purely decorative 3D topology**, and **zero feedback loops** between field inspections and the ML models.

---

## 2. Master Disconnection Matrix

| # | Disconnected Area | Source Reality | Web App / Backend Reality | Severity |
| :- | :--- | :--- | :--- | :--- |
| **1** | **Hourly Smart Meter Telemetry (AMI)** | `interval_readings.parquet` contains **51,819,270 real hourly readings** (322 MB). | Backend code comment claims the data "isn't shipped with the repo" and **fakes a Gaussian/exponential bell curve** (`_diurnal_shape()`). | **CRITICAL** |
| **2** | **Track 2 Feature Engineering** | Root `track2_features.py` builds 7 AMI features (`midday_dip`, `tariff_boundary`, `daily_load_factor`, etc.). | `backend/app/ml/features.py` dropped 4 of the 7 features and only kept 3. | **HIGH** |
| **3** | **Pipeline Comparison (Track 1 vs Track 2)** | Root `uplift_evaluation.py` trains two distinct models (Monthly vs AMI) to measure precision/recall uplift. | Backend does not have a separate smart-meter model. It simply copies `probability` into `smart_meter_probability` if `is_ami == True`. | **HIGH** |
| **4** | **Pipeline Comparison UI Stats** | Real dataset has 2,000 AMI consumers (20.0% coverage). | `PipelineComparisonPage.tsx` displays **hardcoded JSX text: "68.4% coverage (6,840 / 10,000)"**, contradicting backend data. | **MEDIUM** |
| **5** | **3D Grid Topology Canvas** | Power grid has 30 Feeders, 100 PMTs, and geospatial locations in `feeders.csv` and `grid_service.py`. | `GridMeshCanvas.tsx` is a **purely cosmetic Three.js particle script** plotting 180 random floating sine-wave dots. | **MEDIUM** |
| **6** | **Model Training & Evaluation Data Leakage** | `run_pipeline.py` cleanly separates `train.parquet`, `calibrate.parquet`, and `eval.parquet`. | `backend/app/ml/scorer.py` trains on the **entire 360,000-row panel including the test month**, resulting in train/test target leakage. | **HIGH** |
| **7** | **Admin Live Inference Test Modal** | `AdminModelsPage.tsx` provides interactive sliders for load drop, off-peak ratio, PMT residual, etc. | `POST /api/admin/model-services/{id}/test` ignores user inputs and returns **hardcoded `0.912` and `"91.2%"`**. | **MEDIUM** |
| **8** | **Admin System Configuration Persistence** | `AdminConfigPage.tsx` allows admins to tune risk thresholds, SLA hours, and PMT loss limits. | `PATCH /api/admin/config` merely echos the request back without saving to SQLite, JSON, or modifying backend thresholds. | **MEDIUM** |


---

## 3. Deep-Dive of Non-Agentic Disconnections

### Disconnection 1: The 51.8 Million Real AMI Readings vs. Fabricated Gaussian Curve
- **The Ground Reality**: The root directory contains `interval_readings.parquet` (322 MB) containing **51,819,270 rows** of actual hourly smart meter readings (`consumer_id`, `timestamp`, `interval_kwh`) spanning 2022 to 2024.
- **What the Backend Does**: In `backend/app/services/investigation_service.py` line 204:
  ```python
  def get_hourly_readings(consumer_id: str) -> list[HourlyReading] | None:
      """Representative 24-hour profile for the analysis month.
      The raw 1-hour AMI stream isn't shipped with the repo, so this reconstructs a
      plausible diurnal curve from the consumer's monthly total and the Track-2
      aggregate features (peak flatline / night-drop), scaled to daily kWh.
      """
  ```
  The backend author assumed the data wasn't in the repository, so they wrote a synthetic Gaussian function (`_diurnal_shape()`) to fake daily curves.
- **Impact**: When an analyst clicks the "Hourly Smart Meter Pipeline" tab on the Consumer Investigation page, they are looking at synthetic mathematical curves instead of the real 51.8M hourly telemetry data.

---

### Disconnection 2: Pipeline Comparison is a Copy-Paste, Not Two Independent Pipelines
- **The Ground Reality**: In the project specification and `uplift_evaluation.py`, Track 1 is a **monthly billing model** and Track 2 is an **AMI high-frequency model**. The core premise is demonstrating how hourly smart meter data catches thefts that monthly billing misses.
- **What the Backend Does**: In `backend/app/ml/scorer.py` lines 145-147:
  ```python
  ami_mask = df["consumer_id"].isin(self.data.ami_consumer_ids)
  df["smart_meter_probability"] = np.where(ami_mask, df["probability"], 0.0)
  df["is_ami"] = ami_mask
  ```
  There is **no separate smart-meter model** in the backend. If a consumer has AMI, the backend copies the full model probability directly into `smart_meter_probability`.
- **Impact**: The "Pipeline Comparison" Venn diagram (`PipelineComparisonPage.tsx`) does not reflect two truly independent classifiers competing; it reflects one model filtered by whether a meter is AMI-capable.

---

### Disconnection 3: Hardcoded UI Claims vs. Real Backend Metrics
- **The Ground Reality**: `data/consumers.csv` has 10,000 consumers, of which exactly 2,000 have smart meters (20.0%). The backend `GET /api/comparison/pipeline` accurately returns `smart_meter_covered: 2000`.
- **What the Frontend Does**: In `frontend/src/views/PipelineComparisonPage.tsx` lines 54-55:
  ```tsx
  Smart-meter data is active on 68.4% of connections (6,840 / 10,000). For meters without AMI telemetry:
  "Smart-meter data is unavailable for this connection. Monthly analysis remains active."
  ```
  The text string `"68.4% of connections (6,840 / 10,000)"` is hardcoded in the JSX markup rather than reading from `comparison.coverageStats.smartMeterCovered`.
- **Impact**: The UI displays conflicting statistics: the summary card claims 68.4% coverage while the charts and backend report 20.0%.

---

### Disconnection 4: 3D Grid Topology Canvas is Purely Decorative
- **The Ground Reality**: The power grid dataset models a concrete hierarchy:
  - 30 Feeders (`F-01` to `F-30`)
  - 100 PMTs with capacities, line resistance, and service divisions
  - 10,000 consumer connections
- **What the Frontend Does**: In `frontend/src/components/3d/GridMeshCanvas.tsx`:
  ```typescript
  const particleCount = 180;
  for (let i = 0; i < particleCount; i++) {
    positions[i * 3] = (Math.sin(i * 0.4) * 7) + (Math.random() - 0.5) * 2;
    positions[i * 3 + 1] = (Math.cos(i * 0.3) * 4) + (Math.random() - 0.5) * 2;
    positions[i * 3 + 2] = (Math.sin(i * 0.5) * 3) + (Math.random() - 0.5) * 2;
  }
  ```
  The 3D grid does not use any feeder IDs, PMT IDs, connection edges, or substation data. It renders 180 randomized oscillating particles that respond to mouse movement.
- **Impact**: An operator navigating the "Grid Explorer" sees a decorative background rather than an interactive 3D topological map of the physical distribution network.

---

### Disconnection 5: Severe Train/Test Data Leakage in Backend Scorer
- **The Ground Reality**: The ML pipeline in root (`run_pipeline.py`) strictly enforces split integrity:
  - `output/train.parquet`: Months 1–24 (historical training)
  - `output/calibrate.parquet`: Months 25–30 (probability calibration)
  - `output/eval.parquet`: Months 31–36 (unseen evaluation)
- **What the Backend Does**: In `backend/app/ml/scorer.py`:
  ```python
  def _train(self) -> None:
      df = self._feature_frame()
      y = df["is_theft_ground_truth"].fillna(False).astype(int).to_numpy()
      self.model_monthly = _fit_calibrated(df[_MONTHLY_FEATURES], y)
      self.model_full = _fit_calibrated(df[MODEL_FEATURES], y)
  ```
  The backend trains its model on **the entire 360,000-row panel**, including month 36 (the active analysis month being investigated in the UI).
- **Impact**: The risk scores displayed on the dashboard are in-sample predictions. In machine learning operations, this is severe target leakage that gives an artificially optimistic view of model accuracy.

---

### Disconnection 6: Interactive Admin Inference Testing is a Mock Endpoint
- **The Ground Reality**: `AdminModelsPage.tsx` provides an interactive testing workbench:
  - Users can select a model (`Isolation Forest`, `XGBoost Classifier`, `TreeSHAP Engine`).
  - Users adjust sliders for `peakLoadDropPct`, `offPeakUsageRatio`, `pmtResidualDeltaKWh`, and `sanctionedLoadKW`.
  - Users click "Run Inference" to test model reaction.
- **What the Backend Does**: In `backend/app/routers/admin.py`:
  ```python
  @router.post("/model-services/{model_id}/test")
  def test_model_service(model_id: str, payload: dict | None = None) -> dict:
      if model_id == "ms-4":
          return {
              "modelId": model_id,
              "output": "TreeSHAP Computed",
              "riskContribution": 0.34,
              "topFeature": "Peak Tariff Load Ratio (6 PM–10 PM)",
              "latencyMs": 290,
          }
      return {
          "modelId": model_id,
          "predictionScore": 0.912,
          "calibratedProbability": "91.2%",
          "classification": "HIGH_ANOMALY_RISK",
          "latencyMs": 135,
      }
  ```
  The backend completely ignores `payload` and returns hardcoded numbers (`0.912`, `91.2%`).
- **Impact**: No matter what inputs an administrator types or slides, the test always outputs 91.2% risk.

---

### Disconnection 7: Admin Configuration is Non-Persistent
- **The Ground Reality**: `AdminConfigPage.tsx` allows system administrators to customize:
  - Calibrated Risk Threshold (%)
  - TreeSHAP Top Features Count
  - PMT Loss Alert Threshold (%)
  - Safeguard Mode
  - Batch Schedule Cron
- **What the Backend Does**: In `backend/app/routers/admin.py`:
  ```python
  @router.patch("/config")
  def update_config(payload: dict) -> dict:
      return {"success": True, "config": payload}
  ```
  The backend echoes the payload back. It does not write to SQLite or a config file, nor does it update `get_settings().risk_threshold`.
- **Impact**: When the admin refreshes the page, their changes disappear, and the backend continues using default thresholds regardless of user modifications.

---

### Disconnection 8: Closed Loop Failure (Field Inspections -> ML Ground Truth)
- **The Ground Reality**: In a real grid analytics system, field inspection findings are the ultimate ground truth. When a squad finds a direct hook or meter bypass, that verified outcome should update the database, calculate false positive rates, and trigger retraining.
- **What the Backend Does**: In `backend/app/routers/field.py`, when an inspector submits findings (`POST /api/field/jobs/{id}/findings`):
  ```python
  payload["jobCardId"] = job_card_id
  db.upsert_finding(payload)
  card["status"] = "Supervisor Review"
  db.upsert_job_card(card)
  ```
  It updates the job card status in SQLite, but:
  - It does NOT update `is_theft_ground_truth` in `monthly_readings.csv`.
  - It does NOT track the model's actual precision on inspected cases.
  - It does NOT trigger model calibration adjustments.
- **Impact**: The system is an open loop. The AI makes recommendations, but never learns from whether field inspectors confirmed or debunked its findings.

---

## 4. Synthesis: The Complete System Disconnection Blueprint

When combining both documents (`AGENTIC_INTEGRATION_ISSUES.md` and `FULL_SYSTEM_DISCONNECTIONS.md`), the repository breaks down into 4 isolated clusters:

```
┌────────────────────────────────────────┐       ┌────────────────────────────────────────┐
│  Cluster 1: Root ML & Evaluation       │       │  Cluster 2: Standalone CLI Agents      │
│  • run_pipeline.py (XGBoost + Calibr.) │       │  • agents/agent_loop.py (CLI loop)     │
│  • interval_readings.parquet (51.8M)   │       │  • agents/agent_dispatcher.py          │
│  • uplift_evaluation.py                │       │  • audit_log.jsonl                     │
│  • diagnose.py                         │       │                                        │
└───────────────────┬────────────────────┘       └───────────────────┬────────────────────┘
                    │                                                │
         ❌ Disconnected from API                         ❌ CLI-only, no API hooks
                    │                                                │
                    ▼                                                ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│  Cluster 3: FastAPI Backend Services                                                    │
│  • Re-implements its own Scikit-Learn HistGradientBoosting model (ignores Cluster 1)   │
│  • Reconstructs fake diurnal curve (ignores 51.8M real hourly readings in Cluster 1)   │
│  • POST /analyses is a sleep loop (ignores Cluster 2 agent loop)                        │
│  • Generates Urdu alert, but discards it on JobCard creation                            │
│  • PATCH /config and POST /data-sources/sync are empty mock stubs                      │
│  • POST /model-services/test returns hardcoded 0.912 dummy output                       │
└───────────────────────────────────────────┬─────────────────────────────────────────────┘
                                            │
                                 ❌ Partial / Dropped Fields
                                            │
                                            ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│  Cluster 4: React 18 / Vite Frontend Application                                        │
│  • Consumer Investigation Page ignores Urdu alert field                                 │
│  • Job Cards and Field Inspector screens are English-only (Urdu never reaches field)    │
│  • Pipeline Comparison Page has hardcoded 68.4% text (contradicting backend 20%)        │
│  • 3D Grid Topology Canvas is a cosmetic 180-particle sine wave (not real grid)         │
│  • Admin Audit Page shows seed UI logins; blind to automated agent routing decisions    │
│  • Admin Config Page loses edits on refresh (backend doesn't persist)                   │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```
