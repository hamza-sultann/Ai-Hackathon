"""Track 1 (monthly) vs Track 2 (AMI) pipeline comparison."""
from __future__ import annotations

import numpy as np

from app.data.loader import get_data
from app.schemas import AnomalyTypeCount, CoverageStats, PipelineComparison
from app.services.metrics import context


def pipeline_comparison() -> PipelineComparison:
    ctx = context()
    data = get_data()
    df = ctx.latest.reset_index()

    monthly_hit = df["monthly_probability"] >= 0.5
    smart_hit = (df["smart_meter_probability"] >= 0.5) & df["is_ami"]

    both = int((monthly_hit & smart_hit).sum())
    monthly_only = int((monthly_hit & ~smart_hit).sum())
    smart_only = int((~monthly_hit & smart_hit).sum())
    union = both + monthly_only + smart_only

    flagged = df[df["priority_flag"]]
    breakdown = _anomaly_breakdown(flagged)

    n = len(data.consumers)
    ami = len(data.ami_consumer_ids)

    return PipelineComparison(
        monthly_only_count=monthly_only,
        smart_meter_only_count=smart_only,
        both_pipelines_count=both,
        overlap_percentage=round(100 * both / union, 1) if union else 0.0,
        anomaly_type_breakdown=[AnomalyTypeCount(type=t, count=c) for t, c in breakdown],
        coverage_stats=CoverageStats(
            total_connections=n,
            monthly_covered=n,
            smart_meter_covered=ami,
            dual_covered=ami,
        ),
    )


def _anomaly_breakdown(flagged) -> list[tuple[str, int]]:
    if flagged.empty:
        return []
    f = flagged
    peak = _col(f, "peak_window_flatline_fraction") > 0.3
    night = _col(f, "nighttime_drop_index") > 0.6
    cusum = _col(f, "cusum_max_deviation") > _col(f, "cusum_max_deviation").quantile(0.75)
    decline = _col(f, "usage_deviation") < -0.35
    pmt = _col(f, "pmt_loss_rank") > 0.85

    labels = np.full(len(f), "Multivariate Anomaly", dtype=object)
    labels[pmt.to_numpy()] = "PMT Loss Cluster"
    labels[decline.to_numpy()] = "Sustained Usage Decline"
    labels[cusum.to_numpy()] = "Step-Down Trend Shift"
    labels[night.to_numpy()] = "Night-Time Load Drop"
    labels[peak.to_numpy()] = "Peak-Hour Deviation"

    counts: dict[str, int] = {}
    for lbl in labels:
        counts[lbl] = counts.get(lbl, 0) + 1
    return sorted(counts.items(), key=lambda kv: kv[1], reverse=True)


def _col(df, name):
    import pandas as pd

    return df[name] if name in df.columns else pd.Series(np.nan, index=df.index)
