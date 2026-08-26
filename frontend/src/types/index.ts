export type UserRole = 'analyst' | 'field' | 'admin';

export type Priority = 'Low' | 'Medium' | 'High';

export type CaseStatus = 
  | 'New' 
  | 'Under Review' 
  | 'Job Card Created' 
  | 'Inspection In Progress' 
  | 'Inspection Completed' 
  | 'Dismissed';

export type JobCardStatus = 
  | 'Assigned' 
  | 'Accepted' 
  | 'En Route' 
  | 'Inspection Started' 
  | 'Evidence Recorded' 
  | 'Submitted' 
  | 'Supervisor Review' 
  | 'Closed';

export type EvidenceSource = 'Monthly Billing' | 'Smart Meter' | 'Both Pipelines';

export type DataQuality = 'Adequate' | 'Partial' | 'Degraded' | 'Unavailable';

export type ModelServiceHealth = 'Healthy' | 'Degraded' | 'Offline';

export type InspectionOutcome = 
  | 'No Irregularity Found' 
  | 'Technical Fault' 
  | 'Meter Issue' 
  | 'Requires Follow-Up' 
  | 'Irregularity Observed' 
  | 'Unable to Inspect';

export interface Feeder {
  id: string;
  name: string;
  serviceArea: string;
  substation: string;
  uptimePercentage: number;
  injectedEnergyKWh: number;
  accountedEnergyKWh: number;
  unaccountedResidualKWh: number;
  technicalLossPercentage: number;
  priorityPmtCount: number;
  totalPmtCount: number;
  trend: 'stable' | 'increasing' | 'decreasing';
}

export interface PMT {
  id: string;
  feederId: string;
  feederName: string;
  capacityKVA: number;
  connectedConsumerCount: number;
  injectedEnergyKWh: number;
  billedEnergyKWh: number;
  estimatedTechnicalLossKWh: number;
  unaccountedResidualKWh: number;
  dataQuality: DataQuality;
  priorityConnectionCount: number;
  location: string;
}

export interface Consumer {
  id: string;
  meterId: string;
  feederId: string;
  pmtId: string;
  tariffCategory: string;
  sanctionedLoadKW: number;
  address: string;
  hasSmartMeter: boolean;
  isRegisteredSolarProsumer: boolean;
}

export interface SafeguardCheck {
  id: string;
  name: string;
  passed: boolean;
  detail: string;
}

export interface ShapFeatureContribution {
  featureName: string;
  contributionValue: number;
  description: string;
  direction: 'increases_risk' | 'decreases_risk';
}

export interface RiskExplanation {
  consumerId: string;
  summaryText: string;
  treeShapContributions: ShapFeatureContribution[];
  pmtCorroborationText: string;
  safeguards: SafeguardCheck[];
}

export interface MonthlyReading {
  monthYear: string; // e.g., "2025-01"
  billedKWh: number;
  expectedKWh: number;
  peerMedianKWh: number;
  isAbnormal: boolean;
}

export interface HourlyReading {
  timestamp: string; // ISO string
  hourOfDay: number; // 0-23
  actualUsageKWh: number;
  expectedUsageKWh: number;
  pmtResidualKWh: number;
  isPeakTariffHour: boolean;
}

export interface Investigation {
  id: string;
  consumerId: string;
  meterId: string;
  feederId: string;
  pmtId: string;
  priority: Priority;
  calibratedRiskPercentage: number; // e.g., 91 for 91%
  estimatedImpactKWhMonth: number;
  patternName: string;
  evidenceSource: EvidenceSource;
  safeguardStatus: 'All Passed' | 'Action Required' | 'Corroboration Present';
  caseStatus: CaseStatus;
  monthlyRiskPercentage: number;
  smartMeterRiskPercentage: number;
  combinedEvidenceStrength: 'Strong' | 'Moderate' | 'Weak';
  pipelineAgreement: 'Full' | 'Partial' | 'Monthly Only' | 'Smart Meter Only';
  lastUpdated: string;
  analystNotes?: string;
}

export interface PipelineComparison {
  monthlyOnlyCount: number;
  smartMeterOnlyCount: number;
  bothPipelinesCount: number;
  overlapPercentage: number;
  anomalyTypeBreakdown: Array<{ type: string; count: number }>;
  coverageStats: {
    totalConnections: number;
    monthlyCovered: number;
    smartMeterCovered: number;
    dualCovered: number;
  };
}

export type AnalysisScope = 'Entire Grid' | 'Feeder' | 'PMT';
export type AnalysisPipeline = 'Monthly' | 'Smart Meter' | 'Both';

export interface AnalysisJob {
  id: string;
  status: 'queued' | 'validating_data' | 'calculating_pmt_balance' | 'scoring_anomalies' | 'calibrating_risk' | 'generating_explanations' | 'completed' | 'failed';
  progressPercentage: number;
  scope: AnalysisScope;
  targetId?: string;
  pipelines: AnalysisPipeline;
  createdAt: string;
  completedAt?: string;
  errorMessage?: string;
}

export interface JobCard {
  id: string;
  consumerId: string;
  meterId: string;
  serviceArea: string;
  feederId: string;
  pmtId: string;
  priority: Priority;
  evidenceSummary: string;
  relevantPeriodsText: string;
  estimatedImpactKWhMonth: number;
  safeguardsSummary: string;
  recommendedChecks: string[];
  analystNotes: string;
  assignedTeam: string;
  scheduledDate: string;
  status: JobCardStatus;
  createdAt: string;
}

export interface InspectionFinding {
  jobCardId: string;
  meterSealCondition: 'Intact' | 'Tampered' | 'Missing' | 'Not Inspected';
  meterCondition: 'Normal' | 'Damaged' | 'Stopped' | 'Display Fault';
  wiringCondition: 'Standard' | 'Irregular' | 'Bypassed' | 'Unsafe';
  bypassEvidenceObserved: boolean;
  loadObservedKW: number;
  siteAccessStatus: 'Accessible' | 'Refused' | 'Premises Locked' | 'Hazardous';
  consumerPresent: boolean;
  attachmentPlaceholders: string[];
  inspectorNotes: string;
  outcome: InspectionOutcome;
  submittedAt: string;
  submittedBy: string;
}

export interface DataSourceStatus {
  id: string;
  name: string;
  type: string;
  lastIngestedAt: string;
  recordCount: number;
  status: 'Active' | 'Degraded' | 'Syncing' | 'Offline';
  latencyMs: number;
}

export interface ModelServiceStatus {
  id: string;
  name: string;
  technology: string;
  version: string;
  status: ModelServiceHealth;
  p95LatencyMs: number;
  endpoint: string;
}

export interface AuditEvent {
  id: string;
  actor: string;
  timestamp: string;
  action: string;
  objectId: string;
  result: 'Success' | 'Failure' | 'Warning';
}

export interface SystemOverview {
  injectedEnergyMWh: number;
  billedEnergyMWh: number;
  estimatedTechnicalLossMWh: number;
  unaccountedResidualMWh: number;
  highPriorityPmtCount: number;
  connectionsRecommendedForReview: number;
  lastAnalysisTimestamp: string;
  analysisPeriod: string;
  analysisStatus: string;
  monthlyCoveragePercentage: number;
  smartMeterCoveragePercentage: number;
}
