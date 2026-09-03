"""Feature engineering for the risk model.

A trimmed, dependency-light port of the Track 1 features in
`Ai-Hackathon-agentic/features.py` (same signals, same intent). No ground-truth
columns are ever read here.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

# The engineered columns fed to the model, with human-readable phrasing reused
# for field alerts / SHAP-style explanations.
FEATURE_DESCRIPTIONS: dict[str, str] = {
    "pmt_loss_delta_pct": "feeder/PMT-level unaccounted energy is unusually high this month",
    "pmt_loss_rank": "this PMT ranks among the worst in the grid for energy loss",
    "usage_deviation": "billed usage dropped sharply versus the recent 6-month baseline",
    "fixed_baseline_deviation": "consumption collapsed versus the clean first-3-month reference",
    "cusum_max_deviation": "a statistically significant structural break was detected in consumption",
    "months_since_detected_break": "the deficit has persisted continuously since the change-point",
    "peer_deviation": "usage is far below similar peers on the same feeder and load class",
    "arrears_ratio": "the account carries an abnormally high unpaid balance",
    "seasonal_residual": "usage defies this consumer's own seasonal pattern",
    "rolling_trend_3mo": "a sustained downward trend over recent months",
    "feeder_uptime_adj_deviation": "usage dropped despite steady PMT uptime (not load-shedding)",
    "prosumer_gated_usage_deviation": "unexplained drop not attributable to registered solar",
    "iso_forest_score": "the multivariate consumption profile matches rare anomaly patterns",
    "peak_offpeak_ratio": "smart-meter peak vs off-peak ratio is distorted (possible peak shaving)",
    "peak_window_flatline_fraction": "the meter reads near-zero during peak tariff hours",
    "nighttime_drop_index": "night-time consumption drops abnormally (possible night AC theft)",
}

BASE_FEATURES: list[str] = [
    "pmt_loss_delta_pct",
    "pmt_loss_rank",
    "usage_deviation",
    "fixed_baseline_deviation",
    "cusum_max_deviation",
    "months_since_detected_break",
    "peer_deviation",
    "arrears_ratio",
    "seasonal_residual",
    "rolling_trend_3mo",
    "feeder_uptime_adj_deviation",
    "prosumer_gated_usage_deviation",
]

TRACK2_FEATURES: list[str] = [
    "peak_offpeak_ratio",
    "peak_window_flatline_fraction",
    "nighttime_drop_index",
]

MODEL_FEATURES: list[str] = BASE_FEATURES + ["iso_forest_score"] + TRACK2_FEATURES


def build_features(panel: pd.DataFrame, track2: pd.DataFrame | None = None) -> pd.DataFrame:
    df = panel.copy()
    df["month"] = pd.to_datetime(df["month"])
    df = df.sort_values(["consumer_id", "month"]).reset_index(drop=True)

    # 1. PMT-level loss + percentile rank across PMTs per month
    pmt_billed = (
        df.groupby(["pmt_id", "month"])["billed_units_kwh"].sum().rename("pmt_total_billed").reset_index()
    )
    df = df.merge(pmt_billed, on=["pmt_id", "month"], how="left")
    df["pmt_loss_delta_pct"] = (
        (df["injected_energy_kwh"] - df["pmt_total_billed"]) / df["injected_energy_kwh"].replace(0, np.nan)
    )
    loss = df[["pmt_id", "month", "pmt_loss_delta_pct"]].drop_duplicates()
    loss["pmt_loss_rank"] = loss.groupby("month")["pmt_loss_delta_pct"].rank(pct=True)
    df = df.merge(loss[["pmt_id", "month", "pmt_loss_rank"]], on=["pmt_id", "month"], how="left")
    df.drop(columns=["pmt_total_billed"], inplace=True)

    grp = df.groupby("consumer_id")["billed_units_kwh"]

    # 2. Trailing 6-month rolling-mean deviation
    rolling_mean = grp.transform(lambda x: x.shift(1).rolling(6, min_periods=2).mean())
    df["usage_deviation"] = np.where(
        rolling_mean.isna() | (rolling_mean == 0),
        np.nan,
        (df["billed_units_kwh"] - rolling_mean) / rolling_mean,
    )

    # 3. Fixed first-3-month anchor deviation
    first3 = grp.transform(lambda x: x.head(3).mean())
    df["fixed_baseline_deviation"] = np.where(
        first3.isna() | (first3 <= 0), np.nan, (df["billed_units_kwh"] - first3) / first3
    )

    # 4. CUSUM structural-break features
    _add_cusum(df)

    # 5. Peer deviation: z-score within (feeder, consumer_type, month)
    def _z(x: pd.Series) -> pd.Series:
        std = x.std(ddof=1)
        if len(x) < 2 or not std or np.isnan(std):
            return pd.Series(0.0, index=x.index)
        return (x - x.mean()) / std

    df["peer_deviation"] = df.groupby(["feeder_id", "consumer_type", "month"])[
        "billed_units_kwh"
    ].transform(_z)

    # 6. Annualised arrears ratio
    mean_usage = grp.transform("mean")
    df["arrears_ratio"] = (df["arrears_pkr"] / (12 * mean_usage.replace(0, np.nan))).clip(0, 10)

    # 7. Seasonal residual (own calendar-month baseline), normalised
    df["_moy"] = df["month"].dt.month
    seasonal_baseline = df.groupby(["consumer_id", "_moy"])["billed_units_kwh"].transform("mean")
    df["seasonal_residual"] = (df["billed_units_kwh"] - seasonal_baseline) / seasonal_baseline.replace(0, np.nan)
    df.drop(columns=["_moy"], inplace=True)

    # 8. 3-month trajectory slope (normalised by own mean)
    df["rolling_trend_3mo"] = grp.transform(lambda x: (x - x.shift(3)) / 3.0) / mean_usage.replace(0, np.nan)

    # 9. Load-shedding-adjusted deviation
    uptime = (df["pmt_uptime_pct"] / 100.0).clip(lower=0.5).fillna(1.0)
    df["feeder_uptime_adj_deviation"] = df["usage_deviation"] / uptime

    # 10. Prosumer-gated deviation
    df["prosumer_gated_usage_deviation"] = np.where(
        df["is_registered_prosumer"].fillna(False).astype(bool), 0.0, df["usage_deviation"]
    )

    # 11. Track 2 (AMI) signals, when available
    if track2 is not None:
        cols = ["consumer_id", "month"] + [c for c in TRACK2_FEATURES if c in track2.columns]
        df = df.merge(track2[cols], on=["consumer_id", "month"], how="left")
    for c in TRACK2_FEATURES:
        if c not in df.columns:
            df[c] = np.nan

    return df


def _add_cusum(df: pd.DataFrame) -> None:
    counts = df.groupby("consumer_id", sort=False).size()
    n_months = int(counts.iloc[0])
    if (counts == n_months).all():
        n = len(counts)
        vals = df["billed_units_kwh"].to_numpy().reshape(n, n_months)
        cmax = np.zeros((n, n_months))
        msince = np.zeros((n, n_months))
        for t in range(2, n_months):
            sub = vals[:, : t + 1]
            mean_t = sub.mean(axis=1, keepdims=True)
            s = np.cumsum(sub - mean_t, axis=1)
            abs_s = np.abs(s)
            k = np.argmax(abs_s, axis=1)
            peak = np.take_along_axis(abs_s, k[:, None], axis=1).squeeze(1)
            denom = np.where(mean_t.squeeze(1) > 0, mean_t.squeeze(1), 1.0)
            cmax[:, t] = peak / denom
            msince[:, t] = t - k
        df["cusum_max_deviation"] = cmax.ravel()
        df["months_since_detected_break"] = msince.ravel()
    else:  # variable-length fallback
        def _single(s: pd.Series) -> pd.DataFrame:
            v = s.to_numpy()
            n = len(v)
            cm = np.zeros(n)
            ms = np.zeros(n)
            for t in range(2, n):
                sub = v[: t + 1]
                m = sub.mean()
                if m <= 0:
                    continue
                cum = np.abs(np.cumsum(sub - m))
                k = int(np.argmax(cum))
                cm[t] = cum[k] / m
                ms[t] = t - k
            return pd.DataFrame(
                {"cusum_max_deviation": cm, "months_since_detected_break": ms}, index=s.index
            )

        res = df.groupby("consumer_id", group_keys=False)["billed_units_kwh"].apply(_single)
        df["cusum_max_deviation"] = res["cusum_max_deviation"]
        df["months_since_detected_break"] = res["months_since_detected_break"]
