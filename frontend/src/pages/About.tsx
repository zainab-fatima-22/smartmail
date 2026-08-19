/**
 * About.tsx
 * ---------
 * Explains what SmartMail is, how the ML works, the stack, limitations,
 * and privacy — mostly static content, per the Day 3 spec.
 */

import { CATEGORIES } from "../types/api";
import { CategoryBadge } from "../components/CategoryBadge";

export function About() {
  return (
    <div className="about-content">
      <header className="page-header">
        <p className="page-eyebrow">About</p>
        <h1>What SmartMail is</h1>
        <p className="page-lede">
          SmartMail is a portfolio project that classifies emails into six categories using
          a real, classical machine learning pipeline — not a large language model.
        </p>
      </header>

      <h2>How the ML works</h2>
      <p>
        Every email is cleaned, converted into numbers with TF-IDF (a technique that scores
        words by how distinctive they are), and classified by a Logistic Regression model
        trained on a labeled dataset of six categories.
      </p>
      <div className="pipeline-strip">
        <span>Email</span>
        <span className="arrow">→</span>
        <span>Text cleaning</span>
        <span className="arrow">→</span>
        <span>TF-IDF</span>
        <span className="arrow">→</span>
        <span>Logistic Regression</span>
        <span className="arrow">→</span>
        <span>Prediction + Confidence</span>
      </div>

      <h2>Categories</h2>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginBottom: 16 }}>
        {CATEGORIES.map((c) => (
          <CategoryBadge key={c} category={c} />
        ))}
      </div>

      <h2>Technology stack</h2>
      <ul>
        <li>Machine learning: Python, pandas, NumPy, scikit-learn, joblib</li>
        <li>Backend: FastAPI, Pydantic, SQLAlchemy, SQLite</li>
        <li>Frontend: React, TypeScript, Vite</li>
      </ul>

      <h2>Limitations</h2>
      <ul>
        <li>This is an educational ML classifier, not a production email security system.</li>
        <li>The training data is synthetic and template-generated — see the dataset documentation.</li>
        <li>Confidence is a model probability, not a certainty. Categories can overlap.</li>
        <li>Spam detection can produce both false positives and false negatives.</li>
      </ul>

      <h2>Privacy</h2>
      <p>
        SmartMail does not store the full text of any email you classify. Only a short
        preview (the first 80 characters) is saved to prediction history, specifically to
        avoid retaining sensitive content.
      </p>
    </div>
  );
}
