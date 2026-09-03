"""Builds Feeder / PMT / Consumer / SystemOverview payloads from the CSV data."""
from __future__ import annotations

from datetime import datetime

import pandas as pd

from app.data.loader import get_data
from app.schemas import Consumer, Feeder, PMT, SystemOverview
from app.services import labels
from app.services.metrics import context, split_gap


def _data_quality(uptime_pct: float | None) -> str:
    if uptime_pct is None or pd.isna(uptime_pct):
        return "Unavailable"
    if uptime_pct >= 90:
        return "Adequate"
    if uptime_pct >= 75:
        return "Partial"
    return "Degraded"


def _trend(cur: float, prev: float | None) -> str:
    if prev is None or prev == 0:
        return "stable"
    change = (cur - prev) / prev
    if change > 0.05:
        return "increasing"
    if change < -0.05:
        return "decreasing"
    return "stable"


def list_feeders() -> list[Feeder]:
    ctx = context()
    data = get_data()
    out: list[Feeder] = []
    for feeder_id in data.feeder_ids():
        out.append(_feeder(feeder_id, ctx, data))
    out.sort(key=lambda f: f.unaccounted_residual_kwh, reverse=True)
    return out


def get_feeder(feeder_id: str) -> Feeder | None:
    data = get_data()
    if feeder_id not in set(data.feeder_ids()):
        return None
    return _feeder(feeder_id, context(), data)


def _feeder(feeder_id: str, ctx, data) -> Feeder:
    injected = 0.0
    uptime = 100.0
    if feeder_id in ctx.feeder_month.index:
        row = ctx.feeder_month.loc[feeder_id]
        injected = float(row["injected_energy_kwh"])
        uptime = float(row["feeder_uptime_pct"])

    billed = ctx.billed_feeder(feeder_id)
    tech_loss, residual = split_gap(injected, billed)

    pmt_ids = data.pmt_ids(feeder_id)
    prev = ctx.billed_by_feeder_prev.get(feeder_id) if len(ctx.billed_by_feeder_prev) else None
    residual_prev = split_gap(injected, float(prev))[1] if (prev is not None and injected) else None

    return Feeder(
        id=feeder_id,
        name=labels.feeder_name(feeder_id),
        service_area=labels.service_area(feeder_id),
        substation=labels.substation(feeder_id),
        uptime_percentage=round(uptime, 1),
        injected_energy_kwh=round(injected, 1),
        accounted_energy_kwh=round(billed + tech_loss, 1),
        unaccounted_residual_kwh=round(residual, 1),
        technical_loss_percentage=round(100 * tech_loss / injected, 1) if injected else 0.0,
        priority_pmt_count=int(sum(1 for p in pmt_ids if ctx.flagged_pmt(p) > 0)),
        total_pmt_count=len(pmt_ids),
        trend=_trend(residual, residual_prev),
    )


def list_pmts(feeder_id: str) -> list[PMT]:
    data = get_data()
    if feeder_id not in set(data.feeder_ids()):
        return []
    ctx = context()
    return [_pmt(p, feeder_id, ctx, data) for p in data.pmt_ids(feeder_id)]


def get_pmt(pmt_id: str) -> PMT | None:
    data = get_data()
    row = data.consumers[data.consumers["pmt_id"] == pmt_id]
    if row.empty:
        return None
    feeder_id = row.iloc[0]["feeder_id"]
    return _pmt(pmt_id, feeder_id, context(), data)


def _pmt(pmt_id: str, feeder_id: str, ctx, data) -> PMT:
    members = data.consumers[data.consumers["pmt_id"] == pmt_id]
    injected = 0.0
    uptime = None
    if pmt_id in ctx.pmt_month.index:
        prow = ctx.pmt_month.loc[pmt_id]
        injected = float(prow["injected_energy_kwh"])
        uptime = float(prow["pmt_uptime_pct"])

    billed = ctx.billed_pmt(pmt_id)
    tech_loss, residual = split_gap(injected, billed)

    return PMT(
        id=pmt_id,
        feeder_id=feeder_id,
        feeder_name=labels.feeder_name(feeder_id),
        capacity_kva=labels.capacity_kva(float(members["sanctioned_load_kw"].sum())),
        connected_consumer_count=int(len(members)),
        injected_energy_kwh=round(injected, 1),
        billed_energy_kwh=round(billed, 1),
        estimated_technical_loss_kwh=round(tech_loss, 1),
        unaccounted_residual_kwh=round(residual, 1),
        data_quality=_data_quality(uptime),
        priority_connection_count=ctx.flagged_pmt(pmt_id),
        location=labels.pmt_location(pmt_id),
    )


def list_consumers(pmt_id: str) -> list[Consumer]:
    data = get_data()
    members = data.consumers[data.consumers["pmt_id"] == pmt_id]
    return [_consumer(r) for _, r in members.iterrows()]


def get_consumer(consumer_id: str) -> Consumer | None:
    row = get_data().consumer(consumer_id)
    return _consumer(row) if row else None


def _consumer(row) -> Consumer:
    cid = row["consumer_id"]
    return Consumer(
        id=cid,
        meter_id=labels.meter_id(cid),
        feeder_id=row["feeder_id"],
        pmt_id=row["pmt_id"],
        tariff_category=labels.tariff_category(row.get("consumer_type", "residential")),
        sanctioned_load_kw=round(float(row.get("sanctioned_load_kw", 0.0)), 2),
        address=labels.consumer_address(cid, row["pmt_id"], row["feeder_id"]),
        has_smart_meter=bool(row.get("has_ami", False)),
        is_registered_solar_prosumer=bool(row.get("is_registered_prosumer", False)),
    )


def system_overview() -> SystemOverview:
    ctx = context()
    data = get_data()

    injected = float(ctx.feeder_month["injected_energy_kwh"].sum()) if len(ctx.feeder_month) else 0.0
    billed = float(ctx.billed_by_feeder.sum())
    tech_loss, residual = split_gap(injected, billed)

    priority_pmts = len(ctx.priority_pmt_ids())
    n_consumers = len(data.consumers)
    ami = len(data.ami_consumer_ids)

    return SystemOverview(
        injected_energy_mwh=round(injected / 1000, 1),
        billed_energy_mwh=round(billed / 1000, 1),
        estimated_technical_loss_mwh=round(tech_loss / 1000, 1),
        unaccounted_residual_mwh=round(residual / 1000, 1),
        high_priority_pmt_count=priority_pmts,
        connections_recommended_for_review=int((ctx.latest["priority_flag"]).sum()),
        last_analysis_timestamp=datetime.now().strftime("%Y-%m-%d %H:%M PKT"),
        analysis_period=f"{ctx.month_str} (Monthly{' & Hourly' if ami else ''} Sync)",
        analysis_status="Completed (Clean Safeguard Run)",
        monthly_coverage_percentage=100.0,
        smart_meter_coverage_percentage=round(100 * ami / n_consumers, 1) if n_consumers else 0.0,
    )
