import React from "react";

export function ChannelMetadataPanel({ sourceChannel = "api" }) {
  return (
    <aside>
      <h3>Canal de Ingesta</h3>
      <p>Origen: {sourceChannel}</p>
      <p>Autoaprobacion: deshabilitada en v1</p>
    </aside>
  );
}
