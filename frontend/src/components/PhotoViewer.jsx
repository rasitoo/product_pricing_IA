import React from "react";

const MAX_VISIBLE = 10;

const SLIDE_STYLE = {
  flex: "0 0 100%",
  scrollSnapAlign: "start",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  background: "#111",
  minHeight: 320,
};

const IMG_STYLE = {
  maxWidth: "100%",
  maxHeight: 400,
  objectFit: "contain",
};

const PLACEHOLDER_STYLE = {
  ...SLIDE_STYLE,
  color: "#666",
  fontSize: 14,
};

const MORE_SLIDE_STYLE = {
  ...SLIDE_STYLE,
  flexDirection: "column",
  gap: 8,
  color: "#aaa",
  fontSize: 18,
  fontWeight: 600,
  background: "#1a1a1a",
};

export function PhotoViewer({ images = [] }) {
  // CQR-006: render at most MAX_VISIBLE (10) photos; extra shown as indicator
  const visible = images.slice(0, MAX_VISIBLE);
  const extraCount = images.length - MAX_VISIBLE;

  if (images.length === 0) {
    return (
      <div style={PLACEHOLDER_STYLE}>
        <span>Sin fotos disponibles</span>
      </div>
    );
  }

  return (
    <div
      style={{
        display: "flex",
        overflowX: "auto",
        scrollSnapType: "x mandatory",
        WebkitOverflowScrolling: "touch",
        scrollbarWidth: "none",
        borderRadius: 8,
      }}
    >
      {visible.map((img, i) => (
        <div key={i} style={SLIDE_STYLE}>
          <img
            src={img.thumbnail_url || img.url}
            alt={`Foto ${i + 1}`}
            style={IMG_STYLE}
            loading="lazy"
          />
        </div>
      ))}

      {extraCount > 0 && (
        <div style={MORE_SLIDE_STYLE}>
          <span>+{extraCount} {extraCount === 1 ? "foto más" : "fotos más"}</span>
        </div>
      )}
    </div>
  );
}
