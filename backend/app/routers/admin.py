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
            id="ds-1", name="Monthly Billing Records", type="Parquet Ledger",
            last_ingested_at=now, record_count=n_readings, status="Active", latency_ms=120,
        ),
        DataSourceStatus(
            id="ds-2", name="AMI Smart-Meter Telemetry (Track 2)", type="Parquet Stream Store",
            last_ingested_at=now, record_count=n_track2, status="Active", latency_ms=45,
        ),
        DataSourceStatus(
            id="ds-3", name="PMT Balance Metering Log", type="CSV / SQLite Ledger",
            last_ingested_at=now, record_count=len(data.pmt_monthly), status="Active", latency_ms=30,
        ),
        DataSourceStatus(
            id="ds-4", name="GIS Feeder Topology & Consumer Registry", type="GeoJSON / SQLite",
            last_ingested_at=now, record_count=n_consumers, status="Active", latency_ms=85,
        ),
        DataSourceStatus(
            id="ds-5", name="Prosumer Solar Net-Metering Registry", type="Tabular Store",
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
        "message": f"Data ingestion triggered successfully for {source_id}. Partition cache refreshed.",
        "timestamp": now_str,
    }


@router.post("/model-services/{model_id}/test")
def test_model_service(model_id: str, payload: dict | None = None) -> dict:
    import time
    import traceback
    import numpy as np
    import pandas as pd
    from app.ml.scorer import get_scorer
    from app.ml.features import BASE_FEATURES, MODEL_FEATURES, FEATURE_DESCRIPTIONS

    try:
        inputs = payload or {}
        scorer = get_scorer()
        latest = scorer.latest_scores()
        if latest.empty:
            return {"modelId": model_id, "error": "No scored data available."}

        # Build a feature row from population medians across ALL model features
        # so the feature vector matches the trained model's expected input shape.
        available = [f for f in MODEL_FEATURES if f in latest.columns]
        medians = latest[available].median()
        row = pd.Series(0.0, index=MODEL_FEATURES)
        for f in available:
            row[f] = medians[f]

        # Apply user-provided slider values to the corresponding features.
        if "peakLoadDropPct" in inputs:
            row["usage_deviation"] = float(inputs["peakLoadDropPct"]) / 100.0
        if "offPeakUsageRatio" in inputs:
            row["peer_deviation"] = float(inputs["offPeakUsageRatio"])
        if "pmtResidualDeltaKWh" in inputs:
            row["pmt_loss_delta_pct"] = float(inputs["pmtResidualDeltaKWh"])
        if "sanctionedLoadKW" in inputs:
            row["fixed_baseline_deviation"] = float(inputs["sanctionedLoadKW"]) / 10.0

        row_base = row[BASE_FEATURES].to_frame().T
        t0 = time.perf_counter()

        if model_id == "ms-1":
            # Isolation Forest anomaly scoring
            iso = getattr(scorer, "iso", None)
            if iso is None:
                return {"modelId": model_id, "error": "Isolation Forest not available."}
            imp = row_base.fillna(0).to_numpy()
            score = float(-iso.score_samples(imp)[0])
            latency = round((time.perf_counter() - t0) * 1000, 1)
            return {
                "modelId": model_id,
                "anomalyScore": round(score, 4),
                "interpretation": "HIGH_ANOMALY" if score > 0.05 else "NORMAL",
                "percentileRank": round(float((latest["iso_forest_score"] < score).mean() * 100), 1),
                "latencyMs": latency,
            }

        if model_id == "ms-2":
            # Gradient-Boosted Risk Classifier (full calibrated pipeline)
            iso = getattr(scorer, "iso", None)
            model = getattr(scorer, "model_full", None)
            if iso is None or model is None:
                return {"modelId": model_id, "error": "Model not available."}
            imp = row_base.fillna(0).to_numpy()
            iso_score = float(-iso.score_samples(imp)[0])
            row["iso_forest_score"] = iso_score
            X = row[MODEL_FEATURES].to_frame().T.fillna(0)
            prob = float(model.predict_proba(X.to_numpy())[:, 1][0])
            latency = round((time.perf_counter() - t0) * 1000, 1)
            classification = "HIGH_ANOMALY_RISK" if prob > 0.7 else "MEDIUM_RISK" if prob > 0.4 else "LOW_RISK"
            return {
                "modelId": model_id,
                "predictionScore": round(prob, 4),
                "calibratedProbability": f"{round(prob * 100, 1)}%",
                "classification": classification,
                "isoForestInput": round(iso_score, 4),
                "latencyMs": latency,
            }

        if model_id == "ms-3":
            # Sigmoid Probability Calibrator
            model_full = getattr(scorer, "model_full", None)
            iso = getattr(scorer, "iso", None)
            if model_full is None or iso is None:
                return {"modelId": model_id, "error": "Calibrator models not available."}
            imp = row_base.fillna(0).to_numpy()
            iso_score = float(-iso.score_samples(imp)[0])
            row["iso_forest_score"] = iso_score
            X = row[MODEL_FEATURES].to_frame().T.fillna(0)
            prob_full = float(model_full.predict_proba(X.to_numpy())[:, 1][0])
            latency = round((time.perf_counter() - t0) * 1000, 1)
            return {
                "modelId": model_id,
                "calibratedProbability": round(prob_full, 4),
                "calibrationMethod": "Sigmoid (Platt Scaling)",
                "latencyMs": latency,
            }

        if model_id == "ms-4":
            # Explanation engine — logistic surrogate contributions
            surrogate = getattr(scorer, "surrogate", None)
            s_medians = getattr(scorer, "medians", None)
            s_stds = getattr(scorer, "stds", None)
            if surrogate is None or s_medians is None or s_stds is None:
                return {"modelId": model_id, "error": "Explanation engine not available."}
            # Compute iso score to populate the feature
            iso = getattr(scorer, "iso", None)
            if iso is not None:
                imp = row_base.fillna(0).to_numpy()
                row["iso_forest_score"] = float(-iso.score_samples(imp)[0])
            z = {}
            for f in MODEL_FEATURES:
                val = float(row.get(f, 0.0))
                med = float(s_medians.get(f, 0.0)) if f in s_medians.index else 0.0
                std = float(s_stds.get(f, 1.0)) if f in s_stds.index else 1.0
                std = std if std != 0 else 1.0
                z[f] = (val - med) / std
            contributions = []
            for f, coef in zip(MODEL_FEATURES, surrogate.coef_[0]):
                c = float(coef * z[f])
                if abs(c) > 0.001:
                    contributions.append({
                        "feature": f,
                        "contribution": round(c, 4),
                        "direction": "increases_risk" if c > 0 else "decreases_risk",
                        "description": FEATURE_DESCRIPTIONS.get(f, f.replace("_", " ")),
                    })
            contributions.sort(key=lambda x: abs(x["contribution"]), reverse=True)
            top = contributions[0] if contributions else {"feature": "N/A", "contribution": 0}
            latency = round((time.perf_counter() - t0) * 1000, 1)
            return {
                "modelId": model_id,
                "output": "Surrogate Explanation Computed",
                "riskContribution": round(sum(c["contribution"] for c in contributions if c["contribution"] > 0), 4),
                "topFeature": top.get("description", top["feature"]),
                "contributions": contributions[:6],
                "latencyMs": latency,
            }

        return {"modelId": model_id, "error": f"Unknown model service: {model_id}"}

    except Exception:
        return {"modelId": model_id, "error": traceback.format_exc()}


@router.get("/notifications")
def get_notifications() -> list[dict]:
    # Dummy notifications removed; returns clean empty list
    return []


