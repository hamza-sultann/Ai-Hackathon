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

### 1. Run Track 1 (Monthly Billing Legacy Pipeline)
Track 1 processes the 10,000-consumer grid using monthly billing records, transformer energy balances, CUSUM break detection, and Platt-calibrated XGBoost.

```bash
# Step 1: Ingest CSVs, join hierarchy, and perform 60/20/20 stratified split
python data_assembly.py

# Step 2: Execute the full Track 1 ML Pipeline end-to-end
python run_pipeline.py
```
* **Performance:** Precision @ 0.50: **69.7%** (19.3× better than naive audit), Recall: **30.6%**, Solar False Positives: **0.00%**.

---

### 2. Run Track 2 (High-Frequency Smart Meter AMI Pipeline)
Track 2 simulates the 1-hour interval smart grid for the 2,000 residential pilot population, streams 51.8M readings to Parquet, extracts scale-invariant shape features, and benchmarks the uplift against Track 1.

```bash
# Step 1: Select the 2,000 AMI pilot population
python select_ami_population.py

# Step 2: Generate 51.8 Million 1-hour interval readings (streaming Parquet)
python generate_intervals.py

# Step 3: Stream-extract the 7 load curve features in batches (Memory-Safe)
python run_track2_features.py

# Step 4: Run the Smart Grid Uplift Evaluation Benchmark
python uplift_evaluation.py
```
* **Performance Uplift:** Peak Shaver Recall jumps from **10.6% ──► 58.3% (+47.8% Uplift)**, Precision rises by **+19.4 points** (29.9% ──► 49.3%), and overall recall more than doubles!

---

### 3. Run Automated Tests
```bash
pytest test_rewdp_templates.py test_generate_intervals.py test_features.py test_calibrate.py test_iso.py test_merge.py test_train.py -v
```

---

## 📚 Complete Technical Documentation
* [`SYSTEM_ARCHITECTURE_AND_ML_PIPELINE.md`](SYSTEM_ARCHITECTURE_AND_ML_PIPELINE.md): Full machine learning, feature math, calibration, TreeSHAP, and deployment architecture.
* [`track2-interval-design-and-build-plan.md`](track2-interval-design-and-build-plan.md): Complete Track 2 1-hour interval engine, archetype compatibility, and visual component designs.
* [`DATASETS_AND_PHYSICS_SPECIFICATION.md`](DATASETS_AND_PHYSICS_SPECIFICATION.md): Comprehensive grid physics, 14 consumer archetypes, and technical loss formulas.

