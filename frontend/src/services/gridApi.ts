import { apiClient } from '../lib/api/client';
import { API_ENDPOINTS } from '../lib/api/endpoints';
import { Feeder, PMT, Consumer } from '../types';

export const gridApi = {
  getFeeders: async (): Promise<Feeder[]> => {
    return await apiClient.get<unknown, Feeder[]>(API_ENDPOINTS.FEEDERS);
  },

  getFeederById: async (feederId: string): Promise<Feeder | undefined> => {
    return await apiClient.get<unknown, Feeder>(API_ENDPOINTS.FEEDER_DETAIL(feederId));
  },

  getPmtsByFeeder: async (feederId: string): Promise<PMT[]> => {
    return await apiClient.get<unknown, PMT[]>(API_ENDPOINTS.FEEDER_PMTS(feederId));
  },

  getPmtById: async (pmtId: string): Promise<PMT | undefined> => {
    return await apiClient.get<unknown, PMT>(API_ENDPOINTS.PMT_DETAIL(pmtId));
  },

  getConsumersByPmt: async (pmtId: string): Promise<Consumer[]> => {
    return await apiClient.get<unknown, Consumer[]>(API_ENDPOINTS.PMT_CONSUMERS(pmtId));
  },
};

