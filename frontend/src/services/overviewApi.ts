import { apiClient } from '../lib/api/client';
import { API_ENDPOINTS } from '../lib/api/endpoints';
import { SystemOverview } from '../types';

export const overviewApi = {
  getOverview: async (): Promise<SystemOverview> => {
    return await apiClient.get<unknown, SystemOverview>(API_ENDPOINTS.OVERVIEW);
  },
};

