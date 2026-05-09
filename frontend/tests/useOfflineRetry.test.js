/**
 * T061 — Tests for useOfflineRetry hook (FR-014)
 */
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useOfflineRetry } from "../src/hooks/useOfflineRetry.js";

// Helper to fire browser events on window
function fireOnline() {
  window.dispatchEvent(new Event("online"));
}
function fireOffline() {
  window.dispatchEvent(new Event("offline"));
}

describe("useOfflineRetry", () => {
  beforeEach(() => {
    // Ensure navigator.onLine reads as true by default in jsdom
    Object.defineProperty(navigator, "onLine", {
      configurable: true,
      writable: true,
      value: true,
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("isOffline starts as false when navigator.onLine is true", () => {
    const { result } = renderHook(() => useOfflineRetry());
    expect(result.current.isOffline).toBe(false);
  });

  it("isOffline becomes true on 'offline' event", () => {
    const { result } = renderHook(() => useOfflineRetry());
    act(() => { fireOffline(); });
    expect(result.current.isOffline).toBe(true);
  });

  it("isOffline becomes false again on 'online' event", () => {
    const { result } = renderHook(() => useOfflineRetry());
    act(() => { fireOffline(); });
    expect(result.current.isOffline).toBe(true);
    act(() => { fireOnline(); });
    expect(result.current.isOffline).toBe(false);
  });

  it("withOfflineRetry: successful fn resolves normally", async () => {
    const { result } = renderHook(() => useOfflineRetry());
    const fn = vi.fn().mockResolvedValue("ok");

    await act(async () => {
      await result.current.withOfflineRetry(fn)();
    });

    expect(fn).toHaveBeenCalledTimes(1);
  });

  it("withOfflineRetry: TypeError (network error) stores pending and does not rethrow", async () => {
    const { result } = renderHook(() => useOfflineRetry());
    const fn = vi.fn().mockRejectedValue(new TypeError("Failed to fetch"));

    // Should NOT throw
    await act(async () => {
      await result.current.withOfflineRetry(fn)();
    });

    expect(fn).toHaveBeenCalledTimes(1);
    // isOffline should now be true
    expect(result.current.isOffline).toBe(true);
  });

  it("withOfflineRetry: pending fn retried automatically on 'online' event", async () => {
    const { result } = renderHook(() => useOfflineRetry());
    const fn = vi.fn()
      .mockRejectedValueOnce(new TypeError("Failed to fetch"))
      .mockResolvedValue("retried-ok");

    // First call — network error, stores pending
    await act(async () => {
      await result.current.withOfflineRetry(fn)();
    });
    expect(fn).toHaveBeenCalledTimes(1);

    // Simulate reconnection — should trigger retry
    await act(async () => { fireOnline(); });

    expect(fn).toHaveBeenCalledTimes(2);
    expect(result.current.isOffline).toBe(false);
  });

  it("withOfflineRetry: 4xx error is re-thrown (not treated as network error)", async () => {
    const { result } = renderHook(() => useOfflineRetry());
    const err = new Error("review_failed");
    err.status = 422;
    const fn = vi.fn().mockRejectedValue(err);

    await expect(
      act(async () => { await result.current.withOfflineRetry(fn)(); })
    ).rejects.toThrow("review_failed");

    expect(result.current.isOffline).toBe(false);
  });

  it("cleanup: event listeners removed on unmount", () => {
    const addSpy = vi.spyOn(window, "addEventListener");
    const removeSpy = vi.spyOn(window, "removeEventListener");

    const { unmount } = renderHook(() => useOfflineRetry());
    unmount();

    // Both 'offline' and 'online' handlers should have been removed
    const removedEvents = removeSpy.mock.calls.map((c) => c[0]);
    expect(removedEvents).toContain("offline");
    expect(removedEvents).toContain("online");
  });
});
