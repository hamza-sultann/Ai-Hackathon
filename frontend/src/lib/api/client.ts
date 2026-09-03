// Minimal fetch-based API client.
//
// Usage pattern across services: apiClient.get<unknown, T>(url),
// apiClient.post<unknown, T>(url, body), apiClient.patch<unknown, T>(url, body).
// Base URL + mock toggle come from VITE_API_BASE_URL / VITE_USE_MOCK_API.

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
const USE_MOCK = import.meta.env.VITE_USE_MOCK_API === 'true';

async function request<TResponse>(
  method: 'GET' | 'POST' | 'PATCH' | 'PUT' | 'DELETE',
  url: string,
  body?: unknown
): Promise<TResponse> {
  const res = await fetch(`${BASE_URL}${url}`, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    throw new Error(`API request failed: ${method} ${url} (${res.status})`);
  }

  // Handle empty responses gracefully
  const text = await res.text();
  return (text ? JSON.parse(text) : undefined) as TResponse;
}

export const apiClient = {
  get: <_TBody, TResponse>(url: string) => request<TResponse>('GET', url),
  post: <_TBody, TResponse>(url: string, body?: _TBody) => request<TResponse>('POST', url, body),
  patch: <_TBody, TResponse>(url: string, body?: _TBody) => request<TResponse>('PATCH', url, body),
  put: <_TBody, TResponse>(url: string, body?: _TBody) => request<TResponse>('PUT', url, body),
  delete: <_TBody, TResponse>(url: string) => request<TResponse>('DELETE', url),
};

/**
 * Tries the real API call when mock mode is off; falls back to mock data
 * automatically when mock mode is on, OR when the real call fails
 * (e.g. backend isn't running yet).
 */
export async function fetchWithMockFallback<T>(
  realCall: () => Promise<T>,
  mockCall: () => Promise<T>
): Promise<T> {
  if (USE_MOCK) {
    return mockCall();
  }
  try {
    return await realCall();
  } catch (err) {
    console.warn('API call failed, falling back to mock data:', err);
    return mockCall();
  }
}
