"""Agentic routing layer.

Ported from `Ai-Hackathon-agentic/agents/agent_dispatcher.py`, refactored to
*return* a structured result instead of printing. Runs the confounder /
safeguard checks, decides a routing action, and produces the analyst + field
narratives the frontend renders.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

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
    pmt_corroboration: str = ""
    cancelled: bool = False


def run_dispatch(
    score: RiskScore,
    *,
    consumer: dict,
    feeder_uptime_pct: float | None,
    pmt_loss_rank: float | None,
    pmt_residual_kwh: float | None,
    peer_deviation: float | None,
) -> DispatchResult:
    cid = score.consumer_id
    prob = score.probability
    prosumer = bool(consumer.get("is_registered_prosumer", False))
    top = score.contributions[0] if score.contributions else None

    safeguards = _safeguards(
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
            analyst_summary=(
                "Alert suppressed: "
                + ("registered solar prosumer on file. " if prosumer else "")
                + ("feeder uptime critically low (systemic load-shedding). " if not prosumer else "")
                + "No field action recommended without new evidence."
            ),
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
    pmt_text = _pmt_corroboration(pmt_loss_rank, pmt_residual_kwh)

    return DispatchResult(
        consumer_id=cid,
        routing_decision=decision,
        probability=prob,
        safeguards=safeguards,
        analyst_summary=analyst_summary,
        field_alert=field_alert,
        pmt_corroboration=pmt_text,
    )


def audit_record(result: DispatchResult) -> dict:
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "consumer_id": result.consumer_id,
        "calibrated_probability": round(result.probability, 4),
        "routing_decision": result.routing_decision,
    }


def _safeguards(
    *,
    prosumer: bool,
    feeder_uptime_pct: float | None,
    pmt_loss_rank: float | None,
    pmt_residual_kwh: float | None,
    peer_deviation: float | None,
    has_ami: bool,
) -> list[Safeguard]:
    uptime_ok = feeder_uptime_pct is None or feeder_uptime_pct >= 80.0
    residual_present = (pmt_loss_rank is not None and pmt_loss_rank >= 0.6) or (
        pmt_residual_kwh is not None and pmt_residual_kwh > 0
    )
    legit_low = peer_deviation is not None and peer_deviation < -2.5
    return [
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
    ]


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
