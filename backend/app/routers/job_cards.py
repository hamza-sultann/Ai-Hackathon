import random
from datetime import datetime

from fastapi import APIRouter, HTTPException

from app import db
from app.schemas import CreateJobCardRequest, JobCard, UpdateJobCardStatusRequest

router = APIRouter(prefix="/job-cards", tags=["job-cards"])


def _audit(action: str, object_id: str) -> None:
    db.add_audit_event(
        {
            "id": f"aud-{random.randint(100000, 999999)}",
            "actor": "analyst.web@disco.gov.pk",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M PKT"),
            "action": action,
            "objectId": object_id,
            "result": "Success",
        }
    )


@router.get("", response_model=list[JobCard])
def list_job_cards() -> list[JobCard]:
    return [JobCard.model_validate(c) for c in db.list_job_cards()]


@router.post("", response_model=JobCard)
def create_job_card(req: CreateJobCardRequest) -> JobCard:
    now = datetime.now()
    card = JobCard(
        id=f"JC-{now.year}-{random.randint(100, 999)}",
        status="Assigned",
        created_at=now.strftime("%Y-%m-%d %H:%M PKT"),
        **req.model_dump(),
    )
    db.upsert_job_card(card.model_dump(by_alias=True))
    _audit("CREATE_JOB_CARD", card.id)
    return card


@router.get("/{card_id}", response_model=JobCard)
def get_job_card(card_id: str) -> JobCard:
    card = db.get_job_card(card_id)
    if card is None:
        raise HTTPException(status_code=404, detail=f"Job card {card_id} not found")
    return JobCard.model_validate(card)


@router.patch("/{card_id}", response_model=JobCard)
def update_status(card_id: str, req: UpdateJobCardStatusRequest) -> JobCard:
    card = db.get_job_card(card_id)
    if card is None:
        raise HTTPException(status_code=404, detail=f"Job card {card_id} not found")
    card["status"] = req.status
    db.upsert_job_card(card)
    _audit("UPDATE_JOB_CARD_STATUS", card_id)
    return JobCard.model_validate(card)
