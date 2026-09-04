"""One-time seeding of demo job cards + audit trail from the top investigations."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta

from app.db import add_audit_event, count_audit_events, count_job_cards, upsert_job_card
from app.schemas import JobCard
from app.services import labels
from app.services.investigation_service import get_explanation, list_investigations

log = logging.getLogger("istikshaf.seed")

_RECOMMENDED_CHECKS = [
    "Inspect physical meter optical port and terminal cover seals.",
    "Check for neutral loop / shunted current-transformer wiring.",
    "Verify the incoming secondary cable connection before the meter box.",
    "Measure live load with a clamp meter and compare against the meter register.",
]
_TEAMS = ["Field Squad Alpha (Faisalabad)", "Field Squad Bravo (Lahore)", "Field Squad Charlie (Multan)"]


def seed_if_empty() -> None:
    if count_job_cards() == 0:
        _seed_job_cards()
    if count_audit_events() == 0:
        _seed_audit()


def _seed_job_cards(n: int = 6) -> None:
    investigations = list_investigations(limit=n)
    now = datetime.now()
    for i, inv in enumerate(investigations):
        explanation = get_explanation(inv.consumer_id)
        safeguards_summary = (
            f"{sum(s.passed for s in explanation.safeguards)}/{len(explanation.safeguards)} safeguards passed."
            if explanation
            else "Safeguards pending review."
        )
        card = JobCard(
            id=f"JC-{now.year}-{100 + i}",
            consumer_id=inv.consumer_id,
            meter_id=inv.meter_id,
            service_area=labels.service_area(inv.feeder_id),
            feeder_id=inv.feeder_id,
            pmt_id=inv.pmt_id,
            priority=inv.priority,
            evidence_summary=(
                f"{inv.pattern_name}. Calibrated risk {inv.calibrated_risk_percentage:.0f}%. "
                f"{inv.analyst_notes or ''}".strip()
            ),
            relevant_periods_text="Daily 18:00 - 22:00 PKT (analysis month)",
            estimated_impact_kwh_month=inv.estimated_impact_kwh_month,
            safeguards_summary=safeguards_summary,
            recommended_checks=_RECOMMENDED_CHECKS,
            analyst_notes=inv.analyst_notes or "Prioritise inspection during the peak tariff window.",
            assigned_team=_TEAMS[i % len(_TEAMS)],
            scheduled_date=(now + timedelta(days=1 + i)).strftime("%Y-%m-%d"),
            status="Assigned",
            created_at=(now - timedelta(hours=i)).strftime("%Y-%m-%d %H:%M PKT"),
            field_alert=explanation.field_alert if explanation else None,
            field_alert_urdu=explanation.field_alert_urdu if explanation else None,
        )
        upsert_job_card(card.model_dump(by_alias=True))
    log.info("Seeded %d job cards", len(investigations))


def _seed_audit() -> None:
    now = datetime.now()
    events = [
        ("analyst.hamza@disco.gov.pk", "BATCH_GRID_ANALYSIS", "JOB-9021", "Success"),
        ("system.job_runner", "MODEL_SCORING_COMPLETED", "risk_model", "Success"),
        ("field.supervisor@disco.gov.pk", "ASSIGN_JOB_CARD", "JC-latest", "Success"),
        ("admin.system@disco.gov.pk", "UPDATE_THRESHOLD_CONFIG", "SYS_CFG_01", "Success"),
    ]
    for i, (actor, action, obj, result) in enumerate(events):
        add_audit_event(
            {
                "id": f"aud-{1000 + i}",
                "actor": actor,
                "timestamp": (now - timedelta(minutes=10 * i)).strftime("%Y-%m-%d %H:%M PKT"),
                "action": action,
                "objectId": obj,
                "result": result,
            }
        )
