import { describe, it, expect, vi, beforeEach } from "vitest";
import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";

vi.mock("../src/services/api.js", () => ({
  fetchNextQueueItem: vi.fn(),
  reviewProposal: vi.fn(),
  unlockProposal: vi.fn(),
  heartbeatLock: vi.fn(),
}));

vi.mock("../src/state/sessionId.js", () => ({
  getSessionId: () => "test-session",
}));

vi.mock("react-spring", () => ({
  useSpring: () => [{ x: { to: (f) => f(0) }, rotate: { to: (f) => f(0) }, opacity: { to: (f) => f(1) } }, vi.fn()],
  animated: { div: ({ children, ...p }) => <div {...p}>{children}</div> },
}));

vi.mock("@use-gesture/react", () => ({
  useDrag: () => () => ({}),
}));

import * as api from "../src/services/api.js";
import { CarouselPage } from "../src/pages/CarouselPage.jsx";

const MOCK_ITEM = {
  proposal_id: "prop-x",
  description: "Descripción",
  suggested_price: 99,
  images: [],
  queue_total: 1,
  queue_position: 1,
  locked_by_me: true,
};

describe("CarouselPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders empty queue message when backend returns null", async () => {
    api.fetchNextQueueItem.mockResolvedValue(null);
    render(<CarouselPage />);
    await waitFor(() => {
      expect(screen.getByText(/Cola vacía/i)).toBeInTheDocument();
    });
  });

  it("renders CarouselCard when item is available", async () => {
    api.fetchNextQueueItem.mockResolvedValue(MOCK_ITEM);
    render(<CarouselPage />);
    await waitFor(() => {
      expect(screen.getByText("Descripción")).toBeInTheDocument();
    });
  });

  it("shows error banner with retry button on fetch failure", async () => {
    api.fetchNextQueueItem.mockRejectedValue(new Error("queue_fetch_failed"));
    render(<CarouselPage />);
    await waitFor(() => {
      expect(screen.getByText(/Error al cargar la cola/i)).toBeInTheDocument();
      expect(screen.getByRole("button", { name: /Reintentar/i })).toBeInTheDocument();
    });
  });
});
