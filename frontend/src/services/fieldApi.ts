import { apiClient, fetchWithMockFallback } from '../lib/api/client';
import { API_ENDPOINTS } from '../lib/api/endpoints';
import { JobCard, InspectionFinding, FieldSquad, FieldTeamMember } from '../types';
import { MOCK_JOB_CARDS, MOCK_FIELD_SQUADS, MOCK_TEAM_MEMBERS, MOCK_INSPECTION_HISTORY } from './mockData';

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

let localFindings: Record<string, InspectionFinding> = {};

export const fieldApi = {
  getFieldOverviewStats: async () => {
    return fetchWithMockFallback(
      async () => {
        return await apiClient.get<unknown, { assignedToday: number; highPriority: number; inProgress: number; awaitingReview: number; completedToday: number }>(
          API_ENDPOINTS.FIELD_OVERVIEW
        );
      },
      async () => {
        await delay(200);
        return {
          assignedToday: 8,
          highPriority: 5,
          inProgress: 3,
          awaitingReview: 2,
          completedToday: 4,
        };
      }
    );
  },

  getAssignedJobs: async (): Promise<JobCard[]> => {
    return fetchWithMockFallback(
      async () => {
        return await apiClient.get<unknown, JobCard[]>(API_ENDPOINTS.FIELD_JOBS);
      },
      async () => {
        await delay(250);
        return [...MOCK_JOB_CARDS];
      }
    );
  },

  getFieldSquads: async (): Promise<FieldSquad[]> => {
    await delay(200);
    return [...MOCK_FIELD_SQUADS];
  },

  getTeamMembers: async (): Promise<FieldTeamMember[]> => {
    await delay(200);
    return [...MOCK_TEAM_MEMBERS];
  },

  getInspectionHistory: async (): Promise<any[]> => {
    await delay(250);
    return [...MOCK_INSPECTION_HISTORY];
  },

  submitFinding: async (finding: InspectionFinding): Promise<{ success: boolean; message: string }> => {
    return fetchWithMockFallback(
      async () => {
        return await apiClient.post<unknown, { success: boolean; message: string }>(
          API_ENDPOINTS.JOB_CARD_FINDINGS(finding.jobCardId),
          finding
        );
      },
      async () => {
        await delay(400);
        localFindings[finding.jobCardId] = finding;
        return {
          success: true,
          message: 'Inspection findings recorded and queued for supervisor review.',
        };
      }
    );
  },

  getFindingByJobCardId: async (jobCardId: string): Promise<InspectionFinding | undefined> => {
    return fetchWithMockFallback(
      async () => {
        return await apiClient.get<unknown, InspectionFinding>(
          API_ENDPOINTS.JOB_CARD_FINDINGS(jobCardId)
        );
      },
      async () => {
        await delay(150);
        return localFindings[jobCardId];
      }
    );
  },
};

