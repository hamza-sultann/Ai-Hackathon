# Explainable AI for Grid Loss Detection

An end-to-end machine learning pipeline that detects non-technical loss (theft, tampering, and billing fraud) on the power grid. 

Built specifically for grid architectures that rely on monthly manual billing and PMT/feeder totalizer readings, this system identifies anomalies without requiring a smart-meter rollout. 

> [!NOTE]
> **Full Stack Integration**: For a comprehensive architectural overview, branch topology, test verification results, and multi-agent enhancements, see [INTEGRATION_WALKTHROUGH.md](INTEGRATION_WALKTHROUGH.md).

## 🧠 How It Works
This project uses a stacked two-model architecture:
1. **Isolation Forest (Unsupervised):** Scans engineered features for "unknown unknowns" and abnormal consumption patterns, generating an out-of-fold anomaly score.
2. **XGBoost (Supervised):** Acts as the primary decision-maker, using the anomaly score alongside physics-based signals (like feeder-level energy gaps) to classify theft.

## ⚖️ Fairness & Confounder Controls
To ensure innocent consumers aren't wrongfully flagged, the pipeline explicitly accounts for:
* **Load Shedding:** Feeder-wide outages are factored in so they aren't mistaken for coordinated theft.
* **Prosumers (Solar/Net-Metering):** Legitimate drops in grid consumption due to registered rooftop solar are filtered out to prevent false positives.
* **Poverty Bias:** Arrears are tracked but kept as a secondary feature to avoid conflating debt with theft.

## 🔍 Exact Explainability
No flag reaches a field inspector without a reason. The pipeline uses **TreeSHAP** to attach exact, human-readable explanations to every alert (e.g., *"Usage dropped 60% vs. expected baseline while feeder-level loss rose 18% this month."*).

## 🚀 Getting Started

### 1. Environment Setup

```bash
# Python dependencies
pip install -r backend/requirements.txt
pip install xgboost shap pytest deep-translator

# Frontend dependencies
cd frontend
npm install --legacy-peer-deps
cd ..
```

### 2. Machine Learning Pipeline & Agentic Layer

Run the full end-to-end model pipeline (data assembly, feature engineering, Isolation Forest, XGBoost, probability calibration, and SHAP explanations):
```bash
python run_pipeline.py
```

Trigger the multi-agent decision loop (confound checks, seasonal adjustment, deduplication, Urdu localized field alerts, and audit logging):
```bash
python agents/agent_loop.py
```

### 3. FastAPI Backend

Start the backend API server (runs on `http://localhost:8000` with interactive docs at `/docs`):
```bash
cd backend
python run.py
```
Or run the automated backend smoke test suite:
```bash
python scripts/smoke.py
```

### 4. React Frontend

Start the Vite development server (runs on `http://localhost:5173`):
```bash
cd frontend
npm run dev
```
To create a production build:
```bash
npm run build
```
