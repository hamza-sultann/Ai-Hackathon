# Track 2 Design & Implementation Architecture — 1-Hour Smart Meter (AMI) Interval Engine
**A High-Frequency Streaming, Parquet-Backed Architecture for Non-Technical Loss (NTL) Detection**

---

## Executive Summary & Positioning

**Positioning:** Track 2 is **not a separate or detached dataset**. Track 2 disaggregates a designated pilot subset of Track 1's existing consumers (`has_ami = True`, 2,000 residential consumers) into realistic 1-hour load curves, grounded in empirical Pakistani residential load research (REWD-P). Theft signatures are injected at the physical time-of-day (e.g. evening peak tariff hours) rather than spread evenly across the monthly billing cycle.

* **Same `consumer_id`, same PMT, same archetype, same monthly ground truth.**
* **Dedicated High-Frequency Storage:** `interval_readings.parquet` (51.8 Million timestamped hourly readings, 307.5 MB Snappy compressed).
* **Scale-Invariant Feature Extraction:** Aggregates back to `(consumer_id, month)` in `track2_features.csv` (72,000 rows, 5 MB).
* **Unified Downstream AI:** Merges into the exact same XGBoost + Platt Calibration + SHAP decision pipeline.

---

## 1. Population Design & Storage Architecture

In developing power sectors like Pakistan, DISCOs (LESCO, K-Electric, IESCO) do not install smart meters for 100% of consumers overnight. They roll out in **phased pilot programs** (e.g., the Asian Development Bank AMI rollout):
* **Track 1 Grid Universe (100% of Grid — 10,000 Consumers):**
  * `data/consumers.csv`: Metadata across all 30 Feeders and 300 PMTs (includes `has_ami` boolean).
  * `data/monthly_readings.csv`: 360,000 monthly readings (1 reading/month per consumer across 36 months).
  * `data/pmt_monthly.csv` & `data/feeder_monthly.csv`: Grid transformer energy balances, ambient temperatures, and feeder uptimes.
* **Track 2 Smart Meter Pilot (20% of Grid — 2,000 Residential Consumers):**
  * `ami_consumer_ids.csv`: 2,000 randomly selected residential consumer IDs representing a statistically significant cross-section ($N=2,000$, margin of error $<2\%$ at $99\%$ confidence).
  * `interval_readings.parquet`: 24 readings/day $\times$ 36 months $\times$ 2,000 consumers = **51,819,270 hourly rows**.
  * For every consumer-month, physical energy conservation is preserved: $\sum_{h} \text{interval\_kwh} \equiv \text{billed\_units\_kwh}$.

**Scope:** Residential AMI pilot. Grounded in REWD-P (60 real Pakistani households across 6 cities). Commercial and industrial interval modeling is slated as roadmap pending real-world industrial telemetry data.

---

## 2. Archetype Compatibility & Structural Attack Elimination

A critical insight for utility executives and judges: **Smart meters do not just detect theft better—they structurally eliminate several legacy fraud vectors entirely.**

| Archetype | Compatible with AMI? | Attack Vector & Smart Meter Impact |
|---|:---:|---|
| `peak_hour_shaver` | ✅ **Yes (Showcase)** | **Primary Target:** Evening peak bypass (6–10 PM). Completely invisible monthly (~6% drop); glaringly obvious at 1-hour interval resolution. |
| `nighttime_ac` | ✅ **Yes** | **Summer Overnight Bypass:** 11 PM–5 AM AC theft. Captured directly via nocturnal drop indices. |
| `fixed_shunt` | ✅ **Yes** | **Hardware Shunt:** 50% constant reduction across all 24 hours. |
| `kunda` | ✅ **Yes** | **Direct Physical Tap:** Severe 90%+ flatline across all 24 hours. |
| `solar_prosumer` | ✅ **Yes (Non-theft)** | **Duck Curve Protection:** Midday solar generation (10 AM–3 PM) creates a distinct midday trough, cleanly separating solar prosumers from evening thieves. |
| `seasonal_traveler` | ✅ **Yes (Non-theft)** | **Confounder:** 1–3 month vacation blip with near-zero draw across all hours. |
| `efficient_upgrade` | ✅ **Yes (Non-theft)** | **Confounder:** Permanent downward step drop from Inverter AC / LED installations. |
| `vacant` / `standard` | ✅ **Yes (Non-theft)** | Standard baseline and standby phantom loads. |
| `collusion` | ❌ **Eliminated** | **Structurally Eliminated:** Smart meters transmit automated digital telemetry over cellular/GPRS. No human meter reader visits the home $\rightarrow$ bribery vector is eradicated. |
| `gradual_slowdown` | ❌ **Eliminated** | **Structurally Eliminated:** Solid-state digital meters have no rotating mechanical aluminum disc to tamper with or tilt. |
| `intermittent_hookup` | ❌ **Eliminated** | **Structurally Eliminated:** Mechanical terminal disconnection is automatically flagged by smart meter tamper sensors. |
| `slab_defender` | ⚠️ **Excluded** | Analog billing slab manipulation does not map cleanly to automated automated interval reporting. |

---

## 3. High-Frequency Diurnal Engine Physics (`rewdp_templates.py`)

Every 24-hour daily curve is synthesized from base appliance draw plus two Gaussian load peaks matching Pakistani daily routines:

$$P(h) = \text{base} + A_{\text{morning}} \cdot \exp\left(-\frac{(h - \mu_{\text{m}})^2}{2\sigma_{\text{m}}^2}\right) + A_{\text{evening}} \cdot \exp\left(-\frac{(h - \mu_{\text{e}})^2}{2\sigma_{\text{e}}^2}\right)$$

* **Morning Peak ($\mu_{\text{m}} \approx 7\text{:}30\text{ AM}$ weekday, $9\text{:}00\text{ AM}$ weekend):** Breakfast preparation, electric water geysers, morning school/work preparation.
* **Evening Peak ($\mu_{\text{e}} \approx 8\text{:}00\text{ PM}$, 6:00 PM – 10:00 PM):** Families gathered at home, dinner cooking, lighting, television, and heavy summer air conditioning coinciding with **NEPRA's official Time-of-Use (TOU) peak tariff window**.
* **Seasonal Climatic Coupling:**
  * **Summer ($>30^\circ\text{C}$):** Elevated overnight base load (11:00 PM – 5:00 AM) representing bedroom ACs and ceiling fans running all night.
  * **Winter ($<22^\circ\text{C}$):** Low overnight load, elevated morning load from water geysers and room heaters.
* **Micro-Confounders:**
  * **AC Compressor Cycling:** Random duty-cycle modulation (0.80x–1.25x) during summer afternoons (12:00–22:00).
  * **Winter Geyser Spikes:** 40% chance of 2.0x–3.5x spikes during morning bathing hours (06:00–08:00).
  * **Solar Duck Curve:** Solar net-metering prosumers experience a 70–95% drop specifically during sunshine hours (10:00 AM – 3:00 PM).
  * **Cellular Packet Loss:** 1.5% random missing readings (`NaN`) simulating telemetry communication dropouts.
  * **AR(1) Noise Autocorrelation:** $\epsilon_t = 0.60 \cdot \epsilon_{t-1} + \mathcal{N}(0, 0.03)$ ensuring load is temporally continuous.

---

## 4. Complete Model Architecture & ML Engine

Track 1 and Track 2 feed into a **unified enterprise machine learning pipeline**:

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                     UNIFIED MODEL ARCHITECTURE                                         │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘

 [ Track 1: Monthly Features (12 cols) ]          [ Track 2: 1-Hour Interval Features (7 cols) ]
  • cusum_max_deviation                            • peak_offpeak_ratio
  • months_since_detected_break                    • peak_window_flatline_fraction
  • fixed_baseline_deviation                       • midday_dip_index
  • pmt_loss_rank                                  • nighttime_drop_index
  • usage_deviation                                • daily_load_factor
  • peer_deviation                                 • flatline_fraction
  • seasonal_residual                              • tariff_boundary_alignment_score
  • rolling_trend_3mo                              
  • arrears_ratio                                  
  • feeder_uptime_adj_deviation                    
  • prosumer_gated_usage_deviation                 
  • pmt_loss_delta_pct                             
            │                                                            │
            └──────────────────────────────┬─────────────────────────────┘
                                           │
                                           ▼
                       ┌───────────────────────────────────────┐
                       │ Unified Feature Matrix                │
                       │ 360,000 rows (Legacy: Track 2 = NaN)  │
                       └───────────────────┬───────────────────┘
                                           │
                                           ▼
                       ┌───────────────────────────────────────┐
                       │ Out-of-Fold Isolation Forest Scorer   │
                       │ 5-Fold GroupKFold by consumer_id      │
                       │ Appends: iso_forest_oof_score         │
                       └───────────────────┬───────────────────┘
                                           │
                                           ▼
                       ┌───────────────────────────────────────┐
                       │ Extreme Gradient Boosted Trees        │
                       │ (XGBClassifier)                       │
                       │ • scale_pos_weight = 11.5             │
                       │ • eval_metric = 'aucpr'               │
                       │ • max_depth = 5, n_estimators = 300   │
                       └───────────────────┬───────────────────┘
                                           │
                                           ▼
                       ┌───────────────────────────────────────┐
                       │ Platt Probability Calibration         │
                       │ CalibratedClassifierCV                │
                       │ (FrozenEstimator, ensemble=False)     │
                       └───────────────────┬───────────────────┘
                                           │
                            ┌──────────────┴──────────────┐
                            ▼                             ▼
                 ┌─────────────────────┐       ┌─────────────────────┐
                 │ TreeSHAP Explainer  │       │ Field Raid Priority │
                 │ & Natural Language  │       │ Queue & Evidence    │
                 │ Inspection Warrants │       │ Docket Generator    │
                 └─────────────────────┘       └─────────────────────┘
```

### 4.1 Unsupervised Anomaly Scoring (`isolation_forest_oof.py`)
* Model: `IsolationForest(n_estimators=100, contamination='auto', random_state=42)`
* Validation: 5-Fold `GroupKFold` grouped by `consumer_id` so no consumer appears in both training and scoring folds.
* Output: `iso_forest_oof_score` appended as an auxiliary feature, allowing the supervised model to detect novel zero-day tampering.

### 4.2 Supervised Classifier (`train_xgboost.py`)
* Model: `XGBClassifier`
* Loss Function: Binary Logistic Loss (`binary:logistic`)
* Asymmetric Class Weighting: `scale_pos_weight = 11.5` ($\approx \frac{N_{\text{neg}}}{N_{\text{pos}}}$) compensating for the severe 8% theft class imbalance.
* Hyperparameters: `n_estimators=300`, `max_depth=5`, `learning_rate=0.05`, `subsample=0.85`, `colsample_bytree=0.85`.

### 4.3 Platt Scaling Probability Calibration (`calibrate.py`)
* Method: Sigmoid Logistic Calibration on the uncorrupted 20% calibration split ($N=2,000$ consumers).
* Implementation: `CalibratedClassifierCV(estimator=FrozenEstimator(model), method='sigmoid', ensemble=False)`.
* Result: Resolves the scikit-learn 1.9 probability compression bug; maximum calibrated probabilities reach **73.3%** (up from 34.9%), creating an actionable operational decision boundary at $P \ge 0.50$.

### 4.4 Explainable AI (XAI) & Field Raid Dockets (`explain.py`)
* Algorithm: `shap.TreeExplainer(model)`.
* Automation: Converts top positive SHAP contributors into automated English and Urdu physical inspection warrants detailing exact timestamps, peak flatline percentages, and transformer loss correlations.

---

## 5. Visual System Designs (Track 1 vs. Track 2 vs. Unified)

### Design A: Track 1 (Legacy Monthly Grid Pipeline)
```
[ consumers.csv ] + [ monthly_readings.csv ] + [ pmt_monthly.csv ]
                           │
                           ▼ (data_assembly.py)
            [ 60/20/20 Stratified Split by Consumer ]
                           │
                           ▼ (features.py)
            [ CUSUM Break Detection + PMT Loss Rank ]
                           │
                           ▼ (isolation_forest_oof.py)
            [ 5-Fold GroupKFold Anomaly Score ]
                           │
                           ▼ (train_xgboost.py)
            [ XGBoost with Asymmetric Cost Weighting ]
                           │
                           ▼ (calibrate.py)
            [ Platt Calibration via FrozenEstimator ]
                           │
                           ▼ (evaluate.py + explain.py)
            [ Precision: 69.7% | Solar False Alarms: 0.00% ]
```

### Design B: Track 2 (High-Frequency Interval Streaming Pipeline)
```
[ consumers.csv (has_ami=True) ] + [ Monthly Totals ]
                           │
                           ▼ (generate_intervals.py)
     [ Diurnal Engine + Confounders + Time-Targeted Theft ]
                           │
                           ▼ (PyArrow Parquet Streaming Writer)
     [ interval_readings.parquet (51.8M Rows, 307 MB) ]
                           │
                           ▼ (run_track2_features.py - 500k Chunk Batches)
     [ track2_features.csv (72,000 Rows, 5 MB) ]
                           │
                           ▼ (uplift_evaluation.py)
     [ Side-by-Side Controlled Ablation Benchmark ]
     [ Peak Shaver Recall: 10.6% ──► 58.3% (+47.8% Uplift) ]
```

---

## 6. How to Run Track 1 and Track 2 Separately

All commands are executed from the repository root (`d:\hackathon\Ai-Hackathon`).

### 6.1 How to Run Track 1 (Legacy Monthly Pipeline)

Track 1 runs on the monthly billing dataset across the entire 10,000-consumer grid.

```bash
# Step 1: Assemble datasets and perform 60/20/20 stratified split by consumer_id
python data_assembly.py
# Output: output/train.parquet, output/calibrate.parquet, output/eval.parquet

# Step 2: Run the complete Track 1 ML Pipeline end-to-end
python run_pipeline.py
# Executes:
#   - Feature engineering (CUSUM, fixed baseline anchor, PMT loss rank)
#   - Out-of-fold Isolation Forest scoring
#   - XGBoost classifier training with scale_pos_weight
#   - Platt calibration with FrozenEstimator
#   - SHAP explanation generation & sample field alert docket
#   - Full evaluation report across all 14 archetypes

# (Optional) Run the comparative before/after diagnostic report:
python diagnose.py
```

**Expected Track 1 Outputs & Performance:**
* Precision @ 0.50: **69.7%** (19.3× better than naive audit)
* Recall @ 0.50: **30.6%**
* Solar Prosumer False Positive Rate: **0.00%**
* Runtime: **~45 seconds** on standard CPU.

---

### 6.2 How to Run Track 2 (Smart Meter Interval Pipeline)

Track 2 simulates the 1-hour interval smart grid, extracts load-curve shape features, and runs the uplift benchmark.

```bash
# Step 1: Select the 2,000 AMI pilot population
python select_ami_population.py
# Filters residential AMI-compatible consumers
# Output: Updates data/consumers.csv with has_ami=True, writes ami_consumer_ids.csv

# Step 2: Generate 51.8 Million 1-hour interval readings (streaming Parquet)
python generate_intervals.py
# Synthesizes 24-hour diurnal curves, injects confounders & time-targeted theft
# Output: interval_readings.parquet (~307.5 MB, 51,819,270 rows)
# Runtime: ~6 minutes

# Step 3: Run streaming batch feature extraction (Memory-Safe)
python run_track2_features.py
# Streams Parquet in 500,000-row chunks (Peak RAM < 200 MB)
# Extracts 7 interval features: peak_offpeak_ratio, flatline_fraction, etc.
# Output: track2_features.csv (~5 MB, 72,000 rows)
# Runtime: ~5.5 minutes

# Step 4: Run the Smart Grid Uplift Evaluation Benchmark
python uplift_evaluation.py
# Trains Model 1 (Monthly Only) vs. Model 2 (Monthly + Smart Meter Features)
# Evaluates on the exact same 2,000 consumers
# Output: Side-by-side comparison table proving +47.8% peak-shaving uplift
# Runtime: ~10 seconds
```

---

### 6.3 How to Run the Automated Test Suite

To verify all shape generators, seasonal physics, confounders, and interval theft signatures:

```bash
pytest test_rewdp_templates.py test_generate_intervals.py test_features.py test_calibrate.py test_iso.py test_merge.py test_train.py -v
```
**Expected Test Result:** `34 passed in ~2.6s (100%)`.

---

## 7. Empirical Uplift Benchmark Summary

```
===========================================================================
UPLIFT PROOF: IMPACT OF SMART METERS ON DETECTION (AMI POPULATION)
===========================================================================
Archetype            | Monthly Recall  | AMI Recall (1-Hour) | Recall Uplift
---------------------------------------------------------------------------
peak_hour_shaver     |          10.6% |               58.3% | +47.8% (5.5x)
fixed_shunt          |          38.3% |               63.9% | +25.6%
nighttime_ac         |          20.8% |               39.6% | +18.7% (1.9x)
kunda                |          14.9% |               29.5% | +14.6% (2.0x)
---------------------------------------------------------------------------
OVERALL AMI METRICS (ALL CONSUMER-MONTHS):
  Precision:          29.9%  ──────►   49.3%   (+19.4 pts)
  Recall:             20.3%  ──────►   45.7%   (+25.4 pts — More than doubled!)
  F1 Score:           0.242  ──────►   0.474   (+0.232)
  Honest FPR:         2.77%  ──────►   2.73%   (Zero false alarm penalty)
===========================================================================
```
