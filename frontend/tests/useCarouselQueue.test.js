import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, act } from "@testing-library/react";

// Mock the api module
vi.mock("../src/services/api.js", () => ({
  fetchNextQueueItem: vi.fn(),
  reviewProposal: vi.fn(),
  unlockProposal: vi.fn(),
}));

// Mock sessionId
vi.mock("../src/state/sessionId.js", () => ({
  getSessionId: () => "test-session",
}));

import * as api from "../src/services/api.js";
import { useCarouselQueue } from "../src/hooks/useCarouselQueue.js";

const MOCK_ITEM = {
  proposal_id: "prop-1",
  description: "Test",
  suggested_price: 50,
  images: [],
  queue_total: 2,
  queue_position: 1,
  locked_by_me: true,
};

describe("useCarouselQueue", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("advance() loads next item", async () => {
    api.fetchNextQueueItem.mockResolvedValue(MOCK_ITEM);
    const { result } = renderHook(() => useCarouselQueue());

    await act(async () => {
      await result.current.advance();
    });

    expect(result.current.currentItem).toEqual(MOCK_ITEM);
    expect(result.current.queueTotal).toBe(2);
    expect(result.current.isLoading).toBe(false);
  });

  it("advance() sets empty state when backend returns null (204)", async () => {
    api.fetchNextQueueItem.mockResolvedValue(null);
    const { result } = renderHook(() => useCarouselQueue());

    await act(async () => {
      await result.current.advance();
    });

    expect(result.current.currentItem).toBeNull();
    expect(result.current.queueTotal).toBe(0);
  });

  it("advance() sets error on failure", async () => {
    api.fetchNextQueueItem.mockRejectedValue(new Error("queue_fetch_failed"));
    const { result } = renderHook(() => useCarouselQueue());

    await act(async () => {
      await result.current.advance();
    });

    expect(result.current.error).toBe("queue_fetch_failed");
    expect(result.current.currentItem).toBeNull();
  });

  it("confirmDecision calls reviewProposal then advances", async () => {
    api.fetchNextQueueItem.mockResolvedValue(MOCK_ITEM);
    api.reviewProposal.mockResolvedValue({ decision: "approve" });

    const { result } = renderHook(() => useCarouselQueue());
    await act(async () => { await result.current.advance(); });

    api.fetchNextQueueItem.mockResolvedValue(null);
    await act(async () => {
      await result.current.confirmDecision("approve");
    });

    expect(api.reviewProposal).toHaveBeenCalledWith("prop-1", { decision: "approve" });
    expect(result.current.currentItem).toBeNull();
  });

  it("onApprove sets pendingDecision type=approve; undo does not call reviewProposal", async () => {
    api.fetchNextQueueItem.mockResolvedValue(MOCK_ITEM);
    api.unlockProposal.mockResolvedValue();

    const { result } = renderHook(() => useCarouselQueue());
    await act(async () => { await result.current.advance(); });

    act(() => { result.current.setPendingDecision({ type: "approve" }); });
    expect(result.current.pendingDecision).toEqual({ type: "approve" });

    api.fetchNextQueueItem.mockResolvedValue(null);
    await act(async () => { await result.current.undoDecision(); });

    expect(api.reviewProposal).not.toHaveBeenCalled();
    expect(api.unlockProposal).toHaveBeenCalledWith("prop-1");
  });
});
