import React, { useRef } from "react";
import { useSpring, animated } from "react-spring";
import { useDrag } from "@use-gesture/react";

import { PhotoViewer } from "./PhotoViewer.jsx";

const SWIPE_THRESHOLD = 100; // px

export function CarouselCard({ item, onApprove, onReject }) {
  const [{ x, rotate, opacity }, api] = useSpring(() => ({
    x: 0,
    rotate: 0,
    opacity: 1,
  }));

  const isDragging = useRef(false);

  const bind = useDrag(
    ({ movement: [mx], down, velocity: [vx], direction: [dx] }) => {
      isDragging.current = down;
      if (down) {
        api.start({ x: mx, rotate: mx / 15, opacity: 1, immediate: true });
      } else {
        const triggered =
          Math.abs(mx) > SWIPE_THRESHOLD || Math.abs(vx) > 0.5;
        if (triggered) {
          const direction = mx > 0 || dx > 0 ? 1 : -1;
          api.start({ x: direction * 600, rotate: direction * 30, opacity: 0 });
          setTimeout(() => {
            api.start({ x: 0, rotate: 0, opacity: 1, immediate: true });
            if (direction > 0) onApprove?.();
            else onReject?.();
          }, 200);
        } else {
          api.start({ x: 0, rotate: 0, opacity: 1 });
        }
      }
    },
    { filterTaps: true }
  );

  const overlayColor =
    x.to((v) => (v > 20 ? "rgba(34,197,94,0.3)" : v < -20 ? "rgba(239,68,68,0.3)" : "transparent"));

  return (
    <animated.div
      {...bind()}
      style={{
        x,
        rotate,
        opacity,
        touchAction: "none",
        userSelect: "none",
        position: "relative",
        background: "#1a1a1a",
        borderRadius: 16,
        boxShadow: "0 8px 32px rgba(0,0,0,0.5)",
        overflow: "hidden",
        maxWidth: 480,
        width: "100%",
        cursor: "grab",
      }}
    >
      {/* Swipe overlay tint */}
      <animated.div
        style={{
          position: "absolute",
          inset: 0,
          background: overlayColor,
          zIndex: 1,
          pointerEvents: "none",
          borderRadius: 16,
        }}
      />

      <PhotoViewer images={item.images || []} />

      <div style={{ padding: "1rem 1.25rem 1.5rem", position: "relative", zIndex: 2 }}>
        <p style={{ color: "#e5e5e5", fontSize: 15, lineHeight: 1.6, margin: "0 0 1rem" }}>
          {item.description}
        </p>
        <div style={{ display: "flex", alignItems: "baseline", gap: 12 }}>
          <span style={{ color: "#22c55e", fontWeight: 700, fontSize: 22 }}>
            {Number(item.suggested_price).toLocaleString("es-ES", {
              style: "currency",
              currency: "EUR",
            })}
          </span>
          {item.suggested_price_min != null && item.suggested_price_max != null && (
            <span style={{ color: "#888", fontSize: 13 }}>
              ({Number(item.suggested_price_min).toLocaleString("es-ES", { style: "currency", currency: "EUR" })}
              {" – "}
              {Number(item.suggested_price_max).toLocaleString("es-ES", { style: "currency", currency: "EUR" })})
            </span>
          )}
          {item.confidence_score != null && (
            <span style={{ color: "#888", fontSize: 12, marginLeft: "auto" }}>
              Confianza {Math.round(item.confidence_score * 100)}%
            </span>
          )}
        </div>
      </div>

      {/* Action buttons */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-around",
          padding: "0 1.5rem 1.5rem",
          position: "relative",
          zIndex: 2,
        }}
      >
        <button
          onClick={(e) => { e.stopPropagation(); onReject?.(); }}
          style={btnStyle("#ef4444")}
          aria-label="Rechazar"
        >
          ✗
        </button>
        <button
          onClick={(e) => { e.stopPropagation(); onApprove?.(); }}
          style={btnStyle("#22c55e")}
          aria-label="Aprobar"
        >
          ✓
        </button>
      </div>
    </animated.div>
  );
}

function btnStyle(color) {
  return {
    width: 64,
    height: 64,
    borderRadius: "50%",
    border: `3px solid ${color}`,
    background: "transparent",
    color,
    fontSize: 28,
    cursor: "pointer",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    transition: "background 0.15s",
  };
}
