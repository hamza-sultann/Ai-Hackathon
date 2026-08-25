"""
Synthetic data generator — Track 1 (Monthly, 3-year), expanded hierarchy + taxonomy.

Grid hierarchy: Feeder (11kV) -> PMT (transformer) -> Consumer
  30 feeders x 10 PMTs/feeder = 300 PMTs, ~33 consumers/PMT = 10,000 consumers.

Outputs:
    consumers.csv        (10,000 rows)
    pmt_monthly.csv       (300 PMTs x 36 months = 10,800 rows)   -- primary totalizer table
    feeder_monthly.csv    (30 feeders x 36 months = 1,080 rows)  -- rollup of the above
    monthly_readings.csv  (10,000 x 36 = 360,000 rows)

Conservation constraint (per PMT per month, enforced by construction + re-checked):
    injected_energy = sum(billed on PMT) + technical_loss + sum(stolen on PMT)
"""

import numpy as np
import pandas as pd

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
N_COLLUSION_GROUPS = 5                           # 30 collusion users / ~6 per group

CONSUMER_TYPES = np.array(["residential", "commercial", "industrial"])
CONSUMER_TYPE_WEIGHTS = [0.80, 0.15, 0.05]
METER_TYPES = np.array(["analog", "electronic"])
METER_TYPE_WEIGHTS = [0.65, 0.35]

# ---------------------------------------------------------------------------
# 1. Archetype population (counts trimmed to sum exactly to N_CONSUMERS --
#    the source spec summed to 10,100; "standard" absorbs the 100-unit gap)
# ---------------------------------------------------------------------------
# (key, count, is_theft, is_prosumer, is_vacant, is_frugal)
ARCHETYPES = [
    ("standard",             7200, False, False, False, False),
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
]
assert sum(a[1] for a in ARCHETYPES) == N_CONSUMERS


# ---------------------------------------------------------------------------
# 2. Grid hierarchy tables
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


def make_consumers(pmts: pd.DataFrame) -> pd.DataFrame:
    consumer_ids = [f"C-{i:06d}" for i in range(1, N_CONSUMERS + 1)]
    pmt_assignment = rng.choice(pmts["pmt_id"].to_numpy(), size=N_CONSUMERS, replace=True)

    consumer_type = rng.choice(CONSUMER_TYPES, size=N_CONSUMERS, p=CONSUMER_TYPE_WEIGHTS)
    load_base = {"residential": (1.0, 8.0), "commercial": (5.0, 25.0), "industrial": (20.0, 100.0)}
    sanctioned_load_kw = np.array([rng.uniform(*load_base[ct]) for ct in consumer_type]).round(2)
    meter_type = rng.choice(METER_TYPES, size=N_CONSUMERS, p=METER_TYPE_WEIGHTS)

    reader_ids = [f"R-{i:03d}" for i in range(1, N_READERS + 1)]
    reader_id = rng.choice(reader_ids, size=N_CONSUMERS, replace=True)

    # archetype labels, shuffled across the population
    labels = np.concatenate([np.full(count, key) for key, count, *_ in ARCHETYPES])
    rng.shuffle(labels)

    consumers = pd.DataFrame(
        {
            "consumer_id": consumer_ids,
            "pmt_id": pmt_assignment,
            "sanctioned_load_kw": sanctioned_load_kw,
            "consumer_type": consumer_type,
            "meter_type": meter_type,
            "reader_id": reader_id,
            "archetype": labels,
        }
    )
    consumers = consumers.merge(pmts, on="pmt_id", how="left")  # brings in feeder_id

    flag_map = {key: (is_theft, is_pros, is_vac, is_frug) for key, _, is_theft, is_pros, is_vac, is_frug in ARCHETYPES}
    consumers["is_theft_ground_truth"] = consumers["archetype"].map(lambda a: flag_map[a][0])
    consumers["is_registered_prosumer"] = consumers["archetype"].map(lambda a: flag_map[a][1])
    consumers["theft_type"] = np.where(consumers["is_theft_ground_truth"], consumers["archetype"], "none")

    # collusion needs a shared corrupt reader per small group ("adjacent houses" simplified
    # to "shares a reader_id" -- true street-level adjacency isn't modeled here)
    collusion_idx = consumers.index[consumers["archetype"] == "collusion"].to_numpy().copy()
    rng.shuffle(collusion_idx)
    groups = np.array_split(collusion_idx, N_COLLUSION_GROUPS)
    for gi, group in enumerate(groups):
        corrupt_reader = f"R-COL-{gi + 1:02d}"
        consumers.loc[group, "reader_id"] = corrupt_reader

    return consumers.drop(columns=["archetype"]).assign(archetype=consumers["archetype"])


# ---------------------------------------------------------------------------
# 3. True consumption per consumer per month
# ---------------------------------------------------------------------------
def true_consumption(consumers: pd.DataFrame, months: pd.DatetimeIndex) -> pd.DataFrame:
    n = len(consumers)
    archetype = consumers["archetype"].to_numpy()

    # baseline kWh -- special low-baseline handling for vacant / frugal households,
    # log-normal (sanctioned-load-scaled) for everyone else
    mu = np.log(consumers["sanctioned_load_kw"].to_numpy() * 60)
    lognormal_baseline = rng.lognormal(mean=mu, sigma=0.35, size=n)

    vacant_baseline = rng.uniform(5, 15, n)
    frugal_baseline = rng.uniform(30, 60, n)

    baseline = np.where(
        archetype == "vacant", vacant_baseline,
        np.where(archetype == "low_income_frugal", frugal_baseline, lognormal_baseline),
    )

    # seasonal amplitude: dampened for vacant/frugal (they don't chase AC load the way
    # a normal household does), full for everyone else
    seasonal_amp = np.where(np.isin(archetype, ["vacant", "low_income_frugal"]), 0.05, 0.35)

    rows = []
    for m_idx, month in enumerate(months):
        month_num = month.month
        seasonal_mult = 1.0 + seasonal_amp * np.sin(2 * np.pi * (month_num - 3) / 12)
        noise = rng.normal(loc=1.0, scale=0.05, size=n)
        true_kwh = baseline * seasonal_mult * noise
        true_kwh = np.clip(true_kwh, 3, None)

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
                   "is_theft_ground_truth", "theft_type"]],
        on="consumer_id",
        how="left",
    )
    n = len(df)
    true_kwh = df["true_consumption_kwh"].to_numpy()
    arch = df["archetype"].to_numpy()
    billed = true_kwh.copy()

    def mask(key):
        return arch == key

    # -- legit populations: billed ~ true (small metering noise) --
    legit = np.isin(arch, ["standard", "vacant", "low_income_frugal"])
    billed[legit] = true_kwh[legit] * rng.uniform(0.96, 1.02, legit.sum())

    # -- solar/prosumer: grid import drops 70%+ (legit self-consumption/export) --
    m = mask("solar_prosumer")
    billed[m] = true_kwh[m] * rng.uniform(0.05, 0.30, m.sum())

    # -- kunda: 85-95% drop --
    m = mask("kunda")
    billed[m] = true_kwh[m] * rng.uniform(0.05, 0.15, m.sum())

    # -- slab defender: capped at 185-198 kWh regardless of true usage --
    m = mask("slab_defender")
    cap = rng.uniform(185, 198, m.sum())
    billed[m] = np.minimum(true_kwh[m], cap)

    # -- nighttime AC / heavy stealer: only the night portion is missing;
    #    monthly aggregate shows a modest, not dramatic, dip --
    m = mask("nighttime_ac")
    billed[m] = true_kwh[m] * rng.uniform(0.75, 0.85, m.sum())

    # -- peak-hour shaver: drop localized to a 4-hour window, smaller monthly dent --
    m = mask("peak_hour_shaver")
    billed[m] = true_kwh[m] * rng.uniform(0.88, 0.95, m.sum())

    # -- gradual mechanical slowdown: compounding 2-3%/month decay, floors at ~45% --
    m = mask("gradual_slowdown")
    idx_m = df.loc[m].index
    rate = rng.uniform(0.02, 0.03, m.sum())
    month_idx = df.loc[m, "month_idx"].to_numpy()
    decay_mult = np.maximum((1 - rate) ** month_idx, 0.45)
    billed[m] = true_kwh[m] * decay_mult

    # -- fixed gear shunt: flat 50% under-recording, every month --
    m = mask("fixed_shunt")
    billed[m] = true_kwh[m] * 0.50

    # -- intermittent appliance hookup: small, noisy ~8% dent --
    m = mask("intermittent_hookup")
    billed[m] = true_kwh[m] * rng.uniform(0.90, 0.94, m.sum())

    # -- collusion: systemic ~20% under-billing, tied to a corrupt reader_id --
    m = mask("collusion")
    billed[m] = true_kwh[m] * rng.uniform(0.78, 0.82, m.sum())

    billed = np.clip(billed, 0, None)
    df["billed_units_kwh"] = np.round(billed, 2)

    # stolen units only accrue for actual theft archetypes -- solar/vacant/frugal
    # gaps (if any) are legitimate and never counted against the PMT loss ledger
    theft_mask = df["is_theft_ground_truth"].to_numpy()
    stolen = np.zeros(n)
    stolen[theft_mask] = np.clip(true_kwh[theft_mask] - billed[theft_mask], 0, None)
    df["stolen_units_kwh"] = np.round(stolen, 2)

    df["arrears_pkr"] = np.round(rng.exponential(scale=1500, size=n), 2)
    return df


# ---------------------------------------------------------------------------
# 5. PMT-level aggregation (primary totalizer) + feeder-level rollup
# ---------------------------------------------------------------------------
def make_pmt_monthly(readings: pd.DataFrame, pmts: pd.DataFrame, months: pd.DatetimeIndex) -> pd.DataFrame:
    readings = readings.merge(
        readings[["consumer_id"]].drop_duplicates(), on="consumer_id", how="left"
    )  # no-op, keeps merge pattern consistent if extended later

    consumer_pmt = readings[["consumer_id"]].copy()
    # pull pmt_id via the consumers table join done upstream in main(); readings already
    # carries pmt_id/feeder_id by that point (see main()).
    grouped = (
        readings.groupby(["pmt_id", "feeder_id", "month"], as_index=False)
        .agg(billed_sum=("billed_units_kwh", "sum"), stolen_sum=("stolen_units_kwh", "sum"))
    )

    # feeder-level base uptime/temp per month (shared by all PMTs on that feeder),
    # PMT-level uptime perturbed around it
    feeder_ids = pmts["feeder_id"].unique()
    feeder_base_uptime = {fid: rng.uniform(0.85, 1.0) for fid in feeder_ids}

    month_num = grouped["month"].dt.month
    feeder_temp = 18 + 14 * np.sin(2 * np.pi * (month_num - 3) / 12) + rng.normal(0, 1.2, len(grouped))

    base_uptime = grouped["feeder_id"].map(feeder_base_uptime).to_numpy()
    pmt_uptime = np.clip(base_uptime + rng.normal(0, 0.03, len(grouped)), 0.5, 1.0)

    aggregate_load = grouped["billed_sum"].to_numpy() + grouped["stolen_sum"].to_numpy()
    technical_loss = 0.00006 * (aggregate_load ** 1.6)          # PMT-scale I^2Rt-style approx
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
# 6. Conservation constraint check (vectorized, run on every batch)
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

    consumers_out.to_csv("/mnt/user-data/outputs/consumers.csv", index=False)
    pmt_monthly_out.to_csv("/mnt/user-data/outputs/pmt_monthly.csv", index=False)
    feeder_monthly.to_csv("/mnt/user-data/outputs/feeder_monthly.csv", index=False)
    monthly_readings.to_csv("/mnt/user-data/outputs/monthly_readings.csv", index=False)

    print("\n--- Summary ---")
    print(f"Consumers: {len(consumers_out)} | PMTs: {len(pmts)} | Feeders: {len(feeder_ids)} | Months: {N_MONTHS}")
    print(f"monthly_readings rows: {len(monthly_readings):,}")
    print(consumers["archetype"].value_counts())
    print(f"Overall theft prevalence: {consumers['is_theft_ground_truth'].mean():.3%}")


if __name__ == "__main__":
    main()
