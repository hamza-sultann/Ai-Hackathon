import axios from 'axios';
import { ApiError } from './errors';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
export const USE_MOCK_API = import.meta.env.VITE_USE_MOCK_API !== 'false'; // Default to true if not set to false

export const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
});

apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (axios.isAxiosError(error)) {
      const message = error.response?.data?.message || error.message || 'An unexpected API error occurred.';
      const statusCode = error.response?.status;
      throw new ApiError(message, statusCode, error.response?.data);
    }
    throw new ApiError('Network connection failed.');
  }
);

export async function fetchWithMockFallback<T>(
  realApiCall: () => Promise<T>,
  mockApiCall: () => Promise<T>
): Promise<T> {
  if (USE_MOCK_API) {
    return mockApiCall();
  }
  try {
    return await realApiCall();
  } catch (error) {
    console.warn('Real API call failed. Falling back to mock data.', error);
    return mockApiCall();
  }
}
