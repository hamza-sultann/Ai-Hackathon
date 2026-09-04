import { apiClient } from '../lib/api/client';
import { API_ENDPOINTS } from '../lib/api/endpoints';
import { Investigation, RiskExplanation, MonthlyReading, HourlyReading } from '../types';

export const investigationApi = {
  getInvestigations: async (): Promise<Investigation[]> => {
    return await apiClient.get<unknown, Investigation[]>(API_ENDPOINTS.INVESTIGATIONS);
  },

  getInvestigationByConsumerId: async (consumerId: string): Promise<Investigation | undefined> => {
    return await apiClient.get<unknown, Investigation>(
      API_ENDPOINTS.INVESTIGATION_DETAIL(consumerId)
    );
  },

  getExplanationByConsumerId: async (consumerId: string): Promise<RiskExplanation> => {
    return await apiClient.get<unknown, RiskExplanation>(
      API_ENDPOINTS.INVESTIGATION_EXPLANATION(consumerId)
    );
  },

  getMonthlyReadings: async (consumerId: string): Promise<MonthlyReading[]> => {
    return await apiClient.get<unknown, MonthlyReading[]>(
      API_ENDPOINTS.INVESTIGATION_MONTHLY(consumerId)
    );
  },

  getHourlyReadings: async (consumerId: string): Promise<HourlyReading[]> => {
    return await apiClient.get<unknown, HourlyReading[]>(
      API_ENDPOINTS.INVESTIGATION_HOURLY(consumerId)
    );
  },
};

