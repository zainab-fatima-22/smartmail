/**
 * App.test.tsx
 * ------------
 * Covers the Day 3 testing requirements: dashboard rendering, email
 * input, prediction result, loading state, and error state.
 *
 * We mock the services/api module so tests don't need a live backend.
 *
 * Run with:
 *   cd frontend
 *   npm run test
 */

import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { BrowserRouter } from "react-router-dom";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { Dashboard } from "../Dashboard";
import { ClassifyEmail } from "../ClassifyEmail";
import * as api from "../../services/api";
import { ApiError } from "../../types/api";

function renderWithRouter(ui: React.ReactElement) {
  return render(<BrowserRouter>{ui}</BrowserRouter>);
}

describe("Dashboard", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("renders stat cards after loading statistics", async () => {
    vi.spyOn(api, "getStatistics").mockResolvedValue({
      total_predictions: 12,
      most_common_category: "work",
      spam_percentage: 16.7,
      average_confidence: 0.82,
      todays_predictions: 3,
      category_breakdown: { work: 5, spam: 2, promotional: 2, personal: 1, important: 1, social: 1 },
    });
    vi.spyOn(api, "getHistory").mockResolvedValue({ items: [], total: 0 });

    renderWithRouter(<Dashboard />);

    expect(await screen.findByText("Total Classified")).toBeInTheDocument();
    expect(await screen.findByText("12")).toBeInTheDocument();
  });

  it("shows a loading state before data arrives", () => {
    vi.spyOn(api, "getStatistics").mockReturnValue(new Promise(() => {})); // never resolves
    vi.spyOn(api, "getHistory").mockReturnValue(new Promise(() => {}));

    renderWithRouter(<Dashboard />);
    expect(screen.getByText(/loading dashboard/i)).toBeInTheDocument();
  });

  it("shows an error state when the API call fails", async () => {
    vi.spyOn(api, "getStatistics").mockRejectedValue(
      new ApiError("Unable to connect to the server.", null, "Check that the backend is running."),
    );
    vi.spyOn(api, "getHistory").mockResolvedValue({ items: [], total: 0 });

    renderWithRouter(<Dashboard />);
    expect(await screen.findByText(/check that the backend is running/i)).toBeInTheDocument();
  });
});

describe("ClassifyEmail", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("lets the user type an email into the textarea", async () => {
    const user = userEvent.setup();
    renderWithRouter(<ClassifyEmail />);

    const textarea = screen.getByLabelText(/email content/i);
    await user.type(textarea, "Hello there");
    expect(textarea).toHaveValue("Hello there");
  });

  it("shows the prediction result after a successful classification", async () => {
    const user = userEvent.setup();
    vi.spyOn(api, "classifyEmail").mockResolvedValue({
      category: "spam",
      confidence: 0.97,
      processing_time_ms: 3.2,
      timestamp: new Date().toISOString(),
      explanation: "The email contains scam-like language.",
      is_low_confidence: false,
      top_features: [
        { word: "won", weight: 0.42 },
        { word: "prize", weight: 0.31 },
      ],
      all_scores: { spam: 0.97, work: 0.01, personal: 0.01, promotional: 0.005, important: 0.003, social: 0.002 },
    });

    renderWithRouter(<ClassifyEmail />);
    await user.type(screen.getByLabelText(/email content/i), "You won a free prize!");
    await user.click(screen.getByRole("button", { name: /classify email/i }));

    expect(await screen.findByText("Spam")).toBeInTheDocument();
    expect(await screen.findByText("97%")).toBeInTheDocument();
  });

  it("shows an error message when classification fails", async () => {
    const user = userEvent.setup();
    vi.spyOn(api, "classifyEmail").mockRejectedValue(
      new ApiError("Request failed", 500, "Unable to connect to the server."),
    );

    renderWithRouter(<ClassifyEmail />);
    await user.type(screen.getByLabelText(/email content/i), "Test email content");
    await user.click(screen.getByRole("button", { name: /classify email/i }));

    expect(await screen.findByText(/unable to connect to the server/i)).toBeInTheDocument();
  });

  it("shows a validation message for empty input without calling the API", async () => {
    const user = userEvent.setup();
    const spy = vi.spyOn(api, "classifyEmail");

    renderWithRouter(<ClassifyEmail />);
    await user.click(screen.getByRole("button", { name: /classify email/i }));

    expect(await screen.findByText(/please enter an email/i)).toBeInTheDocument();
    expect(spy).not.toHaveBeenCalled();
  });

  it("classifies an uploaded .txt file and shows top contributing words", async () => {
    const user = userEvent.setup();
    vi.spyOn(api, "classifyEmailFile").mockResolvedValue({
      category: "work",
      confidence: 0.83,
      processing_time_ms: 2.1,
      timestamp: new Date().toISOString(),
      explanation: "The email discusses meetings, deadlines, or work-related topics.",
      is_low_confidence: false,
      top_features: [{ word: "meeting", weight: 0.5 }],
      all_scores: { work: 0.83, personal: 0.05, spam: 0.02, promotional: 0.02, important: 0.05, social: 0.03 },
    });

    renderWithRouter(<ClassifyEmail />);
    const file = new File(["Your meeting has been moved to 3 PM."], "email.txt", { type: "text/plain" });
    const fileInput = screen.getByLabelText(/upload a .txt or .eml email file/i);
    await user.upload(fileInput, file);

    expect(await screen.findByText("email.txt")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /classify email/i }));

    expect(await screen.findByText("Work")).toBeInTheDocument();
    expect(await screen.findByText("meeting")).toBeInTheDocument();
  });

  it("rejects an unsupported file type client-side without calling the API", async () => {
    const user = userEvent.setup();
    const spy = vi.spyOn(api, "classifyEmailFile");

    renderWithRouter(<ClassifyEmail />);
    const file = new File(["not an email"], "document.pdf", { type: "application/pdf" });
    const fileInput = screen.getByLabelText(/upload a .txt or .eml email file/i);
    await user.upload(fileInput, file);

    expect(await screen.findByText(/unsupported file type/i)).toBeInTheDocument();
    expect(spy).not.toHaveBeenCalled();
  });

  it("shows the low-confidence warning when the backend flags is_low_confidence", async () => {
    const user = userEvent.setup();
    vi.spyOn(api, "classifyEmail").mockResolvedValue({
      category: "social",
      confidence: 0.42,
      processing_time_ms: 2.0,
      timestamp: new Date().toISOString(),
      explanation: "The email relates to social events.",
      is_low_confidence: true,
      top_features: [],
      all_scores: { social: 0.42, work: 0.3, personal: 0.28, spam: 0, promotional: 0, important: 0 },
    });

    renderWithRouter(<ClassifyEmail />);
    await user.type(screen.getByLabelText(/email content/i), "Ambiguous text between categories");
    await user.click(screen.getByRole("button", { name: /classify email/i }));

    expect(
      await screen.findByText(/low confidence prediction/i)
    ).toBeInTheDocument();
  });

  it("does not show the low-confidence warning for a high-confidence result", async () => {
    const user = userEvent.setup();
    vi.spyOn(api, "classifyEmail").mockResolvedValue({
      category: "spam",
      confidence: 0.97,
      processing_time_ms: 2.0,
      timestamp: new Date().toISOString(),
      explanation: "Spam-like language detected.",
      is_low_confidence: false,
      top_features: [],
      all_scores: { spam: 0.97, work: 0.01, personal: 0.005, promotional: 0.005, important: 0.005, social: 0.005 },
    });

    renderWithRouter(<ClassifyEmail />);
    await user.type(screen.getByLabelText(/email content/i), "Obvious spam text");
    await user.click(screen.getByRole("button", { name: /classify email/i }));

    await screen.findByText("Spam");
    expect(screen.queryByText(/low confidence prediction/i)).not.toBeInTheDocument();
  });
});
