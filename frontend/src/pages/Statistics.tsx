/**
 * Statistics.tsx
 * --------------
 * Charts summarizing prediction history: a bar chart of predictions per
 * category, and a simple breakdown table (confidence distribution is
 * approximated from category averages available today; a true
 * per-prediction distribution chart would need a small backend addition,
 * noted in the README's future improvements).
 */

import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Card } from "../components/Card";
import { ErrorState, LoadingState, EmptyState } from "../components/States";
import { getCategoryMeta } from "../components/CategoryBadge";
import { getStatistics } from "../services/api";
import { ApiError, Category, StatisticsResponse } from "../types/api";

export function Statistics() {
  const [stats, setStats] = useState<StatisticsResponse | null>(null);
  const [status, setStatus] = useState<"loading" | "ready" | "error">("loading");
  const [errorMessage, setErrorMessage] = useState("");

  function load() {
    setStatus("loading");
    getStatistics()
      .then((res) => {
        setStats(res);
        setStatus("ready");
      })
      .catch((err) => {
        setErrorMessage(err instanceof ApiError ? err.detail : "Please try again.");
        setStatus("error");
      });
  }

  useEffect(load, []);

  const chartData = stats
    ? Object.entries(stats.category_breakdown).map(([category, count]) => ({
        category,
        count,
        color: getCategoryMeta(category as Category).color,
      }))
    : [];

  return (
    <div>
      <header className="page-header">
        <p className="page-eyebrow">Statistics</p>
        <h1>Classification Statistics</h1>
      </header>

      {status === "loading" && <LoadingState label="Loading statistics..." />}
      {status === "error" && <ErrorState description={errorMessage} onRetry={load} />}

      {status === "ready" && stats && stats.total_predictions === 0 && (
        <Card>
          <EmptyState
            title="No data yet"
            description="Statistics will appear here once you've classified a few emails."
          />
        </Card>
      )}

      {status === "ready" && stats && stats.total_predictions > 0 && (
        <div className="charts-grid">
          <Card className="chart-card">
            <h2>Predictions by Category</h2>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={chartData} margin={{ top: 4, right: 8, left: -16, bottom: 4 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-line)" vertical={false} />
                <XAxis
                  dataKey="category"
                  tick={{ fontSize: 11, fill: "var(--color-ink-soft)" }}
                  tickFormatter={(v) => v.charAt(0).toUpperCase() + v.slice(1)}
                />
                <YAxis tick={{ fontSize: 11, fill: "var(--color-ink-soft)" }} allowDecimals={false} />
                <Tooltip
                  contentStyle={{
                    background: "var(--color-surface)",
                    border: "1px solid var(--color-line)",
                    borderRadius: 8,
                    fontSize: 13,
                  }}
                />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {chartData.map((entry) => (
                    <Cell key={entry.category} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </Card>

          <Card className="chart-card">
            <h2>Summary</h2>
            <dl className="result-meta" style={{ gridTemplateColumns: "1fr 1fr", borderTop: "none", paddingTop: 0 }}>
              <div>
                <dt>Total predictions</dt>
                <dd className="mono">{stats.total_predictions}</dd>
              </div>
              <div>
                <dt>Most common category</dt>
                <dd className="mono">{stats.most_common_category ?? "—"}</dd>
              </div>
              <div>
                <dt>Spam percentage</dt>
                <dd className="mono">{stats.spam_percentage}%</dd>
              </div>
              <div>
                <dt>Average confidence</dt>
                <dd className="mono">{Math.round(stats.average_confidence * 100)}%</dd>
              </div>
              <div>
                <dt>Today's predictions</dt>
                <dd className="mono">{stats.todays_predictions}</dd>
              </div>
            </dl>
          </Card>
        </div>
      )}
    </div>
  );
}
