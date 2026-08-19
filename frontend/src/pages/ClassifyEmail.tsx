/**
 * ClassifyEmail.tsx
 * -----------------
 * The core workflow: paste an email OR upload a .txt/.eml file, classify
 * it, see the result. Handles loading state (disables duplicate
 * submissions), error state, the low-confidence warning, and (Day 4)
 * top contributing words plus file upload.
 */

import { ChangeEvent, DragEvent, FormEvent, useRef, useState } from "react";
import { Loader2, Sparkles, Upload, FileText, X } from "lucide-react";
import { classifyEmail, classifyEmailFile } from "../services/api";
import {
  ALLOWED_UPLOAD_EXTENSIONS,
  ApiError,
  MAX_UPLOAD_SIZE_BYTES,
  PredictionResponse,
} from "../types/api";
import { CategoryBadge, getCategoryMeta } from "../components/CategoryBadge";
import { Card } from "../components/Card";
import { ConfidenceBar, LowConfidenceWarning } from "../components/Confidence";
import { ErrorState } from "../components/States";

const EXAMPLE_EMAILS = [
  "Congratulations! You have won a $500 gift card. Click this link to claim your reward.",
  "Please review the project report before tomorrow's meeting.",
  "Hey, are you free for dinner this weekend?",
  "Get 50% off our summer collection today.",
  "Your account requires immediate verification due to a security issue.",
  "Join us for the community event this Saturday.",
];

function validateFile(file: File): string | null {
  const lowerName = file.name.toLowerCase();
  const hasValidExtension = ALLOWED_UPLOAD_EXTENSIONS.some((ext) => lowerName.endsWith(ext));
  if (!hasValidExtension) {
    return `Unsupported file type. Please upload a ${ALLOWED_UPLOAD_EXTENSIONS.join(" or ")} file.`;
  }
  if (file.size === 0) {
    return "This file is empty.";
  }
  if (file.size > MAX_UPLOAD_SIZE_BYTES) {
    return `File is too large. Maximum size is ${MAX_UPLOAD_SIZE_BYTES / (1024 * 1024)} MB.`;
  }
  return null;
}

export function ClassifyEmail() {
  const [emailText, setEmailText] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [result, setResult] = useState<PredictionResponse | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  function resetResultState() {
    setResult(null);
    setError(null);
  }

  function handleFileSelected(file: File) {
    const validationError = validateFile(file);
    if (validationError) {
      resetResultState();
      setError(validationError);
      return;
    }
    setSelectedFile(file);
    setEmailText("");
    resetResultState();
  }

  function handleFileInputChange(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) handleFileSelected(file);
    e.target.value = ""; // allow re-selecting the same file later
  }

  function handleDrop(e: DragEvent<HTMLDivElement>) {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file) handleFileSelected(file);
  }

  function removeSelectedFile() {
    setSelectedFile(null);
    resetResultState();
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (isSubmitting) return; // prevent duplicate submissions

    if (!selectedFile && !emailText.trim()) {
      setError("Please enter an email.");
      return;
    }

    setIsSubmitting(true);
    setError(null);
    setResult(null);

    try {
      const prediction = selectedFile
        ? await classifyEmailFile(selectedFile)
        : await classifyEmail(emailText);
      setResult(prediction);
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Unable to classify this email. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  }

  function handleClear() {
    setEmailText("");
    setSelectedFile(null);
    setResult(null);
    setError(null);
  }

  return (
    <div>
      <header className="page-header">
        <p className="page-eyebrow">Classify Email</p>
        <h1>Paste or upload an email to classify</h1>
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
              onChange={(e) => {
                setEmailText(e.target.value);
                setSelectedFile(null);
              }}
              maxLength={10000}
              disabled={isSubmitting || !!selectedFile}
            />
            <div className="textarea-footer">
              <span className="char-count mono">{emailText.length} / 10,000</span>
              <div className="button-row">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={handleClear}
                  disabled={isSubmitting || (!emailText && !result && !selectedFile)}
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

            <div className="upload-divider">
              <span>or</span>
            </div>

            {!selectedFile ? (
              <div
                className={`upload-dropzone${isDragging ? " upload-dropzone-active" : ""}`}
                onDragOver={(e) => {
                  e.preventDefault();
                  setIsDragging(true);
                }}
                onDragLeave={() => setIsDragging(false)}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") fileInputRef.current?.click();
                }}
              >
                <Upload size={20} strokeWidth={1.75} aria-hidden="true" />
                <span>
                  <strong>Upload an email file</strong> — .txt or .eml, up to 2 MB
                </span>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".txt,.eml"
                  className="sr-only"
                  aria-label="Upload a .txt or .eml email file"
                  onChange={handleFileInputChange}
                  disabled={isSubmitting}
                />
              </div>
            ) : (
              <div className="upload-file-chip">
                <FileText size={16} strokeWidth={2} aria-hidden="true" />
                <span className="upload-file-name">{selectedFile.name}</span>
                <span className="mono upload-file-size">
                  {(selectedFile.size / 1024).toFixed(1)} KB
                </span>
                <button
                  type="button"
                  className="icon-btn"
                  onClick={removeSelectedFile}
                  aria-label="Remove selected file"
                  disabled={isSubmitting}
                >
                  <X size={15} />
                </button>
              </div>
            )}
          </form>

          <div className="example-emails">
            <span className="field-label">Try an example</span>
            <div className="example-chip-row">
              {EXAMPLE_EMAILS.map((example) => (
                <button
                  key={example}
                  type="button"
                  className="example-chip"
                  onClick={() => {
                    setEmailText(example);
                    setSelectedFile(null);
                    resetResultState();
                  }}
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

              {result.top_features.length > 0 && (
                <>
                  <span className="field-label">Detected patterns</span>
                  <div className="feature-chip-row">
                    {result.top_features.map((f) => (
                      <span key={f.word} className="feature-chip">
                        {f.word}
                      </span>
                    ))}
                  </div>
                  <p className="feature-disclaimer">
                    These are model-associated features, not guaranteed proof of the category.
                  </p>
                </>
              )}

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
