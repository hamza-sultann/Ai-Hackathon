# Explainable AI for Grid Loss Detection

An end-to-end machine learning pipeline that detects non-technical loss (theft, tampering, and billing fraud) on the power grid. 

Built specifically for grid architectures that rely on monthly manual billing and PMT/feeder totalizer readings, this system identifies anomalies without requiring a smart-meter rollout. 

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
To generate the synthetic dataset and run the pipeline locally:
1. Clone this repository.
2. Run the data generation script to build the core tables (`consumers.csv`, `feeder_monthly.csv`, and `monthly_readings.csv`):
   ```bash
   python generate_data.py
