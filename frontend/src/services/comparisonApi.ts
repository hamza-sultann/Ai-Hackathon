import { apiClient, fetchWithMockFallback } from '../lib/api/client';
import { API_ENDPOINTS } from '../lib/api/endpoints';
import { PipelineComparison } from '../types';
import { MOCK_PIPELINE_COMPARISON } from './mockData';

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export const comparisonApi = {
  getPipelineComparison: async (): Promise<PipelineComparison> => {
    return fetchWithMockFallback(
      async () => {
        return await apiClient.get<unknown, PipelineComparison>(API_ENDPOINTS.PIPELINE_COMPARISON);
      },
      async () => {
        await delay(200);
        return { ...MOCK_PIPELINE_COMPARISON };
      }
    );
  },
};
