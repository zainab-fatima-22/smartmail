/**
 * Layout.tsx
 * ----------
 * The app shell: a fixed sidebar (mail-client style navigation) plus a
 * content area where each page renders. Every page is wrapped in this
 * once, in App.tsx, so navigation stays consistent.
 */

import { NavLink, Outlet } from "react-router-dom";
import { LayoutDashboard, PenSquare, History, BarChart3, Info, Mail } from "lucide-react";

const NAV_ITEMS = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard, end: true },
  { to: "/classify", label: "Classify Email", icon: PenSquare, end: false },
  { to: "/history", label: "History", icon: History, end: false },
  { to: "/statistics", label: "Statistics", icon: BarChart3, end: false },
  { to: "/about", label: "About", icon: Info, end: false },
];

export function Layout() {
  return (
    <div className="app-shell">
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>
      <aside className="sidebar" aria-label="Main navigation">
        <div className="sidebar-brand">
          <span className="sidebar-brand-mark" aria-hidden="true">
            <Mail size={20} strokeWidth={2.25} />
          </span>
          <div>
            <div className="sidebar-brand-name">SmartMail</div>
            <div className="sidebar-brand-tag">Email Classifier</div>
          </div>
        </div>

        <nav>
          <ul className="sidebar-nav">
            {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
              <li key={to}>
                <NavLink
                  to={to}
                  end={end}
                  className={({ isActive }) => `sidebar-link${isActive ? " sidebar-link-active" : ""}`}
                >
                  <Icon size={17} strokeWidth={2.1} aria-hidden="true" />
                  {label}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>

        <div className="sidebar-footer">
          <span className="mono">TF-IDF + Logistic Regression</span>
        </div>
      </aside>

      <main id="main-content" className="content-area">
        <div className="content-inner">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
