import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { CarouselCard } from "../src/components/CarouselCard.jsx";

// Mock react-spring and @use-gesture/react to avoid DOM animation complexity
vi.mock("react-spring", () => ({
  useSpring: () => [
    { x: { to: (fn) => fn(0) }, rotate: { to: (fn) => fn(0) }, opacity: { to: (fn) => fn(1) } },
    vi.fn(),
  ],
  animated: {
    div: ({ children, style, ...props }) => <div style={{}} {...props}>{children}</div>,
  },
}));

vi.mock("@use-gesture/react", () => ({
  useDrag: () => () => ({}),
}));

const ITEM = {
  proposal_id: "abc-123",
  description: "Descripción de prueba",
  suggested_price: 99.99,
  suggested_price_min: 80,
  suggested_price_max: 120,
  confidence_score: 0.85,
  images: [
    { url: "/uploads/photo1.jpg", thumbnail_url: "/uploads/photo1.jpg" },
    { url: "/uploads/photo2.jpg", thumbnail_url: "/uploads/photo2.jpg" },
  ],
};

describe("CarouselCard", () => {
  it("renders description", () => {
    render(<CarouselCard item={ITEM} onApprove={vi.fn()} onReject={vi.fn()} />);
    expect(screen.getByText("Descripción de prueba")).toBeInTheDocument();
  });

  it("renders price", () => {
    render(<CarouselCard item={ITEM} onApprove={vi.fn()} onReject={vi.fn()} />);
    expect(screen.getByText(/99/)).toBeInTheDocument();
  });

  it("renders photos via PhotoViewer", () => {
    render(<CarouselCard item={ITEM} onApprove={vi.fn()} onReject={vi.fn()} />);
    const imgs = screen.getAllByRole("img");
    expect(imgs.length).toBeGreaterThan(0);
  });

  it("approve button calls onApprove", () => {
    const onApprove = vi.fn();
    render(<CarouselCard item={ITEM} onApprove={onApprove} onReject={vi.fn()} />);
    fireEvent.click(screen.getByLabelText("Aprobar"));
    expect(onApprove).toHaveBeenCalledOnce();
  });

  it("reject button calls onReject", () => {
    const onReject = vi.fn();
    render(<CarouselCard item={ITEM} onApprove={vi.fn()} onReject={onReject} />);
    fireEvent.click(screen.getByLabelText("Rechazar"));
    expect(onReject).toHaveBeenCalledOnce();
  });
});
