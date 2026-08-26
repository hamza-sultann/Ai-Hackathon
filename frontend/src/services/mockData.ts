import {
  Feeder,
  PMT,
  Investigation,
  RiskExplanation,
  MonthlyReading,
  HourlyReading,
  PipelineComparison,
  JobCard,
  SystemOverview,
  DataSourceStatus,
  ModelServiceStatus,
  AuditEvent,
} from '../types';

export const MOCK_SYSTEM_OVERVIEW: SystemOverview = {
  injectedEnergyMWh: 14250.8,
  billedEnergyMWh: 11180.2,
  estimatedTechnicalLossMWh: 1210.4,
  unaccountedResidualMWh: 1860.2,
  highPriorityPmtCount: 24,
  connectionsRecommendedForReview: 482,
  lastAnalysisTimestamp: '2026-08-26 18:30 PKT',
  analysisPeriod: 'Aug 2026 (Monthly & Hourly Sync)',
  analysisStatus: 'Completed (Clean Safeguard Run)',
  monthlyCoveragePercentage: 100,
  smartMeterCoveragePercentage: 68.4,
};

export const MOCK_FEEDERS: Feeder[] = [
  {
    id: 'FDR-08',
    name: 'Industrial Estate Feeder 08',
    serviceArea: 'Faisalabad West Division',
    substation: 'GS-132KV Nishtatabad',
    uptimePercentage: 98.4,
    injectedEnergyKWh: 850000,
    accountedEnergyKWh: 646000,
    unaccountedResidualKWh: 136000,
    technicalLossPercentage: 8.0,
    priorityPmtCount: 5,
    totalPmtCount: 14,
    trend: 'increasing',
  },
  {
    id: 'FDR-01',
    name: 'Mall Road Commercial 01',
    serviceArea: 'Lahore Central',
    substation: 'GS-132KV Egerton',
    uptimePercentage: 99.1,
    injectedEnergyKWh: 620000,
    accountedEnergyKWh: 520800,
    unaccountedResidualKWh: 49600,
    technicalLossPercentage: 8.0,
    priorityPmtCount: 2,
    totalPmtCount: 10,
    trend: 'stable',
  },
  {
    id: 'FDR-03',
    name: 'Gulberg Mixed Feeder 03',
    serviceArea: 'Lahore East',
    substation: 'GS-132KV Gulberg',
    uptimePercentage: 97.8,
    injectedEnergyKWh: 940000,
    accountedEnergyKWh: 723800,
    unaccountedResidualKWh: 131600,
    technicalLossPercentage: 9.0,
    priorityPmtCount: 4,
    totalPmtCount: 12,
    trend: 'increasing',
  },
  {
    id: 'FDR-12',
    name: 'Samanabad Residential 12',
    serviceArea: 'Lahore South',
    substation: 'GS-132KV Samanabad',
    uptimePercentage: 98.9,
    injectedEnergyKWh: 410000,
    accountedEnergyKWh: 348500,
    unaccountedResidualKWh: 32800,
    technicalLossPercentage: 7.0,
    priorityPmtCount: 1,
    totalPmtCount: 8,
    trend: 'decreasing',
  },
];

export const MOCK_PMTS: PMT[] = [
  {
    id: 'PMT-081',
    feederId: 'FDR-08',
    feederName: 'Industrial Estate Feeder 08',
    capacityKVA: 400,
    connectedConsumerCount: 38,
    injectedEnergyKWh: 68000,
    billedEnergyKWh: 46920,
    estimatedTechnicalLossKWh: 5440,
    unaccountedResidualKWh: 15640,
    dataQuality: 'Adequate',
    priorityConnectionCount: 4,
    location: 'Sector C-2, Block B, Industrial Area',
  },
  {
    id: 'PMT-082',
    feederId: 'FDR-08',
    feederName: 'Industrial Estate Feeder 08',
    capacityKVA: 200,
    connectedConsumerCount: 22,
    injectedEnergyKWh: 32000,
    billedEnergyKWh: 24960,
    estimatedTechnicalLossKWh: 2560,
    unaccountedResidualKWh: 4480,
    dataQuality: 'Adequate',
    priorityConnectionCount: 1,
    location: 'Sector C-2, Main Avenue',
  },
  {
    id: 'PMT-014',
    feederId: 'FDR-01',
    feederName: 'Mall Road Commercial 01',
    capacityKVA: 630,
    connectedConsumerCount: 64,
    injectedEnergyKWh: 110000,
    billedEnergyKWh: 94600,
    estimatedTechnicalLossKWh: 7700,
    unaccountedResidualKWh: 7700,
    dataQuality: 'Adequate',
    priorityConnectionCount: 2,
    location: 'Regal Chowk Shopping Complex',
  },
];

export const MOCK_INVESTIGATIONS: Investigation[] = [
  {
    id: 'INV-08124',
    consumerId: 'C-08124',
    meterId: 'MTR-481092',
    feederId: 'FDR-08',
    pmtId: 'PMT-081',
    priority: 'High',
    calibratedRiskPercentage: 91,
    estimatedImpactKWhMonth: 184,
    patternName: 'Peak-Hour Deviation',
    evidenceSource: 'Both Pipelines',
    safeguardStatus: 'All Passed',
    caseStatus: 'Under Review',
    monthlyRiskPercentage: 64,
    smartMeterRiskPercentage: 91,
    combinedEvidenceStrength: 'Strong',
    pipelineAgreement: 'Partial',
    lastUpdated: '2026-08-26 14:15 PKT',
    analystNotes: 'Monthly records show moderate decline, while hourly readings reveal repeated drops isolated to peak-tariff hours.',
  },
  {
    id: 'INV-08129',
    consumerId: 'C-08129',
    meterId: 'MTR-481105',
    feederId: 'FDR-08',
    pmtId: 'PMT-081',
    priority: 'High',
    calibratedRiskPercentage: 86,
    estimatedImpactKWhMonth: 142,
    patternName: 'Off-Peak Zero Consumption',
    evidenceSource: 'Smart Meter',
    safeguardStatus: 'All Passed',
    caseStatus: 'New',
    monthlyRiskPercentage: 42,
    smartMeterRiskPercentage: 86,
    combinedEvidenceStrength: 'Strong',
    pipelineAgreement: 'Partial',
    lastUpdated: '2026-08-26 10:00 PKT',
  },
  {
    id: 'INV-08111',
    consumerId: 'C-08111',
    meterId: 'MTR-390112',
    feederId: 'FDR-08',
    pmtId: 'PMT-082',
    priority: 'Medium',
    calibratedRiskPercentage: 68,
    estimatedImpactKWhMonth: 95,
    patternName: 'Step-Down Trend Shift',
    evidenceSource: 'Monthly Billing',
    safeguardStatus: 'All Passed',
    caseStatus: 'New',
    monthlyRiskPercentage: 68,
    smartMeterRiskPercentage: 0,
    combinedEvidenceStrength: 'Moderate',
    pipelineAgreement: 'Monthly Only',
    lastUpdated: '2026-08-25 16:45 PKT',
  },
  {
    id: 'INV-01402',
    consumerId: 'C-01402',
    meterId: 'MTR-102948',
    feederId: 'FDR-01',
    pmtId: 'PMT-014',
    priority: 'Medium',
    calibratedRiskPercentage: 62,
    estimatedImpactKWhMonth: 110,
    patternName: 'Night-Time Negative Load Drop',
    evidenceSource: 'Both Pipelines',
    safeguardStatus: 'Action Required',
    caseStatus: 'Under Review',
    monthlyRiskPercentage: 58,
    smartMeterRiskPercentage: 62,
    combinedEvidenceStrength: 'Moderate',
    pipelineAgreement: 'Full',
    lastUpdated: '2026-08-24 11:30 PKT',
  },
];

export const MOCK_EXPLANATION_C08124: RiskExplanation = {
  consumerId: 'C-08124',
  summaryText: 'Monthly records show a moderate decline, while hourly readings reveal repeated drops isolated to peak-tariff hours. PMT residual energy remains elevated during the same periods.',
  treeShapContributions: [
    {
      featureName: 'Peak Tariff Load Ratio (6 PM–10 PM)',
      contributionValue: +0.34,
      description: 'Usage drops by 72% specifically between 18:00 and 22:00 compared to off-peak benchmark.',
      direction: 'increases_risk',
    },
    {
      featureName: 'PMT Residual Co-occurrence',
      contributionValue: +0.28,
      description: 'PMT-081 unaccounted residual surges by 14.2 kWh during peak hours when this meter drops.',
      direction: 'increases_risk',
    },
    {
      featureName: 'Historical 12-Month Slope',
      contributionValue: +0.18,
      description: 'Persistent negative consumption trend (-4.2% per quarter) despite constant connected load.',
      direction: 'increases_risk',
    },
    {
      featureName: 'Registered Solar Generation',
      contributionValue: -0.05,
      description: 'No net-metered solar export registered on account profile.',
      direction: 'decreases_risk',
    },
  ],
  pmtCorroborationText: 'PMT-081 aggregate residual correlates with C-08124 peak-tariff drop with Pearson r = 0.88.',
  safeguards: [
    { id: 'sg-1', name: 'Registered Solar Prosumer', passed: true, detail: 'No solar export active. No rooftop PV system reported.' },
    { id: 'sg-2', name: 'Feeder Outage Impact', passed: true, detail: 'Feeder uptime normalized (98.4%). Outages excluded.' },
    { id: 'sg-3', name: 'Sustained Legitimate Low Baseline', passed: true, detail: 'Not Detected. Sanctioned load 15 kW actively utilized during day.' },
    { id: 'sg-4', name: 'PMT Residual Corroboration', passed: true, detail: 'Present. Residual spike aligns with meter deviation window.' },
    { id: 'sg-5', name: 'Data Quality Check', passed: true, detail: 'Adequate. 99.2% hourly packet reception rate.' },
    { id: 'sg-6', name: 'Field Verification Required', passed: true, detail: 'Mandatory before taking operational or administrative action.' },
  ],
};

export const MOCK_MONTHLY_READINGS: MonthlyReading[] = Array.from({ length: 36 }).map((_, idx) => {
  const date = new Date(2023, idx, 1);
  const monthStr = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
  // Moderate decline in last 8 months
  const base = 450;
  const decline = idx > 28 ? (idx - 28) * 35 : 0;
  const actual = Math.max(120, base + Math.sin(idx) * 30 - decline);
  return {
    monthYear: monthStr,
    billedKWh: Math.round(actual),
    expectedKWh: 460,
    peerMedianKWh: 440,
    isAbnormal: idx > 28,
  };
});

export const MOCK_HOURLY_READINGS: HourlyReading[] = Array.from({ length: 24 }).map((_, hour) => {
  const isPeak = hour >= 18 && hour <= 22; // 6 PM - 10 PM peak tariff
  const expected = hour >= 8 && hour <= 22 ? 8.5 : 2.2;
  const actual = isPeak ? 1.4 : (hour >= 8 && hour <= 17 ? 8.2 : 2.1);
  const residual = isPeak ? 14.5 : 2.4;

  return {
    timestamp: `2026-08-26T${String(hour).padStart(2, '0')}:00:00+05:00`,
    hourOfDay: hour,
    actualUsageKWh: Number(actual.toFixed(1)),
    expectedUsageKWh: Number(expected.toFixed(1)),
    pmtResidualKWh: Number(residual.toFixed(1)),
    isPeakTariffHour: isPeak,
  };
});

export const MOCK_PIPELINE_COMPARISON: PipelineComparison = {
  monthlyOnlyCount: 142,
  smartMeterOnlyCount: 215,
  bothPipelinesCount: 125,
  overlapPercentage: 38.6,
  anomalyTypeBreakdown: [
    { type: 'Peak-Hour Deviation', count: 182 },
    { type: 'Step-Down Trend Shift', count: 114 },
    { type: 'Zero-Consumption Spells', count: 96 },
    { type: 'Phase Imbalance / Load Shift', count: 54 },
    { type: 'Off-Peak Zero Load', count: 36 },
  ],
  coverageStats: {
    totalConnections: 10000,
    monthlyCovered: 10000,
    smartMeterCovered: 6840,
    dualCovered: 6840,
  },
};

export const MOCK_JOB_CARDS: JobCard[] = [
  {
    id: 'JC-2026-081',
    consumerId: 'C-08124',
    meterId: 'MTR-481092',
    serviceArea: 'Faisalabad West Division',
    feederId: 'FDR-08',
    pmtId: 'PMT-081',
    priority: 'High',
    evidenceSummary: 'Peak-hour usage drop (18:00-22:00 PKT) co-occurring with PMT-081 residual spike. Calibrated risk 91%.',
    relevantPeriodsText: 'Daily 18:00 - 22:00 PKT (Aug 1 - Aug 26, 2026)',
    estimatedImpactKWhMonth: 184,
    safeguardsSummary: 'All 6 safeguards verified. Solar prosumer excluded. Feeder outages normalized.',
    recommendedChecks: [
      'Inspect physical meter optical port & terminal cover seals.',
      'Check for neutral loop / shunted current transformer (CT) wiring.',
      'Verify incoming secondary cable connection before meter box.',
      'Test meter display under live clamp-meter load measurement.',
    ],
    analystNotes: 'Prioritize physical inspection during peak tariff window (18:00 - 20:00). Contact supervisor if meter box is locked.',
    assignedTeam: 'Field Squad Alpha (Faisalabad)',
    scheduledDate: '2026-08-27',
    status: 'Assigned',
    createdAt: '2026-08-26 15:00 PKT',
  },
  {
    id: 'JC-2026-042',
    consumerId: 'C-01402',
    meterId: 'MTR-102948',
    serviceArea: 'Lahore Central',
    feederId: 'FDR-01',
    pmtId: 'PMT-014',
    priority: 'Medium',
    evidenceSummary: 'Night-time negative load drop co-occurring with PMT balance residual. Calibrated risk 62%.',
    relevantPeriodsText: '01:00 - 05:00 PKT daily',
    estimatedImpactKWhMonth: 110,
    safeguardsSummary: 'Requires prosumer tariff re-verification.',
    recommendedChecks: [
      'Inspect meter terminal blocks and CT ratio.',
      'Check for physical bypass switch behind wall panel.',
    ],
    analystNotes: 'Check commercial operating hours.',
    assignedTeam: 'Field Squad Bravo (Lahore)',
    scheduledDate: '2026-08-26',
    status: 'In Progress' as any,
    createdAt: '2026-08-25 09:30 PKT',
  },
];

export const MOCK_DATA_SOURCES: DataSourceStatus[] = [
  { id: 'ds-1', name: 'Monthly Billing ERP (SAP IS-U)', type: 'Database CDC', lastIngestedAt: '2026-08-26 04:00 PKT', recordCount: 124500, status: 'Active', latencyMs: 120 },
  { id: 'ds-2', name: 'AMI Smart-Meter Telemetry (HES)', type: 'Kafka Stream', lastIngestedAt: '2026-08-26 18:28 PKT', recordCount: 6840000, status: 'Active', latencyMs: 45 },
  { id: 'ds-3', name: 'PMT Balance Metering System', type: 'Modbus / MQTT', lastIngestedAt: '2026-08-26 18:29 PKT', recordCount: 300, status: 'Active', latencyMs: 30 },
  { id: 'ds-4', name: 'GIS Feeder Topology & Consumer Registry', type: 'PostGIS API', lastIngestedAt: '2026-08-25 00:00 PKT', recordCount: 10000, status: 'Active', latencyMs: 85 },
  { id: 'ds-5', name: 'Prosumer Solar Registry (NEPRA)', type: 'REST Import', lastIngestedAt: '2026-08-20 12:00 PKT', recordCount: 420, status: 'Active', latencyMs: 210 },
];

export const MOCK_MODEL_SERVICES: ModelServiceStatus[] = [
  { id: 'ms-1', name: 'Isolation Forest Anomaly Scoring', technology: 'Python Scikit-Learn', version: 'v2.4.1', status: 'Healthy', p95LatencyMs: 85, endpoint: 'http://localhost:8000/api/models/iforest' },
  { id: 'ms-2', name: 'XGBoost Risk Classifier', technology: 'Alibaba Cloud PAI-EAS', version: 'v3.1.0', status: 'Healthy', p95LatencyMs: 140, endpoint: 'http://localhost:8000/api/models/xgboost' },
  { id: 'ms-3', name: 'Isotonic Probability Calibrator', technology: 'Python Function Compute', version: 'v1.0.2', status: 'Healthy', p95LatencyMs: 25, endpoint: 'http://localhost:8000/api/models/calibrate' },
  { id: 'ms-4', name: 'TreeSHAP Explanation Engine', technology: 'SHAP C-Extension', version: 'v0.44.0', status: 'Healthy', p95LatencyMs: 310, endpoint: 'http://localhost:8000/api/models/treeshap' },
];

export const MOCK_AUDIT_EVENTS: AuditEvent[] = [
  { id: 'aud-101', actor: 'analyst.hamza@disco.gov.pk', timestamp: '2026-08-26 18:35 PKT', action: 'CREATE_JOB_CARD', objectId: 'JC-2026-081', result: 'Success' },
  { id: 'aud-102', actor: 'system.job_runner', timestamp: '2026-08-26 18:30 PKT', action: 'BATCH_GRID_ANALYSIS', objectId: 'JOB-9021', result: 'Success' },
  { id: 'aud-103', actor: 'field.supervisor@disco.gov.pk', timestamp: '2026-08-26 16:10 PKT', action: 'ASSIGN_JOB_CARD', objectId: 'JC-2026-042', result: 'Success' },
  { id: 'aud-104', actor: 'admin.user@disco.gov.pk', timestamp: '2026-08-25 14:20 PKT', action: 'TRIGGER_MODEL_RECALIBRATION', objectId: 'ms-3', result: 'Success' },
];
