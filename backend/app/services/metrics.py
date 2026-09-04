"""Shared, cached derivations used by the grid / overview / investigation services."""
from __future__ import annotations

import functools

import pandas as pd

from app.config import get_settings
from app.data.loader import get_data
from app.ml.scorer import get_scorer

# The CSVs carry no technical-loss figure, so the injected-minus-billed gap is
# split into a technical component and a non-technical (loss/theft) residual.
# NTL_SHARE_OF_GAP is the fraction of that gap attributed to non-technical loss.
NTL_SHARE_OF_GAP = 0.55


def split_gap(injected: float, billed: float) -> tuple[float, float]:
    """Return (technical_loss_kwh, unaccounted_residual_kwh) for a metered gap."""
    gap = max(injected - billed, 0.0)
    residual = gap * NTL_SHARE_OF_GAP
    return gap - residual, residual


@functools.lru_cache(maxsize=1)
def context() -> "AnalysisContext":
    return AnalysisContext()


def reset_context() -> None:
    context.cache_clear()


class AnalysisContext:
    def __init__(self) -> None:
        self.data = get_data()
        self.scorer = get_scorer()
        self.threshold = get_settings().risk_threshold
        self.month = self.data.analysis_month
        self.month_str = self.data.month_str()

        months = self.data.all_months
        idx = months.index(self.month) if self.month in months else len(months) - 1
        self.prev_month = months[idx - 1] if idx > 0 else None

        latest = self.scorer.latest_scores().copy()
        latest["priority_flag"] = latest["probability"] >= self.threshold
        self.latest = latest

        # billed energy per feeder / per pmt for this month and the previous one
        r = self.data.readings
        cur = r[r["month"] == self.month]
        self._billed_by_consumer = cur.set_index("consumer_id")["billed_units_kwh"]
        merged = cur.merge(self.data.consumers[["consumer_id", "pmt_id", "feeder_id"]], on="consumer_id")
        self.billed_by_feeder = merged.groupby("feeder_id")["billed_units_kwh"].sum()
        self.billed_by_pmt = merged.groupby("pmt_id")["billed_units_kwh"].sum()

        if self.prev_month is not None:
            prev = r[r["month"] == self.prev_month].merge(
                self.data.consumers[["consumer_id", "feeder_id"]], on="consumer_id"
            )
            self.billed_by_feeder_prev = prev.groupby("feeder_id")["billed_units_kwh"].sum()
        else:
            self.billed_by_feeder_prev = pd.Series(dtype=float)

        # flagged-consumer counts per pmt / per feeder
        # (self.latest already carries pmt_id / feeder_id from the feature frame)
        flagged = self.latest[self.latest["priority_flag"]]
        self.flagged_by_pmt = flagged.groupby("pmt_id").size()
        self.flagged_by_feeder = flagged.groupby("feeder_id").size()
        self.flagged_consumer_ids = set(flagged.index)

        fm = self.data.feeder_monthly
        self.feeder_month = fm[fm["month"] == self.month].set_index("feeder_id")
        pm = self.data.pmt_monthly
        self.pmt_month = pm[pm["month"] == self.month].set_index("pmt_id")

    # -- convenience ----------------------------------------------------
    def billed_feeder(self, feeder_id: str) -> float:
        return float(self.billed_by_feeder.get(feeder_id, 0.0))

    def billed_pmt(self, pmt_id: str) -> float:
        return float(self.billed_by_pmt.get(pmt_id, 0.0))

    def flagged_pmt(self, pmt_id: str) -> int:
        return int(self.flagged_by_pmt.get(pmt_id, 0))

    def flagged_feeder(self, feeder_id: str) -> int:
        return int(self.flagged_by_feeder.get(feeder_id, 0))

    def priority_pmt_ids(self) -> set[str]:
        return set(self.flagged_by_pmt[self.flagged_by_pmt > 0].index)
