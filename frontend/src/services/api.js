import { getSessionId } from "../state/sessionId.js";

const API_BASE = "http://localhost:8000/api/v1";

function sessionHeaders() {
  return {
    "Content-Type": "application/json",
    "X-Session-Id": getSessionId(),
  };
}

export async function fetchProposal(proposalId) {
  const response = await fetch(`${API_BASE}/proposals/${proposalId}`);
  if (!response.ok) throw new Error("proposal_not_found");
  return response.json();
}

export async function reviewProposal(proposalId, payload) {
  const response = await fetch(`${API_BASE}/proposals/${proposalId}/review`, {
    method: "POST",
    headers: sessionHeaders(),
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const err = new Error("review_failed");
    err.status = response.status;
    throw err;
  }
  return response.json();
}

export async function exportProduct(productId) {
  const response = await fetch(`${API_BASE}/products/${productId}/export`, { method: "POST" });
  if (!response.ok) throw new Error("export_failed");
  return response.json();
}

export async function fetchNextQueueItem() {
  const response = await fetch(`${API_BASE}/review-queue`, {
    headers: { "X-Session-Id": getSessionId() },
  });
  if (response.status === 204) return null;
  if (!response.ok) throw new Error("queue_fetch_failed");
  return response.json();
}

export async function lockProposal(proposalId) {
  const response = await fetch(`${API_BASE}/proposals/${proposalId}/lock`, {
    method: "POST",
    headers: { "X-Session-Id": getSessionId() },
  });
  if (response.status === 409) throw new Error("lock_conflict");
  if (!response.ok) throw new Error("lock_failed");
  return response.json();
}

export async function unlockProposal(proposalId) {
  await fetch(`${API_BASE}/proposals/${proposalId}/lock`, {
    method: "DELETE",
    headers: { "X-Session-Id": getSessionId() },
  });
}

export async function heartbeatLock(proposalId) {
  const response = await fetch(`${API_BASE}/proposals/${proposalId}/lock/heartbeat`, {
    method: "POST",
    headers: { "X-Session-Id": getSessionId() },
  });
  if (response.status === 404) throw new Error("lock_not_found");
  if (!response.ok) throw new Error("heartbeat_failed");
  return response.json();
}
