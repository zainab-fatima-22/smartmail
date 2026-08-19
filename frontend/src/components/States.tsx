/**
 * States.tsx
 * ----------
 * Shared empty/loading/error state components. Per the design brief,
 * these are treated as "moments for direction, not mood": they explain
 * what happened and what to do next, in a plain, consistent voice.
 */

import { ReactNode } from "react";
import { Inbox, AlertCircle, Loader2 } from "lucide-react";

interface EmptyStateProps {
  title: string;
  description: string;
  icon?: ReactNode;
}

export function EmptyState({ title, description, icon }: EmptyStateProps) {
  return (
    <div className="state-block" role="status">
      <span className="state-icon state-icon-neutral" aria-hidden="true">
        {icon ?? <Inbox size={22} strokeWidth={1.75} />}
      </span>
      <h3>{title}</h3>
      <p>{description}</p>
    </div>
  );
}

interface ErrorStateProps {
  title?: string;
  description: string;
  onRetry?: () => void;
}

export function ErrorState({ title = "Something went wrong", description, onRetry }: ErrorStateProps) {
  return (
    <div className="state-block" role="alert">
      <span className="state-icon state-icon-danger" aria-hidden="true">
        <AlertCircle size={22} strokeWidth={1.75} />
      </span>
      <h3>{title}</h3>
      <p>{description}</p>
      {onRetry && (
        <button className="btn btn-secondary" onClick={onRetry}>
          Try again
        </button>
      )}
    </div>
  );
}

interface LoadingStateProps {
  label?: string;
}

export function LoadingState({ label = "Loading..." }: LoadingStateProps) {
  return (
    <div className="state-block" role="status" aria-live="polite">
      <span className="state-icon state-icon-neutral spin" aria-hidden="true">
        <Loader2 size={22} strokeWidth={1.75} />
      </span>
      <p>{label}</p>
    </div>
  );
}
