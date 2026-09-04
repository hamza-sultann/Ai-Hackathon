import { apiClient } from '../lib/api/client';
import { API_ENDPOINTS } from '../lib/api/endpoints';
import { JobCard, InspectionFinding, FieldSquad, FieldTeamMember } from '../types';

export const fieldApi = {
  getFieldOverviewStats: async () => {
    return await apiClient.get<unknown, { assignedToday: number; highPriority: number; inProgress: number; awaitingReview: number; completedToday: number }>(
      API_ENDPOINTS.FIELD_OVERVIEW
    );
  },

  getAssignedJobs: async (): Promise<JobCard[]> => {
    return await apiClient.get<unknown, JobCard[]>(API_ENDPOINTS.FIELD_JOBS);
  },

  getFieldSquads: async (): Promise<FieldSquad[]> => {
    return await apiClient.get<unknown, FieldSquad[]>(API_ENDPOINTS.FIELD_SQUADS);
  },

  getTeamMembers: async (): Promise<FieldTeamMember[]> => {
    return await apiClient.get<unknown, FieldTeamMember[]>(API_ENDPOINTS.FIELD_TEAM);
  },

  getInspectionHistory: async (): Promise<any[]> => {
    return await apiClient.get<unknown, any[]>(API_ENDPOINTS.FIELD_HISTORY);
  },

  submitFinding: async (finding: InspectionFinding): Promise<{ success: boolean; message: string }> => {
    return await apiClient.post<unknown, { success: boolean; message: string }>(
      API_ENDPOINTS.JOB_CARD_FINDINGS(finding.jobCardId),
      finding
    );
  },

  getFindingByJobCardId: async (jobCardId: string): Promise<InspectionFinding | undefined> => {
    return await apiClient.get<unknown, InspectionFinding>(
      API_ENDPOINTS.JOB_CARD_FINDINGS(jobCardId)
    );
  },
};


