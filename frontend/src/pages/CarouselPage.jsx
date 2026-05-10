import React, { useEffect, useState } from "react";

import { CarouselCard } from "../components/CarouselCard.jsx";
import { EditFormPanel } from "../components/EditFormPanel.jsx";
import { UndoToast } from "../components/UndoToast.jsx";
import { useCarouselQueue } from "../hooks/useCarouselQueue.js";
import { useLockHeartbeat } from "../hooks/useLockHeartbeat.js";
import { reviewProposal, unlockProposal } from "../services/api.js";

export function CarouselPage() {
  const {
    currentItem,
    queueTotal,
    isLoading,
    error,
    advance,
    pendingDecision,
    setPendingDecision,
    confirmDecision,
    undoDecision,
  } = useCarouselQueue();

  const [showEditForm, setShowEditForm] = useState(false);

  useLockHeartbeat(currentItem?.proposal_id);

  // Load queue on mount
  useEffect(() => {
    advance();
  }, []);

  // --- Approve flow ---
  function handleApprove() {
    setPendingDecision({ type: "approve" });
  }

  async function handleApproveConfirm() {
    await confirmDecision("approve");
  }

  // --- Reject flow ---
  function handleReject() {
    setPendingDecision({ type: "reject" });
  }

  async function handleRejectConfirm() {
    await confirmDecision("reject");
  }

  // --- Edit flow (from EditFormPanel) ---
  async function handleEditConfirm(editPayload) {
    setShowEditForm(false);
    if (!currentItem) return;
    try {
      await reviewProposal(currentItem.proposal_id, { decision: "edit", ...editPayload });
    } catch (_) {
      // continue regardless
    }
    await advance();
  }

  function handleEditCancel() {
    setShowEditForm(false);
    setPendingDecision(null);
  }

  // --- Undo ---
  async function handleUndo() {
    setPendingDecision(null);
    setShowEditForm(false);
    await undoDecision();
  }

  // When reject toast fires open edit form option
  function onRejectToastConfirm() {
    // Direct reject without edit
    handleRejectConfirm();
  }

  // Show edit form when reject button pressed (optional — show form before confirming)
  function handleRejectWithEdit() {
    setPendingDecision(null);
    setShowEditForm(true);
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#0f0f0f",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        padding: "2rem 1rem",
        fontFamily: "system-ui, sans-serif",
        color: "#e5e5e5",
      }}
    >
      <header style={{ width: "100%", maxWidth: 480, marginBottom: "1.5rem" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <h1 style={{ margin: 0, fontSize: 20, fontWeight: 700 }}>Revisión de Propuestas</h1>
          {queueTotal > 0 && (
            <span
              style={{
                background: "#333",
                borderRadius: 20,
                padding: "4px 12px",
                fontSize: 13,
                color: "#aaa",
              }}
            >
              {queueTotal} pendiente{queueTotal !== 1 ? "s" : ""}
            </span>
          )}
        </div>
      </header>

      <main style={{ width: "100%", maxWidth: 480, display: "flex", flexDirection: "column", gap: "1rem" }}>
        {isLoading && (
          <div style={{ textAlign: "center", color: "#666", padding: "3rem 0" }}>
            Cargando...
          </div>
        )}

        {!isLoading && error && (
          <div
            style={{
              background: "#2a1515",
              border: "1px solid #5a2020",
              borderRadius: 12,
              padding: "1.5rem",
              textAlign: "center",
            }}
          >
            <p style={{ color: "#f87171", margin: "0 0 1rem" }}>
              Error al cargar la cola: {error}
            </p>
            <button
              onClick={advance}
              style={{
                padding: "8px 20px",
                borderRadius: 8,
                border: "1px solid #f87171",
                background: "transparent",
                color: "#f87171",
                cursor: "pointer",
              }}
            >
              Reintentar
            </button>
          </div>
        )}

        {!isLoading && !error && !currentItem && (
          <div
            style={{
              textAlign: "center",
              padding: "4rem 2rem",
              color: "#666",
            }}
          >
            <p style={{ fontSize: 18, margin: "0 0 0.5rem" }}>✓ Cola vacía</p>
            <p style={{ fontSize: 14 }}>No hay propuestas pendientes de revisión.</p>
            <button
              onClick={advance}
              style={{
                marginTop: "1rem",
                padding: "8px 20px",
                borderRadius: 8,
                border: "1px solid #555",
                background: "transparent",
                color: "#aaa",
                cursor: "pointer",
              }}
            >
              Actualizar
            </button>
          </div>
        )}

        {!isLoading && !error && currentItem && !showEditForm && (
          <CarouselCard
            item={currentItem}
            onApprove={handleApprove}
            onReject={handleReject}
          />
        )}

        {showEditForm && currentItem && (
          <>
            <div style={{ textAlign: "center", marginBottom: 8 }}>
              <button
                onClick={handleEditCancel}
                style={{
                  background: "transparent",
                  border: "none",
                  color: "#888",
                  cursor: "pointer",
                  fontSize: 13,
                }}
              >
                ← Volver a la tarjeta
              </button>
            </div>
            <EditFormPanel
              item={currentItem}
              onConfirm={handleEditConfirm}
              onCancel={handleEditCancel}
            />
          </>
        )}

        {/* Reject options bar */}
        {currentItem && !showEditForm && pendingDecision?.type === "reject" && (
          <div
            style={{
              display: "flex",
              gap: 10,
              marginTop: 8,
              justifyContent: "center",
            }}
          >
            <button
              onClick={onRejectToastConfirm}
              style={{
                padding: "8px 18px",
                borderRadius: 8,
                border: "1px solid #ef4444",
                background: "transparent",
                color: "#ef4444",
                cursor: "pointer",
                fontSize: 13,
              }}
            >
              Rechazar directamente
            </button>
            <button
              onClick={handleRejectWithEdit}
              style={{
                padding: "8px 18px",
                borderRadius: 8,
                border: "1px solid #f59e0b",
                background: "transparent",
                color: "#f59e0b",
                cursor: "pointer",
                fontSize: 13,
              }}
            >
              Rechazar con modificación
            </button>
          </div>
        )}
      </main>

      {/* Undo Toast for approve */}
      {pendingDecision?.type === "approve" && (
        <UndoToast
          message="Propuesta aprobada"
          onUndo={handleUndo}
          onConfirm={handleApproveConfirm}
          durationMs={5000}
        />
      )}

      {/* Undo Toast for direct reject */}
      {pendingDecision?.type === "reject" && (
        <UndoToast
          message="Propuesta rechazada"
          onUndo={handleUndo}
          onConfirm={onRejectToastConfirm}
          durationMs={5000}
        />
      )}
    </div>
  );
}
