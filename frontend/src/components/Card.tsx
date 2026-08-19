/**
 * Card.tsx
 * --------
 * A simple bordered surface used throughout the app (dashboard stat
 * tiles, the classify result panel, history rows). Keeping it as one
 * component means padding/radius/shadow stay consistent everywhere.
 */

import { ReactNode } from "react";

interface CardProps {
  children: ReactNode;
  className?: string;
  as?: "div" | "section" | "article";
}

export function Card({ children, className = "", as: Tag = "div" }: CardProps) {
  return <Tag className={`card ${className}`}>{children}</Tag>;
}
