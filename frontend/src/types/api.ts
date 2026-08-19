/**
 * api.ts
 * ------
 * TypeScript types that mirror backend/app/schemas/prediction.py exactly.
 * Keeping these in sync with the backend means the compiler catches
 * mismatches (e.g. a renamed field) at build time instead of at runtime.
 */

export type Category =
  | "spam"
  | "promotional"
  | "work"
  | "personal"
  | "important"
  | "social";

export const CATEGORIES: Category[] = [
  "spam",
  "promotional",
  "work",
  "personal",
  "important",
  "social",
];

export interface PredictionResponse {
  category: Category;
  confidence: number;
  processing_time_ms: number;
  timestamp: string;
  explanation: string;
  is_low_confidence: boolean;
  all_scores: Record<string, number>;
}

export interface HistoryItem {
  id: number;
  email_preview: string;
  category: Category;
  confidence: number;
  processing_time_ms: number;
  created_at: string;
}

export interface HistoryResponse {
  items: HistoryItem[];
  total: number;
}

export interface StatisticsResponse {
  total_predictions: number;
  most_common_category: Category | null;
  spam_percentage: number;
  average_confidence: number;
  todays_predictions: number;
  category_breakdown: Partial<Record<Category, number>>;
}

export interface ApiErrorBody {
  error: string;
  detail: string;
}

/** Thrown by the api client on any non-2xx response or network failure. */
export class ApiError extends Error {
  status: number | null;
  detail: string;

  constructor(message: string, status: number | null, detail: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

export type SortOption =
  | "newest"
  | "oldest"
  | "highest_confidence"
  | "lowest_confidence";
