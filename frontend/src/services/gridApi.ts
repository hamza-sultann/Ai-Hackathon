import { apiClient, fetchWithMockFallback } from '../lib/api/client';
import { API_ENDPOINTS } from '../lib/api/endpoints';
import { Feeder, PMT, Consumer } from '../types';
import { MOCK_FEEDERS, MOCK_PMTS } from './mockData';

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export const gridApi = {
  getFeeders: async (): Promise<Feeder[]> => {
    return fetchWithMockFallback(
      async () => {
        return await apiClient.get<unknown, Feeder[]>(API_ENDPOINTS.FEEDERS);
      },
      async () => {
        await delay(200);
        return [...MOCK_FEEDERS];
      }
    );
  },

  getFeederById: async (feederId: string): Promise<Feeder | undefined> => {
    return fetchWithMockFallback(
      async () => {
        return await apiClient.get<unknown, Feeder>(API_ENDPOINTS.FEEDER_DETAIL(feederId));
      },
      async () => {
        await delay(150);
        return MOCK_FEEDERS.find((f) => f.id === feederId);
      }
    );
  },

  getPmtsByFeeder: async (feederId: string): Promise<PMT[]> => {
    return fetchWithMockFallback(
      async () => {
        return await apiClient.get<unknown, PMT[]>(API_ENDPOINTS.FEEDER_PMTS(feederId));
      },
      async () => {
        await delay(200);
        return MOCK_PMTS.filter((p) => p.feederId === feederId);
      }
    );
  },

  getPmtById: async (pmtId: string): Promise<PMT | undefined> => {
    return fetchWithMockFallback(
      async () => {
        return await apiClient.get<unknown, PMT>(API_ENDPOINTS.PMT_DETAIL(pmtId));
      },
      async () => {
        await delay(150);
        return MOCK_PMTS.find((p) => p.id === pmtId);
      }
    );
  },

  getConsumersByPmt: async (pmtId: string): Promise<Consumer[]> => {
    return fetchWithMockFallback(
      async () => {
        return await apiClient.get<unknown, Consumer[]>(API_ENDPOINTS.PMT_CONSUMERS(pmtId));
      },
      async () => {
        await delay(200);
        return [
          {
            id: 'C-08124',
            meterId: 'MTR-481092',
            feederId: 'FDR-08',
            pmtId: pmtId,
            tariffCategory: 'B-2 Industrial',
            sanctionedLoadKW: 15,
            address: 'Plot 42, Sector C-2, Industrial Estate',
            hasSmartMeter: true,
            isRegisteredSolarProsumer: false,
          },
          {
            id: 'C-08129',
            meterId: 'MTR-481105',
            feederId: 'FDR-08',
            pmtId: pmtId,
            tariffCategory: 'A-2 Commercial',
            sanctionedLoadKW: 10,
            address: 'Plot 48, Sector C-2, Main Road',
            hasSmartMeter: true,
            isRegisteredSolarProsumer: false,
          },
        ];
      }
    );
  },
};
