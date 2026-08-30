// Endpoint definitions — generated to unblock local dev while the real
// src/lib/api/endpoints.ts is missing from this branch.
// Update paths to match the actual FastAPI backend once confirmed.

export const API_ENDPOINTS = {
  // Overview
  OVERVIEW: '/overview',

  // Admin
  ADMIN_DATA_SOURCES: '/admin/data-sources',
  ADMIN_MODEL_SERVICES: '/admin/model-services',
  ADMIN_AUDIT: '/admin/audit',

  // Analyses
  ANALYSES: '/analyses',
  ANALYSIS_STATUS: (jobId: string) => `/analyses/${jobId}`,

  // Comparison
  PIPELINE_COMPARISON: '/comparison/pipeline',

  // Field
  FIELD_OVERVIEW: '/field/overview',
  FIELD_JOBS: '/field/jobs',
  JOB_CARD_FINDINGS: (jobCardId: string) => `/field/jobs/${jobCardId}/findings`,

  // Grid
  FEEDERS: '/grid/feeders',
  FEEDER_DETAIL: (feederId: string) => `/grid/feeders/${feederId}`,
  FEEDER_PMTS: (feederId: string) => `/grid/feeders/${feederId}/pmts`,
  PMT_DETAIL: (pmtId: string) => `/grid/pmts/${pmtId}`,
  PMT_CONSUMERS: (pmtId: string) => `/grid/pmts/${pmtId}/consumers`,

  // Investigations
  INVESTIGATIONS: '/investigations',
  INVESTIGATION_DETAIL: (consumerId: string) => `/investigations/${consumerId}`,
  INVESTIGATION_EXPLANATION: (consumerId: string) => `/investigations/${consumerId}/explanation`,

  // Job Cards
  JOB_CARDS: '/job-cards',
  JOB_CARD_DETAIL: (id: string) => `/job-cards/${id}`,
};
