import { apiClient } from '../lib/api/client';
import { API_ENDPOINTS } from '../lib/api/endpoints';
import { DataSourceStatus, ModelServiceStatus, AuditEvent, AdminUser, SystemConfig, AppNotification } from '../types';

export const adminApi = {
  getDataSources: async (): Promise<DataSourceStatus[]> => {
    return await apiClient.get<unknown, DataSourceStatus[]>(API_ENDPOINTS.ADMIN_DATA_SOURCES);
  },

  triggerDataSourceSync: async (sourceId: string): Promise<{ success: boolean; message: string; timestamp: string }> => {
    return await apiClient.post<unknown, { success: boolean; message: string; timestamp: string }>(
      API_ENDPOINTS.ADMIN_SYNC_DATA_SOURCE(sourceId)
    );
  },

  getModelServices: async (): Promise<ModelServiceStatus[]> => {
    return await apiClient.get<unknown, ModelServiceStatus[]>(API_ENDPOINTS.ADMIN_MODEL_SERVICES);
  },

  testModelInference: async (modelId: string, inputPayload?: any): Promise<any> => {
    return await apiClient.post<unknown, any>(
      API_ENDPOINTS.ADMIN_TEST_MODEL(modelId),
      inputPayload || {}
    );
  },

  getUsers: async (): Promise<AdminUser[]> => {
    return await apiClient.get<unknown, AdminUser[]>(API_ENDPOINTS.ADMIN_USERS);
  },

  addUser: async (user: Omit<AdminUser, 'id' | 'lastLogin'>): Promise<AdminUser> => {
    const newUser: AdminUser = {
      ...user,
      id: `usr-${Date.now()}`,
      lastLogin: 'Never (Invited)',
    };
    return newUser;
  },

  getAuditActivity: async (): Promise<AuditEvent[]> => {
    return await apiClient.get<unknown, AuditEvent[]>(API_ENDPOINTS.ADMIN_AUDIT);
  },

  getConfig: async (): Promise<SystemConfig> => {
    return await apiClient.get<unknown, SystemConfig>(API_ENDPOINTS.ADMIN_CONFIG);
  },

  updateConfig: async (newConfig: Partial<SystemConfig>): Promise<{ success: boolean; config: SystemConfig }> => {
    return await apiClient.patch<unknown, { success: boolean; config: SystemConfig }>(
      API_ENDPOINTS.ADMIN_CONFIG,
      newConfig
    );
  },

  getNotifications: async (): Promise<AppNotification[]> => {
    // Dummy notifications removed - strictly empty/live notifications
    return [];
  },

  markNotificationsRead: async (): Promise<void> => {
    // No-op since dummy notifications are removed
  },
};


