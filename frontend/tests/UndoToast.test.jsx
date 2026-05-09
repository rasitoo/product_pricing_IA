import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import React from "react";
import { render, screen, fireEvent, act } from "@testing-library/react";
import { UndoToast } from "../src/components/UndoToast.jsx";

describe("UndoToast", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("calls onConfirm after duration expires", () => {
    const onConfirm = vi.fn();
    render(
      <UndoToast message="Acción realizada" onUndo={vi.fn()} onConfirm={onConfirm} durationMs={5000} />
    );
    act(() => { vi.advanceTimersByTime(5000); });
    expect(onConfirm).toHaveBeenCalledOnce();
  });

  it("calls onUndo when button is clicked before expiry", () => {
    const onUndo = vi.fn();
    const onConfirm = vi.fn();
    render(
      <UndoToast message="Acción realizada" onUndo={onUndo} onConfirm={onConfirm} durationMs={5000} />
    );
    fireEvent.click(screen.getByRole("button", { name: /Deshacer/i }));
    expect(onUndo).toHaveBeenCalledOnce();
  });

  it("does not call onConfirm after unmount", () => {
    const onConfirm = vi.fn();
    const { unmount } = render(
      <UndoToast message="Acción realizada" onUndo={vi.fn()} onConfirm={onConfirm} durationMs={5000} />
    );
    unmount();
    act(() => { vi.advanceTimersByTime(5000); });
    expect(onConfirm).not.toHaveBeenCalled();
  });

  it("renders the message text", () => {
    render(
      <UndoToast message="Propuesta aprobada" onUndo={vi.fn()} onConfirm={vi.fn()} durationMs={5000} />
    );
    expect(screen.getByText("Propuesta aprobada")).toBeInTheDocument();
  });
});
