const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.teder.com.br";

function getKey(): string | null {
  if (typeof window === "undefined") return null;
  return sessionStorage.getItem("teder_key");
}

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const key = getKey();
  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(key ? { "X-Teder-Key": key } : {}),
      ...options?.headers,
    },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export interface Event {
  id: string;
  request_id: string;
  agent_id: string;
  action: "allow" | "warn" | "block";
  risk_score: number;
  threats: string[];
  session_id: string | null;
  latency_ms: number;
  platform_aggregate: boolean;
  created_at: string;
}

export interface EventsResponse {
  items: Event[];
  total: number;
  page: number;
  page_size: number;
}

export interface HealthResponse {
  status: string;
  version: string;
  postgres: string;
  redis: string;
}

export const api = {
  health: () => apiFetch<HealthResponse>("/health"),

  events: (page = 1, pageSize = 50, action?: string) => {
    const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
    if (action) params.set("action", action);
    return apiFetch<EventsResponse>(`/events?${params}`);
  },

  createKey: (plan: string, adminSecret: string) =>
    apiFetch<{ id: string; key: string; plan: string; created_at: string }>("/keys", {
      method: "POST",
      headers: { "X-Admin-Secret": adminSecret },
      body: JSON.stringify({ plan }),
    }),

  revokeKey: (id: string, adminSecret: string) =>
    apiFetch(`/keys/${id}`, {
      method: "DELETE",
      headers: { "X-Admin-Secret": adminSecret },
    }),
};
