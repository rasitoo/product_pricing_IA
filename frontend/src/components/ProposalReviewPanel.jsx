import React, { useState } from "react";

export function ProposalReviewPanel({ onReview }) {
  const [operatorId, setOperatorId] = useState("ops-1");
  const [decision, setDecision] = useState("approve");

  return (
    <section>
      <h3>Decision Operativa</h3>
      <label>
        Operador
        <input value={operatorId} onChange={(e) => setOperatorId(e.target.value)} />
      </label>
      <label>
        Decision
        <select value={decision} onChange={(e) => setDecision(e.target.value)}>
          <option value="approve">Aprobar</option>
          <option value="reject">Rechazar</option>
          <option value="edit">Editar</option>
        </select>
      </label>
      <button onClick={() => onReview({ operator_id: operatorId, decision })}>Enviar</button>
    </section>
  );
}
