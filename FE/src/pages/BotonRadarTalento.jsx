// BotonRadarTalento.jsx
import React from "react";
import "./BotonRadarTalento.css";

const BotonRadarTalento = () => {
  const abrirRadar = () => {
    window.open("/radar-talento", "_blank");
  };

  return (
    <button className="btn-radar-talento" onClick={abrirRadar}>
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="18"
        height="18"
        viewBox="0 0 24 24"
        fill="none"
        stroke="white"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        className="icono-radar"
      >
        <circle cx="12" cy="12" r="10"></circle>
        <path d="M12 12l6-6"></path>
        <path d="M12 12l4 4"></path>
        <path d="M12 12l-3 3"></path>
        <circle cx="12" cy="12" r="3"></circle>
      </svg>

      Radar de Talento Humano
    </button>
  );
};

export default BotonRadarTalento;
