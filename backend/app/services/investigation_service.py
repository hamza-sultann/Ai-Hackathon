"""Investigation queue, case detail, explainability, and reading history."""
from __future__ import annotations

import functools
import math
from datetime import datetime

import numpy as np
import pandas as pd
import pyarrow.dataset as pa_ds

from app.agents.dispatcher import DispatchResult, run_dispatch
from app.config import get_settings
from app.data.loader import get_data
from app.db import get_finding, get_job_card
from app.ml.scorer import RiskScore, get_scorer
from app.schemas import (
    HourlyReading,
    Investigation,
    MonthlyReading,
    RiskExplanation,
    SafeguardCheck,
    ShapFeatureContribution,
)
from app.services import labels
from app.services.metrics import context, split_gap

MAX_QUEUE = 200
PEAK_HOURS = {18, 19, 20, 21}

# Priority / strength tiers on the *calibrated* probability scale. The real
# Track-1 XGBoost calibrator compresses probabilities (observed max ~0.73, true-
# theft consumers cluster ~0.48-0.73), so these sit lower than raw-classifier
# intuition. 0.50 is the operating point run_pipeline.py evaluates at.
HIGH_TIER = 0.62
MEDIUM_TIER = 0.50

FEATURE_LABELS: dict[str, str] = {
    "pmt_loss_delta_pct": "PMT Unaccounted-Energy Gap",
    "pmt_loss_rank": "PMT Loss Percentile Rank",
    "usage_deviation": "6-Month Rolling Usage Deviation",
    "fixed_baseline_deviation": "Deviation vs Clean Baseline",
    "cusum_max_deviation": "CUSUM Structural Break",
    "months_since_detected_break": "Months Since Change-Point",
    "peer_deviation": "Peer-Group Usage Deviation",
    "arrears_ratio": "Arrears-to-Billing Ratio",
    "seasonal_residual": "Seasonal Pattern Residual",
    "rolling_trend_3mo": "3-Month Consumption Trend",
    "feeder_uptime_adj_deviation": "Uptime-Adjusted Usage Deviation",
    "prosumer_gated_usage_deviation": "Solar-Gated Usage Deviation",
    "iso_forest_score": "Isolation Forest Anomaly Score",
    "peak_offpeak_ratio": "Peak / Off-Peak Ratio (AMI)",
    "peak_window_flatline_fraction": "Peak-Window Flatline Fraction (AMI)",
    "nighttime_drop_index": "Night-Time Drop Index (AMI)",
}

_PATTERN_BY_FEATURE: dict[str, str] = {
    "peak_window_flatline_fraction": "Peak-Hour Deviation",
    "peak_offpeak_ratio": "Peak-Hour Deviation",
    "nighttime_drop_index": "Night-Time Load Drop",
    "cusum_max_deviation": "Step-Down Trend Shift",
    "months_since_detected_break": "Step-Down Trend Shift",
    "usage_deviation": "Sustained Usage Decline",
    "rolling_trend_3mo": "Sustained Usage Decline",
    "fixed_baseline_deviation": "Sustained Usage Decline",
    "pmt_loss_rank": "PMT Loss Cluster",
    "pmt_loss_delta_pct": "PMT Loss Cluster",
    "peer_deviation": "Peer-Group Outlier",
    "arrears_ratio": "Arrears-Linked Anomaly",
    "seasonal_residual": "Seasonal Pattern Break",
    "iso_forest_score": "Multivariate Anomaly",
}


# ---------------------------------------------------------------------------
# Queue + detail
# ---------------------------------------------------------------------------
def list_investigations(limit: int = MAX_QUEUE) -> list[Investigation]:
    ctx = context()
    flagged = ctx.latest[ctx.latest["priority_flag"]].sort_values("probability", ascending=False)
    out: list[Investigation] = []
    for consumer_id in flagged.index[:limit]:
        inv = _investigation(consumer_id, ctx)
        if inv is not None:
            out.append(inv)
    return out


def get_investigation(consumer_id: str) -> Investigation | None:
    return _investigation(consumer_id, context())


def _investigation(consumer_id: str, ctx) -> Investigation | None:
    data = get_data()
    consumer = data.consumer(consumer_id)
    if consumer is None:
        return None
    score = get_scorer().explain(consumer_id)
    if score is None:
        return None

    dispatch = _dispatch_for(consumer_id, score, consumer, ctx)
    prob = score.probability
    monthly_p = score.monthly_probability
    smart_p = score.smart_meter_probability

    top_feature = score.contributions[0].feature if score.contributions else ""
    pattern = _PATTERN_BY_FEATURE.get(top_feature, "Consumption Anomaly")

    impact = _estimated_impact(consumer_id, ctx)

    return Investigation(
        id=f"INV-{consumer_id.split('-')[-1]}",
        consumer_id=consumer_id,
        meter_id=labels.meter_id(consumer_id),
        feeder_id=consumer["feeder_id"],
        pmt_id=consumer["pmt_id"],
        priority=_priority(prob),
        calibrated_risk_percentage=round(prob * 100, 1),
        estimated_impact_kwh_month=round(impact, 1),
        pattern_name=pattern,
        evidence_source=_evidence_source(score),
        safeguard_status=_safeguard_status(dispatch),
        case_status=_case_status(consumer_id),
        monthly_risk_percentage=round(monthly_p * 100, 1),
        smart_meter_risk_percentage=round(smart_p * 100, 1),
        combined_evidence_strength=_strength(prob),
        pipeline_agreement=_pipeline_agreement(score),
        last_updated=datetime.now().strftime("%Y-%m-%d %H:%M PKT"),
        analyst_notes=dispatch.analyst_summary or None,
    )


# ---------------------------------------------------------------------------
# Explanation
# ---------------------------------------------------------------------------
def get_explanation(consumer_id: str) -> RiskExplanation | None:
    ctx = context()
    data = get_data()
    consumer = data.consumer(consumer_id)
    if consumer is None:
        return None
    score = get_scorer().explain(consumer_id)
    if score is None:
        return None
    dispatch = _dispatch_for(consumer_id, score, consumer, ctx, include_urdu=True)

    contributions = []
    for c in score.contributions[:6]:
        val_txt = "" if math.isnan(c.raw_value) else f" (observed value {c.raw_value:+.2f})"
        contributions.append(
            ShapFeatureContribution(
                feature_name=FEATURE_LABELS.get(c.feature, c.feature),
                contribution_value=round(c.contribution, 3),
                description=f"{c.description.capitalize()}{val_txt}.",
                direction=c.direction,
            )
        )

    return RiskExplanation(
        consumer_id=consumer_id,
        summary_text=dispatch.analyst_summary
        or f"Calibrated theft probability {score.probability:.0%} for {consumer_id}.",
        tree_shap_contributions=contributions,
        pmt_corroboration_text=dispatch.pmt_corroboration or "No PMT corroboration available.",
        safeguards=[
            SafeguardCheck(id=s.id, name=s.name, passed=s.passed, detail=s.detail)
            for s in dispatch.safeguards
        ],
        field_alert=dispatch.field_alert,
        field_alert_urdu=dispatch.field_alert_urdu,
        routing_decision=dispatch.routing_decision,
        cancelled=dispatch.cancelled,
        is_recidivist=dispatch.is_recidivist,
        is_duplicate=dispatch.is_duplicate,
        effective_probability=round(dispatch.effective_probability, 4),
    )


# ---------------------------------------------------------------------------
# Reading history
# ---------------------------------------------------------------------------
def get_monthly_readings(consumer_id: str) -> list[MonthlyReading] | None:
    data = get_data()
    if data.consumer(consumer_id) is None:
        return None
    scorer = get_scorer()
    sub = scorer.scored_for(consumer_id).sort_values("month")
    if sub.empty:
        return None

    first3 = sub["billed_units_kwh"].head(3).mean()
    ctype = data.consumer(consumer_id).get("consumer_type", "residential")
    feeder = data.consumer(consumer_id)["feeder_id"]
    scored = scorer.scored
    peer = scored[(scored["feeder_id"] == feeder) & (scored["consumer_type"] == ctype)]
    peer_median = peer.groupby("month")["billed_units_kwh"].median()

    out: list[MonthlyReading] = []
    for _, r in sub.iterrows():
        month = pd.Timestamp(r["month"])
        dev = r.get("usage_deviation")
        abnormal = (pd.notna(dev) and dev < -0.3) or (first3 and r["billed_units_kwh"] < 0.6 * first3)
        out.append(
            MonthlyReading(
                month_year=month.strftime("%Y-%m"),
                billed_kwh=round(float(r["billed_units_kwh"]), 1),
                expected_kwh=round(float(first3) if first3 else float(r["billed_units_kwh"]), 1),
                peer_median_kwh=round(float(peer_median.get(month, r["billed_units_kwh"])), 1),
                is_abnormal=bool(abnormal),
            )
        )
    return out


def get_hourly_readings(consumer_id: str) -> list[HourlyReading] | None:
    """Representative 24-hour profile for the analysis month.

    Real AMI consumers are served from the actual 1-hour interval stream
    (`interval_readings.parquet`, produced by root `generate_intervals.py`)
    when it's present locally. For consumers without a real smart meter (or
    if the interval file hasn't been generated), this falls back to a
    reconstructed diurnal curve from the monthly total and the Track-2
    aggregate features (peak flatline / night-drop), scaled to daily kWh.
    """
    ctx = context()
    data = get_data()
    if data.consumer(consumer_id) is None:
        return None
    sub = get_scorer().scored_for(consumer_id)
    row = sub[sub["month"] == ctx.month]
    if row.empty:
        return None
    row = row.iloc[0]

    daily = float(row["billed_units_kwh"]) / 30.0
    is_flagged = consumer_id in ctx.flagged_consumer_ids

    real = _real_hourly_profile(consumer_id, ctx.month) if data.has_ami(consumer_id) else None
    if real is not None:
        actual, expected = real
    else:
        shape = _diurnal_shape()
        peak_flatline = _num(row.get("peak_window_flatline_fraction")) or 0.0
        night_drop = _num(row.get("nighttime_drop_index")) or 0.0

        expected = shape * daily / shape.sum()
        actual = expected.copy()
        if is_flagged and (peak_flatline > 0.1 or night_drop > 0.4):
            for h in range(24):
                if h in PEAK_HOURS and peak_flatline > 0.1:
                    actual[h] *= max(0.05, 1 - peak_flatline)
                if h in (23, 0, 1, 2, 3, 4) and night_drop > 0.4:
                    actual[h] *= max(0.1, 1 - night_drop)

    diverted = np.clip(expected - actual, 0, None)
    pmt_base_residual = 2.0

    out: list[HourlyReading] = []
    for h in range(24):
        out.append(
            HourlyReading(
                timestamp=f"{ctx.month_str}-15T{h:02d}:00:00+05:00",
                hour_of_day=h,
                actual_usage_kwh=round(float(actual[h]), 2),
                expected_usage_kwh=round(float(expected[h]), 2),
                pmt_residual_kwh=round(pmt_base_residual + float(diverted[h]) * 8, 2),
                is_peak_tariff_hour=h in PEAK_HOURS,
            )
        )
    return out


# ---------------------------------------------------------------------------
# internals
# ---------------------------------------------------------------------------
def _dispatch_for(consumer_id: str, score: RiskScore, consumer: dict, ctx, include_urdu: bool = False) -> DispatchResult:
    sub = get_scorer().scored_for(consumer_id)
    frow = sub[sub["month"] == ctx.month]
    frow = frow.iloc[0] if not frow.empty else None

    feeder_uptime = _num(frow.get("feeder_uptime_pct")) if frow is not None else None
    pmt_loss_rank = _num(frow.get("pmt_loss_rank")) if frow is not None else None
    peer_dev = _num(frow.get("peer_deviation")) if frow is not None else None

    pmt_id = consumer["pmt_id"]
    injected = float(ctx.pmt_month.loc[pmt_id]["injected_energy_kwh"]) if pmt_id in ctx.pmt_month.index else 0.0
    residual = split_gap(injected, ctx.billed_pmt(pmt_id))[1]

    return run_dispatch(
        score,
        consumer=consumer,
        feeder_uptime_pct=feeder_uptime,
        pmt_loss_rank=pmt_loss_rank,
        pmt_residual_kwh=residual,
        peer_deviation=peer_dev,
        include_urdu=include_urdu,
    )


def _estimated_impact(consumer_id: str, ctx) -> float:
    sub = get_scorer().scored_for(consumer_id).sort_values("month")
    if sub.empty:
        return 0.0
    first3 = sub["billed_units_kwh"].head(3).mean()
    cur = sub[sub["month"] == ctx.month]
    current = float(cur.iloc[0]["billed_units_kwh"]) if not cur.empty else float(sub.iloc[-1]["billed_units_kwh"])
    return max(float(first3) - current, 0.0)


def _priority(prob: float) -> str:
    return "High" if prob >= HIGH_TIER else "Medium" if prob >= MEDIUM_TIER else "Low"


def _strength(prob: float) -> str:
    return "Strong" if prob >= HIGH_TIER else "Moderate" if prob >= MEDIUM_TIER else "Weak"


def _evidence_source(score: RiskScore) -> str:
    if score.is_ami and score.smart_meter_probability >= 0.5 and score.monthly_probability >= 0.5:
        return "Both Pipelines"
    if score.is_ami and score.smart_meter_probability >= 0.5:
        return "Smart Meter"
    return "Monthly Billing"


def _pipeline_agreement(score: RiskScore) -> str:
    m = score.monthly_probability >= 0.5
    s = score.is_ami and score.smart_meter_probability >= 0.5
    if not score.is_ami:
        return "Monthly Only"
    if m and s:
        return "Full"
    if m and not s:
        return "Monthly Only"
    if s and not m:
        return "Smart Meter Only"
    return "Partial"


def _safeguard_status(dispatch: DispatchResult) -> str:
    critical = {s.id: s.passed for s in dispatch.safeguards}
    if not critical.get("sg-1", True) or not critical.get("sg-2", True):
        return "Action Required"
    if critical.get("sg-4", False):
        return "Corroboration Present"
    return "All Passed"


def _case_status(consumer_id: str) -> str:
    for card in _cards_for_consumer(consumer_id):
        if get_finding(card["id"]):
            return "Inspection Completed"
        return "Job Card Created"
    return "New"


def _cards_for_consumer(consumer_id: str) -> list[dict]:
    from app.db import list_job_cards

    return [c for c in list_job_cards() if c.get("consumerId") == consumer_id]


def _num(v) -> float | None:
    if v is None:
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return None if math.isnan(f) else f


@functools.lru_cache(maxsize=1)
def _interval_dataset() -> pa_ds.Dataset | None:
    """Real 1-hour AMI interval readings, lazily opened once per process.

    Returns None when `interval_readings.parquet` hasn't been generated
    locally (it's gitignored — run `python generate_intervals.py`).
    """
    path = get_settings().interval_readings_path
    if not path.exists():
        return None
    return pa_ds.dataset(str(path), format="parquet")


@functools.lru_cache(maxsize=512)
def _interval_readings_for(consumer_id: str) -> pd.DataFrame | None:
    """All real hourly rows for one consumer, or None if unavailable."""
    dataset = _interval_dataset()
    if dataset is None:
        return None
    table = dataset.to_table(filter=pa_ds.field("consumer_id") == consumer_id)
    if table.num_rows == 0:
        return None
    df = table.to_pandas()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["hour"] = df["timestamp"].dt.hour
    df["month"] = df["timestamp"].dt.to_period("M").dt.to_timestamp()
    return df


def _real_hourly_profile(consumer_id: str, month: pd.Timestamp) -> tuple[np.ndarray, np.ndarray] | None:
    """(actual, expected) 24-length kWh-per-hour arrays from real interval data.

    `actual` is this consumer's real average hourly profile for the analysis
    month. `expected` is their real profile from their earliest 3 metered
    months (always pre-theft-onset, per `generate_intervals.py`), rescaled to
    the same daily total so the two curves are visually comparable. Returns
    None if the interval file isn't generated or has no rows for this
    consumer/month, so the caller can fall back to the synthesized curve.
    """
    df = _interval_readings_for(consumer_id)
    if df is None:
        return None

    current = df[df["month"] == pd.Timestamp(month).normalize().replace(day=1)]
    if current.empty:
        return None
    actual = current.groupby("hour")["interval_kwh"].mean().reindex(range(24), fill_value=0.0).to_numpy()

    baseline_months = sorted(df["month"].unique())[:3]
    baseline = df[df["month"].isin(baseline_months)]
    baseline_shape = baseline.groupby("hour")["interval_kwh"].mean().reindex(range(24), fill_value=0.0).to_numpy()
    shape_total = baseline_shape.sum()
    if shape_total <= 0:
        expected = actual.copy()
    else:
        expected = baseline_shape * (actual.sum() / shape_total)

    return actual, expected


_SHAPE_CACHE: np.ndarray | None = None


def _diurnal_shape() -> np.ndarray:
    global _SHAPE_CACHE
    if _SHAPE_CACHE is None:
        hours = np.arange(24, dtype=float)
        base = np.full(24, 0.35)
        morning = 0.6 * np.exp(-((hours - 8) ** 2) / (2 * 1.6 ** 2))
        evening = 1.0 * np.exp(-((hours - 20) ** 2) / (2 * 1.9 ** 2))
        shape = base + morning + evening
        _SHAPE_CACHE = shape
    return _SHAPE_CACHE.copy()
