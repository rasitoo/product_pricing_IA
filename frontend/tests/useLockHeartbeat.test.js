import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { renderHook, act } from "@testing-library/react";

vi.mock("../src/services/api.js", () => ({
  heartbeatLock: vi.fn(),
}));

vi.mock("../src/state/sessionId.js", () => ({
  getSessionId: () => "test-session",
}));

import * as api from "../src/services/api.js";
import { useLockHeartbeat } from "../src/hooks/useLockHeartbeat.js";

describe("useLockHeartbeat", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("calls heartbeat after 20s", async () => {
    api.heartbeatLock.mockResolvedValue({ expires_at: "2026-05-09T21:00:00" });
    renderHook(() => useLockHeartbeat("prop-1"));

    await act(async () => {
      vi.advanceTimersByTime(20_000);
    });

    expect(api.heartbeatLock).toHaveBeenCalledWith("prop-1");
  });

  it("calls heartbeat twice after 40s", async () => {
    api.heartbeatLock.mockResolvedValue({ expires_at: "2026-05-09T21:00:00" });
    renderHook(() => useLockHeartbeat("prop-1"));

    await act(async () => {
      vi.advanceTimersByTime(40_000);
    });

    expect(api.heartbeatLock).toHaveBeenCalledTimes(2);
  });

  it("cancels on unmount", async () => {
    api.heartbeatLock.mockResolvedValue({ expires_at: "2026-05-09T21:00:00" });
    const { unmount } = renderHook(() => useLockHeartbeat("prop-1"));

    unmount();

    await act(async () => {
      vi.advanceTimersByTime(20_000);
    });

    expect(api.heartbeatLock).not.toHaveBeenCalled();
  });

  it("does not call heartbeat when proposalId is null", async () => {
    renderHook(() => useLockHeartbeat(null));

    await act(async () => {
      vi.advanceTimersByTime(20_000);
    });

    expect(api.heartbeatLock).not.toHaveBeenCalled();
  });
});
