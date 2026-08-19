/**
 * Dashboard.tsx
 * -------------
 * The landing page: summary stat tiles plus a quick view of recent
 * predictions. Pulls from GET /api/statistics and GET /api/history.
 */

import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Inbox, ShieldAlert, Tag, Star, Percent } from "lucide-react";
import { StatCard } from "../components/StatCard";
import { Card } from "../components/Card";
import { CategoryBadge } from "../components/CategoryBadge";
import { EmptyState, ErrorState, LoadingState } from "../components/States";
import { getStatistics, getHistory } from "../services/api";
import { ApiError, HistoryItem, StatisticsResponse } from "../types/api";

export function Dashboard() {
  const [stats, setStats] = useState<StatisticsResponse | null>(null);
  const [recent, setRecent] = useState<HistoryItem[]>([]);
  const [status, setStatus] = useState<"loading" | "ready" | "error">("loading");
  const [errorMessage, setErrorMessage] = useState("");

  async function load() {
    setStatus("loading");
    try {
      const [statsRes, historyRes] = await Promise.all([
        getStatistics(),
        getHistory({ limit: 5, sortBy: "newest" }),
      ]);
      setStats(statsRes);
      setRecent(historyRes.items);
      setStatus("ready");
    } catch (err) {
      const message = err instanceof ApiError ? err.detail : "Please try again.";
      setErrorMessage(message);
      setStatus("error");
    }
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <div>
      <header className="page-header">
        <p className="page-eyebrow">Dashboard</p>
        <h1>Your Intelligent Email Classifier</h1>
        <p className="page-lede">
          SmartMail sorts your inbox with a TF-IDF and Logistic Regression model — no
          guesswork, no black box.
        </p>
      </header>

      {status === "loading" && <LoadingState label="Loading dashboard..." />}
      {status === "error" && <ErrorState description={errorMessage} onRetry={load} />}

      {status === "ready" && stats && (
        <>
          <div className="stat-grid">
            <StatCard
              label="Total Classified"
              value={stats.total_predictions.toLocaleString()}
              icon={<Inbox size={18} />}
            />
            <StatCard
              label="Spam Detected"
              value={String(stats.category_breakdown.spam ?? 0)}
              icon={<ShieldAlert size={18} />}
              accentColor="var(--color-spam)"
            />
            <StatCard
              label="Promotional"
              value={String(stats.category_breakdown.promotional ?? 0)}
              icon={<Tag size={18} />}
              accentColor="var(--color-promotional)"
            />
            <StatCard
              label="Important"
              value={String(stats.category_breakdown.important ?? 0)}
              icon={<Star size={18} />}
              accentColor="var(--color-important)"
            />
            <StatCard
              label="Avg. Confidence"
              value={`${Math.round(stats.average_confidence * 100)}%`}
              icon={<Percent size={18} />}
            />
          </div>

          <section className="section">
            <div className="section-head">
              <h2>Recent Predictions</h2>
              <Link to="/history" className="link-quiet">
                View all history
              </Link>
            </div>

            {recent.length === 0 ? (
              <Card>
                <EmptyState
                  title="No predictions yet"
                  description="Classify your first email to see it appear here."
                />
              </Card>
            ) : (
              <Card className="recent-list">
                {recent.map((item) => (
                  <div key={item.id} className="recent-row">
                    <span className="recent-preview">{item.email_preview}</span>
                    <CategoryBadge category={item.category} size="sm" />
                  </div>
                ))}
              </Card>
            )}
          </section>

          <div className="cta-row">
            <Link to="/classify" className="btn btn-primary">
              Classify an email
            </Link>
          </div>
        </>
      )}
    </div>
  );
}
