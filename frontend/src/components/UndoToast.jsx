import React, { useEffect } from "react";

export function UndoToast({ message, onUndo, onConfirm, durationMs = 5000 }) {
  useEffect(() => {
    const timer = setTimeout(() => {
      onConfirm?.();
    }, durationMs);
    return () => clearTimeout(timer);
  }, [durationMs, onConfirm]);

  return (
    <div
      style={{
        position: "fixed",
        bottom: 32,
        left: "50%",
        transform: "translateX(-50%)",
        background: "#333",
        color: "#fff",
        padding: "14px 24px",
        borderRadius: 12,
        display: "flex",
        alignItems: "center",
        gap: 16,
        boxShadow: "0 4px 20px rgba(0,0,0,0.4)",
        zIndex: 1000,
        minWidth: 280,
        fontSize: 14,
      }}
      role="status"
      aria-live="polite"
    >
      <span style={{ flex: 1 }}>{message}</span>
      <button
        onClick={onUndo}
        style={{
          background: "transparent",
          border: "1px solid #aaa",
          color: "#fff",
          padding: "6px 14px",
          borderRadius: 8,
          cursor: "pointer",
          fontSize: 13,
          whiteSpace: "nowrap",
        }}
      >
        Deshacer
      </button>
    </div>
  );
}
