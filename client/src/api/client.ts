export interface HealthResponse {
  status: string;
  uptime: number;
  timestamp: string;
}

export interface HelloResponse {
  message: string;
  timestamp: string;
}

export interface ApiError {
  error: {
    code: string;
    message: string;
  };
}

const API_BASE = import.meta.env.VITE_API_BASE_URL || '';

export async function fetchHealth(signal?: AbortSignal): Promise<HealthResponse> {
  const res = await fetch(`${API_BASE}/health`, { signal });
  if (!res.ok) {
    throw new Error(`Health check failed with status ${res.status}`);
  }
  return res.json();
}

export async function fetchHello(signal?: AbortSignal): Promise<HelloResponse> {
  const res = await fetch(`${API_BASE}/api/hello`, { signal });
  if (!res.ok) {
    throw new Error(`API request failed with status ${res.status}`);
  }
  return res.json();
}
