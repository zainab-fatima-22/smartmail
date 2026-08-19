/**
 * api.ts (services)
 * ------------------
 * All HTTP calls to the SmartMail backend live here. Components never
 * call fetch() directly — they call these functions. This means:
 *   - There's one place to change the base URL, headers, or error
 *     handling if the backend changes.
 *   - Components stay focused on rendering, not networking.
 *
 * WHICH file:
 *   frontend/src/services/api.ts
 *
 * HOW it connects to other files:
 *   - Uses types from types/api.ts.
 *   - Called from pages/ClassifyEmail.tsx, pages/History.tsx,
 *     pages/Statistics.tsx, pages/Dashboard.tsx.
 */

import {
  ApiError,
  ApiErrorBody,
  HistoryResponse,
  PredictionResponse,
  SortOption,
  StatisticsResponse,
} from "../types/api";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
  } catch {
    // Network-level failure: server down, CORS blocked, no connection, etc.
    throw new ApiError(
      "Unable to connect to the server.",
      null,
      "Check that the SmartMail backend is running and reachable."
    );
  }

  if (!response.ok) {
    let body: ApiErrorBody | null = null;
    try {
      body = await response.json();
    } catch {
      // Response wasn't JSON; fall through with a generic message.
    }
    throw new ApiError(
      body?.error ?? `Request failed (${response.status})`,
      response.status,
      typeof body?.detail === "string" ? body.detail : "Please try again.",
    );
  }

  return response.json() as Promise<T>;
}

export function classifyEmail(emailText: string): Promise<PredictionResponse> {
  return request<PredictionResponse>("/api/predict", {
    method: "POST",
    body: JSON.stringify({ email_text: emailText }),
  });
}

export async function classifyEmailFile(file: File): Promise<PredictionResponse> {
  const formData = new FormData();
  formData.append("file", file);

  let response: Response;
  try {
    response = await fetch(`${API_URL}/api/predict/upload`, {
      method: "POST",
      body: formData, // no Content-Type header — the browser sets the multipart boundary
    });
  } catch {
    throw new ApiError(
      "Unable to connect to the server.",
      null,
      "Check that the SmartMail backend is running and reachable."
    );
  }

  if (!response.ok) {
    let body: ApiErrorBody | null = null;
    try {
      body = await response.json();
    } catch {
      // ignore, fall through to generic message
    }
    throw new ApiError(
      body?.error ?? `Upload failed (${response.status})`,
      response.status,
      typeof body?.detail === "string" ? body.detail : "Please try again.",
    );
  }

  return response.json() as Promise<PredictionResponse>;
}

export function getHistory(params: {
  search?: string;
  category?: string;
  sortBy?: SortOption;
  limit?: number;
  offset?: number;
}): Promise<HistoryResponse> {
  const query = new URLSearchParams();
  if (params.search) query.set("search", params.search);
  if (params.category) query.set("category", params.category);
  if (params.sortBy) query.set("sort_by", params.sortBy);
  if (params.limit) query.set("limit", String(params.limit));
  if (params.offset) query.set("offset", String(params.offset));

  const queryString = query.toString();
  return request<HistoryResponse>(`/api/history${queryString ? `?${queryString}` : ""}`);
}

export function deleteHistoryItem(id: number): Promise<{ deleted: boolean; detail: string }> {
  return request(`/api/history/${id}`, { method: "DELETE" });
}

export function deleteAllHistory(): Promise<{ deleted: boolean; detail: string }> {
  return request("/api/history", { method: "DELETE" });
}

export function getStatistics(): Promise<StatisticsResponse> {
  return request<StatisticsResponse>("/api/statistics");
}

export function checkHealth(): Promise<{ status: string; model_loaded: boolean }> {
  return request("/api/health");
}
