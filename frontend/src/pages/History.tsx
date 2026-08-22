/**
 * History.tsx
 * -----------
 * Lists past predictions with search, category filter, sorting, and
 * per-row / bulk delete. Talks to GET/DELETE /api/history.
 */

import { useEffect, useRef, useState } from "react";
import { Trash2, ShieldAlert, AlertCircle } from "lucide-react";
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
  // `searchInput` is what the text box shows/updates on every keystroke;
  // `search` is the debounced value actually sent to the API (see the
  // debounce effect below). Splitting these stops a fast typist from
  // firing a request per keystroke.
  const [searchInput, setSearchInput] = useState("");
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState<Category | "">("");
  const [sortBy, setSortBy] = useState<SortOption>("newest");
  const [status, setStatus] = useState<"loading" | "ready" | "error">("loading");
  const [errorMessage, setErrorMessage] = useState("");
  const [actionError, setActionError] = useState<string | null>(null);
  const [confirmingClearAll, setConfirmingClearAll] = useState(false);

  // Debounce the search box — wait 300ms after the user stops typing
  // before it feeds into `search` (and therefore into the API call).
  useEffect(() => {
    const timeout = setTimeout(() => setSearch(searchInput), 300);
    return () => clearTimeout(timeout);
  }, [searchInput]);

  // Guards against a request race condition: if an older request (e.g.
  // from a previous keystroke) resolves AFTER a newer one, its response
  // is stale and must not overwrite the newer, correct results.
  const requestIdRef = useRef(0);

  async function load() {
    const requestId = ++requestIdRef.current;
    setStatus("loading");
    try {
      const res = await getHistory({
        search: search || undefined,
        category: category || undefined,
        sortBy,
        limit: 100,
      });
      if (requestId !== requestIdRef.current) return; // a newer request is in flight; ignore this stale result
      setItems(res.items);
      setTotal(res.total);
      setStatus("ready");
    } catch (err) {
      if (requestId !== requestIdRef.current) return;
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
      setActionError(null);
    } catch (err) {
      setActionError(
        err instanceof ApiError ? err.detail : "Could not delete this item. Please try again."
      );
    }
  }

  async function handleDeleteAll() {
    try {
      await deleteAllHistory();
      setConfirmingClearAll(false);
      setActionError(null);
      load();
    } catch (err) {
      setActionError(
        err instanceof ApiError ? err.detail : "Could not delete history. Please try again."
      );
    }
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

      {actionError && (
        <div className="confirm-banner" role="alert">
          <span>
            <AlertCircle size={15} style={{ verticalAlign: "-2px", marginRight: 6 }} />
            {actionError}
          </span>
          <div className="button-row">
            <button className="btn btn-secondary" onClick={() => setActionError(null)}>
              Dismiss
            </button>
          </div>
        </div>
      )}

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
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
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
