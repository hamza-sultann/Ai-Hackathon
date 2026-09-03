from fastapi import APIRouter, HTTPException

from app.schemas import Consumer, Feeder, PMT
from app.services import grid_service

router = APIRouter(prefix="/grid", tags=["grid"])


@router.get("/feeders", response_model=list[Feeder])
def list_feeders() -> list[Feeder]:
    return grid_service.list_feeders()


@router.get("/feeders/{feeder_id}", response_model=Feeder)
def get_feeder(feeder_id: str) -> Feeder:
    feeder = grid_service.get_feeder(feeder_id)
    if feeder is None:
        raise HTTPException(status_code=404, detail=f"Feeder {feeder_id} not found")
    return feeder


@router.get("/feeders/{feeder_id}/pmts", response_model=list[PMT])
def list_pmts(feeder_id: str) -> list[PMT]:
    return grid_service.list_pmts(feeder_id)


@router.get("/pmts/{pmt_id}", response_model=PMT)
def get_pmt(pmt_id: str) -> PMT:
    pmt = grid_service.get_pmt(pmt_id)
    if pmt is None:
        raise HTTPException(status_code=404, detail=f"PMT {pmt_id} not found")
    return pmt


@router.get("/pmts/{pmt_id}/consumers", response_model=list[Consumer])
def list_consumers(pmt_id: str) -> list[Consumer]:
    return grid_service.list_consumers(pmt_id)
