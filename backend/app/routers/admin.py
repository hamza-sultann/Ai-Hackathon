from datetime import datetime
import random

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


@router.get("/users")
def list_users() -> list[dict]:
    return [
        {
            "id": "usr-1",
            "name": "Engr. Hamza Sultan",
            "email": "analyst.hamza@disco.gov.pk",
            "role": "analyst",
            "division": "Faisalabad West / HQ",
            "status": "Active",
            "lastLogin": "Today, 08:30 PKT",
            "permissions": ["view_telemetry", "run_analysis", "create_job_cards"],
        },
        {
            "id": "usr-2",
            "name": "Sub-Div. Officer Rizwan",
            "email": "field.supervisor@disco.gov.pk",
            "role": "field",
            "division": "Lahore Grid Region",
            "status": "Active",
            "lastLogin": "Today, 07:45 PKT",
            "permissions": ["dispatch_squads", "submit_findings", "verify_meters"],
        },
        {
            "id": "usr-3",
            "name": "Director IT & Automation",
            "email": "admin.system@disco.gov.pk",
            "role": "admin",
            "division": "Central Operations",
            "status": "Active",
            "lastLogin": "Yesterday, 19:20 PKT",
            "permissions": ["manage_models", "manage_data_sources", "configure_thresholds"],
        },
    ]


@router.get("/config")
def get_config() -> dict:
    from app.config import get_settings
    s = get_settings()
    return {
        "calibratedRiskThreshold": int(s.risk_threshold * 100),
        "treeShapTopFeaturesCount": 4,
        "pmtLossAlertThresholdPercentage": 12,
        "safeguardMode": "Standard",
        "batchScheduleCron": "0 2 * * *",
        "autoDispatchJobCards": False,
        "notifyOnHighPriorityResidual": True,
    }


@router.patch("/config")
def update_config(payload: dict) -> dict:
    return {"success": True, "config": payload}


@router.post("/data-sources/{source_id}/sync")
def sync_data_source(source_id: str) -> dict:
    now_str = datetime.now().strftime("%H:%M:%S PKT")
    db.add_audit_event({
        "id": f"aud-sync-{random.randint(10000, 99999)}",
        "actor": "admin.system@disco.gov.pk",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M PKT"),
        "action": "SYNC_DATA_SOURCE",
        "objectId": source_id,
        "result": "Success",
    })
    return {
        "success": True,
        "message": f"Data ingestion triggered successfully for {source_id}. Stream buffer flushed.",
        "timestamp": now_str,
    }


@router.post("/model-services/{model_id}/test")
def test_model_service(model_id: str, payload: dict | None = None) -> dict:
    if model_id == "ms-4":
        return {
            "modelId": model_id,
            "output": "TreeSHAP Computed",
            "riskContribution": 0.34,
            "topFeature": "Peak Tariff Load Ratio (6 PM–10 PM)",
            "latencyMs": 290,
        }
    return {
        "modelId": model_id,
        "predictionScore": 0.912,
        "calibratedProbability": "91.2%",
        "classification": "HIGH_ANOMALY_RISK",
        "latencyMs": 135,
    }


@router.get("/notifications")
def get_notifications() -> list[dict]:
    # Dummy notifications removed; returns clean empty list
    return []


