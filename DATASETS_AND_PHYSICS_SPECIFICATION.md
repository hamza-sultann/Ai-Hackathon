# Pakistan Power Grid & Synthetic AMI Dataset Specification (v3.0)
**Enterprise-Grade Synthetic Simulation of Non-Technical Losses (NTL), Grid Hierarchy, and Diurnal Load Curves**

---

## 1. Executive Summary & National Context

In Pakistan's power sector, **Circular Debt** exceeds **PKR 2.6 Trillion**, driven primarily by **Non-Technical Losses (NTL)**—electricity theft, meter tampering, billing collusion, and unmetered direct hookups (*kundas*). Distribution Companies (DISCOs such as LESCO, K-Electric, IESCO, MEPCO, and PESCO) lose between 12% and 38% of distributed power.

Because real utility theft ground-truth data in Pakistan is legally restricted, heavily confidential, and distorted by unrecorded collusion, this dataset provides a **physically grounded, mathematically rigorous synthetic simulation** designed to mirror the operational, behavioral, climatic, and electrical realities of Pakistan's distribution grid.

This dataset bridges two distinct eras of the power sector:
1. **Track 1 (Legacy Grid):** 10,000 consumers with monthly billing cycles, analog/electronic meters, manual reader assignments, and severe class imbalance (8% theft rate).
2. **Track 2 (Future Smart Grid):** 2,000 residential consumers disaggregated into **51.8 Million 1-Hour Interval Readings** (stored as high-compression Parquet), grounded in real Pakistani diurnal load profiles (REWD-P), Time-of-Use (TOU) tariff windows, and micro-confounders.

---

## 2. Electrical Grid Hierarchy & Network Topology

The dataset models a complete 3-tier distribution network hierarchy operating under National Electric Power Regulatory Authority (NEPRA) grid standards:

```
                      [ 132kV / 11kV Grid Substation ]
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         ▼                           ▼                           ▼
    [ Feeder F-01 ]             [ Feeder F-02 ]     ...     [ Feeder F-30 ]  (30 Feeders)
         │
    ┌────┴───────────────────────────┐
    ▼                                ▼
[ PMT-0001 ] ...               [ PMT-0010 ]  (10 PMTs / Feeder = 300 Total PMTs)
    │
    ├─► Consumer C-000001 (Residential, 5 kW)
    ├─► Consumer C-000002 (Commercial, 15 kW)
    └─► Consumer C-000033 (Industrial, 75 kW)  (~33.3 Consumers / PMT = 10,000 Total)
```

### 2.1 Grid Topology Parameters
* **Primary Feeders ($N = 30$):** 11 kV medium-voltage distribution lines (`F-01` to `F-30`).
* **Distribution Transformers ($N = 300$):** 11 kV / 415 V Pole-Mounted Transformers (PMTs, `PMT-0001` to `PMT-0300`), each serving an average of ~33 consumers.
* **Consumer Population ($N = 10,000$):**
  * **Residential (80%, $N=8,000$):** Sanctioned load $\sim \text{Uniform}(1.0, 8.0)\text{ kW}$.
  * **Commercial (15%, $N=1,500$):** Sanctioned load $\sim \text{Uniform}(5.0, 25.0)\text{ kW}$ (shops, plazas, clinics).
  * **Industrial (5%, $N=500$):** Sanctioned load $\sim \text{Uniform}(20.0, 100.0)\text{ kW}$ (flour mills, small manufacturing).
* **Meter Infrastructure:**
  * **Analog / Electromechanical Meters (65%):** Rotating disc meters vulnerable to mechanical slow-downs, magnets, and tilt tampering.
  * **Digital / Electronic Static Meters (35%):** LCD meters vulnerable to internal shunt bypasses, neutral disconnection, and incoming terminal taps.
* **Timespan:** 36 consecutive calendar months (January 2022 to December 2024, 3 full annual cycles).

---

## 3. Physical Grid Laws & Realism Mechanisms

### 3.1 Non-Linear Technical Loss ($I^2R$) Modeling
Energy injected at the PMT level does not equal the sum of consumer consumption due to natural resistance dissipation in conductors. Technical loss is modeled as a non-linear convex power function of total throughput:

$$\text{Technical Loss (kWh)} = \max\left(0.00006 \times (\text{Aggregate Load})^{1.6},\; 0.02 \times \text{Aggregate Load}\right)$$

$$\text{Injected Energy}_{\text{PMT}} = \sum \text{Billed Units} + \sum \text{Stolen Units} + \text{Technical Loss}$$

*Every single PMT-month satisfies the conservation law: $|\text{Injected} - (\text{Billed} + \text{Stolen} + \text{TL})| < 0.5\text{ kWh}$.*

### 3.2 High-Risk Geographic PMT Clustering (Theft Pockets)
In Pakistan, power theft is rarely distributed uniformly; socio-economic factors and local enforcement create heavy geographic clustering:
* **High-Risk PMT Core (15% of PMTs, $N=45$):** 75% of all theft consumers ($p=0.75$) are clustered across these 45 transformers.
* **Background Scatter (85% of PMTs, $N=255$):** The remaining 25% of theft consumers are distributed randomly as isolated incidents.

### 3.3 Ambient Temperature & Climatic Load Coupling
Electricity consumption in Pakistan is heavily weather-driven (summer cooling vs. winter gas/heating):
$$T(m) = 18.0 + 14.0 \cdot \sin\left(\frac{2\pi (m - 3)}{12}\right) + \mathcal{N}(0, 1.2)\quad (^\circ\text{C})$$
* **June Peak:** $\sim 32^\circ\text{C}$ to $44^\circ\text{C}$ average ambient temperature (heavy air conditioner load).
* **January Trough:** $\sim 4^\circ\text{C}$ to $12^\circ\text{C}$ (geysers and electric heaters).
* **Seasonal Consumption Multiplier:**
  $$S(m) = 1.0 + A \cdot \sin\left(\frac{2\pi (m - 3)}{12}\right),\quad A=0.35\text{ (Standard)}, A=0.05\text{ (Lifeline/Vacant)}$$

### 3.4 Feeder & PMT Load-Shedding / Outage Simulation
Unscheduled outages and feeder load management reduce recorded consumption:
* **Feeder Uptime:** $\sim \text{Uniform}(0.82, 0.98)$ (82% to 98% monthly availability).
* Confounded drops: When a feeder experiences 75% uptime, all consumers drop proportionally—the model must distinguish load-shedding from theft!

---

## 4. Comprehensive Archetype Taxonomy (14 Detailed Profiles)

The dataset contains **14 distinct consumer archetypes** (92% legitimate, 8% theft ground truth), covering every major fraud and legitimate confounder seen in DISCO jurisdictions:

```
                               CONSUMER POPULATION (10,000)
                                            │
               ┌────────────────────────────┴────────────────────────────┐
               ▼                                                         ▼
    LEGITIMATE / CONFOUNDERS (9,200)                             THEFT / NTL (800)
    ├─ standard (6,600)                                         ├─ kunda (150)
    ├─ solar_prosumer (1,200)                                   ├─ slab_defender (150)
    ├─ vacant (500)                                             ├─ nighttime_ac (120)
    ├─ low_income_frugal (300)                                  ├─ peak_hour_shaver (100)
    ├─ seasonal_traveler (300) [Confounder]                     ├─ gradual_slowdown (100)
    └─ efficient_upgrade (300) [Confounder]                     ├─ fixed_shunt (100)
                                                                ├─ intermittent_hookup (50)
                                                                └─ collusion (30)
```

### 4.1 Legitimate & Confounder Archetypes (9,200 Consumers)

| Archetype | Count | Prosumer? | Real-World Behavior & Mathematical Model |
|---|:---:|:---:|---|
| `standard` | 6,600 | No | Standard household. Base log-normal baseline $\mu = \ln(\text{load} \times 60), \sigma=0.35$ modulated by summer cooling seasonality. |
| `solar_prosumer` | 1,200 | **Yes** | Rooftop solar net-metering under NEPRA regulations. High summer generation factor $F_{\text{solar}}(m) = \text{clip}(1.0 + 0.4\sin(\frac{2\pi(m-4)}{12}), 0.5, 1.3)$. Monthly billed energy: $\text{Billed} = \text{True} \times (1 - \text{SelfSufficiency})$. |
| `vacant` | 500 | No | Unoccupied or locked properties. Standby phantom draw only ($5\text{--}15\text{ kWh/month}$) with minimal seasonal variance ($A=0.05$). |
| `low_income_frugal` | 300 | No | Lifeline tariff consumers (<50 kWh/mo). Basic lighting and 1 ceiling fan only ($30\text{--}60\text{ kWh/month}$). |
| `seasonal_traveler` | 300 | No | **Major Confounder:** Families travelling to ancestral villages or abroad for 1–3 months ($\text{start} \in [0, 32]$). Consumption drops sharply to $5\text{--}15\text{ kWh}$ during the trip, perfectly mimicking sudden theft before rebounding. |
| `efficient_upgrade` | 300 | No | **Major Confounder:** House retrofitted with Inverter ACs and LED lighting ($\text{month} \in [6, 29]$). Permanent step-down drop of 15% to 35% ($\text{factor} \sim \text{Uniform}(0.65, 0.85)$) that persists permanently without being fraudulent. |

---

### 4.2 Theft Archetypes (800 Consumers — 8.0% Ground Truth)

All theft archetypes feature a randomized **Theft Onset Month** ($\text{onset} \sim \text{UniformInt}(4, 29)$). Months $1\text{--}3$ are guaranteed uncontaminated baseline.

| Archetype | Count | Target Window | Physical Theft Mechanism & Ramp Dynamics |
|---|:---:|:---:|---|
| `kunda` | 150 | All Hours (Whole Day) | **Direct Physical Tap:** Bare wire hooked directly over the low-voltage distribution line. Escalates in 5 stages as consumer gains confidence: 5% drop (months 1–2) $\rightarrow$ 8% (months 3–4) $\rightarrow$ 12% (months 5–7) $\rightarrow$ 20% (months 8–10) $\rightarrow$ Plateau at 75–92% bypass. |
| `slab_defender` | 150 | Monthly Billing Threshold | **Tariff Slab Gaming:** In Pakistan, crossing 200 units or 300 units triggers punitive protected-to-unprotected tariff slab rates. The consumer tampers with the meter only when consumption threatens to exceed $\sim 185\text{--}198\text{ kWh}$, artificially pinning their monthly reading below the slab penalty. |
| `nighttime_ac` | 120 | 11:00 PM – 5:00 AM (Summer) | **Overnight AC Shunt:** Consumer uses normal power during daytime, but engages an unmetered bypass switch at night during summer months (June–September) to run heavy bedroom air conditioning. Billed units drop by 15–25% in summer only. |
| `peak_hour_shaver` | 100 | 6:00 PM – 10:00 PM (TOU Peak) | **NEPRA Peak Tariff Evasion:** Under Time-of-Use metering, peak units cost 2.5× off-peak units. The consumer bypasses the meter strictly during peak hours on ~55% of days. Invisible in monthly aggregations (only ~6% monthly drop) but glaring at interval resolution. |
| `gradual_slowdown` | 100 | Compounding Monthly Decay | **Mechanical Meter Tampering:** Friction applied to analog disc (needle injection, magnet, or foreign matter). Compounding degradation: $\text{decay} = (1 - \text{rate})^{\text{months}}$, degrading by 2–3% each month until capped at 45% throughput. |
| `fixed_shunt` | 100 | All Hours (Hardware) | **Resistive Shunt Device:** Fixed hardware resistor installed across meter current transformer (CT). Constant 45%–55% proportional reduction across all hours, year-round. |
| `intermittent_hookup` | 50 | Periodic Burst | Periodic connection of unmetered industrial/welding or agricultural machinery for a few days each month, creating noisy 6–12% monthly deficits. |
| `collusion` | 30 | Meter Reader Route | **Corrupt Meter Reader Ring:** 5 collusion groups (`R-COL-01` to `R-COL-05`) of 6 consumers each. Meter reader manually records 16–24% lower readings in the handheld terminal in exchange for bribes. |

---

## 5. Track 2: 1-Hour High-Frequency Interval Engine

For the 2,000 residential AMI pilot population, monthly numbers are disaggregated into **51,819,270 hourly timestamps** ($2,000\text{ consumers} \times 36\text{ months} \times \approx 720\text{ hours/month}$), stored in **Apache Parquet with Snappy compression (307.5 MB)**.

```
Hour:    00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23
         ┌────────────────────────────────────────────────────────────────────────┐
Normal:  │─── Low Base (0.15) ───│▲ Breakfast (0.45)│── Daytime (0.28) ──│▲ TOU Peak (0.85)│
         └────────────────────────────────────────────────────────────────────────┘
                                                         │
                                  ┌──────────────────────┴──────────────────────┐
                                  ▼                                             ▼
                     [ Solar Prosumer Duck Curve ]             [ Peak Shaver Theft ]
                     Midday Drop: 10 AM - 3 PM (0.05)         Peak Drop: 7 PM - 10 PM (0.02)
```

### 5.1 Diurnal Shape Formulation & Donor Household Pool
Using 60 empirical Pakistani load profiles (grounded in REWD-P residential micro-data), normalized curves sum to 1.0 per day:
* **Morning Gaussian Peak:** Center $\mu_{\text{m}} = 7.5\text{ AM}$ (weekday), $\mu_{\text{m}} = 9.0\text{ AM}$ (weekend), $\sigma_{\text{m}} = 1.3\text{ h}$.
* **Evening TOU Peak:** Center $\mu_{\text{e}} = 20.0\text{ PM}$ (8:00 PM), $\sigma_{\text{e}} = 1.8\text{ h}$ (6:00 PM – 10:00 PM window).
* **Summer Nocturnal Base:** Elevated base between 23:00 and 05:00 representing constant ceiling fan and AC cooling.
* **Winter Geyser Injection:** 40% probability of a 2.0x–3.5x discrete spike during morning bathing hours (06:00–08:00).
* **Temporal Autocorrelation (AR-1):** Hour-to-hour noise autocorrelation: $\epsilon_t = 0.60 \cdot \epsilon_{t-1} + \mathcal{N}(0, 0.03)$.
* **Smart Meter Packet Drops:** 1.5% random missing readings (`NaN`) simulating GPRS/cellular telemetry dropouts.

---

## 6. Mathematical Schema & Entity Relationship

```
                       [ consumers.csv ] (10,000 rows)
                       ├─ consumer_id (PK)
                       ├─ pmt_id (FK)
                       ├─ feeder_id (FK)
                       ├─ sanctioned_load_kw
                       ├─ consumer_type (residential/commercial/industrial)
                       ├─ meter_type (analog/electronic)
                       ├─ is_registered_prosumer (bool)
                       └─ has_ami (bool - 2,000 True, 8,000 False)
                                │
          ┌─────────────────────┴─────────────────────┐
          ▼                                           ▼
[ monthly_readings.csv ] (360k rows)       [ interval_readings.parquet ] (51.8M rows)
├─ consumer_id (FK)                        ├─ consumer_id (FK - AMI only)
├─ month (YYYY-MM-01)                      ├─ timestamp (YYYY-MM-DD HH:00:00)
├─ billed_units_kwh                        └─ interval_kwh (float32)
├─ arrears_pkr (Exponential β=1500)
├─ reader_id (R-001..R-220)
├─ is_theft_ground_truth (bool)
└─ theft_type (14 classes)
```

---

## 7. Data Quality & Audit Integrity

* **Stratified 3-Way Split:** Grouped strictly by `consumer_id` (60% Train, 20% Calibrate, 20% Evaluate) ensuring **zero temporal or spatial data leakage**.
* **Conservation Laws:** Grid energy balances verified on all 300 PMTs.
* **Parquet Optimization:** 51.8M rows stored in only 307.5 MB with PyArrow streaming support (<200 MB peak RAM during ETL).
