"""Pydantic response/request models.

Field names are Python snake_case but serialise to camelCase so the payloads
match the TypeScript interfaces in `frontend/src/types/index.ts` verbatim.
"""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

# The TS interfaces keep domain acronyms upper-cased (kWh -> KWh, MWh, kVA, kW).
# Plain camelCase would give "Kwh"; fix those up so payload keys match exactly.
_ACRONYM_FIXES = (
    ("Kwh", "KWh"),
    ("Mwh", "MWh"),
    ("Kva", "KVA"),
    ("Kw", "KW"),
)


def camel_alias(field_name: str) -> str:
    name = to_camel(field_name)
    for wrong, right in _ACRONYM_FIXES:
        name = name.replace(wrong, right)
    return name


class CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=camel_alias,
        populate_by_name=True,
        protected_namespaces=(),
    )


# ---------------------------------------------------------------------------
# Grid hierarchy
# ---------------------------------------------------------------------------
class Feeder(CamelModel):
    id: str
    name: str
    service_area: str
    substation: str
    uptime_percentage: float
    injected_energy_kwh: float
    accounted_energy_kwh: float
    unaccounted_residual_kwh: float
    technical_loss_percentage: float
    priority_pmt_count: int
    total_pmt_count: int
    trend: Literal["stable", "increasing", "decreasing"]


class PMT(CamelModel):
    id: str
    feeder_id: str
    feeder_name: str
    capacity_kva: float
    connected_consumer_count: int
    injected_energy_kwh: float
    billed_energy_kwh: float
    estimated_technical_loss_kwh: float
    unaccounted_residual_kwh: float
    data_quality: Literal["Adequate", "Partial", "Degraded", "Unavailable"]
    priority_connection_count: int
    location: str


class Consumer(CamelModel):
    id: str
    meter_id: str
    feeder_id: str
    pmt_id: str
    tariff_category: str
    sanctioned_load_kw: float
    address: str
    has_smart_meter: bool
    is_registered_solar_prosumer: bool


# ---------------------------------------------------------------------------
# Investigations & explainability
# ---------------------------------------------------------------------------
class ShapFeatureContribution(CamelModel):
    feature_name: str
    contribution_value: float
    description: str
    direction: Literal["increases_risk", "decreases_risk"]


class SafeguardCheck(CamelModel):
    id: str
    name: str
    passed: bool
    detail: str


class RiskExplanation(CamelModel):
    consumer_id: str
    summary_text: str
    tree_shap_contributions: list[ShapFeatureContribution]
    pmt_corroboration_text: str
    safeguards: list[SafeguardCheck]
    field_alert: Optional[str] = None
    field_alert_urdu: Optional[str] = None


class MonthlyReading(CamelModel):
    month_year: str
    billed_kwh: float
    expected_kwh: float
    peer_median_kwh: float
    is_abnormal: bool


class HourlyReading(CamelModel):
    timestamp: str
    hour_of_day: int
    actual_usage_kwh: float
    expected_usage_kwh: float
    pmt_residual_kwh: float
    is_peak_tariff_hour: bool


class Investigation(CamelModel):
    id: str
    consumer_id: str
    meter_id: str
    feeder_id: str
    pmt_id: str
    priority: Literal["Low", "Medium", "High"]
    calibrated_risk_percentage: float
    estimated_impact_kwh_month: float
    pattern_name: str
    evidence_source: Literal["Monthly Billing", "Smart Meter", "Both Pipelines"]
    safeguard_status: Literal["All Passed", "Action Required", "Corroboration Present"]
    case_status: Literal[
        "New", "Under Review", "Job Card Created",
        "Inspection In Progress", "Inspection Completed", "Dismissed",
    ]
    monthly_risk_percentage: float
    smart_meter_risk_percentage: float
    combined_evidence_strength: Literal["Strong", "Moderate", "Weak"]
    pipeline_agreement: Literal["Full", "Partial", "Monthly Only", "Smart Meter Only"]
    last_updated: str
    analyst_notes: Optional[str] = None


# ---------------------------------------------------------------------------
# Pipeline comparison
# ---------------------------------------------------------------------------
class AnomalyTypeCount(CamelModel):
    type: str
    count: int


class CoverageStats(CamelModel):
    total_connections: int
    monthly_covered: int
    smart_meter_covered: int
    dual_covered: int


class PipelineComparison(CamelModel):
    monthly_only_count: int
    smart_meter_only_count: int
    both_pipelines_count: int
    overlap_percentage: float
    anomaly_type_breakdown: list[AnomalyTypeCount]
    coverage_stats: CoverageStats


# ---------------------------------------------------------------------------
# Analysis jobs
# ---------------------------------------------------------------------------
AnalysisStatus = Literal[
    "queued", "validating_data", "calculating_pmt_balance", "scoring_anomalies",
    "calibrating_risk", "generating_explanations", "completed", "failed",
]


class AgentDecisionCounts(CamelModel):
    flagged: int = 0
    suppressed_confounder: int = 0
    consolidated_duplicate: int = 0
    soft_warning: int = 0
    routed_to_field: int = 0
    recidivist: int = 0


class AnalysisJob(CamelModel):
    id: str
    status: AnalysisStatus
    progress_percentage: int
    scope: Literal["Entire Grid", "Feeder", "PMT"]
    target_id: Optional[str] = None
    pipelines: Literal["Monthly", "Smart Meter", "Both"]
    created_at: str
    completed_at: Optional[str] = None
    error_message: Optional[str] = None
    # Populated once the real pipeline finishes.
    model_scored: Optional[str] = None
    flagged_count: Optional[int] = None
    agent_decisions: Optional[AgentDecisionCounts] = None
    audit_events_written: Optional[int] = None
    analysis_month: Optional[str] = None


class StartAnalysisRequest(CamelModel):
    scope: Literal["Entire Grid", "Feeder", "PMT"]
    pipelines: Literal["Monthly", "Smart Meter", "Both"]
    target_id: Optional[str] = None


# ---------------------------------------------------------------------------
# Job cards & field findings
# ---------------------------------------------------------------------------
JobCardStatus = Literal[
    "Assigned", "Accepted", "En Route", "Inspection Started",
    "Evidence Recorded", "Submitted", "Supervisor Review", "Closed",
]


class JobCard(CamelModel):
    id: str
    consumer_id: str
    meter_id: str
    service_area: str
    feeder_id: str
    pmt_id: str
    priority: Literal["Low", "Medium", "High"]
    evidence_summary: str
    relevant_periods_text: str
    estimated_impact_kwh_month: float
    safeguards_summary: str
    recommended_checks: list[str]
    analyst_notes: str
    assigned_team: str
    scheduled_date: str
    status: JobCardStatus
    created_at: str
    # Bilingual field alert carried from the investigation's Urdu localization agent.
    field_alert: Optional[str] = None
    field_alert_urdu: Optional[str] = None


class CreateJobCardRequest(CamelModel):
    consumer_id: str
    meter_id: str
    service_area: str
    feeder_id: str
    pmt_id: str
    priority: Literal["Low", "Medium", "High"]
    evidence_summary: str
    relevant_periods_text: str
    estimated_impact_kwh_month: float
    safeguards_summary: str
    recommended_checks: list[str]
    analyst_notes: str
    assigned_team: str
    scheduled_date: str
    field_alert: Optional[str] = None
    field_alert_urdu: Optional[str] = None


class UpdateJobCardStatusRequest(CamelModel):
    status: JobCardStatus


class InspectionFinding(CamelModel):
    job_card_id: str
    meter_seal_condition: Literal["Intact", "Tampered", "Missing", "Not Inspected"]
    meter_condition: Literal["Normal", "Damaged", "Stopped", "Display Fault"]
    wiring_condition: Literal["Standard", "Irregular", "Bypassed", "Unsafe"]
    bypass_evidence_observed: bool
    load_observed_kw: float
    site_access_status: Literal["Accessible", "Refused", "Premises Locked", "Hazardous"]
    consumer_present: bool
    attachment_placeholders: list[str]
    inspector_notes: str
    outcome: Literal[
        "No Irregularity Found", "Technical Fault", "Meter Issue",
        "Requires Follow-Up", "Irregularity Observed", "Unable to Inspect",
    ]
    submitted_at: str
    submitted_by: str


class SubmitFindingResponse(CamelModel):
    success: bool
    message: str


# ---------------------------------------------------------------------------
# Overview / admin
# ---------------------------------------------------------------------------
class SystemOverview(CamelModel):
    injected_energy_mwh: float
    billed_energy_mwh: float
    estimated_technical_loss_mwh: float
    unaccounted_residual_mwh: float
    high_priority_pmt_count: int
    connections_recommended_for_review: int
    last_analysis_timestamp: str
    analysis_period: str
    analysis_status: str
    monthly_coverage_percentage: float
    smart_meter_coverage_percentage: float


class FieldOverviewStats(CamelModel):
    assigned_today: int
    high_priority: int
    in_progress: int
    awaiting_review: int
    completed_today: int


class DataSourceStatus(CamelModel):
    id: str
    name: str
    type: str
    last_ingested_at: str
    record_count: int
    status: Literal["Active", "Degraded", "Syncing", "Offline"]
    latency_ms: int


class ModelServiceStatus(CamelModel):
    id: str
    name: str
    technology: str
    version: str
    status: Literal["Healthy", "Degraded", "Offline"]
    p95_latency_ms: int
    endpoint: str


class AuditEvent(CamelModel):
    id: str
    actor: str
    timestamp: str
    action: str
    object_id: str
    result: Literal["Success", "Failure", "Warning"]
