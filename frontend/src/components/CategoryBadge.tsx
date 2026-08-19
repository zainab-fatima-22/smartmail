/**
 * CategoryBadge.tsx
 * -----------------
 * The signature visual element of SmartMail: every category is shown as
 * a small postage-stamp-styled badge (a perforated edge, drawn with a
 * repeating radial-gradient, plus an icon and label). This reinforces
 * the mail-sorting metaphor everywhere a category appears — the
 * dashboard, the classify result, and the history table.
 *
 * ACCESSIBILITY: we never rely on color alone. Every badge always shows
 * an icon AND a text label, so color-blind users and screen readers get
 * the same information as everyone else.
 */

import { Category } from "../types/api";
import {
  AlertTriangle,
  Tag,
  Briefcase,
  User,
  Star,
  Users,
} from "lucide-react";

const CATEGORY_META: Record<
  Category,
  { label: string; icon: typeof AlertTriangle; color: string; soft: string }
> = {
  spam: { label: "Spam", icon: AlertTriangle, color: "var(--color-spam)", soft: "var(--color-spam-soft)" },
  promotional: { label: "Promotional", icon: Tag, color: "var(--color-promotional)", soft: "var(--color-promotional-soft)" },
  work: { label: "Work", icon: Briefcase, color: "var(--color-work)", soft: "var(--color-work-soft)" },
  personal: { label: "Personal", icon: User, color: "var(--color-personal)", soft: "var(--color-personal-soft)" },
  important: { label: "Important", icon: Star, color: "var(--color-important)", soft: "var(--color-important-soft)" },
  social: { label: "Social", icon: Users, color: "var(--color-social)", soft: "var(--color-social-soft)" },
};

export function getCategoryMeta(category: Category) {
  return CATEGORY_META[category];
}

interface CategoryBadgeProps {
  category: Category;
  size?: "sm" | "md" | "lg";
}

export function CategoryBadge({ category, size = "md" }: CategoryBadgeProps) {
  const meta = CATEGORY_META[category];
  const Icon = meta.icon;

  const dims = {
    sm: { pad: "3px 10px 3px 8px", font: 12, icon: 12, perf: 4 },
    md: { pad: "5px 14px 5px 10px", font: 13, icon: 14, perf: 5 },
    lg: { pad: "8px 20px 8px 14px", font: 15, icon: 17, perf: 6 },
  }[size];

  return (
    <span
      className="category-badge"
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 6,
        padding: dims.pad,
        borderRadius: 999,
        background: meta.soft,
        color: meta.color,
        fontFamily: "var(--font-body)",
        fontWeight: 600,
        fontSize: dims.font,
        lineHeight: 1,
        border: `1px dashed ${meta.color}66`,
        whiteSpace: "nowrap",
      }}
    >
      <Icon size={dims.icon} strokeWidth={2.25} aria-hidden="true" />
      {meta.label}
    </span>
  );
}
