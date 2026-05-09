/**
 * T063 — Tests for PhotoViewer CQR-006: max 10 photos + "N fotos más" indicator
 */
import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { PhotoViewer } from "../src/components/PhotoViewer.jsx";

function makeImages(n) {
  return Array.from({ length: n }, (_, i) => ({
    url: `https://example.com/foto-${i + 1}.jpg`,
    thumbnail_url: null,
  }));
}

describe("PhotoViewer", () => {
  it("renders placeholder when images is empty", () => {
    render(<PhotoViewer images={[]} />);
    expect(screen.getByText("Sin fotos disponibles")).toBeTruthy();
  });

  it("renders all slides when 10 photos or fewer", () => {
    render(<PhotoViewer images={makeImages(10)} />);
    const imgs = document.querySelectorAll("img");
    expect(imgs).toHaveLength(10);
    // No 'fotos más' indicator
    expect(screen.queryByText(/foto.*más/i)).toBeNull();
  });

  it("renders exactly 10 slides + 'N fotos más' slide when 11 photos (T063)", () => {
    render(<PhotoViewer images={makeImages(11)} />);
    const imgs = document.querySelectorAll("img");
    // Only 10 img elements — the extra slide has no img
    expect(imgs).toHaveLength(10);
    expect(screen.getByText("+1 foto más")).toBeTruthy();
  });

  it("renders 10 slides + 'N fotos más' indicator for 15 photos", () => {
    render(<PhotoViewer images={makeImages(15)} />);
    const imgs = document.querySelectorAll("img");
    expect(imgs).toHaveLength(10);
    expect(screen.getByText("+5 fotos más")).toBeTruthy();
  });

  it("renders correctly with exactly 1 photo", () => {
    render(<PhotoViewer images={makeImages(1)} />);
    const imgs = document.querySelectorAll("img");
    expect(imgs).toHaveLength(1);
    expect(screen.queryByText(/fotos* más/i)).toBeNull();
  });
});
