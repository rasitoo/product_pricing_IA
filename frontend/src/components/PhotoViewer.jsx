import React, { useRef } from "react";

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

export function PhotoViewer({ images = [] }) {
  const scrollRef = useRef(null);

  const visible = images.slice(0, 9);
  const hasThumbnails = images.length > 1;

  function scrollTo(index) {
    if (!scrollRef.current) return;
    const width = scrollRef.current.clientWidth;
    scrollRef.current.scrollTo({ left: index * width, behavior: "smooth" });
  }

  if (images.length === 0) {
    return (
      <div style={PLACEHOLDER_STYLE}>
        <span>Sin fotos disponibles</span>
      </div>
    );
  }

  return (
    <div>
      <div
        ref={scrollRef}
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
      </div>

      {hasThumbnails && (
        <div style={{ display: "flex", gap: 6, marginTop: 8, justifyContent: "center" }}>
          {visible.map((img, i) => (
            <button
              key={i}
              onClick={() => scrollTo(i)}
              style={{
                padding: 0,
                border: "2px solid #444",
                borderRadius: 4,
                cursor: "pointer",
                background: "none",
              }}
            >
              <img
                src={img.thumbnail_url || img.url}
                alt={`Miniatura ${i + 1}`}
                style={{ width: 40, height: 40, objectFit: "cover", display: "block", borderRadius: 2 }}
              />
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
