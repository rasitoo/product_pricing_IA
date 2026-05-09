import { describe, it, expect, vi } from "vitest";
import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { EditFormPanel } from "../src/components/EditFormPanel.jsx";

const ITEM = {
  proposal_id: "prop-1",
  description: "Descripción original",
  suggested_price: 100,
  images: [],
};

describe("EditFormPanel", () => {
  it("pre-loads fields with original values", () => {
    render(<EditFormPanel item={ITEM} onConfirm={vi.fn()} onCancel={vi.fn()} />);
    expect(screen.getByDisplayValue("Descripción original")).toBeInTheDocument();
    expect(screen.getByDisplayValue("100")).toBeInTheDocument();
  });

  it("Cancel calls onCancel without emitting changes", () => {
    const onConfirm = vi.fn();
    const onCancel = vi.fn();
    render(<EditFormPanel item={ITEM} onConfirm={onConfirm} onCancel={onCancel} />);
    fireEvent.click(screen.getByRole("button", { name: /Cancelar/i }));
    expect(onCancel).toHaveBeenCalledOnce();
    expect(onConfirm).not.toHaveBeenCalled();
  });

  it("Confirm emits only changed fields", () => {
    const onConfirm = vi.fn();
    render(<EditFormPanel item={ITEM} onConfirm={onConfirm} onCancel={vi.fn()} />);
    const textarea = screen.getByDisplayValue("Descripción original");
    fireEvent.change(textarea, { target: { value: "Nueva descripción" } });
    fireEvent.click(screen.getByRole("button", { name: /Confirmar/i }));
    expect(onConfirm).toHaveBeenCalledWith(
      expect.objectContaining({ edited_description: "Nueva descripción" })
    );
    expect(onConfirm.mock.calls[0][0]).not.toHaveProperty("edited_price");
  });

  it("Confirm button is disabled when no changes", () => {
    render(<EditFormPanel item={ITEM} onConfirm={vi.fn()} onCancel={vi.fn()} />);
    const btn = screen.getByRole("button", { name: /Confirmar/i });
    expect(btn).toBeDisabled();
  });

  it("Confirm button enabled after editing description", () => {
    render(<EditFormPanel item={ITEM} onConfirm={vi.fn()} onCancel={vi.fn()} />);
    const textarea = screen.getByDisplayValue("Descripción original");
    fireEvent.change(textarea, { target: { value: "Cambio" } });
    expect(screen.getByRole("button", { name: /Confirmar/i })).not.toBeDisabled();
  });
});
