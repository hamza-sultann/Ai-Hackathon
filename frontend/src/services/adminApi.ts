import { apiClient, fetchWithMockFallback } from '../lib/api/client';
import { API_ENDPOINTS } from '../lib/api/endpoints';
import { DataSourceStatus, ModelServiceStatus, AuditEvent, AdminUser, SystemConfig, AppNotification } from '../types';
import {
  MOCK_DATA_SOURCES,
  MOCK_MODEL_SERVICES,
  MOCK_AUDIT_EVENTS,
  MOCK_ADMIN_USERS,
  MOCK_SYSTEM_CONFIG,
  MOCK_NOTIFICATIONS,
} from './mockData';

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

let currentUsers = [...MOCK_ADMIN_USERS];
let currentConfig = { ...MOCK_SYSTEM_CONFIG };
let currentNotifications = [...MOCK_NOTIFICATIONS];

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

  triggerDataSourceSync: async (sourceId: string): Promise<{ success: boolean; message: string; timestamp: string }> => {
    await delay(600);
    return {
      success: true,
      message: `Data ingestion triggered successfully for ${sourceId}. Stream buffer flushed.`,
      timestamp: new Date().toLocaleTimeString('en-US', { hour12: false }) + ' PKT',
    };
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

  testModelInference: async (modelId: string, inputPayload: any): Promise<any> => {
    await delay(450);
    if (modelId === 'ms-4') {
      return {
        modelId,
        output: 'TreeSHAP Computed',
        riskContribution: +0.34,
        topFeature: 'Peak Tariff Load Ratio (6 PM–10 PM)',
        latencyMs: 290,
      };
    }
    return {
      modelId,
      predictionScore: 0.912,
      calibratedProbability: '91.2%',
      classification: 'HIGH_ANOMALY_RISK',
      latencyMs: 135,
    };
  },

  getUsers: async (): Promise<AdminUser[]> => {
    await delay(200);
    return [...currentUsers];
  },

  addUser: async (user: Omit<AdminUser, 'id' | 'lastLogin'>): Promise<AdminUser> => {
    await delay(300);
    const newUser: AdminUser = {
      ...user,
      id: `usr-${Date.now()}`,
      lastLogin: 'Never (Invited)',
    };
    currentUsers.push(newUser);
    return newUser;
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

  getConfig: async (): Promise<SystemConfig> => {
    await delay(150);
    return { ...currentConfig };
  },

  updateConfig: async (newConfig: Partial<SystemConfig>): Promise<{ success: boolean; config: SystemConfig }> => {
    await delay(350);
    currentConfig = { ...currentConfig, ...newConfig };
    return { success: true, config: currentConfig };
  },

  getNotifications: async (): Promise<AppNotification[]> => {
    await delay(150);
    return [...currentNotifications];
  },

  markNotificationsRead: async (): Promise<void> => {
    await delay(100);
    currentNotifications = currentNotifications.map((n) => ({ ...n, read: true }));
  },
};

