import { apiClient, fetchWithMockFallback } from '../lib/api/client';
import { API_ENDPOINTS } from '../lib/api/endpoints';
import { JobCard } from '../types';
import { MOCK_JOB_CARDS } from './mockData';

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

let localJobCards = [...MOCK_JOB_CARDS];

export const jobCardsApi = {
  getJobCards: async (): Promise<JobCard[]> => {
    return fetchWithMockFallback(
      async () => {
        return await apiClient.get<unknown, JobCard[]>(API_ENDPOINTS.JOB_CARDS);
      },
      async () => {
        await delay(200);
        return [...localJobCards];
      }
    );
  },

  getJobCardById: async (id: string): Promise<JobCard | undefined> => {
    return fetchWithMockFallback(
      async () => {
        return await apiClient.get<unknown, JobCard>(API_ENDPOINTS.JOB_CARD_DETAIL(id));
      },
      async () => {
        await delay(150);
        return localJobCards.find((jc) => jc.id === id);
      }
    );
  },

  createJobCard: async (data: Omit<JobCard, 'id' | 'createdAt' | 'status'>): Promise<JobCard> => {
    return fetchWithMockFallback(
      async () => {
        return await apiClient.post<unknown, JobCard>(API_ENDPOINTS.JOB_CARDS, data);
      },
      async () => {
        await delay(300);
        const newCard: JobCard = {
          ...data,
          id: `JC-${new Date().getFullYear()}-${Math.floor(100 + Math.random() * 900)}`,
          status: 'Assigned',
          createdAt: new Date().toLocaleString() + ' PKT',
        };
        localJobCards.unshift(newCard);
        return newCard;
      }
    );
  },

  updateJobCardStatus: async (id: string, status: JobCard['status']): Promise<JobCard> => {
    return fetchWithMockFallback(
      async () => {
        return await apiClient.patch<unknown, JobCard>(API_ENDPOINTS.JOB_CARD_DETAIL(id), { status });
      },
      async () => {
        await delay(200);
        const card = localJobCards.find((c) => c.id === id);
        if (card) {
          card.status = status;
        }
        return card || localJobCards[0];
      }
    );
  },
};
