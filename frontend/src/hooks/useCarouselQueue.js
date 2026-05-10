import { useState, useCallback } from "react";
import { fetchNextQueueItem, reviewProposal, unlockProposal } from "../services/api.js";
import { useOfflineRetry } from "./useOfflineRetry.js";

/**
 * Manages the carousel queue state.
 * Returns: { currentItem, queueTotal, isLoading, error, advance, pendingDecision,
 *            confirmDecision, undoDecision, setPendingDecision, conflictToast, isOffline }
 */
export function useCarouselQueue() {
  const [currentItem, setCurrentItem] = useState(null);
  const [queueTotal, setQueueTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  // pendingDecision: { type: "approve"|"reject"|"edit", payload?: object } | null
  const [pendingDecision, setPendingDecision] = useState(null);
  // conflictToast: shown when backend returns 409 on reviewProposal (FR-017)
  const [conflictToast, setConflictToast] = useState(false);

  const { isOffline, withOfflineRetry } = useOfflineRetry();

  const advance = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    setPendingDecision(null);
    try {
      const item = await fetchNextQueueItem();
      setCurrentItem(item);
      setQueueTotal(item?.queue_total ?? 0);
    } catch (err) {
      setError(err.message ?? "queue_fetch_failed");
    } finally {
      setIsLoading(false);
    }
  }, []);

  const confirmDecision = useCallback(
    async (type, payload = {}) => {
      if (!currentItem) return;
      const proposalId = currentItem.proposal_id;

      // Wrap the actual network call with offline-retry logic (FR-014)
      const sendReview = withOfflineRetry(async () => {
        try {
          await reviewProposal(proposalId, { decision: type, ...payload });
        } catch (err) {
          if (err?.status === 409) {
            // FR-017: show non-blocking toast and auto-advance after 3 s
            setConflictToast(true);
            setTimeout(() => {
              setConflictToast(false);
              advance();
            }, 3000);
            return; // handled — do not propagate
          }
          throw err; // let withOfflineRetry decide if it's a network error
        }
        await advance();
      });

      await sendReview();
    },
    [currentItem, advance, withOfflineRetry]
  );

  const undoDecision = useCallback(async () => {
    // Release lock and reload same item (advance fetches next available,
    // which may be the same proposal if its lock was released)
    if (currentItem) {
      try {
        await unlockProposal(currentItem.proposal_id);
      } catch (_) {
        // ignore
      }
    }
    setPendingDecision(null);
    await advance();
  }, [currentItem, advance]);

  return {
    currentItem,
    queueTotal,
    isLoading,
    error,
    advance,
    pendingDecision,
    setPendingDecision,
    confirmDecision,
    undoDecision,
    conflictToast,
    isOffline,
  };
}
