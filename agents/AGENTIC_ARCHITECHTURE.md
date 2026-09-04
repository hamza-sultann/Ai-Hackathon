# ⚡ Agentic Layer: Explainable Grid-Loss & Theft Detection

## 🎯 System Overview
The **Agentic Layer** for the electricity theft detection system intercepts raw ML model outputs (Isolation Forest → XGBoost, calibrated) and transforms them into explained, verified, and correctly-routed actions rather than black-box alerts.

## 🔄 The Pipeline Architecture
1. **Feature Engineering** (`scripts/features.py`) 
2. **Ensemble Scoring** (Isolation Forest + XGBoost + Calibrator)
3. **Orchestrator** (`agent_loop.py`): The scheduler loading models, filtering anomalies by threshold, and dispatching per consumer.
4. **Dispatcher** (`agent_dispatcher.py`): The per-consumer agent chain handling confounds, recidivism, deduplication, localization, and audit logging.
5. **Output**: Analyst Dashboard (`/api/logs`), Field Crew SMS, or Field Feedback.

## 🤖 Agent Roster & Status
All core agents and tools are fully implemented:

| Agent | Responsibility | Status |
| :--- | :--- | :--- |
| **Confound Checker** | Cancels alerts if the consumer is a registered prosumer or if feeder uptime is abnormally low. | ✅ Implemented |
| **Soft-Warning Agent** | Sends direct-to-consumer SMS nudges for mid-confidence flags (0.65–0.70). | ✅ Implemented |
| **Dual-Router** | Splits confirmed flags into a detailed Analyst View (SHAP) and a short Field Alert (SMS). | ✅ Implemented |
| **PII/Privacy Agent** | Masks consumer IDs before outbound transmission. | ✅ Implemented |
| **Audit Logger** | Writes routing decisions and SHAP rationales to an append-only log for compliance. | ✅ Implemented |
| **Report Generator** | Converts SHAP feature attributions into plain-language field reports. | ✅ Implemented |
| **Recidivism Checker** | Flags repeat offenders and boosts effective priority via investigation log tracking. | ✅ Implemented |
| **Case Dedup Guard** | Skips re-dispatching a consumer already under active investigation. | ✅ Implemented |
| **Seasonal Agent** | Adjusts the flagging threshold dynamically based on the current month. | ✅ Implemented |
| **Urdu Localization** | Translates outgoing SMS alerts into natural Roman Urdu. | ✅ Implemented |

## 🔌 Frontend Integration Note
Outputs from these agents stream to the frontend via the FastAPI endpoint:
* **Endpoint:** `GET /api/logs`
* **Contract:** Refer to `API_DOCS.md` for the exact JSONL payload structure.