/**
 * Confidence.tsx
 * --------------
 * Visualizes a prediction's confidence score as a labeled bar, plus a
 * warning banner shown when confidence is low. We never present model
 * probability as certainty — see LOW_CONFIDENCE_THRESHOLD in the
 * backend's config.py, which the `is_low_confidence` flag reflects.
 */

import { AlertTriangle } from "lucide-react";

interface ConfidenceBarProps {
  confidence: number; // 0..1
  color?: string;
}

export function ConfidenceBar({ confidence, color = "var(--color-accent)" }: ConfidenceBarProps) {
  const pct = Math.round(confidence * 100);
  return (
    <div className="confidence-bar-wrap">
      <div
        className="confidence-bar-track"
        role="progressbar"
        aria-valuenow={pct}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label="Prediction confidence"
      >
        <div className="confidence-bar-fill" style={{ width: `${pct}%`, background: color }} />
      </div>
      <span className="confidence-bar-label mono">{pct}%</span>
    </div>
  );
}

export function LowConfidenceWarning() {
  return (
    <div className="low-confidence-warning" role="status">
      <AlertTriangle size={16} strokeWidth={2} aria-hidden="true" />
      <span>
        Low confidence prediction. This email may contain patterns shared by multiple categories.
      </span>
    </div>
  );
}
