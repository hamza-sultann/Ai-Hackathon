import axios from 'axios';
import { ApiError } from './errors';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
export const USE_MOCK_API = false;

export const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
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
  _mockApiCall?: () => Promise<T>
): Promise<T> {
  return await realApiCall();
}

