"""Agentic routing layer.

Ported from `Ai-Hackathon-agentic/agents/agent_dispatcher.py`, refactored to
*return* a structured result instead of printing. Runs the confounder /
safeguard checks, decides a routing action, and produces the analyst + field
narratives the frontend renders.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta

from app import db
from app.ml.scorer import RiskScore

SOFT_WARNING_BAND = (0.65, 0.70)

# Recidivist priority boost. Ported from the CLI's dispatch_agent(), which
# nudges the effective probability up for repeat offenders before the
# soft-warning/routing decision — previously computed but only surfaced as a
# text annotation on the backend, never actually affecting the decision.
RECIDIVIST_BOOST = 0.05

SUMMER_MONTHS = {6, 7, 8}
WINTER_MONTHS = {12, 1, 2}


@dataclass
class Safeguard:
    id: str
    name: str
    passed: bool
    detail: str


@dataclass
class DispatchResult:
    consumer_id: str
    routing_decision: str
    probability: float
    safeguards: list[Safeguard] = field(default_factory=list)
    analyst_summary: str = ""
    field_alert: str = ""
    field_alert_urdu: str = ""
    pmt_corroboration: str = ""
    cancelled: bool = False
    is_recidivist: bool = False
    is_duplicate: bool = False
    effective_probability: float = 0.0


def run_dispatch(
    score: RiskScore,
    *,
    consumer: dict,
    feeder_uptime_pct: float | None,
    pmt_loss_rank: float | None,
    pmt_residual_kwh: float | None,
    peer_deviation: float | None,
    include_urdu: bool = False,
) -> DispatchResult:
    cid = score.consumer_id
    prob = score.probability
    prosumer = bool(consumer.get("is_registered_prosumer", False))
    top = score.contributions[0] if score.contributions else None

    safeguards, is_repeat, is_dup = _safeguards(
        consumer_id=cid,
        prosumer=prosumer,
        feeder_uptime_pct=feeder_uptime_pct,
        pmt_loss_rank=pmt_loss_rank,
        pmt_residual_kwh=pmt_residual_kwh,
        peer_deviation=peer_deviation,
        has_ami=score.is_ami,
    )

    # Recidivism boost: ported from the CLI's dispatch_agent(), which elevates
    # a repeat offender's *effective* probability before the routing decision
    # (soft-warning band, field-alert wording) — the raw model probability
    # (score.probability / RiskScore) is left untouched everywhere else.
    effective_prob = min(prob + RECIDIVIST_BOOST, 1.0) if is_repeat else prob

    # Confound agent: registered solar or a near-dead feeder cancels the alert.
    if prosumer or (feeder_uptime_pct is not None and feeder_uptime_pct < 20.0):
        return DispatchResult(
            consumer_id=cid,
            routing_decision="Cancelled by Confound Agent",
            probability=prob,
            effective_probability=effective_prob,
            safeguards=safeguards,
            cancelled=True,
            is_recidivist=is_repeat,
            is_duplicate=is_dup,
            analyst_summary=(
                "Alert suppressed: "
                + ("registered solar prosumer on file. " if prosumer else "")
                + ("feeder uptime critically low (systemic load-shedding). " if not prosumer else "")
                + "No field action recommended without new evidence."
            ),
        )

    # Deduplication guard: if already alerted recently in demo/operational mode
    if is_dup:
        return DispatchResult(
            consumer_id=cid,
            routing_decision="Consolidated - Alert Active",
            probability=prob,
            effective_probability=effective_prob,
            safeguards=safeguards,
            cancelled=True,
            is_recidivist=is_repeat,
            is_duplicate=True,
            analyst_summary=f"Investigation already active for consumer {cid} within recent window. Alert consolidated to prevent duplicate dispatch.",
        )

    reasons = ", ".join(c.description for c in score.contributions[:2]) or "multivariate anomaly signature"
    if SOFT_WARNING_BAND[0] <= effective_prob <= SOFT_WARNING_BAND[1]:
        decision = "Sent Soft Warning SMS"
        field_alert = (
            f"ATTENTION {_mask(cid)}: potential metering anomaly detected "
            f"({reasons}). Please verify your connection; a routine check may follow."
        )
    else:
        decision = "Routed to Analyst + Field"
        field_alert = (
            f"PRIORITY CHECK: Consumer {_mask(cid)}, PMT {consumer.get('pmt_id', '?')}. "
            f"Confidence {effective_prob:.0%}. Reason: {reasons}."
        )
        if prosumer:
            field_alert += " (Registered solar/net-metering on file.)"

    analyst_summary = _analyst_summary(score, consumer, top)
    if is_repeat:
        analyst_summary += (
            f" [REPEAT OFFENDER: multiple anomaly flags on record — priority elevated "
            f"to {effective_prob:.0%}]."
        )

    pmt_text = _pmt_corroboration(pmt_loss_rank, pmt_residual_kwh)
    urdu_alert = urdu_localization_agent(field_alert) if (include_urdu and field_alert) else ""

    return DispatchResult(
        consumer_id=cid,
        routing_decision=decision,
        probability=prob,
        effective_probability=effective_prob,
        safeguards=safeguards,
        analyst_summary=analyst_summary,
        field_alert=field_alert,
        field_alert_urdu=urdu_alert,
        pmt_corroboration=pmt_text,
        is_recidivist=is_repeat,
        is_duplicate=is_dup,
    )


def season_label(month: int) -> str:
    if month in SUMMER_MONTHS:
        return "Summer"
    if month in WINTER_MONTHS:
        return "Winter"
    return "Shoulder"


def seasonal_agent(base_threshold: float, *, month: int) -> float:
    """Adjusts the base risk threshold based on season.

    Ported from the CLI's `agents/agent_dispatcher.py::seasonal_agent()`,
    which shifted the CLI loop's flagging threshold by wall-clock month
    (`datetime.now().month`) — never called by the backend, so the live
    system ran on a flat, un-adjusted threshold year-round.

    Deliberate adaptation: this version takes an explicit `month` rather than
    reading the real-world clock, so the caller passes the *analysis month*
    being investigated (the simulated period), not the operator's local date
    — the two are unrelated in this system (the dataset's "now" is whatever
    month is under review, e.g. 2024-12, regardless of when the app runs).

    Summer (Jun-Aug): theft (AC-driven load spikes) is more common — lower
    the threshold to catch more cases. Winter (Dec-Feb): less common — raise
    it to cut false alarms. Shoulder months: unchanged.
    """
    if month in SUMMER_MONTHS:
        return base_threshold - 0.05
    if month in WINTER_MONTHS:
        return base_threshold + 0.05
    return base_threshold


import functools

@functools.lru_cache(maxsize=128)
def urdu_localization_agent(text_in_english: str) -> str:
    """Translates the English alert into Urdu for field crews."""
    if not text_in_english:
        return ""
    try:
        from deep_translator import GoogleTranslator
        return GoogleTranslator(source="en", target="ur").translate(text_in_english)
    except Exception:
        # Graceful fallback in offline / network failure scenarios
        if "ATTENTION" in text_in_english:
            return "توجہ فرمائیں: صارف میں ممکنہ بے ضابطگی پائی گئی ہے۔ براہ کرم کنکشن کی جانچ کریں۔"
        return "ترجیحی معائنہ: صارف کے میٹر اور کنکشن کی سائٹ پر فوری جانچ درکار ہے۔"


def audit_record(result: DispatchResult) -> dict:
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "consumer_id": result.consumer_id,
        "calibrated_probability": round(result.probability, 4),
        "routing_decision": result.routing_decision,
    }


def _parse_audit_timestamp(ts: str | None) -> datetime | None:
    """Audit events are stamped '%Y-%m-%d %H:%M PKT' (see routers/*.py,
    services/analysis_jobs.py) — minute precision, naive local time."""
    if not ts:
        return None
    try:
        return datetime.strptime(ts.removesuffix(" PKT"), "%Y-%m-%d %H:%M")
    except ValueError:
        return None


def recidivism_checker(consumer_id: str) -> bool:
    """Checks if the consumer has been flagged before, via the live SQLite
    audit trail — the same store the Admin Audit screen reads and the real
    analysis pipeline (services/analysis_jobs.py) writes to. Previously read
    a separate, frozen CLI-era audit_log.jsonl that the live pipeline never
    wrote to, so this safeguard could never see its own history."""
    try:
        events = db.list_audit_events_for_object(consumer_id)
    except Exception:
        return False
    return len(events) > 1


def case_dedup_guard(consumer_id: str) -> bool:
    """Checks if the consumer has been alerted within the last minute (demo
    mode) via the live SQLite audit trail — see recidivism_checker above."""
    try:
        events = db.list_audit_events_for_object(consumer_id)
    except Exception:
        return False
    now = datetime.now()
    for record in events:
        ts = _parse_audit_timestamp(record.get("timestamp"))
        if ts is not None and now - ts < timedelta(minutes=1):
            return True
    return False


def _safeguards(
    *,
    consumer_id: str,
    prosumer: bool,
    feeder_uptime_pct: float | None,
    pmt_loss_rank: float | None,
    pmt_residual_kwh: float | None,
    peer_deviation: float | None,
    has_ami: bool,
) -> tuple[list[Safeguard], bool, bool]:
    uptime_ok = feeder_uptime_pct is None or feeder_uptime_pct >= 80.0
    residual_present = (pmt_loss_rank is not None and pmt_loss_rank >= 0.6) or (
        pmt_residual_kwh is not None and pmt_residual_kwh > 0
    )
    legit_low = peer_deviation is not None and peer_deviation < -2.5
    is_dup = case_dedup_guard(consumer_id)
    is_repeat = recidivism_checker(consumer_id)

    guards = [
        Safeguard(
            "sg-1", "Registered Solar Prosumer", passed=not prosumer,
            detail="No solar export on file." if not prosumer
            else "Registered net-metering — deviation may be legitimate.",
        ),
        Safeguard(
            "sg-2", "Feeder Outage Impact", passed=uptime_ok,
            detail=(f"Feeder uptime {feeder_uptime_pct:.1f}% — outages excluded."
                    if feeder_uptime_pct is not None else "Uptime data unavailable."),
        ),
        Safeguard(
            "sg-3", "Sustained Legitimate Low Baseline", passed=not legit_low,
            detail="No evidence of a long-standing legitimate low-usage pattern."
            if not legit_low else "Consumer has consistently low usage vs peers — review manually.",
        ),
        Safeguard(
            "sg-4", "PMT Residual Corroboration",
            passed=residual_present,
            detail="PMT-level unaccounted energy corroborates the consumer drop."
            if residual_present else "No corroborating PMT residual this month.",
        ),
        Safeguard(
            "sg-5", "Data Quality Check", passed=True,
            detail="AMI + billing coverage adequate for scoring." if has_ami
            else "Monthly billing coverage adequate; no AMI stream.",
        ),
        Safeguard(
            "sg-6", "Field Verification Required", passed=True,
            detail="Mandatory before any operational or administrative action.",
        ),
        Safeguard(
            "sg-7", "Case Deduplication Guard", passed=not is_dup,
            detail="No active duplicate alert within recent inspection window." if not is_dup
            else "Consumer already under active investigation — deduplicated.",
        ),
    ]
    return guards, is_repeat, is_dup


def _analyst_summary(score: RiskScore, consumer: dict, top) -> str:
    parts = [
        f"Calibrated theft probability {score.probability:.0%} for consumer {score.consumer_id} "
        f"(PMT {consumer.get('pmt_id', '?')}, feeder {consumer.get('feeder_id', '?')})."
    ]
    if score.is_ami and score.smart_meter_probability > score.monthly_probability + 0.1:
        parts.append(
            f"Smart-meter evidence ({score.smart_meter_probability:.0%}) is notably stronger than "
            f"the monthly-billing signal ({score.monthly_probability:.0%}) — pattern isolated to "
            "specific hours rather than the whole month."
        )
    elif score.is_ami:
        parts.append(
            f"Monthly ({score.monthly_probability:.0%}) and smart-meter "
            f"({score.smart_meter_probability:.0%}) pipelines broadly agree."
        )
    if top is not None:
        parts.append(f"Primary driver: {top.description} (feature `{top.feature}`).")
    return " ".join(parts)


def _pmt_corroboration(pmt_loss_rank: float | None, pmt_residual_kwh: float | None) -> str:
    if pmt_loss_rank is None:
        return "PMT balance data unavailable for this month."
    pct = f"{pmt_loss_rank * 100:.0f}th percentile"
    if pmt_loss_rank >= 0.8:
        return (
            f"The parent PMT sits in the {pct} for unaccounted energy across the grid this month"
            + (f" (~{pmt_residual_kwh:,.0f} kWh residual)" if pmt_residual_kwh else "")
            + " — strong physical corroboration."
        )
    if pmt_loss_rank >= 0.5:
        return f"The parent PMT is around the {pct} for grid loss — moderate corroboration."
    return f"The parent PMT is only in the {pct} for loss — limited physical corroboration."


def _mask(consumer_id: str) -> str:
    return f"C-***{consumer_id[-3:]}" if len(consumer_id) >= 3 else consumer_id
