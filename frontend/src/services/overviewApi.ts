import { apiClient, fetchWithMockFallback } from '../lib/api/client';
import { API_ENDPOINTS } from '../lib/api/endpoints';
import { SystemOverview } from '../types';
import { MOCK_SYSTEM_OVERVIEW } from './mockData';

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export const overviewApi = {
  getOverview: async (): Promise<SystemOverview> => {
    return fetchWithMockFallback(
      async () => {
        const response = await apiClient.get<unknown, SystemOverview>(API_ENDPOINTS.OVERVIEW);
        return response;
      },
      async () => {
        await delay(250);
        return { ...MOCK_SYSTEM_OVERVIEW };
      }
    );
  },
};
