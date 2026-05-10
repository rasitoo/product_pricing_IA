import { useEffect, useRef } from "react";
import { heartbeatLock } from "../services/api.js";

const HEARTBEAT_INTERVAL_MS = 20_000;

/**
 * Sends a heartbeat every 20s for the active proposal lock.
 * Cancels when proposalId changes or component unmounts.
 */
export function useLockHeartbeat(proposalId) {
  const intervalRef = useRef(null);

  useEffect(() => {
    if (!proposalId) return;

    async function beat() {
      try {
        await heartbeatLock(proposalId);
      } catch (_) {
        // Lock may have expired or been released — no action needed here
      }
    }

    intervalRef.current = setInterval(beat, HEARTBEAT_INTERVAL_MS);
    return () => clearInterval(intervalRef.current);
  }, [proposalId]);
}
