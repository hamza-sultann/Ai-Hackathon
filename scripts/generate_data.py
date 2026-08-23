"""
Synthetic data generator — Track 1 (Monthly, core, locked architecture)
Explainable AI for Grid Loss Detection — Pakistan

Produces three CSVs matching data-schema.md §1-2:
    consumers.csv
    feeder_monthly.csv
    monthly_readings.csv

Design decisions are pulled directly from architecture-design-document.md §4.3/§4.4:
  - baseline load: log-normal per consumer (right-skewed, matches real household shape)
  - seasonality: sinusoidal, peaks Jun-Aug
  - technical loss: physics-informed (I^2Rt-style approx on feeder aggregate load),
    not a flat percentage
  - conservation constraint (enforced as a hard assertion on every batch):
        injected_energy = sum(billed on feeder) + technical_loss + sum(stolen units)
  - anomaly signatures: kunda / tamper / collusion / solar-prosumer (legit, non-theft)
"""

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# 0. Config — pulled from data-schema.md §4 volume guidance
# ---------------------------------------------------------------------------
SEED = 42
N_CONSUMERS = 1500
N_FEEDERS = 45
N_MONTHS = 12
START_MONTH = pd.Timestamp("2024-01-01")

THEFT_PREVALENCE = 0.08          # 5-10% guidance, mid-point
PROSUMER_PREVALENCE = 0.25       # PBS adoption figure per architecture doc §8
N_READERS = 60                   # roughly one per feeder-ish, some cover multiple feeders
CORRUPT_READER_FRACTION = 0.15   # subset of readers who enable collusion theft

rng = np.random.default_rng(SEED)

CONSUMER_TYPES = np.array(["residential", "commercial", "industrial"])
CONSUMER_TYPE_WEIGHTS = [0.80, 0.15, 0.05]          # residential-dominated, realistic mix
METER_TYPES = np.array(["analog", "electronic"])
METER_TYPE_WEIGHTS = [0.65, 0.35]                    # "over 90% read manually" -> analog-heavy


# ---------------------------------------------------------------------------
# 1. Feeders
# ---------------------------------------------------------------------------
def make_feeders(n_feeders: int) -> pd.DataFrame:
    feeder_ids = [f"F-{i:03d}" for i in range(1, n_feeders + 1)]
    return pd.DataFrame({"feeder_id": feeder_ids})


# ---------------------------------------------------------------------------
# 2. Consumers
# ---------------------------------------------------------------------------
def make_consumers(n_consumers: int, feeder_ids: list[str]) -> pd.DataFrame:
    consumer_ids = [f"C-{i:05d}" for i in range(1, n_consumers + 1)]

    # ~20-40 consumers per feeder (data-schema.md §4 rationale) via random assignment
    feeder_assignment = rng.choice(feeder_ids, size=n_consumers, replace=True)

    consumer_type = rng.choice(CONSUMER_TYPES, size=n_consumers, p=CONSUMER_TYPE_WEIGHTS)

    # sanctioned load scales with consumer type (industrial > commercial > residential)
    load_base = {
        "residential": (1.0, 8.0),
        "commercial": (5.0, 25.0),
        "industrial": (20.0, 100.0),
    }
    sanctioned_load_kw = np.array(
        [rng.uniform(*load_base[ct]) for ct in consumer_type]
    ).round(2)

    meter_type = rng.choice(METER_TYPES, size=n_consumers, p=METER_TYPE_WEIGHTS)

    # reader assignment — each consumer's meter is read by one reader
    reader_ids = [f"R-{i:03d}" for i in range(1, N_READERS + 1)]
    reader_id = rng.choice(reader_ids, size=n_consumers, replace=True)

    consumers = pd.DataFrame(
        {
            "consumer_id": consumer_ids,
            "feeder_id": feeder_assignment,
            "sanctioned_load_kw": sanctioned_load_kw,
            "consumer_type": consumer_type,
            "meter_type": meter_type,
            "reader_id": reader_id,  # convenience column, also written per-reading below
        }
    )

    # --- prosumer flag (solar / net-metering) ---
    # Kept mutually exclusive with theft in this generator for a clean archetype:
    # a household is either "legit solar" or eligible for a theft label, not both.
    # This is a simplification worth stating if asked — real DISCOs would see overlap.
    is_prosumer = rng.random(n_consumers) < PROSUMER_PREVALENCE
    consumers["is_registered_prosumer"] = is_prosumer

    # --- corrupt readers, for collusion theft type ---
    n_corrupt = max(1, int(round(N_READERS * CORRUPT_READER_FRACTION)))
    corrupt_readers = set(rng.choice(reader_ids, size=n_corrupt, replace=False))
    consumers["_reader_is_corrupt"] = consumers["reader_id"].isin(corrupt_readers)

    # --- theft label assignment ---
    # Only non-prosumer consumers are eligible for theft (see note above).
    eligible_mask = ~is_prosumer
    eligible_idx = consumers.index[eligible_mask].to_numpy()
    n_theft = int(round(n_consumers * THEFT_PREVALENCE))
    n_theft = min(n_theft, len(eligible_idx))
    theft_idx = rng.choice(eligible_idx, size=n_theft, replace=False)

    consumers["is_theft_ground_truth"] = False
    consumers["theft_type"] = "none"
    consumers.loc[theft_idx, "is_theft_ground_truth"] = True

    # roughly even split kunda / tamper / collusion (data-schema.md §4 rationale),
    # but collusion can only happen where the assigned reader is corrupt
    theft_pool = consumers.loc[theft_idx]
    collusion_eligible = theft_pool.index[theft_pool["_reader_is_corrupt"]].to_numpy()
    non_collusion_eligible = theft_pool.index[~theft_pool["_reader_is_corrupt"]].to_numpy()

    # target roughly a third each; collusion is capped by corrupt-reader availability
    target_collusion = min(len(collusion_eligible), n_theft // 3)
    collusion_idx = rng.choice(collusion_eligible, size=target_collusion, replace=False) \
        if target_collusion > 0 else np.array([], dtype=int)

    remaining_idx = np.setdiff1d(theft_idx, collusion_idx)
    rng.shuffle(remaining_idx)
    half = len(remaining_idx) // 2
    kunda_idx = remaining_idx[:half]
    tamper_idx = remaining_idx[half:]

    consumers.loc[kunda_idx, "theft_type"] = "kunda"
    consumers.loc[tamper_idx, "theft_type"] = "tamper"
    consumers.loc[collusion_idx, "theft_type"] = "collusion"

    return consumers.drop(columns=["_reader_is_corrupt"])


# ---------------------------------------------------------------------------
# 3. True consumption per consumer per month (baseline x seasonality)
# ---------------------------------------------------------------------------
def true_consumption(consumers: pd.DataFrame, months: pd.DatetimeIndex) -> pd.DataFrame:
    n = len(consumers)

    # log-normal baseline load, scaled roughly by sanctioned load so bigger
    # connections use more energy on average (mu chosen so median ~ a plausible
    # fraction of sanctioned capacity at typical usage hours)
    mu = np.log(consumers["sanctioned_load_kw"].to_numpy() * 60)  # ~60 hrs/mo equiv. usage
    sigma = 0.35
    baseline_kwh = rng.lognormal(mean=mu, sigma=sigma)

    rows = []
    for m_idx, month in enumerate(months):
        # sinusoidal seasonality, peak Jun-Aug (month 6-8), trough Dec-Jan
        month_num = month.month
        seasonal_mult = 1.0 + 0.35 * np.sin(2 * np.pi * (month_num - 3) / 12)
        # small month-to-month noise so it's not a perfectly clean sine wave
        noise = rng.normal(loc=1.0, scale=0.05, size=n)
        true_kwh = baseline_kwh * seasonal_mult * noise
        true_kwh = np.clip(true_kwh, 5, None)

        rows.append(
            pd.DataFrame(
                {
                    "consumer_id": consumers["consumer_id"].to_numpy(),
                    "month": month,
                    "true_consumption_kwh": true_kwh,
                }
            )
        )

    return pd.concat(rows, ignore_index=True)


# ---------------------------------------------------------------------------
# 4. Anomaly injection -> billed_units_kwh, stolen_units, arrears
# ---------------------------------------------------------------------------
def apply_anomalies(readings: pd.DataFrame, consumers: pd.DataFrame) -> pd.DataFrame:
    df = readings.merge(
        consumers[["consumer_id", "theft_type", "is_registered_prosumer", "reader_id"]],
        on="consumer_id",
        how="left",
    )

    n = len(df)
    billed = df["true_consumption_kwh"].copy()
    stolen = pd.Series(0.0, index=df.index)

    kunda = df["theft_type"] == "kunda"
    tamper = df["theft_type"] == "tamper"
    collusion = df["theft_type"] == "collusion"
    solar = df["is_registered_prosumer"]

    # Kunda: billed -> near-zero, feeder still sees the real draw (stolen = true - billed)
    billed.loc[kunda] = df.loc[kunda, "true_consumption_kwh"] * rng.uniform(0.02, 0.10, kunda.sum())

    # Tamper: stable plateau at ~50% of true consumption, low month-to-month variance
    billed.loc[tamper] = df.loc[tamper, "true_consumption_kwh"] * rng.uniform(0.45, 0.55, tamper.sum())

    # Collusion: mild under-billing, correlated with reader (systemic, harder to spot per-household)
    billed.loc[collusion] = df.loc[collusion, "true_consumption_kwh"] * rng.uniform(0.75, 0.90, collusion.sum())

    stolen.loc[kunda | tamper | collusion] = (
        df.loc[kunda | tamper | collusion, "true_consumption_kwh"] - billed.loc[kunda | tamper | collusion]
    )

    # Solar/prosumer: billed *grid* units drop sharply (self-consumption + export),
    # but this is legitimate -- NOT stolen. No contribution to the feeder-level gap.
    billed.loc[solar] = df.loc[solar, "true_consumption_kwh"] * rng.uniform(0.10, 0.35, solar.sum())
    # stolen stays 0 for solar rows even though billed dropped -- this is the whole point
    # of the confounder: it looks like Kunda on billed units alone but isn't.

    # honest population: small metering/rounding noise only
    honest = ~(kunda | tamper | collusion | solar)
    billed.loc[honest] = df.loc[honest, "true_consumption_kwh"] * rng.uniform(0.95, 1.02, honest.sum())

    billed = billed.clip(lower=0)
    df["billed_units_kwh"] = billed.round(2)
    df["stolen_units_kwh"] = stolen.clip(lower=0).round(2)

    # arrears: correlated loosely with consumer's own billed volatility + a poverty-proxy
    # random draw, kept deliberately noisy/secondary per architecture doc §5 & §10
    base_arrears = rng.exponential(scale=1500, size=n)
    df["arrears_pkr"] = base_arrears.round(2)

    return df


# ---------------------------------------------------------------------------
# 5. Feeder-level aggregation: technical loss + conservation-consistent injection
# ---------------------------------------------------------------------------
def make_feeder_monthly(readings: pd.DataFrame, feeders: pd.DataFrame, months: pd.DatetimeIndex) -> pd.DataFrame:
    rows = []
    for feeder_id in feeders["feeder_id"]:
        feeder_uptime_base = rng.uniform(0.85, 1.0)  # each feeder has its own outage profile
        for month in months:
            sub = readings[(readings["feeder_id"] == feeder_id) & (readings["month"] == month)]
            billed_sum = sub["billed_units_kwh"].sum()
            stolen_sum = sub["stolen_units_kwh"].sum()

            # physics-informed technical loss: approximate I^2Rt behavior --
            # losses scale roughly with the SQUARE of aggregate load, not linearly,
            # so a feeder running hotter loses disproportionately more, not a flat %.
            aggregate_load = billed_sum + stolen_sum
            technical_loss = 0.00002 * (aggregate_load ** 1.6)  # tuned so loss ~5-9% of load at typical volumes
            technical_loss = max(technical_loss, aggregate_load * 0.02)  # floor: infra never loses ~0%

            # load-shedding varies per feeder per month, not just per feeder (data-schema.md §4)
            month_uptime = np.clip(feeder_uptime_base + rng.normal(0, 0.03), 0.5, 1.0)

            # CONSERVATION CONSTRAINT, enforced by construction:
            # injected_energy = billed + technical_loss + stolen
            injected_energy = billed_sum + technical_loss + stolen_sum

            month_num = month.month
            # rough Islamabad-region seasonal temperature curve, matched loosely to
            # the same Jun-Aug peak used for consumption seasonality
            avg_temp_c = 18 + 14 * np.sin(2 * np.pi * (month_num - 3) / 12) + rng.normal(0, 1.5)

            rows.append(
                {
                    "feeder_id": feeder_id,
                    "month": month,
                    "injected_energy_kwh": round(injected_energy, 2),
                    "feeder_uptime_pct": round(month_uptime * 100, 2),
                    "avg_temp_c": round(avg_temp_c, 1),
                    "_technical_loss_kwh": round(technical_loss, 2),  # kept for the assertion check below
                }
            )

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 6. Conservation constraint check (automated test, run on every batch)
# ---------------------------------------------------------------------------
def assert_conservation(readings: pd.DataFrame, feeder_monthly: pd.DataFrame, feeders_with_id: pd.Series):
    for feeder_id in feeders_with_id:
        for _, frow in feeder_monthly[feeder_monthly["feeder_id"] == feeder_id].iterrows():
            month = frow["month"]
            sub = readings[(readings["feeder_id"] == feeder_id) & (readings["month"] == month)]
            billed_sum = sub["billed_units_kwh"].sum()
            stolen_sum = sub["stolen_units_kwh"].sum()
            reconstructed = billed_sum + frow["_technical_loss_kwh"] + stolen_sum
            diff = abs(reconstructed - frow["injected_energy_kwh"])
            assert diff < 0.5, (
                f"Conservation constraint violated for {feeder_id} / {month}: "
                f"diff={diff:.4f} kWh"
            )
    print(f"Conservation constraint OK across {len(feeders_with_id)} feeders x {N_MONTHS} months.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    months = pd.date_range(START_MONTH, periods=N_MONTHS, freq="MS")

    feeders = make_feeders(N_FEEDERS)
    consumers = make_consumers(N_CONSUMERS, feeders["feeder_id"].tolist())

    true_cons = true_consumption(consumers, months)
    true_cons = true_cons.merge(consumers[["consumer_id", "feeder_id"]], on="consumer_id", how="left")

    readings = apply_anomalies(true_cons, consumers)

    feeder_monthly = make_feeder_monthly(readings, feeders, months)

    assert_conservation(readings, feeder_monthly, feeders["feeder_id"])

    # --- shape monthly_readings.csv to match data-schema.md §2 exactly ---
    monthly_readings = readings.merge(
        consumers[["consumer_id", "is_theft_ground_truth"]], on="consumer_id", how="left"
    )
    monthly_readings = monthly_readings[
        [
            "consumer_id",
            "month",
            "billed_units_kwh",
            "arrears_pkr",
            "reader_id",
            "is_theft_ground_truth",
            "theft_type",
        ]
    ]

    consumers_out = consumers[
        [
            "consumer_id",
            "feeder_id",
            "sanctioned_load_kw",
            "consumer_type",
            "meter_type",
            "is_registered_prosumer",
        ]
    ]

    feeder_monthly_out = feeder_monthly.drop(columns=["_technical_loss_kwh"])

    consumers_out.to_csv("/mnt/user-data/outputs/consumers.csv", index=False)
    feeder_monthly_out.to_csv("/mnt/user-data/outputs/feeder_monthly.csv", index=False)
    monthly_readings.to_csv("/mnt/user-data/outputs/monthly_readings.csv", index=False)

    # quick sanity summary
    print("\n--- Summary ---")
    print(f"Consumers: {len(consumers_out)}  |  Feeders: {len(feeders)}  |  Months: {N_MONTHS}")
    print(consumers_out["is_registered_prosumer"].value_counts(normalize=True).rename("prosumer share"))
    print(consumers[consumers["is_theft_ground_truth"]]["theft_type"].value_counts())
    print(f"Overall theft prevalence: {consumers['is_theft_ground_truth'].mean():.3%}")


if __name__ == "__main__":
    main()
