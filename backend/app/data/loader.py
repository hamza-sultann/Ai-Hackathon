"""Loads the grid CSVs once and exposes joined panel data + lookups.

The four core tables mirror `Ai-Hackathon-agentic/data/`:
  consumers.csv        consumer_id, pmt_id, feeder_id, sanctioned_load_kw,
                       consumer_type, meter_type, is_registered_prosumer, has_ami
  feeder_monthly.csv   feeder_id, month, injected_energy_kwh, feeder_uptime_pct, avg_temp_c
  pmt_monthly.csv      pmt_id, feeder_id, month, injected_energy_kwh, pmt_uptime_pct, avg_temp_c
  monthly_readings.csv consumer_id, month, billed_units_kwh, arrears_pkr, reader_id,
                       is_theft_ground_truth, theft_type
  track2_features.csv  consumer_id, month, peak_offpeak_ratio, daily_load_factor,
                       flatline_fraction, peak_window_flatline_fraction, midday_dip_index,
                       tariff_boundary_alignment_score, nighttime_drop_index
"""
from __future__ import annotations

import functools

import pandas as pd

from app.config import get_settings


@functools.lru_cache(maxsize=1)
def get_data() -> "GridData":
    return GridData()


class GridData:
    def __init__(self) -> None:
        settings = get_settings()
        d = settings.data_dir
        if not (d / "consumers.csv").exists():
            raise FileNotFoundError(
                f"Grid CSVs not found in {d}. Set ISTIKSHAF_DATA_DIR or copy the "
                "files from Ai-Hackathon-agentic/data/."
            )

        self.consumers = pd.read_csv(d / "consumers.csv")
        self.feeder_monthly = _with_month(pd.read_csv(d / "feeder_monthly.csv"))
        self.pmt_monthly = _with_month(pd.read_csv(d / "pmt_monthly.csv"))
        self.readings = _with_month(pd.read_csv(d / "monthly_readings.csv"))

        track2_path = d / "track2_features.csv"
        self.track2 = _with_month(pd.read_csv(track2_path)) if track2_path.exists() else None

        # Analysis month: configured, else the latest month present in the readings.
        months = sorted(self.readings["month"].dropna().unique())
        self.all_months: list[pd.Timestamp] = list(months)
        configured = settings.analysis_month
        if configured:
            self.analysis_month = pd.Timestamp(configured).normalize().replace(day=1)
        else:
            self.analysis_month = pd.Timestamp(months[-1])

        self.ami_consumer_ids: set[str] = (
            set(self.track2["consumer_id"].unique()) if self.track2 is not None else set()
        )

        # Consumer -> static attributes lookup (dict of dicts).
        self._consumer_lookup = self.consumers.set_index("consumer_id").to_dict("index")

        # Panel = readings joined to consumer attributes + pmt/feeder monthly context.
        panel = self.readings.merge(self.consumers, on="consumer_id", how="left")
        panel = panel.merge(
            self.pmt_monthly.rename(columns={"avg_temp_c": "pmt_avg_temp_c"}),
            on=["pmt_id", "feeder_id", "month"],
            how="left",
        )
        panel = panel.merge(
            self.feeder_monthly[["feeder_id", "month", "feeder_uptime_pct"]],
            on=["feeder_id", "month"],
            how="left",
        )
        self.panel = panel

    # -- lookups ------------------------------------------------------------
    def consumer(self, consumer_id: str) -> dict | None:
        row = self._consumer_lookup.get(consumer_id)
        return {"consumer_id": consumer_id, **row} if row else None

    def has_ami(self, consumer_id: str) -> bool:
        row = self._consumer_lookup.get(consumer_id, {})
        return bool(row.get("has_ami", False)) or consumer_id in self.ami_consumer_ids

    def month_str(self, ts: pd.Timestamp | None = None) -> str:
        ts = ts or self.analysis_month
        return pd.Timestamp(ts).strftime("%Y-%m")

    def feeder_ids(self) -> list[str]:
        return sorted(self.consumers["feeder_id"].dropna().unique().tolist())

    def pmt_ids(self, feeder_id: str | None = None) -> list[str]:
        df = self.consumers
        if feeder_id:
            df = df[df["feeder_id"] == feeder_id]
        return sorted(df["pmt_id"].dropna().unique().tolist())


def _with_month(df: pd.DataFrame) -> pd.DataFrame:
    if "month" in df.columns:
        df["month"] = pd.to_datetime(df["month"]).dt.normalize()
    return df
