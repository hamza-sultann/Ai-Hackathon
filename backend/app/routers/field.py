from datetime import datetime

from fastapi import APIRouter, HTTPException

from app import db
from app.schemas import FieldOverviewStats, InspectionFinding, JobCard, SubmitFindingResponse

router = APIRouter(prefix="/field", tags=["field"])

_OPEN_STATUSES = {"Assigned", "Accepted", "En Route", "Inspection Started"}
_REVIEW_STATUSES = {"Evidence Recorded", "Submitted", "Supervisor Review"}


@router.get("/overview", response_model=FieldOverviewStats)
def field_overview() -> FieldOverviewStats:
    cards = db.list_job_cards()
    findings = {f["jobCardId"] for f in _all_findings()}
    today = datetime.now().strftime("%Y-%m-%d")
    return FieldOverviewStats(
        assigned_today=sum(1 for c in cards if c.get("scheduledDate") == today),
        high_priority=sum(1 for c in cards if c.get("priority") == "High" and c["status"] != "Closed"),
        in_progress=sum(1 for c in cards if c["status"] in _OPEN_STATUSES),
        awaiting_review=sum(1 for c in cards if c["status"] in _REVIEW_STATUSES),
        completed_today=sum(1 for c in cards if c["id"] in findings),
    )


@router.get("/jobs", response_model=list[JobCard])
def assigned_jobs() -> list[JobCard]:
    return [JobCard.model_validate(c) for c in db.list_job_cards()]


@router.get("/jobs/{job_card_id}/findings", response_model=InspectionFinding | None)
def get_finding(job_card_id: str) -> InspectionFinding | None:
    finding = db.get_finding(job_card_id)
    return InspectionFinding.model_validate(finding) if finding else None


@router.post("/jobs/{job_card_id}/findings", response_model=SubmitFindingResponse)
def submit_finding(job_card_id: str, finding: InspectionFinding) -> SubmitFindingResponse:
    card = db.get_job_card(job_card_id)
    if card is None:
        raise HTTPException(status_code=404, detail=f"Job card {job_card_id} not found")

    payload = finding.model_dump(by_alias=True)
    payload["jobCardId"] = job_card_id
    db.upsert_finding(payload)

    card["status"] = "Supervisor Review"
    db.upsert_job_card(card)
    db.add_audit_event(
        {
            "id": f"aud-{job_card_id}-finding",
            "actor": finding.submitted_by or "field.inspector@disco.gov.pk",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M PKT"),
            "action": "SUBMIT_FINDING",
            "objectId": job_card_id,
            "result": "Success",
        }
    )
    return SubmitFindingResponse(
        success=True,
        message="Inspection findings recorded and queued for supervisor review.",
    )


def _all_findings() -> list[dict]:
    with db.connect() as conn:
        rows = conn.execute("SELECT payload FROM findings").fetchall()
    import json

    return [json.loads(r["payload"]) for r in rows]
