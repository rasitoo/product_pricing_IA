import React, { useState } from "react";

import { ChannelMetadataPanel } from "../components/ChannelMetadataPanel.jsx";
import { ProposalReviewPanel } from "../components/ProposalReviewPanel.jsx";
import { exportProduct, reviewProposal } from "../services/api.js";
import { canExport } from "../state/reviewState.js";

export function ReviewPage() {
  const [proposalId, setProposalId] = useState("");
  const [productId, setProductId] = useState("");
  const [status, setStatus] = useState("in_review");
  const [message, setMessage] = useState("");

  async function onReview(payload) {
    if (!proposalId) {
      setMessage("Indica un proposal_id");
      return;
    }
    const result = await reviewProposal(proposalId, payload);
    setStatus(result.next_status);
    setMessage(`Revision aplicada: ${result.next_status}`);
  }

  async function onExport() {
    if (!productId) {
      setMessage("Indica un product_id");
      return;
    }
    const result = await exportProduct(productId);
    setMessage(`Export generado: ${result.export_id}`);
  }

  return (
    <main style={{ fontFamily: "sans-serif", maxWidth: 760, margin: "2rem auto" }}>
      <h1>Consola de Revision</h1>
      <p>Revision humana obligatoria para propuestas de pricing IA.</p>

      <label>
        Proposal ID
        <input value={proposalId} onChange={(e) => setProposalId(e.target.value)} style={{ width: "100%" }} />
      </label>
      <label>
        Product ID
        <input value={productId} onChange={(e) => setProductId(e.target.value)} style={{ width: "100%" }} />
      </label>

      <ProposalReviewPanel onReview={onReview} />
      <ChannelMetadataPanel sourceChannel="api" />

      <button disabled={!canExport(status)} onClick={onExport}>
        Exportar borrador aprobado
      </button>

      <p>{message}</p>
    </main>
  );
}
