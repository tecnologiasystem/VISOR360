import React, { useState, useEffect, useMemo } from "react";
import "./ComparativoRecaudo.css";
import { Select, Spin } from "antd";
import dayjs from "dayjs";
import "dayjs/locale/es";
import {
  getInfoDiaHabilActual,
  compararDiasHabiles,
  getRecaudoComparativoDiaHabil,
} from "../services/recaudoApiService";
import { recaudoApi } from "../services/recaudoApiService";

dayjs.locale("es");

const { Option } = Select;

// Formatters
const fmt = (v) => {
  if (!v && v !== 0) return "$0";
  return new Intl.NumberFormat("es-CO", {
    style: "currency",
    currency: "COP",
    maximumFractionDigits: 0,
  }).format(v);
};

const fmtPercent = (v) => {
  if (!v && v !== 0) return "0%";
  const sign = v >= 0 ? "+" : "";
  return `${sign}${(v * 100).toFixed(1)}%`;
};

const fmtDate = (fecha) => {
  if (!fecha) return "-";
  return dayjs(fecha).format("DD MMM");
};

const monthNames = [
  "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
  "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
];

const monthNamesShort = [
  "Ene", "Feb", "Mar", "Abr", "May", "Jun",
  "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"
];

// Generar opciones de meses para comparar (últimos 12 meses)
const generateMonthOptions = () => {
  const options = [];
  const now = dayjs();
  for (let i = 1; i <= 12; i++) {
    const d = now.subtract(i, "month");
    options.push({
      mes: d.month() + 1,
      anio: d.year(),
      label: `${monthNames[d.month()]} ${d.year()}`,
    });
  }
  return options;
};

// Componente de detalle expandido para una subcampaña
const SubcampanaDetail = ({ 
  subcampana, 
  mesActual, 
  anioActual, 
  mesComparar, 
  anioComparar,
  diaHabil,
  comparacionDias 
}) => {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);

  useEffect(() => {
    const cargarComparacion = async () => {
      setLoading(true);
      try {
        // Por ahora usamos datos simulados basados en la subcampaña
        // En producción, llamar al endpoint específico por subcampaña
        const response = await recaudoApi.get(
          `/dias-habiles/recaudo-comparativo/${encodeURIComponent(subcampana.pais)}`,
          {
            params: {
              mes_actual: mesActual,
              anio_actual: anioActual,
              mes_comparar: mesComparar,
              anio_comparar: anioComparar,
              hasta_dia_habil: diaHabil,
            },
          }
        );
        
        // Extraer datos de la subcampaña específica
        const dataResp = response.data;
        const recaudoActual = dataResp.mes_actual?.por_campana?.[subcampana.nombre] || subcampana.recaudoActual || 0;
        const recaudoComparar = dataResp.mes_comparar?.por_campana?.[subcampana.nombre] || subcampana.recaudoComparar || 0;
        
        const variacion = recaudoComparar > 0 
          ? (recaudoActual - recaudoComparar) / recaudoComparar 
          : 0;
        
        setData({
          recaudoActual,
          recaudoComparar,
          variacion,
          variacionAbsoluta: recaudoActual - recaudoComparar,
          fechaActual: comparacionDias?.mes_actual?.fecha,
          fechaComparar: comparacionDias?.mes_comparar?.fecha,
        });
      } catch (error) {
        console.error("Error cargando comparación:", error);
        // Fallback con datos de la subcampaña
        const recaudoActual = subcampana.recaudoActual || 0;
        const recaudoComparar = subcampana.recaudoComparar || 0;
        const variacion = recaudoComparar > 0 
          ? (recaudoActual - recaudoComparar) / recaudoComparar 
          : 0;
        
        setData({
          recaudoActual,
          recaudoComparar,
          variacion,
          variacionAbsoluta: recaudoActual - recaudoComparar,
          fechaActual: comparacionDias?.mes_actual?.fecha,
          fechaComparar: comparacionDias?.mes_comparar?.fecha,
        });
      } finally {
        setLoading(false);
      }
    };

    cargarComparacion();
  }, [subcampana, mesActual, anioActual, mesComparar, anioComparar, diaHabil]);

  if (loading) {
    return (
      <div className="comparison-loading">
        <div className="loading-spinner"></div>
        <span>Cargando comparación...</span>
      </div>
    );
  }

  if (!data) return null;

  const maxRecaudo = Math.max(data.recaudoActual, data.recaudoComparar, 1);
  const progressActual = (data.recaudoActual / maxRecaudo) * 100;
  const progressComparar = (data.recaudoComparar / maxRecaudo) * 100;

  return (
    <>
      {/* Indicador de variación */}
      <div className={`variation-indicator ${data.variacion < 0 ? "negative" : ""}`}>
        <span className="variation-label">Variación vs mes anterior</span>
        <div className="variation-value">
          <span className="variation-arrow">
            {data.variacion >= 0 ? "↑" : "↓"}
          </span>
          {fmtPercent(data.variacion)}
        </div>
        <span className="variation-absolute">
          {data.variacionAbsoluta >= 0 ? "+" : ""}
          {fmt(data.variacionAbsoluta)}
        </span>
      </div>

      {/* Grid de comparación */}
      <div className="comparison-grid">
        {/* Card mes actual */}
        <div className="month-card actual">
          <div className="month-card-header">
            <span className="month-name">
              {monthNames[mesActual - 1]} {anioActual}
            </span>
            <span className="month-date-badge">
              Día hábil {diaHabil} • {fmtDate(data.fechaActual)}
            </span>
          </div>
          <div className="month-value">{fmt(data.recaudoActual)}</div>
          <div className="month-detail">
            Recaudo acumulado hasta hoy
          </div>
        </div>

        {/* Card mes comparar */}
        <div className="month-card comparar">
          <div className="month-card-header">
            <span className="month-name">
              {monthNames[mesComparar - 1]} {anioComparar}
            </span>
            <span className="month-date-badge">
              Día hábil {diaHabil} • {fmtDate(data.fechaComparar)}
            </span>
          </div>
          <div className="month-value">{fmt(data.recaudoComparar)}</div>
          <div className="month-detail">
            Recaudo al mismo día hábil
          </div>
        </div>
      </div>

      {/* Barras de progreso comparativas */}
      <div className="comparison-chart">
        <div className="chart-title">
          📊 Comparación Visual
        </div>
        <div className="chart-legend">
          <div className="legend-item">
            <span className="legend-dot actual"></span>
            {monthNamesShort[mesActual - 1]} {anioActual}
          </div>
          <div className="legend-item">
            <span className="legend-dot comparar"></span>
            {monthNamesShort[mesComparar - 1]} {anioComparar}
          </div>
        </div>
        <div className="progress-comparison">
          <div className="progress-row">
            <div className="progress-bars">
              <div className="progress-bar-wrapper">
                <div 
                  className="progress-bar actual" 
                  style={{ width: `${Math.max(progressActual, 15)}%` }}
                >
                  {fmt(data.recaudoActual)}
                </div>
              </div>
              <div className="progress-bar-wrapper">
                <div 
                  className="progress-bar comparar" 
                  style={{ width: `${Math.max(progressComparar, 15)}%` }}
                >
                  {fmt(data.recaudoComparar)}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

// Componente principal
export default function ComparativoRecaudo({ 
  nombreCampana, 
  mes, 
  anio,
  subcampanasData = [] 
}) {
  const [expandedId, setExpandedId] = useState(null);
  const [mesComparar, setMesComparar] = useState(null);
  const [anioComparar, setAnioComparar] = useState(null);
  const [infoHoy, setInfoHoy] = useState(null);
  const [comparacionDias, setComparacionDias] = useState(null);
  const [loading, setLoading] = useState(true);
  const [subcampanas, setSubcampanas] = useState([]);

  const monthOptions = useMemo(() => generateMonthOptions(), []);

  // Cargar info del día hábil actual
  useEffect(() => {
    const cargarInfoHoy = async () => {
      try {
        const info = await getInfoDiaHabilActual();
        setInfoHoy(info);
        
        // Por defecto comparar con el mes anterior
        const mesAnterior = dayjs().subtract(1, "month");
        setMesComparar(mesAnterior.month() + 1);
        setAnioComparar(mesAnterior.year());
      } catch (error) {
        console.error("Error cargando info del día:", error);
        // Fallback
        const now = dayjs();
        setInfoHoy({
          dia_habil: 8,
          total_dias_habiles_mes: 21,
          dias_habiles_restantes: 13,
        });
        const mesAnterior = now.subtract(1, "month");
        setMesComparar(mesAnterior.month() + 1);
        setAnioComparar(mesAnterior.year());
      }
    };
    cargarInfoHoy();
  }, []);

  // Cargar comparación de días cuando cambie el mes a comparar
  useEffect(() => {
    if (!mesComparar || !anioComparar || !infoHoy) return;

    const cargarComparacion = async () => {
      try {
        const comp = await compararDiasHabiles(
          mes, anio, mesComparar, anioComparar, infoHoy.dia_habil
        );
        setComparacionDias(comp);
      } catch (error) {
        console.error("Error cargando comparación días:", error);
      }
    };
    cargarComparacion();
  }, [mes, anio, mesComparar, anioComparar, infoHoy]);

  // Cargar subcampañas con recaudo de ambos meses
  useEffect(() => {
    if (!nombreCampana || !mesComparar || !anioComparar) return;

    const cargarSubcampanas = async () => {
      setLoading(true);
      try {
        // Cargar recaudo del mes actual
        const paisName = encodeURIComponent(nombreCampana);
        const [respActual, respComparar] = await Promise.all([
          recaudoApi.get(`/recaudos/pais_by_name/${paisName}`, { 
            params: { mes, anio } 
          }),
          recaudoApi.get(`/recaudos/pais_by_name/${paisName}`, { 
            params: { mes: mesComparar, anio: anioComparar } 
          }),
        ]);

        const subcampsActual = respActual.data?.subcampanas || [];
        const subcampsComparar = respComparar.data?.subcampanas || [];

        // Crear mapa de recaudo comparar
        const mapaComparar = {};
        subcampsComparar.forEach((s) => {
          const nombre = s.nombre_campana || s.nombre || s.name || "";
          mapaComparar[nombre.toLowerCase()] = s.total || s.recaudo_total || 0;
        });

        // Combinar datos
        const combined = subcampsActual.map((s) => {
          const nombre = s.nombre_campana || s.nombre || s.name || "";
          const recaudoActual = s.total || s.recaudo_total || 0;
          const recaudoComparar = mapaComparar[nombre.toLowerCase()] || 0;
          const variacion = recaudoComparar > 0 
            ? (recaudoActual - recaudoComparar) / recaudoComparar 
            : 0;

          return {
            id: nombre,
            nombre,
            pais: nombreCampana,
            recaudoActual,
            recaudoComparar,
            variacion,
          };
        });

        setSubcampanas(combined.filter(s => s.recaudoActual > 0 || s.recaudoComparar > 0));
      } catch (error) {
        console.error("Error cargando subcampañas:", error);
        setSubcampanas([]);
      } finally {
        setLoading(false);
      }
    };

    cargarSubcampanas();
  }, [nombreCampana, mes, anio, mesComparar, anioComparar]);

  const handleToggleExpand = (id) => {
    setExpandedId(expandedId === id ? null : id);
  };

  const handleMesChange = (value) => {
    const [m, a] = value.split("-");
    setMesComparar(parseInt(m));
    setAnioComparar(parseInt(a));
    setExpandedId(null); // Cerrar expandidos al cambiar mes
  };

  if (!infoHoy) {
    return (
      <div className="comparativo-container">
        <div className="comparison-loading">
          <div className="loading-spinner"></div>
          <span>Cargando información...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="comparativo-container">
      {/* Título con badge de día hábil */}
      <div className="comparativo-title">
        <span className="comparativo-title-icon">📈</span>
        Comparativo por Día Hábil
      </div>
      
      <div className="comparativo-subtitle">
        <span>Hoy es el</span>
        <span className="dia-habil-badge">
          Día hábil {infoHoy.dia_habil} de {infoHoy.total_dias_habiles_mes}
        </span>
        <span>• Quedan {infoHoy.dias_habiles_restantes} días</span>
      </div>

      {/* Selector de mes a comparar */}
      <div className="comparativo-selector">
        <span className="selector-label">Comparar con:</span>
        <Select
          value={mesComparar && anioComparar ? `${mesComparar}-${anioComparar}` : undefined}
          onChange={handleMesChange}
          style={{ width: 200 }}
          placeholder="Seleccione mes"
        >
          {monthOptions.map((opt) => (
            <Option key={`${opt.mes}-${opt.anio}`} value={`${opt.mes}-${opt.anio}`}>
              {opt.label}
            </Option>
          ))}
        </Select>
        {comparacionDias && (
          <span style={{ color: "#64748b", fontSize: "13px" }}>
            (Día {comparacionDias.mes_comparar?.dia_mes} de {monthNamesShort[mesComparar - 1]})
          </span>
        )}
      </div>

      {/* Tabla de subcampañas */}
      {loading ? (
        <div className="comparison-loading">
          <div className="loading-spinner"></div>
          <span>Cargando subcampañas...</span>
        </div>
      ) : subcampanas.length === 0 ? (
        <div className="comparativo-empty">
          <div className="empty-icon">📊</div>
          <div className="empty-text">No hay subcampañas disponibles</div>
          <div className="empty-subtext">
            Seleccione una campaña con subcampañas para ver la comparación
          </div>
        </div>
      ) : (
        <div className="comparativo-table">
          {subcampanas.map((sub) => {
            const isExpanded = expandedId === sub.id;
            const initials = sub.nombre
              .split(" ")
              .map((w) => w[0])
              .join("")
              .substring(0, 2)
              .toUpperCase();

            return (
              <div
                key={sub.id}
                className={`subcampana-item ${isExpanded ? "expanded" : ""}`}
              >
                {/* Header clickeable */}
                <div
                  className="subcampana-header"
                  onClick={() => handleToggleExpand(sub.id)}
                >
                  {/* Nombre */}
                  <div className="subcampana-nombre">
                    <span className="subcampana-icon">{initials}</span>
                    {sub.nombre}
                  </div>

                  {/* Recaudo actual */}
                  <div className="header-cell">
                    <div className="header-label">
                      {monthNamesShort[mes - 1]} {anio}
                    </div>
                    <div className="header-value">{fmt(sub.recaudoActual)}</div>
                  </div>

                  {/* Recaudo mes comparar */}
                  <div className="header-cell">
                    <div className="header-label">
                      {monthNamesShort[mesComparar - 1]} {anioComparar}
                    </div>
                    <div className="header-value">{fmt(sub.recaudoComparar)}</div>
                  </div>

                  {/* Variación */}
                  <div className="header-cell">
                    <div className="header-label">Variación</div>
                    <div
                      className={`header-value ${
                        sub.variacion >= 0 ? "positive" : "negative"
                      }`}
                    >
                      {fmtPercent(sub.variacion)}
                    </div>
                  </div>

                  {/* Icono expandir */}
                  <div className="expand-icon">
                    ▼
                  </div>
                </div>

                {/* Contenido expandible */}
                <div className="subcampana-content">
                  {isExpanded && (
                    <SubcampanaDetail
                      subcampana={sub}
                      mesActual={mes}
                      anioActual={anio}
                      mesComparar={mesComparar}
                      anioComparar={anioComparar}
                      diaHabil={infoHoy.dia_habil}
                      comparacionDias={comparacionDias}
                    />
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
