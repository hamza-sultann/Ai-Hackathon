import { apiClient } from '../lib/api/client';
import { API_ENDPOINTS } from '../lib/api/endpoints';
import { PipelineComparison } from '../types';

export const comparisonApi = {
  getPipelineComparison: async (): Promise<PipelineComparison> => {
    return await apiClient.get<unknown, PipelineComparison>(API_ENDPOINTS.PIPELINE_COMPARISON);
  },
};

