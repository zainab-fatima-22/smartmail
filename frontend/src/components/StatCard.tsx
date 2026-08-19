/**
 * StatCard.tsx
 * ------------
 * A dashboard metric tile: a big number, a label, and an optional icon.
 * Used on the Dashboard page for "Total Classified", "Spam Detected", etc.
 */

import { ReactNode } from "react";
import { Card } from "./Card";

interface StatCardProps {
  label: string;
  value: string;
  icon?: ReactNode;
  accentColor?: string;
}

export function StatCard({ label, value, icon, accentColor = "var(--color-accent)" }: StatCardProps) {
  return (
    <Card className="stat-card">
      <div className="stat-card-top">
        <span className="stat-card-label">{label}</span>
        {icon && (
          <span className="stat-card-icon" style={{ color: accentColor }} aria-hidden="true">
            {icon}
          </span>
        )}
      </div>
      <div className="stat-card-value mono">{value}</div>
    </Card>
  );
}
