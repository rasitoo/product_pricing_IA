const API_BASE = "http://localhost:8000/api/v1";

export async function fetchProposal(proposalId) {
  const response = await fetch(`${API_BASE}/proposals/${proposalId}`);
  if (!response.ok) throw new Error("proposal_not_found");
  return response.json();
}

export async function reviewProposal(proposalId, payload) {
  const response = await fetch(`${API_BASE}/proposals/${proposalId}/review`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error("review_failed");
  return response.json();
}

export async function exportProduct(productId) {
  const response = await fetch(`${API_BASE}/products/${productId}/export`, { method: "POST" });
  if (!response.ok) throw new Error("export_failed");
  return response.json();
}
