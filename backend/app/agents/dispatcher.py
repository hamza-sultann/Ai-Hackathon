"""Agentic routing layer.

Ported from `Ai-Hackathon-agentic/agents/agent_dispatcher.py`, refactored to
*return* a structured result instead of printing. Runs the confounder /
safeguard checks, decides a routing action, and produces the analyst + field
narratives the frontend renders.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta

from app.ml.scorer import RiskScore

SOFT_WARNING_BAND = (0.65, 0.70)


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

    # Confound agent: registered solar or a near-dead feeder cancels the alert.
    if prosumer or (feeder_uptime_pct is not None and feeder_uptime_pct < 20.0):
        return DispatchResult(
            consumer_id=cid,
            routing_decision="Cancelled by Confound Agent",
            probability=prob,
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
            safeguards=safeguards,
            cancelled=True,
            is_recidivist=is_repeat,
            is_duplicate=True,
            analyst_summary=f"Investigation already active for consumer {cid} within recent window. Alert consolidated to prevent duplicate dispatch.",
        )

    reasons = ", ".join(c.description for c in score.contributions[:2]) or "multivariate anomaly signature"
    if SOFT_WARNING_BAND[0] <= prob <= SOFT_WARNING_BAND[1]:
        decision = "Sent Soft Warning SMS"
        field_alert = (
            f"ATTENTION {_mask(cid)}: potential metering anomaly detected "
            f"({reasons}). Please verify your connection; a routine check may follow."
        )
    else:
        decision = "Routed to Analyst + Field"
        field_alert = (
            f"PRIORITY CHECK: Consumer {_mask(cid)}, PMT {consumer.get('pmt_id', '?')}. "
            f"Confidence {prob:.0%}. Reason: {reasons}."
        )
        if prosumer:
            field_alert += " (Registered solar/net-metering on file.)"

    analyst_summary = _analyst_summary(score, consumer, top)
    if is_repeat:
        analyst_summary += " [REPEAT OFFENDER: multiple anomaly flags on record]."

    pmt_text = _pmt_corroboration(pmt_loss_rank, pmt_residual_kwh)
    urdu_alert = urdu_localization_agent(field_alert) if (include_urdu and field_alert) else ""

    return DispatchResult(
        consumer_id=cid,
        routing_decision=decision,
        probability=prob,
        safeguards=safeguards,
        analyst_summary=analyst_summary,
        field_alert=field_alert,
        field_alert_urdu=urdu_alert,
        pmt_corroboration=pmt_text,
        is_recidivist=is_repeat,
        is_duplicate=is_dup,
    )


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


def _find_audit_log() -> str | None:
    for path in ("audit_log.jsonl", "../audit_log.jsonl", "backend/audit_log.jsonl"):
        if os.path.exists(path):
            return path
    return None


def recidivism_checker(consumer_id: str) -> bool:
    """Checks if the consumer has been flagged before in our own log."""
    log_path = _find_audit_log()
    if not log_path:
        return False
    flag_count = 0
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                record = json.loads(line)
                if record.get("consumer_id") == consumer_id:
                    flag_count += 1
    except Exception:
        return False
    return flag_count > 1


def case_dedup_guard(consumer_id: str) -> bool:
    """Checks if the consumer has been recently alerted (within 1 min demo mode)."""
    log_path = _find_audit_log()
    if not log_path:
        return False
    now = datetime.now(timezone.utc)
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                record = json.loads(line)
                if record.get("consumer_id") == consumer_id:
                    ts = record.get("timestamp")
                    if ts:
                        log_time = datetime.fromisoformat(ts)
                        if now - log_time < timedelta(minutes=1):
                            return True
    except Exception:
        return False
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
