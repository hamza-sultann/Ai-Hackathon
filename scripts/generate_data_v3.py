"""
Synthetic data generator — Track 1 (Monthly, 3-year), v3.

Changes vs v2:
  - Mid-history theft onset: every theft archetype starts "clean" and switches on at a
    random onset month (4-29). Pre-onset behaviour is indistinguishable from a normal
    household -- the model has to detect a change, not memorize a fixed split.
  - PMT-level clustering: 15% of PMTs are "high-risk"; theft consumers land there ~75%
    of the time instead of being spread uniformly across all 300 PMTs.
  - Kunda severity ramp: staged escalation (5% -> 8% -> 12% -> 20% -> per-consumer
    plateau ~22-32%) instead of a flat 85-95% drop from day one.
  - Wider noise floor (~6%+) on legit billing AND on theft severity.
  - Seasonal theft intensity: theft severity scales up in summer/monsoon, down in winter.
  - Seasonal, noisier solar self-sufficiency instead of one flat clean draw.
  - Two new LEGIT confound archetypes for genuine false-positive risk:
      seasonal_traveler  -- temporary near-vacant blip (village trip / extended travel)
      efficient_upgrade  -- permanent step-down in baseline consumption (new appliances)
"""

import os
import numpy as np
import pandas as pd

# Script lives in <project>/scripts/; output goes to <project>/data/ (created if missing).
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "..", "data")

SEED = 42
rng = np.random.default_rng(SEED)

# ---------------------------------------------------------------------------
# 0. Grid hierarchy + volume
# ---------------------------------------------------------------------------
N_FEEDERS = 30
N_PMTS_PER_FEEDER = 10
N_PMTS = N_FEEDERS * N_PMTS_PER_FEEDER          # 300
N_CONSUMERS = 10_000
N_MONTHS = 36
START_MONTH = pd.Timestamp("2022-01-01")

N_READERS = 220
N_COLLUSION_GROUPS = 5

HIGH_RISK_PMT_FRACTION = 0.15                    # ~45 of 300 PMTs
THEFT_CLUSTER_PROB = 0.75                          # theft consumers land on a high-risk PMT this often

CONSUMER_TYPES = np.array(["residential", "commercial", "industrial"])
CONSUMER_TYPE_WEIGHTS = [0.80, 0.15, 0.05]
METER_TYPES = np.array(["analog", "electronic"])
METER_TYPE_WEIGHTS = [0.65, 0.35]

# (key, count, is_theft, is_prosumer, is_vacant, is_frugal)
# standard trimmed to 6,600 to make room for the two new legit confound archetypes
# (300 each) while keeping every other count from the original spec unchanged.
ARCHETYPES = [
    ("standard",             6600, False, False, False, False),
    ("kunda",                 150, True,  False, False, False),
    ("slab_defender",         150, True,  False, False, False),
    ("nighttime_ac",          120, True,  False, False, False),
    ("peak_hour_shaver",      100, True,  False, False, False),
    ("gradual_slowdown",      100, True,  False, False, False),
    ("fixed_shunt",           100, True,  False, False, False),
    ("intermittent_hookup",    50, True,  False, False, False),
    ("collusion",              30, True,  False, False, False),
    ("solar_prosumer",       1200, False, True,  False, False),
    ("vacant",                 500, False, False, True,  False),
    ("low_income_frugal",      300, False, False, False, True),
    ("seasonal_traveler",      300, False, False, False, False),
    ("efficient_upgrade",      300, False, False, False, False),
]
assert sum(a[1] for a in ARCHETYPES) == N_CONSUMERS
THEFT_KEYS = {k for k, _, is_theft, *_ in ARCHETYPES if is_theft}


def seasonal_mult(month_num, amplitude=0.35, phase=3):
    """Consumption seasonality: peaks ~Jun-Aug, troughs ~Dec-Jan."""
    return 1.0 + amplitude * np.sin(2 * np.pi * (month_num - phase) / 12)


def seasonal_theft_mult(month_num):
    """Theft incentive scales with the seasonal bill: higher in summer/monsoon, lower in winter."""
    return np.clip(1.0 + 0.45 * np.sin(2 * np.pi * (month_num - 3) / 12), 0.4, 1.8)


def seasonal_solar_factor(month_num):
    """Solar generation potential: best Apr-Oct, worst Nov-Feb (short days / winter fog)."""
    return np.clip(1.0 + 0.4 * np.sin(2 * np.pi * (month_num - 4) / 12), 0.5, 1.3)


# ---------------------------------------------------------------------------
# 1. Grid hierarchy tables
# ---------------------------------------------------------------------------
def make_grid():
    feeder_ids = [f"F-{i:02d}" for i in range(1, N_FEEDERS + 1)]
    pmt_rows = []
    for fi, feeder_id in enumerate(feeder_ids):
        for pi in range(1, N_PMTS_PER_FEEDER + 1):
            pmt_id = f"PMT-{fi * N_PMTS_PER_FEEDER + pi:04d}"
            pmt_rows.append({"pmt_id": pmt_id, "feeder_id": feeder_id})
    pmts = pd.DataFrame(pmt_rows)
    return feeder_ids, pmts


# ---------------------------------------------------------------------------
# 2. Consumers, incl. onset/upgrade/blip metadata + PMT clustering
# ---------------------------------------------------------------------------
def make_consumers(pmts: pd.DataFrame) -> pd.DataFrame:
    n = N_CONSUMERS
    consumer_ids = [f"C-{i:06d}" for i in range(1, n + 1)]

    consumer_type = rng.choice(CONSUMER_TYPES, size=n, p=CONSUMER_TYPE_WEIGHTS)
    load_base = {"residential": (1.0, 8.0), "commercial": (5.0, 25.0), "industrial": (20.0, 100.0)}
    sanctioned_load_kw = np.array([rng.uniform(*load_base[ct]) for ct in consumer_type]).round(2)
    meter_type = rng.choice(METER_TYPES, size=n, p=METER_TYPE_WEIGHTS)

    reader_ids = [f"R-{i:03d}" for i in range(1, N_READERS + 1)]
    reader_id = rng.choice(reader_ids, size=n, replace=True)

    labels = np.concatenate([np.full(count, key) for key, count, *_ in ARCHETYPES])
    rng.shuffle(labels)
    is_theft = np.isin(labels, list(THEFT_KEYS))

    # --- PMT assignment: clustered for theft, uniform otherwise ---
    all_pmt_ids = pmts["pmt_id"].to_numpy()
    n_high_risk = max(1, round(N_PMTS * HIGH_RISK_PMT_FRACTION))
    high_risk_pmts = rng.choice(all_pmt_ids, size=n_high_risk, replace=False)

    pmt_assignment = rng.choice(all_pmt_ids, size=n, replace=True)  # default: uniform
    theft_idx = np.where(is_theft)[0]
    cluster_roll = rng.random(len(theft_idx)) < THEFT_CLUSTER_PROB
    pmt_assignment[theft_idx[cluster_roll]] = rng.choice(
        high_risk_pmts, size=cluster_roll.sum(), replace=True
    )
    # the remaining ~25% of theft_idx keep their uniform draw -- deliberate background scatter

    consumers = pd.DataFrame(
        {
            "consumer_id": consumer_ids,
            "pmt_id": pmt_assignment,
            "sanctioned_load_kw": sanctioned_load_kw,
            "consumer_type": consumer_type,
            "meter_type": meter_type,
            "reader_id": reader_id,
            "archetype": labels,
            "is_theft_ground_truth": is_theft,
        }
    )
    consumers = consumers.merge(pmts, on="pmt_id", how="left")

    flag_map = {key: (is_pros, is_vac, is_frug) for key, _, _, is_pros, is_vac, is_frug in ARCHETYPES}
    consumers["is_registered_prosumer"] = consumers["archetype"].map(lambda a: flag_map[a][0])
    consumers["theft_type"] = np.where(consumers["is_theft_ground_truth"], consumers["archetype"], "none")

    # collusion: shared corrupt reader per small group
    collusion_idx = consumers.index[consumers["archetype"] == "collusion"].to_numpy().copy()
    rng.shuffle(collusion_idx)
    for gi, group in enumerate(np.array_split(collusion_idx, N_COLLUSION_GROUPS)):
        consumers.loc[group, "reader_id"] = f"R-COL-{gi + 1:02d}"

    # --- change-point / event metadata ---
    consumers["onset_month"] = -1
    consumers.loc[consumers["is_theft_ground_truth"], "onset_month"] = rng.integers(
        4, 30, size=int(consumers["is_theft_ground_truth"].sum())
    )
    consumers["kunda_final_cap"] = rng.uniform(0.22, 0.32, n)  # only used for kunda rows

    consumers["upgrade_month"] = -1
    consumers["upgrade_factor"] = 1.0
    m = consumers["archetype"] == "efficient_upgrade"
    consumers.loc[m, "upgrade_month"] = rng.integers(6, 30, size=m.sum())
    consumers.loc[m, "upgrade_factor"] = rng.uniform(0.65, 0.85, m.sum())

    consumers["blip_start"] = -1
    consumers["blip_len"] = 0
    m = consumers["archetype"] == "seasonal_traveler"
    consumers.loc[m, "blip_start"] = rng.integers(0, N_MONTHS - 3, size=m.sum())
    consumers.loc[m, "blip_len"] = rng.integers(1, 4, size=m.sum())

    return consumers


# ---------------------------------------------------------------------------
# 3. True consumption per consumer per month
# ---------------------------------------------------------------------------
def true_consumption(consumers: pd.DataFrame, months: pd.DatetimeIndex) -> pd.DataFrame:
    n = len(consumers)
    archetype = consumers["archetype"].to_numpy()

    mu = np.log(consumers["sanctioned_load_kw"].to_numpy() * 60)
    lognormal_baseline = rng.lognormal(mean=mu, sigma=0.35, size=n)
    vacant_baseline = rng.uniform(5, 15, n)
    frugal_baseline = rng.uniform(30, 60, n)

    base_baseline = np.where(
        archetype == "vacant", vacant_baseline,
        np.where(archetype == "low_income_frugal", frugal_baseline, lognormal_baseline),
    )
    seasonal_amp = np.where(np.isin(archetype, ["vacant", "low_income_frugal"]), 0.05, 0.35)

    upgrade_month = consumers["upgrade_month"].to_numpy()
    upgrade_factor = consumers["upgrade_factor"].to_numpy()
    is_traveler = (archetype == "seasonal_traveler")
    blip_start = consumers["blip_start"].to_numpy()
    blip_len = consumers["blip_len"].to_numpy()

    rows = []
    for m_idx, month in enumerate(months):
        month_num = month.month
        s_mult = seasonal_mult(month_num, amplitude=seasonal_amp)
        noise = rng.normal(loc=1.0, scale=0.06, size=n)

        # efficient_upgrade: permanent step-down in baseline once past upgrade_month
        after_upgrade = upgrade_month >= 0
        eff_factor = np.where(after_upgrade & (m_idx >= upgrade_month), upgrade_factor, 1.0)
        baseline = base_baseline * eff_factor

        true_kwh = baseline * s_mult * noise
        true_kwh = np.clip(true_kwh, 3, None)

        # seasonal_traveler: near-vacant blip overrides everything for that window,
        # weather-independent (nobody's home to run seasonal loads)
        in_blip = is_traveler & (m_idx >= blip_start) & (m_idx < blip_start + blip_len)
        blip_kwh = rng.uniform(5, 15, n) * rng.normal(1.0, 0.05, n)
        true_kwh = np.where(in_blip, blip_kwh, true_kwh)
        true_kwh = np.clip(true_kwh, 2, None)

        rows.append(
            pd.DataFrame(
                {
                    "consumer_id": consumers["consumer_id"].to_numpy(),
                    "month": month,
                    "month_idx": m_idx,
                    "true_consumption_kwh": true_kwh,
                }
            )
        )
    return pd.concat(rows, ignore_index=True)


# ---------------------------------------------------------------------------
# 4. Anomaly injection -> billed_units_kwh, stolen_units_kwh
# ---------------------------------------------------------------------------
def apply_anomalies(readings: pd.DataFrame, consumers: pd.DataFrame) -> pd.DataFrame:
    df = readings.merge(
        consumers[["consumer_id", "archetype", "reader_id", "is_registered_prosumer",
                   "is_theft_ground_truth", "theft_type", "onset_month", "kunda_final_cap"]],
        on="consumer_id", how="left",
    )
    n = len(df)
    true_kwh = df["true_consumption_kwh"].to_numpy()
    arch = df["archetype"].to_numpy()
    month_idx = df["month_idx"].to_numpy()
    month_num = df["month"].dt.month.to_numpy()
    onset = df["onset_month"].to_numpy()

    billed = true_kwh.copy()
    theft_season = seasonal_theft_mult(month_num)

    def mask(key):
        return arch == key

    # -- legit populations (incl. the two new confound archetypes): billed ~ true,
    #    wider metering/rounding noise than before (~6%) --
    legit = np.isin(arch, ["standard", "vacant", "low_income_frugal",
                            "seasonal_traveler", "efficient_upgrade"])
    billed[legit] = true_kwh[legit] * rng.normal(1.0, 0.06, legit.sum())

    # -- solar/prosumer: seasonal, noisy self-sufficiency instead of one flat draw --
    m = mask("solar_prosumer")
    base_self_suff = rng.uniform(0.55, 0.85, m.sum())              # per-consumer system quality
    seasonal_solar = seasonal_solar_factor(month_num[m])
    noise_solar = rng.normal(1.0, 0.08, m.sum())
    self_suff = np.clip(base_self_suff * seasonal_solar * noise_solar, 0.1, 0.95)
    billed[m] = true_kwh[m] * (1 - self_suff)

    # --- theft archetypes: pre-onset behaves like a legit household; post-onset
    #     applies the archetype's severity, scaled by season, with wider noise ---
    pre_onset = (onset >= 0) & (month_idx < onset)
    post_onset = (onset >= 0) & (month_idx >= onset)
    billed[pre_onset] = true_kwh[pre_onset] * rng.normal(1.0, 0.06, pre_onset.sum())

    # Kunda: staged ramp (5% -> 8% -> 12% -> 20% -> per-consumer plateau), seasonally scaled
    m = mask("kunda") & post_onset
    msn = month_idx[m] - onset[m]                                    # months since onset
    cap = df.loc[m, "kunda_final_cap"].to_numpy()
    base_drop = np.select(
        [msn < 2, msn < 4, msn < 7, msn < 10],
        [0.05, 0.08, 0.12, 0.20],
        default=cap,
    )
    drop = np.clip(base_drop * theft_season[m] + rng.normal(0, 0.025, m.sum()), 0.02, 0.55)
    billed[m] = true_kwh[m] * (1 - drop)

    # Slab defender: cap-based (post-onset only); small monthly jitter on the cap itself
    m = mask("slab_defender") & post_onset
    cap_val = rng.uniform(185, 198, m.sum()) + rng.normal(0, 5, m.sum())
    billed[m] = np.minimum(true_kwh[m], cap_val)
    billed[mask("slab_defender") & pre_onset] = true_kwh[mask("slab_defender") & pre_onset] \
        * rng.normal(1.0, 0.06, (mask("slab_defender") & pre_onset).sum())

    # Nighttime AC: modest seasonal-scaled dip (only the night portion is missing)
    m = mask("nighttime_ac") & post_onset
    base_drop = rng.uniform(0.15, 0.25, m.sum())
    drop = np.clip(base_drop * theft_season[m] + rng.normal(0, 0.03, m.sum()), 0.02, 0.5)
    billed[m] = true_kwh[m] * (1 - drop)

    # Peak-hour shaver: smaller dip, localized theft window
    m = mask("peak_hour_shaver") & post_onset
    base_drop = rng.uniform(0.05, 0.12, m.sum())
    drop = np.clip(base_drop * theft_season[m] + rng.normal(0, 0.025, m.sum()), 0.01, 0.4)
    billed[m] = true_kwh[m] * (1 - drop)

    # Gradual mechanical slowdown: compounding decay measured from ONSET, not absolute month
    m = mask("gradual_slowdown") & post_onset
    msn = month_idx[m] - onset[m]
    rate = rng.uniform(0.02, 0.03, m.sum())
    decay_mult = np.maximum((1 - rate) ** msn, 0.45)
    drop = np.clip((1 - decay_mult) * theft_season[m] + rng.normal(0, 0.02, m.sum()), 0.01, 0.6)
    billed[m] = true_kwh[m] * (1 - drop)

    # Fixed gear shunt: ~50% under-recording but noisier and mildly seasonal now
    m = mask("fixed_shunt") & post_onset
    base_drop = rng.normal(0.50, 0.05, m.sum())
    drop = np.clip(base_drop * (0.85 + 0.15 * theft_season[m]) , 0.15, 0.7)  # dampened seasonal swing
    billed[m] = true_kwh[m] * (1 - drop)

    # Intermittent appliance hookup: small, noisy dent
    m = mask("intermittent_hookup") & post_onset
    base_drop = rng.uniform(0.06, 0.12, m.sum())
    drop = np.clip(base_drop * theft_season[m] + rng.normal(0, 0.03, m.sum()), 0.01, 0.4)
    billed[m] = true_kwh[m] * (1 - drop)

    # Collusion: systemic under-billing, seasonally scaled, noisier
    m = mask("collusion") & post_onset
    base_drop = rng.uniform(0.16, 0.24, m.sum())
    drop = np.clip(base_drop * theft_season[m] + rng.normal(0, 0.03, m.sum()), 0.02, 0.5)
    billed[m] = true_kwh[m] * (1 - drop)

    billed = np.clip(billed, 0, None)
    df["billed_units_kwh"] = np.round(billed, 2)

    theft_mask = df["is_theft_ground_truth"].to_numpy()
    stolen = np.zeros(n)
    stolen[theft_mask] = np.clip(true_kwh[theft_mask] - billed[theft_mask], 0, None)
    df["stolen_units_kwh"] = np.round(stolen, 2)

    df["arrears_pkr"] = np.round(rng.exponential(scale=1500, size=n), 2)
    return df


# ---------------------------------------------------------------------------
# 5. PMT-level aggregation + feeder-level rollup
# ---------------------------------------------------------------------------
def make_pmt_monthly(readings: pd.DataFrame, pmts: pd.DataFrame, months: pd.DatetimeIndex) -> pd.DataFrame:
    grouped = (
        readings.groupby(["pmt_id", "feeder_id", "month"], as_index=False)
        .agg(billed_sum=("billed_units_kwh", "sum"), stolen_sum=("stolen_units_kwh", "sum"))
    )

    feeder_ids = pmts["feeder_id"].unique()
    feeder_base_uptime = {fid: rng.uniform(0.85, 1.0) for fid in feeder_ids}

    month_num = grouped["month"].dt.month
    feeder_temp = 18 + 14 * np.sin(2 * np.pi * (month_num - 3) / 12) + rng.normal(0, 1.2, len(grouped))

    base_uptime = grouped["feeder_id"].map(feeder_base_uptime).to_numpy()
    pmt_uptime = np.clip(base_uptime + rng.normal(0, 0.03, len(grouped)), 0.5, 1.0)

    aggregate_load = grouped["billed_sum"].to_numpy() + grouped["stolen_sum"].to_numpy()
    technical_loss = 0.00006 * (aggregate_load ** 1.6)
    technical_loss = np.maximum(technical_loss, aggregate_load * 0.02)

    injected_energy = grouped["billed_sum"].to_numpy() + technical_loss + grouped["stolen_sum"].to_numpy()

    grouped["pmt_uptime_pct"] = np.round(pmt_uptime * 100, 2)
    grouped["avg_temp_c"] = np.round(feeder_temp, 1)
    grouped["injected_energy_kwh"] = np.round(injected_energy, 2)
    grouped["_technical_loss_kwh"] = np.round(technical_loss, 2)

    return grouped[
        ["pmt_id", "feeder_id", "month", "injected_energy_kwh", "pmt_uptime_pct", "avg_temp_c", "_technical_loss_kwh"]
    ]


def make_feeder_monthly(pmt_monthly: pd.DataFrame) -> pd.DataFrame:
    rollup = (
        pmt_monthly.groupby(["feeder_id", "month"], as_index=False)
        .agg(
            injected_energy_kwh=("injected_energy_kwh", "sum"),
            feeder_uptime_pct=("pmt_uptime_pct", "mean"),
            avg_temp_c=("avg_temp_c", "mean"),
        )
    )
    rollup["feeder_uptime_pct"] = rollup["feeder_uptime_pct"].round(2)
    rollup["avg_temp_c"] = rollup["avg_temp_c"].round(1)
    return rollup


# ---------------------------------------------------------------------------
# 6. Conservation constraint check
# ---------------------------------------------------------------------------
def assert_conservation(readings: pd.DataFrame, pmt_monthly: pd.DataFrame):
    check = (
        readings.groupby(["pmt_id", "month"])
        .agg(billed_sum=("billed_units_kwh", "sum"), stolen_sum=("stolen_units_kwh", "sum"))
        .reset_index()
        .merge(pmt_monthly, on=["pmt_id", "month"], how="inner")
    )
    reconstructed = check["billed_sum"] + check["_technical_loss_kwh"] + check["stolen_sum"]
    diff = (reconstructed - check["injected_energy_kwh"]).abs()
    assert diff.max() < 0.5, f"Conservation constraint violated, max diff={diff.max():.4f} kWh"
    print(f"Conservation constraint OK across {pmt_monthly['pmt_id'].nunique()} PMTs x {N_MONTHS} months "
          f"({len(check)} PMT-month rows checked).")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    months = pd.date_range(START_MONTH, periods=N_MONTHS, freq="MS")

    feeder_ids, pmts = make_grid()
    consumers = make_consumers(pmts)

    true_cons = true_consumption(consumers, months)
    true_cons = true_cons.merge(consumers[["consumer_id", "pmt_id", "feeder_id"]], on="consumer_id", how="left")

    readings = apply_anomalies(true_cons, consumers)

    pmt_monthly = make_pmt_monthly(readings, pmts, months)
    feeder_monthly = make_feeder_monthly(pmt_monthly)
    assert_conservation(readings, pmt_monthly)

    monthly_readings = readings[
        ["consumer_id", "month", "billed_units_kwh", "arrears_pkr", "reader_id",
         "is_theft_ground_truth", "theft_type"]
    ]
    consumers_out = consumers[
        ["consumer_id", "pmt_id", "feeder_id", "sanctioned_load_kw", "consumer_type",
         "meter_type", "is_registered_prosumer"]
    ]
    pmt_monthly_out = pmt_monthly.drop(columns=["_technical_loss_kwh"])

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    consumers_out.to_csv(os.path.join(OUTPUT_DIR, "consumers.csv"), index=False)
    pmt_monthly_out.to_csv(os.path.join(OUTPUT_DIR, "pmt_monthly.csv"), index=False)
    feeder_monthly.to_csv(os.path.join(OUTPUT_DIR, "feeder_monthly.csv"), index=False)
    monthly_readings.to_csv(os.path.join(OUTPUT_DIR, "monthly_readings.csv"), index=False)
    print(f"\nCSVs written to: {os.path.abspath(OUTPUT_DIR)}")

    print("\n--- Summary ---")
    print(f"Consumers: {len(consumers_out)} | PMTs: {len(pmts)} | Feeders: {len(feeder_ids)} | Months: {N_MONTHS}")
    print(consumers["archetype"].value_counts())
    print(f"Overall theft prevalence: {consumers['is_theft_ground_truth'].mean():.3%}")

    # quick clustering sanity check: theft-consumer density per PMT
    theft_per_pmt = consumers[consumers["is_theft_ground_truth"]].groupby("pmt_id").size()
    print(f"\nTheft consumers per PMT -- mean: {theft_per_pmt.mean():.2f}, "
          f"max: {theft_per_pmt.max()}, PMTs with 0 theft consumers: "
          f"{N_PMTS - theft_per_pmt.shape[0]}")
    print(f"Top 5 PMTs by theft-consumer count:\n{theft_per_pmt.sort_values(ascending=False).head(5)}")


if __name__ == "__main__":
    main()
