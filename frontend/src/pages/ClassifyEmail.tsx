/**
 * ClassifyEmail.tsx
 * -----------------
 * The core workflow: paste an email, classify it, see the result.
 * Handles loading state (disables duplicate submissions), error state,
 * and the low-confidence warning.
 */

import { FormEvent, useState } from "react";
import { classifyEmail } from "../services/api";
import { ApiError, PredictionResponse } from "../types/api";
import { CategoryBadge, getCategoryMeta } from "../components/CategoryBadge";
import { Card } from "../components/Card";
import { ConfidenceBar, LowConfidenceWarning } from "../components/Confidence";
import { ErrorState } from "../components/States";
import { Loader2, Sparkles } from "lucide-react";

const EXAMPLE_EMAILS = [
  "Congratulations! You have won a $500 gift card. Click this link to claim your reward.",
  "Please review the project report before tomorrow's meeting.",
  "Hey, are you free for dinner this weekend?",
  "Get 50% off our summer collection today.",
  "Your account requires immediate verification due to a security issue.",
  "Join us for the community event this Saturday.",
];

export function ClassifyEmail() {
  const [emailText, setEmailText] = useState("");
  const [result, setResult] = useState<PredictionResponse | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (isSubmitting) return; // prevent duplicate submissions

    if (!emailText.trim()) {
      setError("Please enter an email.");
      return;
    }

    setIsSubmitting(true);
    setError(null);
    setResult(null);

    try {
      const prediction = await classifyEmail(emailText);
      setResult(prediction);
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Unable to classify this email. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  }

  function handleClear() {
    setEmailText("");
    setResult(null);
    setError(null);
  }

  return (
    <div>
      <header className="page-header">
        <p className="page-eyebrow">Classify Email</p>
        <h1>Paste an email to classify</h1>
      </header>

      <div className="classify-grid">
        <Card as="section">
          <form onSubmit={handleSubmit}>
            <label htmlFor="email-input" className="field-label">
              Email content
            </label>
            <textarea
              id="email-input"
              className="textarea"
              placeholder="Paste your email here..."
              value={emailText}
              onChange={(e) => setEmailText(e.target.value)}
              maxLength={10000}
              disabled={isSubmitting}
            />
            <div className="textarea-footer">
              <span className="char-count mono">{emailText.length} / 10,000</span>
              <div className="button-row">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={handleClear}
                  disabled={isSubmitting || (!emailText && !result)}
                >
                  Clear
                </button>
                <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
                  {isSubmitting ? (
                    <>
                      <Loader2 size={16} className="spin" /> Analyzing email...
                    </>
                  ) : (
                    "Classify Email"
                  )}
                </button>
              </div>
            </div>
          </form>

          <div className="example-emails">
            <span className="field-label">Try an example</span>
            <div className="example-chip-row">
              {EXAMPLE_EMAILS.map((example) => (
                <button
                  key={example}
                  type="button"
                  className="example-chip"
                  onClick={() => setEmailText(example)}
                  disabled={isSubmitting}
                >
                  {example.slice(0, 28)}...
                </button>
              ))}
            </div>
          </div>
        </Card>

        <Card as="section" className="result-card">
          {!result && !error && !isSubmitting && (
            <div className="state-block">
              <span className="state-icon state-icon-neutral" aria-hidden="true">
                <Sparkles size={22} strokeWidth={1.75} />
              </span>
              <h3>Ready when you are</h3>
              <p>Your classification result will appear here.</p>
            </div>
          )}

          {isSubmitting && (
            <div className="state-block" role="status" aria-live="polite">
              <span className="state-icon state-icon-neutral spin" aria-hidden="true">
                <Loader2 size={22} strokeWidth={1.75} />
              </span>
              <p>Analyzing email...</p>
            </div>
          )}

          {!isSubmitting && error && <ErrorState description={error} />}

          {!isSubmitting && result && (
            <div className="result-content">
              <span className="field-label">Prediction</span>
              <div className="result-category-row">
                <CategoryBadge category={result.category} size="lg" />
              </div>

              <span className="field-label">Confidence</span>
              <ConfidenceBar
                confidence={result.confidence}
                color={getCategoryMeta(result.category).color}
              />
              {result.is_low_confidence && <LowConfidenceWarning />}

              <span className="field-label result-why-label">Why?</span>
              <p className="result-explanation">{result.explanation}</p>

              <dl className="result-meta">
                <div>
                  <dt>Processing time</dt>
                  <dd className="mono">{result.processing_time_ms} ms</dd>
                </div>
                <div>
                  <dt>Timestamp</dt>
                  <dd className="mono">{new Date(result.timestamp).toLocaleString()}</dd>
                </div>
              </dl>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
