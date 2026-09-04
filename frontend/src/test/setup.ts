import '@testing-library/jest-dom';
import { vi } from 'vitest';
import React from 'react';

// Mock matchMedia for tests
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// Mock ResizeObserver
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));

// Mock IntersectionObserver for framer-motion useInView
class MockIntersectionObserver {
  readonly root: Element | null = null;
  readonly rootMargin: string = '';
  readonly thresholds: ReadonlyArray<number> = [];
  observe = vi.fn();
  unobserve = vi.fn();
  disconnect = vi.fn();
  takeRecords = vi.fn(() => []);
}

Object.defineProperty(global, 'IntersectionObserver', {
  writable: true,
  configurable: true,
  value: MockIntersectionObserver,
});
Object.defineProperty(window, 'IntersectionObserver', {
  writable: true,
  configurable: true,
  value: MockIntersectionObserver,
});

// Mock React Three Fiber Canvas & GridMeshCanvas for JSDOM
vi.mock('@react-three/fiber', () => ({
  Canvas: ({ children }: any) => React.createElement('div', { 'data-testid': 'mock-canvas' }, children),
  useFrame: vi.fn(),
  useThree: () => ({ camera: {}, scene: {}, gl: {} }),
}));

vi.mock('../components/3d/GridMeshCanvas', () => ({
  GridMeshCanvas: () => React.createElement('div', { 'data-testid': 'grid-mesh-canvas' }, '3D Grid Topology Canvas Mock'),
  StaticGridFallback: () => React.createElement('div', null, 'Static Grid Fallback'),
}));

vi.mock('../components/3d/ElectricityShader', () => ({
  ElectricityShader: () => React.createElement('canvas', { 'data-testid': 'electricity-shader' }),
}));

// Mock echarts-for-react for JSDOM
vi.mock('echarts-for-react', () => ({
  default: () => React.createElement('div', { 'data-testid': 'mock-echart' }, 'EChart Mock Component'),
}));

// Mock apiClient for headless Vitest testing
import { apiClient } from '../lib/api/client';

vi.spyOn(apiClient, 'get').mockImplementation(async (url: string) => {
  if (url.includes('/overview')) {
    return {
      injectedEnergyMWh: 12500,
      billedEnergyMWh: 10200,
      estimatedTechnicalLossMWh: 850,
      unaccountedResidualMWh: 1450,
      highPriorityPmtCount: 12,
      connectionsRecommendedForReview: 48,
      lastAnalysisTimestamp: new Date().toISOString(),
      analysisPeriod: 'July 2025 - August 2025',
      analysisStatus: 'Completed',
      monthlyCoveragePercentage: 98.4,
      smartMeterCoveragePercentage: 42.1,
    } as any;
  }
  if (url.includes('/feeders')) {
    return [
      {
        id: 'FDR-01',
        name: 'Industrial Sector 1',
        serviceArea: 'North Zone',
        substation: 'Grid Station A',
        uptimePercentage: 99.2,
        injectedEnergyKWh: 4500000,
        accountedEnergyKWh: 3900000,
        unaccountedResidualKWh: 450000,
        technicalLossPercentage: 3.3,
        priorityPmtCount: 3,
        totalPmtCount: 15,
        trend: 'stable',
      },
    ] as any;
  }
  if (url.includes('/explanation')) {
    return {
      consumerId: 'C-08124',
      summaryText: 'Multi-agent corroboration indicates anomalous behavior requiring field audit.',
      treeShapContributions: [
        { featureName: 'mean_daily_kwh_drop', contributionValue: 0.42, description: '42% drop in daily consumption', direction: 'increases_risk' },
      ],
      pmtCorroborationText: 'PMT corroboration present.',
      safeguards: [
        { id: 'sg-1', name: 'Zero-Consumption Check', passed: true, detail: 'Connection is active' },
      ],
    } as any;
  }
  if (url.includes('/monthly')) {
    return [
      { monthYear: '2025-01', billedKWh: 450, expectedKWh: 460, peerMedianKWh: 440, isAbnormal: false },
    ] as any;
  }
  if (url.includes('/hourly')) {
    return [
      { timestamp: '2025-02-01T00:00:00Z', hourOfDay: 0, actualUsageKWh: 0.5, expectedUsageKWh: 1.8, pmtResidualKWh: 12.4, isPeakTariffHour: false },
    ] as any;
  }
  if (url.includes('/investigations')) {
    const parts = url.split('?')[0].split('/');
    const cid = parts[parts.length - 1] || 'C-08124';
    return {
      id: `INV-${cid}`,
      consumerId: cid,
      meterId: 'MTR-98210',
      feederId: 'FDR-01',
      pmtId: 'PMT-04',
      priority: 'High',
      calibratedRiskPercentage: 89,
      estimatedImpactKWhMonth: 1250,
      patternName: 'Sudden Consumption Drop',
      evidenceSource: 'Both Pipelines',
      safeguardStatus: 'All Passed',
      caseStatus: 'New',
      monthlyRiskPercentage: 85,
      smartMeterRiskPercentage: 92,
      combinedEvidenceStrength: 'Strong',
      pipelineAgreement: 'Full',
      lastUpdated: new Date().toISOString(),
      analystNotes: 'Flagged for audit',
    } as any;
  }
  return [] as any;
});

vi.spyOn(apiClient, 'post').mockImplementation(async () => ({ success: true } as any));
vi.spyOn(apiClient, 'put').mockImplementation(async () => ({ success: true } as any));
vi.spyOn(apiClient, 'patch').mockImplementation(async () => ({ success: true } as any));
vi.spyOn(apiClient, 'delete').mockImplementation(async () => ({ success: true } as any));

