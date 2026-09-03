from fastapi import APIRouter, HTTPException

from app.schemas import HourlyReading, Investigation, MonthlyReading, RiskExplanation
from app.services import investigation_service as svc

router = APIRouter(prefix="/investigations", tags=["investigations"])


@router.get("", response_model=list[Investigation])
def list_investigations() -> list[Investigation]:
    return svc.list_investigations()


@router.get("/{consumer_id}", response_model=Investigation)
def get_investigation(consumer_id: str) -> Investigation:
    inv = svc.get_investigation(consumer_id)
    if inv is None:
        raise HTTPException(status_code=404, detail=f"No investigation for {consumer_id}")
    return inv


@router.get("/{consumer_id}/explanation", response_model=RiskExplanation)
def get_explanation(consumer_id: str) -> RiskExplanation:
    exp = svc.get_explanation(consumer_id)
    if exp is None:
        raise HTTPException(status_code=404, detail=f"No explanation for {consumer_id}")
    return exp


@router.get("/{consumer_id}/monthly", response_model=list[MonthlyReading])
def get_monthly(consumer_id: str) -> list[MonthlyReading]:
    rows = svc.get_monthly_readings(consumer_id)
    if rows is None:
        raise HTTPException(status_code=404, detail=f"No readings for {consumer_id}")
    return rows


@router.get("/{consumer_id}/hourly", response_model=list[HourlyReading])
def get_hourly(consumer_id: str) -> list[HourlyReading]:
    rows = svc.get_hourly_readings(consumer_id)
    if rows is None:
        raise HTTPException(status_code=404, detail=f"No hourly profile for {consumer_id}")
    return rows
