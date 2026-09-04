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


@router.get("/squads")
def list_squads() -> list[dict]:
    cards = db.list_job_cards()
    findings = {f["jobCardId"] for f in _all_findings()}
    squad_defs = [
        ("sq-1", "Field Squad Alpha (Faisalabad)", "Faisalabad Industrial Area", "Engr. Tariq Mehmood", "LEA-8912"),
        ("sq-2", "Field Squad Bravo (Lahore)", "Lahore Grid Region", "Sub-Div. Officer Rizwan", "LHR-4402"),
        ("sq-3", "Field Squad Charlie (Multan)", "Multan Substation Region", "Engr. Shahid Malik", "MN-6180"),
    ]
    res = []
    for sq_id, name, div, leader, plate in squad_defs:
        sq_cards = [c for c in cards if c.get("assignedTeam") == name]
        assigned = len(sq_cards)
        completed = sum(1 for c in sq_cards if c["id"] in findings)
        res.append({
            "id": sq_id,
            "name": name,
            "division": div,
            "leaderName": leader,
            "assignedJobsCount": assigned,
            "completedJobsCount": completed,
            "activeInspectorsCount": 4,
            "vehiclePlate": plate,
            "status": "Active Field",
            "efficiencyRate": round(90.0 + (completed / max(1, assigned)) * 10, 1),
        })
    return res


@router.get("/team")
def list_team() -> list[dict]:
    cards = db.list_job_cards()
    active_cards_by_team = {}
    for c in cards:
        if c.get("assignedTeam") and c.get("status") in _OPEN_STATUSES:
            active_cards_by_team.setdefault(c["assignedTeam"], []).append(c)

    inspectors = [
        ("tm-1", "Engr. Tariq Mehmood", "Senior Field Lead", "sq-1", "Field Squad Alpha (Faisalabad)", "+92-300-8419201"),
        ("tm-2", "Muhammad Bilal", "Certified Metering Tech", "sq-1", "Field Squad Alpha (Faisalabad)", "+92-301-4458291"),
        ("tm-3", "Sub-Div. Officer Rizwan", "Enforcement Supervisor", "sq-2", "Field Squad Bravo (Lahore)", "+92-321-9984123"),
        ("tm-4", "Asad Farooq", "Tamper Investigator", "sq-2", "Field Squad Bravo (Lahore)", "+92-333-1284759"),
        ("tm-5", "Engr. Shahid Malik", "Senior Field Lead", "sq-3", "Field Squad Charlie (Multan)", "+92-302-8812940"),
        ("tm-6", "Usman Qureshi", "Secondary Line Inspector", "sq-3", "Field Squad Charlie (Multan)", "+92-305-6671049"),
    ]
    res = []
    for tm_id, name, desig, sq_id, sq_name, phone in inspectors:
        team_jobs = active_cards_by_team.get(sq_name, [])
        active_job = team_jobs[0]["id"] if team_jobs else None
        loc = team_jobs[0]["serviceArea"] if team_jobs else "Base Station"
        res.append({
            "id": tm_id,
            "name": name,
            "designation": desig,
            "squadId": sq_id,
            "squadName": sq_name,
            "phone": phone,
            "currentStatus": "On-Site Inspection" if active_job else "Available",
            "activeJobId": active_job,
            "assignedLocation": loc,
            "jobsCompletedToday": 1 if active_job else 0,
        })
    return res


@router.get("/history")
def list_history() -> list[dict]:
    return _all_findings()


def _all_findings() -> list[dict]:
    with db.connect() as conn:
        rows = conn.execute("SELECT payload FROM findings").fetchall()
    import json

    return [json.loads(r["payload"]) for r in rows]

