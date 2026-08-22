/**
 * History.test.tsx
 * -----------------
 * Covers the History page: rendering, empty state, delete success, and
 * the Day 5 regression test for the delete-failure bug fix (previously
 * a failed delete gave no feedback — see History.tsx for the fix).
 */

import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { BrowserRouter } from "react-router-dom";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { History } from "../History";
import * as api from "../../services/api";
import { ApiError } from "../../types/api";

function renderWithRouter(ui: React.ReactElement) {
  return render(<BrowserRouter>{ui}</BrowserRouter>);
}

const SAMPLE_ITEM = {
  id: 1,
  email_preview: "Congratulations! You have won a prize...",
  category: "spam" as const,
  confidence: 0.95,
  processing_time_ms: 3.1,
  created_at: new Date().toISOString(),
};

describe("History", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("renders history rows once loaded", async () => {
    vi.spyOn(api, "getHistory").mockResolvedValue({ items: [SAMPLE_ITEM], total: 1 });

    renderWithRouter(<History />);

    expect(await screen.findByText(/Congratulations! You have won a prize/i)).toBeInTheDocument();
    expect(screen.getByText("Spam")).toBeInTheDocument();
  });

  it("shows an empty state when there is no history", async () => {
    vi.spyOn(api, "getHistory").mockResolvedValue({ items: [], total: 0 });

    renderWithRouter(<History />);

    expect(await screen.findByText(/no predictions yet/i)).toBeInTheDocument();
  });

  it("shows a loading state before data arrives", () => {
    vi.spyOn(api, "getHistory").mockReturnValue(new Promise(() => {})); // never resolves

    renderWithRouter(<History />);
    expect(screen.getByText(/loading history/i)).toBeInTheDocument();
  });

  it("shows an error state when the initial load fails", async () => {
    vi.spyOn(api, "getHistory").mockRejectedValue(
      new ApiError("Request failed", 500, "Unable to connect to the server.")
    );

    renderWithRouter(<History />);
    expect(await screen.findByText(/unable to connect to the server/i)).toBeInTheDocument();
  });

  it("removes a row from the list after a successful delete", async () => {
    const user = userEvent.setup();
    vi.spyOn(api, "getHistory").mockResolvedValue({ items: [SAMPLE_ITEM], total: 1 });
    vi.spyOn(api, "deleteHistoryItem").mockResolvedValue({ deleted: true, detail: "Deleted." });

    renderWithRouter(<History />);
    await screen.findByText(/Congratulations! You have won a prize/i);

    await user.click(screen.getByLabelText(/delete history entry/i));

    await waitFor(() => {
      expect(screen.queryByText(/Congratulations! You have won a prize/i)).not.toBeInTheDocument();
    });
  });

  it("shows an error message (not a silent failure) when delete fails — regression test", async () => {
    // Regression test for a real bug found during debugging: a failed
    // delete used to just silently reload the list with zero feedback
    // to the user about what happened. Now it must show an error.
    const user = userEvent.setup();
    vi.spyOn(api, "getHistory").mockResolvedValue({ items: [SAMPLE_ITEM], total: 1 });
    vi.spyOn(api, "deleteHistoryItem").mockRejectedValue(
      new ApiError("Request failed", 500, "Could not delete this item. Please try again.")
    );

    renderWithRouter(<History />);
    await screen.findByText(/Congratulations! You have won a prize/i);

    await user.click(screen.getByLabelText(/delete history entry/i));

    expect(await screen.findByText(/could not delete this item/i)).toBeInTheDocument();
    // And the row must still be there — the delete didn't actually happen.
    expect(screen.getByText(/Congratulations! You have won a prize/i)).toBeInTheDocument();
  });

  it("shows a confirmation banner before clearing all history", async () => {
    const user = userEvent.setup();
    vi.spyOn(api, "getHistory").mockResolvedValue({ items: [SAMPLE_ITEM], total: 1 });
    const deleteAllSpy = vi.spyOn(api, "deleteAllHistory");

    renderWithRouter(<History />);
    await screen.findByText(/Congratulations! You have won a prize/i);

    await user.click(screen.getByRole("button", { name: /clear all/i }));

    expect(await screen.findByText(/delete all 1 history entries/i)).toBeInTheDocument();
    expect(deleteAllSpy).not.toHaveBeenCalled(); // confirmation required first
  });
});
