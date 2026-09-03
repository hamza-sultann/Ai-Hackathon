export const COLOR_TOKENS = {
  bgPrimary: '#070A09',
  bgSecondary: '#0C110E',
  surfacePrimary: '#101512',
  surfaceElevated: '#161D19',
  borderSubtle: '#263129',
  textPrimary: '#F3F7F4',
  textSecondary: '#9BA8A0',
  brandPrimary: '#B6F542',
  brandHover: '#CAFF69',
  monthly: '#F5B942',
  smartMeter: '#40D9E8',
  healthy: '#63D98A',
  priorityMedium: '#FF9F43',
  priorityHigh: '#FF6262',
} as const;

export const CHART_COLORS = {
  injected: '#40D9E8',
  billed: '#63D98A',
  technicalLoss: '#F5B942',
  residual: '#FF6262',
  monthlyPipeline: '#F5B942',
  smartMeterPipeline: '#40D9E8',
  agreement: '#B6F542',
};

export const RESPONSIBLE_TERMINOLOGY = {
  SYSTEM_DISCLAIMER: 'Istikshaf is an inspection-support system. It prioritizes evidence-backed grid-loss patterns and does not determine or confirm electricity theft.',
  FIELD_VERIFICATION_REQUIRED: 'This recommendation indicates anomalous behavior and requires field verification. It is not a determination of theft.',
  JOB_CARD_DISCLAIMER: 'This job-card is an inspection recommendation based on anomalous data patterns. It is not proof or a determination of electricity theft.',
};

export const GLOSSARY_HELPERS = {
  PMT: 'Pole-Mounted Transformer — local step-down transformer supplying low-voltage energy to a neighborhood consumer group.',
  UNACCOUNTED_RESIDUAL: 'The energy difference remaining after accounting for billed usage and estimated grid technical loss from total injected energy.',
  CALIBRATED_ANOMALY_RISK: 'Statistical probability score (0–100%) indicating how strongly observed consumption patterns deviate from physical and historical baselines.',
  PIPELINE_AGREEMENT: 'Consensus degree between long-term monthly billing trends and hourly smart-meter telemetry.',
};
