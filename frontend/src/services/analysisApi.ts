import { apiClient } from '../lib/api/client';
import { API_ENDPOINTS } from '../lib/api/endpoints';
import { AnalysisJob, AnalysisScope, AnalysisPipeline } from '../types';

export const analysisApi = {
  startAnalysis: async (scope: AnalysisScope, pipelines: AnalysisPipeline, targetId?: string): Promise<AnalysisJob> => {
    return await apiClient.post<unknown, AnalysisJob>(API_ENDPOINTS.ANALYSES, {
      scope,
      pipelines,
      targetId,
    });
  },

  getAnalysisStatus: async (jobId: string): Promise<AnalysisJob> => {
    return await apiClient.get<unknown, AnalysisJob>(API_ENDPOINTS.ANALYSIS_STATUS(jobId));
  },
};

