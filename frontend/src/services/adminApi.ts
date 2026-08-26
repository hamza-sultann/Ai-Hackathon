import { apiClient, fetchWithMockFallback } from '../lib/api/client';
import { API_ENDPOINTS } from '../lib/api/endpoints';
import { DataSourceStatus, ModelServiceStatus, AuditEvent } from '../types';
import { MOCK_DATA_SOURCES, MOCK_MODEL_SERVICES, MOCK_AUDIT_EVENTS } from './mockData';

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export const adminApi = {
  getDataSources: async (): Promise<DataSourceStatus[]> => {
    return fetchWithMockFallback(
      async () => await apiClient.get<unknown, DataSourceStatus[]>(API_ENDPOINTS.ADMIN_DATA_SOURCES),
      async () => {
        await delay(200);
        return [...MOCK_DATA_SOURCES];
      }
    );
  },

  getModelServices: async (): Promise<ModelServiceStatus[]> => {
    return fetchWithMockFallback(
      async () => await apiClient.get<unknown, ModelServiceStatus[]>(API_ENDPOINTS.ADMIN_MODEL_SERVICES),
      async () => {
        await delay(200);
        return [...MOCK_MODEL_SERVICES];
      }
    );
  },

  getAuditActivity: async (): Promise<AuditEvent[]> => {
    return fetchWithMockFallback(
      async () => await apiClient.get<unknown, AuditEvent[]>(API_ENDPOINTS.ADMIN_AUDIT),
      async () => {
        await delay(200);
        return [...MOCK_AUDIT_EVENTS];
      }
    );
  },
};
