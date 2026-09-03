from datetime import datetime

from fastapi import APIRouter

from app import db
from app.data.loader import get_data
from app.schemas import AuditEvent, DataSourceStatus, ModelServiceStatus

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/data-sources", response_model=list[DataSourceStatus])
def data_sources() -> list[DataSourceStatus]:
    data = get_data()
    now = datetime.now().strftime("%Y-%m-%d %H:%M PKT")
    n_readings = len(data.readings)
    n_consumers = len(data.consumers)
    n_track2 = len(data.track2) if data.track2 is not None else 0
    return [
        DataSourceStatus(
            id="ds-1", name="Monthly Billing ERP (SAP IS-U)", type="Database CDC",
            last_ingested_at=now, record_count=n_readings, status="Active", latency_ms=120,
        ),
        DataSourceStatus(
            id="ds-2", name="AMI Smart-Meter Telemetry (HES)", type="Kafka Stream",
            last_ingested_at=now, record_count=n_track2, status="Active", latency_ms=45,
        ),
        DataSourceStatus(
            id="ds-3", name="PMT Balance Metering System", type="Modbus / MQTT",
            last_ingested_at=now, record_count=len(data.pmt_monthly), status="Active", latency_ms=30,
        ),
        DataSourceStatus(
            id="ds-4", name="GIS Feeder Topology & Consumer Registry", type="PostGIS API",
            last_ingested_at=now, record_count=n_consumers, status="Active", latency_ms=85,
        ),
        DataSourceStatus(
            id="ds-5", name="Prosumer Solar Registry (NEPRA)", type="REST Import",
            last_ingested_at=now,
            record_count=int(data.consumers["is_registered_prosumer"].sum()),
            status="Active", latency_ms=210,
        ),
    ]


@router.get("/model-services", response_model=list[ModelServiceStatus])
def model_services() -> list[ModelServiceStatus]:
    base = "http://localhost:8000/api/models"
    return [
        ModelServiceStatus(
            id="ms-1", name="Isolation Forest Anomaly Scoring", technology="scikit-learn",
            version="v3.0.0", status="Healthy", p95_latency_ms=85, endpoint=f"{base}/iforest",
        ),
        ModelServiceStatus(
            id="ms-2", name="Gradient-Boosted Risk Classifier", technology="scikit-learn HGB",
            version="v3.0.0", status="Healthy", p95_latency_ms=140, endpoint=f"{base}/classifier",
        ),
        ModelServiceStatus(
            id="ms-3", name="Sigmoid Probability Calibrator", technology="scikit-learn",
            version="v3.0.0", status="Healthy", p95_latency_ms=25, endpoint=f"{base}/calibrate",
        ),
        ModelServiceStatus(
            id="ms-4", name="Additive Explanation Engine (logistic surrogate)",
            technology="scikit-learn", version="v3.0.0", status="Degraded",
            p95_latency_ms=310, endpoint=f"{base}/explain",
        ),
    ]


@router.get("/audit", response_model=list[AuditEvent])
def audit() -> list[AuditEvent]:
    return [AuditEvent.model_validate(e) for e in db.list_audit_events()]
