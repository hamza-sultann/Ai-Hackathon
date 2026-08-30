# Enterprise Revenue Protection & Anti-Theft AI Architecture
**A Unified Machine Learning & High-Frequency Streaming Engine for Non-Technical Loss (NTL) Detection**

---

## 1. System Architecture & Dual-Track Paradigm

The system is designed to operate seamlessly across both eras of power distribution in developing economies:
* **Track 1 (Legacy Monthly Grid):** Operates on 1 reading per month across 100% of consumers using grid balance CUSUM, PMT percentile loss ranking, and unsupervised anomaly scoring.
* **Track 2 (High-Frequency AMI Smart Grid):** Operates on 1-hour interval streams, computing 7 scale-invariant load curve features to unmask time-of-use (TOU) peak shaving and night AC theft.

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   ENTERPRISE SYSTEM ARCHITECTURE                                       │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘

 [ 10,000 Grid Consumers ]                                [ 2,000 AMI Pilot Consumers ]
  (Monthly Billing Data)                                    (51.8M Hourly Parquet Stream)
            │                                                            │
            ▼                                                            ▼
 ┌──────────────────────┐                                     ┌──────────────────────┐
 │  Track 1 Feature     │                                     │  Track 2 Streaming   │
 │  Engineering Engine  │                                     │  Batch Extractor     │
 │  • CUSUM Change-Point│                                     │  • Peak/Offpeak Ratio│
 │  • PMT Loss Percentile                                     │  • Flatline Fraction │
 │  • Fixed Baseline    │                                     │  • Midday Duck Index │
 └──────────┬───────────┘                                     └──────────┬───────────┘
            │                                                            │
            │               ┌────────────────────────┐                   │
            └──────────────►│ Unified Feature Table  │◄──────────────────┘
                            │ (consumer_id, month)   │  (Left-Joined; NaN for legacy meters)
                            └───────────┬────────────┘
                                        │
                                        ▼
                            ┌────────────────────────┐
                            │ Out-of-Fold Isolation  │
                            │ Forest Anomaly Scorer  │
                            └───────────┬────────────┘
                                        │
                                        ▼
                            ┌────────────────────────┐
                            │ XGBoost Classifier     │
                            │ (scale_pos_weight = 12)│
                            └───────────┬────────────┘
                                        │
                                        ▼
                            ┌────────────────────────┐
                            │ Platt Probability      │
                            │ Calibration (Frozen)   │
                            └───────────┬────────────┘
                                        │
                         ┌──────────────┴──────────────┐
                         ▼                             ▼
              ┌─────────────────────┐       ┌─────────────────────┐
              │ TreeSHAP Explainer  │       │ Field Raid Priority │
              │ & Natural Language  │       │ Queue & Evidence    │
              │ Inspection Alerts   │       │ Docket Generator    │
              └─────────────────────┘       └─────────────────────┘
```

---

## 2. End-to-End Machine Learning Pipeline

### Stage 1: Leakage-Free Stratified Splitting (`data_assembly.py`)
To prevent temporal and spatial contamination, data is partitioned strictly by `consumer_id` across a 3-way split:
* **Train Split (60%, $N=6,000$ consumers, 216,000 consumer-months):** Model parameter optimization.
* **Calibration Split (20%, $N=2,000$ consumers, 72,000 consumer-months):** Platt scaling calibration without training bias.
* **Evaluation Split (20%, $N=2,000$ consumers, 72,000 consumer-months):** Out-of-sample ground truth benchmarking.

---

### Stage 2: Feature Engineering & Domain Physics (`features.py`)

The pipeline extracts **12 domain-grounded Track 1 features** and **7 Track 2 interval features**:

#### 1. Vectorized CUSUM Change-Point Detection
Detects structural downward step-breaks in consumption while filtering out seasonal trends:
$$S_0 = 0,\quad S_t = \max\left(0, S_{t-1} + (\bar{x}_{\text{baseline}} - x_t) - k\right)$$
* `cusum_max_deviation`: Maximum cumulative negative deviation score across the 36-month timeline.
* `months_since_detected_break`: Time elapsed since the cumulative sum crossed the critical decision threshold $h$.

#### 2. Fixed 3-Month Uncontaminated Baseline Anchor
$$D_{\text{fixed}} = \frac{\text{mean}(x_1, x_2, x_3) - x_t}{\text{mean}(x_1, x_2, x_3) + 1.0}$$
Because theft onset never occurs before Month 4 ($m \ge 4$), Months 1–3 provide a guaranteed clean reference anchor, preventing trailing rolling windows from absorbing ongoing theft into "normal" baselines.

#### 3. PMT Percentile Loss Rank (`pmt_loss_rank`)
$$\text{Rank}_{\text{PMT}}(t) = \text{PercentileRank}\left(\frac{\text{Injected}_{\text{PMT}}(t) - \sum \text{Billed}_{\text{PMT}}(t)}{\text{Injected}_{\text{PMT}}(t)}\right)$$
Transforms noisy raw technical loss percentages into a normalized $0.0\text{--}1.0$ percentile across all 300 transformers in that specific month, exposing geographic theft pockets.

#### 4. Prosumer-Gated & Load-Shedding Invariance
* `prosumer_gated_usage_deviation`: Suppressed for registered solar prosumers to prevent false alarms on legitimate solar exports.
* `feeder_uptime_adj_deviation`: Normalizes billed consumption by feeder availability uptime ($\frac{\text{Billed}}{\text{Uptime}_{\text{feeder}}}$), ensuring load-shedding blackouts are not misclassified as theft.

---

### Stage 3: Unsupervised Out-of-Fold Isolation Forest (`isolation_forest_oof.py`)
To capture novel, zero-day tampering techniques unseen in historical labels, an unsupervised **Isolation Forest** is trained via 5-Fold GroupKFold cross-validation on `consumer_id`:
$$\text{Score}(x) = 2^{-\frac{E(h(x))}{c(n)}}$$
The out-of-fold anomaly score (`iso_forest_oof_score`) is appended directly as an input feature for the gradient boosted classifier.

---

### Stage 4: Supervised Ensemble & Asymmetric Cost Optimization (`train_xgboost.py`)
Power theft is heavily imbalanced (8.0% positive class). An extreme gradient boosted decision tree ensemble (**XGBoost**) is trained with asymmetric loss weighting:

$$\text{scale\_pos\_weight} = \frac{N_{\text{negative}}}{N_{\text{positive}}} = \frac{198,720}{17,280} \approx 11.5$$

```python
xgb_model = xgb.XGBClassifier(
    objective='binary:logistic',
    scale_pos_weight=11.5,
    eval_metric='aucpr',
    n_estimators=300,
    max_depth=5,
    learning_rate=0.05,
    subsample=0.85,
    colsample_bytree=0.85,
    random_state=42
)
```

---

### Stage 5: Platt Probability Calibration (`calibrate.py`)
Raw tree outputs on imbalanced data produce uncalibrated pseudo-probabilities that cluster near 0.1–0.3. 

Using **Platt Scaling with `FrozenEstimator` and `ensemble=False`** fitted on the dedicated 20% calibration split:
$$P(Y=1 \mid f(x)) = \frac{1}{1 + \exp(A \cdot f(x) + B)}$$

* **Result:** Maximum calibrated probabilities reach **73.3%** (up from 34.9%), allowing DISCO management to set strict operational decision thresholds ($P \ge 0.50$ for field raids, $0.30 \le P < 0.50$ for automated smart meter auditing).

---

### Stage 6: Explainability & Field Raid Warrants (`explain.py`)
Inspectors and legal tribunals require human-interpretable justifications. Using **TreeSHAP** (Shapley Additive Explanations):

$$\phi_i(x) = \sum_{S \subseteq F \setminus \{i\}} \frac{|S|!(|F| - |S| - 1)!}{|F|!} \Big(f_x(S \cup \{i\}) - f_x(S)\Big)$$

#### Automated Field Inspection Alert Generation:
```
================================================================================
                    DISCO REVENUE PROTECTION FIELD RAID DOCKET
================================================================================
Consumer ID      : C-000480
Feeder / PMT     : F-12 / PMT-0114 (Loss Rank: 94th Percentile)
Tamper Class     : PEAK_HOUR_SHAVER (Time-of-Use Bypass)
Theft Probability: 71.4% [HIGH RISK - DISPATCH RAID TEAM]

PHYSICAL EVIDENCE AUDIT:
1. [PEAK_WINDOW_FLATLINE]: Recorded 0.00 kW on 84.6% of peak hours (6:00-10:00 PM) 
   despite active daytime consumption of 3.8 kW (SHAP Impact: +0.34).
2. [CUSUM_BREAK]: Abrupt 48% drop detected starting Month 11; persisted continuously 
   for 25 consecutive months (SHAP Impact: +0.21).
3. [TRANSFORMER_BALANCE]: PMT-0114 non-technical loss rose by 14.2% concurrently with 
   consumer drop (SHAP Impact: +0.12).
================================================================================
```

---

## 3. Track 2 Streaming Parquet Batch Processing Architecture

Processing **51,819,270 hourly intervals** on standard enterprise hardware requires strict memory bounds. 

`run_track2_features.py` implements an out-of-core streaming architecture:
1. **PyArrow `iter_batches(batch_size=500,000)`:** Streams contiguous chunks directly from Parquet.
2. **Consumer Boundary Retention:** The tail consumer of each batch is buffered until the next chunk completes its 36-month timeline, preventing partial aggregation artifacts.
3. **Scale-Invariant Extraction:** Computes the 7 interval ratios and returns a compact 5 MB CSV table (`track2_features.csv`).
4. **Performance:** Total run time **5.5 minutes**, peak memory **< 200 MB RAM**.

---

## 4. Empirical Benchmarks & Performance Verification

### 4.1 Track 1 (Monthly Grid Baseline)
* **Precision @ 0.50 Threshold:** **69.7%**
* **Recall @ 0.50 Threshold:** **30.6%**
* **Naive Audit Improvement:** **19.3× better** than random/heuristic auditing (3.6% baseline precision).
* **Solar False Alarm Rate:** **0.00%** (100% specificity on solar prosumers).

### 4.2 Track 2 (Smart Grid Uplift Proof)
Evaluated on the exact same 2,000 AMI consumers:

```
===========================================================================
UPLIFT PROOF: IMPACT OF SMART METERS ON DETECTION (AMI POPULATION)
===========================================================================
Theft Archetype      | Monthly Recall  | AMI Recall (1-Hour) | Uplift Gain
---------------------------------------------------------------------------
peak_hour_shaver     |          10.6% |               58.3% | +47.8% (5.5x)
fixed_shunt          |          38.3% |               63.9% | +25.6%
nighttime_ac         |          20.8% |               39.6% | +18.7% (1.9x)
kunda                |          14.9% |               29.5% | +14.6% (2.0x)
---------------------------------------------------------------------------
Overall AMI Precision:   29.9%  ──────►  49.3%   (+19.4 pts)
Overall AMI Recall:      20.3%  ──────►  45.7%   (+25.4 pts — More than doubled!)
Overall AMI F1 Score:    0.242  ──────►  0.474   (+0.232)
Honest Consumer FPR:     2.77%  ──────►  2.73%   (Stable false alarms)
===========================================================================
```

---

## 5. Enterprise Deployment & Integration Blueprint

```
                      [ DISCO MDMS / AMI Head-End ]
                                    │
                         (Hourly Interval Feeds)
                                    ▼
             ┌───────────────────────────────────────────────┐
             │       Kafka / RabbitMQ Streaming Ingest       │
             └──────────────────────┬────────────────────────┘
                                    │
                                    ▼
             ┌───────────────────────────────────────────────┐
             │       FastAPI Microservice Engine             │
             │       • run_track2_features (Vectorized)      │
             │       • XGBoost + Platt Scaler Inference      │
             │       • TreeSHAP Evidence Generator           │
             └──────────────────────┬────────────────────────┘
                                    │
                     ┌──────────────┴──────────────┐
                     ▼                             ▼
         [ GIS Inspection Map UI ]      [ DISCO Billing System ]
         (Live GPS Raid Dispatch)       (Automated Audit Flagging)
```

1. **SCADA / AMI Integration:** Ingests hourly JSON/Parquet payloads from smart meter collectors.
2. **Real-Time Priority Queue:** Ranks all consumers daily by expected recoverable revenue ($\text{Recoverable PKR} = P_{\text{theft}} \times \text{Deficit kWh} \times \text{Tariff Rate}$).
3. **Bandwidth Optimization:** Proves that **1-hour sampling** captures >90% of maximum possible theft signals while cutting cellular telecom transmission costs by **75%** compared to 15-minute polling.
