// src/components/VisualizacionNPL.jsx
import React, { useMemo, useRef } from "react";
import { Select } from "antd";
import dayjs from "dayjs";
import "dayjs/locale/es";
dayjs.locale("es");

const { Option } = Select;

const fmtMoney0 = (v) =>
  v == null
    ? "$0"
    : Intl.NumberFormat(undefined, {
        style: "currency",
        currency: "USD",
        maximumFractionDigits: 0,
      }).format(v);

const VisualizacionNPL = () => {
  const today = dayjs();

  // Generamos días mock (igual que en el tablero principal)
  const timelineData = useMemo(
    () =>
      Array.from({ length: 10 }, (_, i) => ({
        day: i + 1,
        date: today.date(i + 1).format("DD/MM"),
        value: Math.floor(Math.random() * 50000) + 20000,
      })),
    [today]
  );

  const trackRef = useRef(null);

  const scrollDays = (dir) => {
    if (!trackRef.current) return;
    trackRef.current.scrollBy({
      left: dir === "left" ? -300 : 300,
      behavior: "smooth",
    });
  };

  return (
    <div className="kpi-vis-panel">

      {/* ==== VISUALIZACIÓN + CHIPS ==== */}
      <div className="kpi-vis-header">

        {/* Select arriba SIEMPRE */}
        <div className="kpi-vis-select-row">
          <Select defaultValue="Visualización" className="kpi-visual-select">
            <Option value="vis1">Visualización</Option>
          </Select>
        </div>

        {/* Chips debajo */}
        <div className="kpi-month-carousel">

          <button className="nav-btn left" onClick={() => scrollDays("left")}>
            ‹
          </button>

          <div className="kpi-month-track">
            <div className="kpi-chip">
              <span className="chip-month">Ago</span>
              <span className="chip-divider">|</span>
              <span className="chip-label">Meta</span>
              <span className="chip-divider">|</span>
              <span className="chip-label">%Cum</span>
            </div>

            <div className="kpi-chip">
              <span className="chip-month">Sep</span>
              <span className="chip-divider">|</span>
              <span className="chip-label">Meta</span>
              <span className="chip-divider">|</span>
              <span className="chip-label">%Cum</span>
            </div>

            <div className="kpi-chip">
              <span className="chip-month">Nov</span>
              <span className="chip-divider">|</span>
              <span className="chip-label">Meta</span>
              <span className="chip-divider">|</span>
              <span className="chip-label">%Cum</span>
              <span className="chip-divider">|</span>
              <span className="chip-extra">Días cierre: 05</span>
            </div>
          </div>

          <button className="nav-btn right" onClick={() => scrollDays("right")}>
            ›
          </button>
        </div>
      </div>

      {/* ==== CARRUSEL DE DÍAS ==== */}
      <div className="kpi-days-scroll">
        <button
          className="scroll-btn left"
          type="button"
          onClick={() => scrollDays("left")}
        >
          ‹
        </button>

        <div className="kpi-days-track" ref={trackRef}>
          {timelineData.map((item) => (
            <div key={item.day} className="kpi-day-card">
              <div className="amount">{fmtMoney0(item.value)}</div>
              <div className="day-label">
                Día {item.day} · {item.date}
              </div>
            </div>
          ))}
        </div>

        <button
          className="scroll-btn right"
          type="button"
          onClick={() => scrollDays("right")}
        >
          ›
        </button>
      </div>
    </div>
  );
};

export default VisualizacionNPL;
