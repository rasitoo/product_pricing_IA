import React, { useState } from "react";

export function EditFormPanel({ item, onConfirm, onCancel }) {
  const [description, setDescription] = useState(item?.description ?? "");
  const [price, setPrice] = useState(item?.suggested_price ?? "");
  const [rejectReason, setRejectReason] = useState("");

  function handleConfirm() {
    const payload = {};
    if (description !== item?.description) payload.edited_description = description;
    if (Number(price) !== Number(item?.suggested_price)) payload.edited_price = Number(price);
    if (rejectReason.trim()) payload.reject_reason = rejectReason.trim();
    onConfirm?.(payload);
  }

  const hasChanges =
    description !== item?.description ||
    Number(price) !== Number(item?.suggested_price);

  return (
    <div
      style={{
        background: "#222",
        borderRadius: 12,
        padding: "1.5rem",
        maxWidth: 480,
        width: "100%",
        boxShadow: "0 8px 32px rgba(0,0,0,0.5)",
      }}
    >
      <h2 style={{ color: "#e5e5e5", margin: "0 0 1rem", fontSize: 18 }}>
        Modificar propuesta
      </h2>

      <label style={labelStyle}>
        Descripción
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={5}
          style={inputStyle}
        />
      </label>

      <label style={labelStyle}>
        Precio sugerido (€)
        <input
          type="number"
          min={0}
          step={0.01}
          value={price}
          onChange={(e) => setPrice(e.target.value)}
          style={inputStyle}
        />
      </label>

      <label style={labelStyle}>
        Motivo del rechazo (opcional)
        <input
          type="text"
          value={rejectReason}
          onChange={(e) => setRejectReason(e.target.value)}
          style={inputStyle}
          placeholder="Indica el motivo si lo deseas"
        />
      </label>

      <div style={{ display: "flex", gap: 12, marginTop: "1rem" }}>
        <button onClick={onCancel} style={cancelBtnStyle}>
          Cancelar
        </button>
        <button
          onClick={handleConfirm}
          disabled={!hasChanges}
          style={confirmBtnStyle(!hasChanges)}
        >
          Confirmar
        </button>
      </div>
    </div>
  );
}

const labelStyle = {
  display: "flex",
  flexDirection: "column",
  gap: 6,
  color: "#aaa",
  fontSize: 13,
  marginBottom: "1rem",
};

const inputStyle = {
  background: "#333",
  border: "1px solid #444",
  borderRadius: 8,
  color: "#e5e5e5",
  padding: "10px 12px",
  fontSize: 14,
  resize: "vertical",
  outline: "none",
};

const cancelBtnStyle = {
  flex: 1,
  padding: "10px 0",
  borderRadius: 8,
  border: "1px solid #555",
  background: "transparent",
  color: "#aaa",
  cursor: "pointer",
  fontSize: 14,
};

function confirmBtnStyle(disabled) {
  return {
    flex: 1,
    padding: "10px 0",
    borderRadius: 8,
    border: "none",
    background: disabled ? "#333" : "#22c55e",
    color: disabled ? "#666" : "#fff",
    cursor: disabled ? "not-allowed" : "pointer",
    fontSize: 14,
    fontWeight: 600,
  };
}
