import { apiClient, fetchWithMockFallback } from '../lib/api/client';
import { API_ENDPOINTS } from '../lib/api/endpoints';
import { AnalysisJob, AnalysisScope, AnalysisPipeline } from '../types';

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

const mockJobs: Record<string, AnalysisJob> = {};

export const analysisApi = {
  startAnalysis: async (scope: AnalysisScope, pipelines: AnalysisPipeline, targetId?: string): Promise<AnalysisJob> => {
    return fetchWithMockFallback(
      async () => {
        return await apiClient.post<unknown, AnalysisJob>(API_ENDPOINTS.ANALYSES, {
          scope,
          pipelines,
          targetId,
        });
      },
      async () => {
        await delay(300);
        const jobId = `JOB-${Math.floor(1000 + Math.random() * 9000)}`;
        const job: AnalysisJob = {
          id: jobId,
          status: 'validating_data',
          progressPercentage: 15,
          scope,
          targetId,
          pipelines,
          createdAt: new Date().toISOString(),
        };
        mockJobs[jobId] = job;
        return job;
      }
    );
  },

  getAnalysisStatus: async (jobId: string): Promise<AnalysisJob> => {
    return fetchWithMockFallback(
      async () => {
        return await apiClient.get<unknown, AnalysisJob>(API_ENDPOINTS.ANALYSIS_STATUS(jobId));
      },
      async () => {
        await delay(200);
        let job = mockJobs[jobId];
        if (!job) {
          job = {
            id: jobId,
            status: 'completed',
            progressPercentage: 100,
            scope: 'Entire Grid',
            pipelines: 'Both',
            createdAt: new Date().toISOString(),
          };
          return job;
        }

        // Advance progress deterministically in mock mode
        if (job.status === 'validating_data') {
          job.status = 'calculating_pmt_balance';
          job.progressPercentage = 35;
        } else if (job.status === 'calculating_pmt_balance') {
          job.status = 'scoring_anomalies';
          job.progressPercentage = 55;
        } else if (job.status === 'scoring_anomalies') {
          job.status = 'calibrating_risk';
          job.progressPercentage = 75;
        } else if (job.status === 'calibrating_risk') {
          job.status = 'generating_explanations';
          job.progressPercentage = 90;
        } else if (job.status === 'generating_explanations') {
          job.status = 'completed';
          job.progressPercentage = 100;
          job.completedAt = new Date().toISOString();
        }

        return { ...job };
      }
    );
  },
};
