import { useState, useCallback } from "react";
import { fetchNextQueueItem, reviewProposal, unlockProposal } from "../services/api.js";

/**
 * Manages the carousel queue state.
 * Returns: { currentItem, queueTotal, isLoading, error, advance, pendingDecision,
 *            confirmDecision, undoDecision, setPendingDecision }
 */
export function useCarouselQueue() {
  const [currentItem, setCurrentItem] = useState(null);
  const [queueTotal, setQueueTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  // pendingDecision: { type: "approve"|"reject"|"edit", payload?: object } | null
  const [pendingDecision, setPendingDecision] = useState(null);

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
      try {
        await reviewProposal(proposalId, { decision: type, ...payload });
      } catch (_) {
        // Swallow: advance anyway so UI doesn't get stuck
      }
      await advance();
    },
    [currentItem, advance]
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
  };
}
