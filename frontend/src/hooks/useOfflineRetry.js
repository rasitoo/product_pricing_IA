import { useState, useEffect, useRef, useCallback } from "react";

/**
 * FR-014 — Offline retry hook.
 *
 * Usage:
 *   const { isOffline, withOfflineRetry } = useOfflineRetry();
 *
 * - isOffline: true while the browser reports no network connection.
 * - withOfflineRetry(fn): wraps an async fetch function. On NetworkError/TypeError,
 *   stores the function in memory and retries automatically when the browser comes back
 *   online. On 4xx/5xx errors (non-network), re-throws so the caller can handle normally.
 */
export function useOfflineRetry() {
  const [isOffline, setIsOffline] = useState(!navigator.onLine);
  const pendingRef = useRef(null); // { fn: async () => any }

  useEffect(() => {
    function handleOffline() {
      setIsOffline(true);
    }

    async function handleOnline() {
      setIsOffline(false);
      if (pendingRef.current) {
        const { fn } = pendingRef.current;
        pendingRef.current = null;
        try {
          await fn();
        } catch (_) {
          // If it fails again for a non-network reason, there's nothing more to do here.
          // The caller already swallowed the network error; this attempt is best-effort.
        }
      }
    }

    window.addEventListener("offline", handleOffline);
    window.addEventListener("online", handleOnline);
    return () => {
      window.removeEventListener("offline", handleOffline);
      window.removeEventListener("online", handleOnline);
    };
  }, []);

  /**
   * Wraps `fn` (an async function with no arguments) so that network failures
   * (TypeError — fetch failed) are deferred for retry on reconnection.
   * Non-network errors are re-thrown immediately.
   */
  const withOfflineRetry = useCallback((fn) => {
    return async () => {
      try {
        await fn();
      } catch (err) {
        // TypeError is the browser's fetch NetworkError (no connection)
        const isNetworkError =
          err instanceof TypeError ||
          err?.message === "Failed to fetch" ||
          err?.message === "NetworkError when attempting to fetch resource.";
        if (isNetworkError) {
          // Store the pending action; it will retry on 'online' event
          pendingRef.current = { fn };
          setIsOffline(true);
          return; // don't rethrow — caller will see no error
        }
        throw err; // 4xx / 5xx or other error — propagate normally
      }
    };
  }, []);

  return { isOffline, withOfflineRetry };
}
