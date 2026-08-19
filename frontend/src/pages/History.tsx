/**
 * History.tsx
 * -----------
 * Lists past predictions with search, category filter, sorting, and
 * per-row / bulk delete. Talks to GET/DELETE /api/history.
 */

import { useEffect, useState } from "react";
import { Trash2, ShieldAlert } from "lucide-react";
import { Card } from "../components/Card";
import { CategoryBadge } from "../components/CategoryBadge";
import { EmptyState, ErrorState, LoadingState } from "../components/States";
import { deleteAllHistory, deleteHistoryItem, getHistory } from "../services/api";
import { ApiError, Category, CATEGORIES, HistoryItem, SortOption } from "../types/api";

const SORT_LABELS: Record<SortOption, string> = {
  newest: "Newest first",
  oldest: "Oldest first",
  highest_confidence: "Highest confidence",
  lowest_confidence: "Lowest confidence",
};

export function History() {
  const [items, setItems] = useState<HistoryItem[]>([]);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState<Category | "">("");
  const [sortBy, setSortBy] = useState<SortOption>("newest");
  const [status, setStatus] = useState<"loading" | "ready" | "error">("loading");
  const [errorMessage, setErrorMessage] = useState("");
  const [confirmingClearAll, setConfirmingClearAll] = useState(false);

  async function load() {
    setStatus("loading");
    try {
      const res = await getHistory({
        search: search || undefined,
        category: category || undefined,
        sortBy,
        limit: 100,
      });
      setItems(res.items);
      setTotal(res.total);
      setStatus("ready");
    } catch (err) {
      setErrorMessage(err instanceof ApiError ? err.detail : "Please try again.");
      setStatus("error");
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [search, category, sortBy]);

  async function handleDeleteOne(id: number) {
    try {
      await deleteHistoryItem(id);
      setItems((prev) => prev.filter((item) => item.id !== id));
      setTotal((prev) => prev - 1);
    } catch {
      // Keep it simple: reload the list so state stays consistent
      // with the server if the delete failed for some reason.
      load();
    }
  }

  async function handleDeleteAll() {
    await deleteAllHistory();
    setConfirmingClearAll(false);
    load();
  }

  return (
    <div>
      <div className="history-header-row">
        <header className="page-header" style={{ marginBottom: 0 }}>
          <p className="page-eyebrow">History</p>
          <h1>Prediction History</h1>
        </header>
        {items.length > 0 && (
          <button className="btn btn-danger" onClick={() => setConfirmingClearAll(true)}>
            <Trash2 size={16} /> Clear all
          </button>
        )}
      </div>

      {confirmingClearAll && (
        <div className="confirm-banner">
          <span>
            <ShieldAlert size={15} style={{ verticalAlign: "-2px", marginRight: 6 }} />
            Delete all {total} history entries? This can't be undone.
          </span>
          <div className="button-row">
            <button className="btn btn-secondary" onClick={() => setConfirmingClearAll(false)}>
              Cancel
            </button>
            <button className="btn btn-danger" onClick={handleDeleteAll}>
              Delete all
            </button>
          </div>
        </div>
      )}

      <div className="history-toolbar">
        <input
          className="text-input"
          type="search"
          placeholder="Search email previews..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          aria-label="Search history"
        />
        <select
          className="select-input"
          value={category}
          onChange={(e) => setCategory(e.target.value as Category | "")}
          aria-label="Filter by category"
        >
          <option value="">All categories</option>
          {CATEGORIES.map((c) => (
            <option key={c} value={c}>
              {c.charAt(0).toUpperCase() + c.slice(1)}
            </option>
          ))}
        </select>
        <select
          className="select-input"
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value as SortOption)}
          aria-label="Sort order"
        >
          {Object.entries(SORT_LABELS).map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>
      </div>

      {status === "loading" && <LoadingState label="Loading history..." />}
      {status === "error" && <ErrorState description={errorMessage} onRetry={load} />}

      {status === "ready" && items.length === 0 && (
        <Card>
          <EmptyState
            title="No predictions yet"
            description={
              search || category
                ? "No history entries match your filters."
                : "Classify an email to see it appear here."
            }
          />
        </Card>
      )}

      {status === "ready" && items.length > 0 && (
        <Card className="history-table-wrap">
          <table className="history-table">
            <thead>
              <tr>
                <th>Email Preview</th>
                <th>Category</th>
                <th>Confidence</th>
                <th>Processing Time</th>
                <th>Date</th>
                <th aria-label="Actions"></th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.id}>
                  <td className="history-preview-cell">{item.email_preview}</td>
                  <td>
                    <CategoryBadge category={item.category} size="sm" />
                  </td>
                  <td className="mono">{Math.round(item.confidence * 100)}%</td>
                  <td className="mono">{item.processing_time_ms} ms</td>
                  <td className="mono">{new Date(item.created_at).toLocaleString()}</td>
                  <td className="history-actions-cell">
                    <button
                      className="icon-btn"
                      onClick={() => handleDeleteOne(item.id)}
                      aria-label={`Delete history entry: ${item.email_preview}`}
                    >
                      <Trash2 size={15} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      )}
    </div>
  );
}
