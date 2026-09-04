import { apiClient } from '../lib/api/client';
import { API_ENDPOINTS } from '../lib/api/endpoints';
import { JobCard } from '../types';

export const jobCardsApi = {
  getJobCards: async (): Promise<JobCard[]> => {
    return await apiClient.get<unknown, JobCard[]>(API_ENDPOINTS.JOB_CARDS);
  },

  getJobCardById: async (id: string): Promise<JobCard | undefined> => {
    return await apiClient.get<unknown, JobCard>(API_ENDPOINTS.JOB_CARD_DETAIL(id));
  },

  createJobCard: async (data: Omit<JobCard, 'id' | 'createdAt' | 'status'>): Promise<JobCard> => {
    return await apiClient.post<unknown, JobCard>(API_ENDPOINTS.JOB_CARDS, data);
  },

  updateJobCardStatus: async (id: string, status: JobCard['status']): Promise<JobCard> => {
    return await apiClient.patch<unknown, JobCard>(API_ENDPOINTS.JOB_CARD_DETAIL(id), { status });
  },
};

