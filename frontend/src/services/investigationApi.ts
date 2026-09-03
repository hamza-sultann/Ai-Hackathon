import { apiClient, fetchWithMockFallback } from '../lib/api/client';
import { API_ENDPOINTS } from '../lib/api/endpoints';
import { Investigation, RiskExplanation, MonthlyReading, HourlyReading } from '../types';
import {
  MOCK_INVESTIGATIONS,
  MOCK_EXPLANATION_C08124,
  MOCK_MONTHLY_READINGS,
  MOCK_HOURLY_READINGS,
} from './mockData';

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export const investigationApi = {
  getInvestigations: async (): Promise<Investigation[]> => {
    return fetchWithMockFallback(
      async () => {
        return await apiClient.get<unknown, Investigation[]>(API_ENDPOINTS.INVESTIGATIONS);
      },
      async () => {
        await delay(250);
        return [...MOCK_INVESTIGATIONS];
      }
    );
  },

  getInvestigationByConsumerId: async (consumerId: string): Promise<Investigation | undefined> => {
    return fetchWithMockFallback(
      async () => {
        return await apiClient.get<unknown, Investigation>(
          API_ENDPOINTS.INVESTIGATION_DETAIL(consumerId)
        );
      },
      async () => {
        await delay(200);
        return MOCK_INVESTIGATIONS.find((inv) => inv.consumerId === consumerId);
      }
    );
  },

  getExplanationByConsumerId: async (consumerId: string): Promise<RiskExplanation> => {
    return fetchWithMockFallback(
      async () => {
        return await apiClient.get<unknown, RiskExplanation>(
          API_ENDPOINTS.INVESTIGATION_EXPLANATION(consumerId)
        );
      },
      async () => {
        await delay(250);
        if (consumerId === 'C-08124') {
          return { ...MOCK_EXPLANATION_C08124 };
        }
        return {
          consumerId,
          summaryText: `Analysis indicates anomalous usage pattern for ${consumerId}. PMT residual corroboration active.`,
          treeShapContributions: [
            {
              featureName: 'Usage Deviation',
              contributionValue: +0.25,
              description: 'Observed usage is lower than expected baseline.',
              direction: 'increases_risk',
            },
          ],
          pmtCorroborationText: 'PMT residual correlates with consumption drops.',
          safeguards: [
            { id: 'sg-1', name: 'Registered Solar Prosumer', passed: true, detail: 'No solar export active.' },
            { id: 'sg-2', name: 'Feeder Outage Impact', passed: true, detail: 'Feeder uptime normalized.' },
            { id: 'sg-6', name: 'Field Verification Required', passed: true, detail: 'Mandatory prior to action.' },
          ],
        };
      }
    );
  },

  getMonthlyReadings: async (consumerId: string): Promise<MonthlyReading[]> => {
    return fetchWithMockFallback(
      async () => {
        return await apiClient.get<unknown, MonthlyReading[]>(
          `${API_ENDPOINTS.INVESTIGATION_DETAIL(consumerId)}/monthly`
        );
      },
      async () => {
        await delay(200);
        return [...MOCK_MONTHLY_READINGS];
      }
    );
  },

  getHourlyReadings: async (consumerId: string): Promise<HourlyReading[]> => {
    return fetchWithMockFallback(
      async () => {
        return await apiClient.get<unknown, HourlyReading[]>(
          `${API_ENDPOINTS.INVESTIGATION_DETAIL(consumerId)}/hourly`
        );
      },
      async () => {
        await delay(200);
        return [...MOCK_HOURLY_READINGS];
      }
    );
  },
};
