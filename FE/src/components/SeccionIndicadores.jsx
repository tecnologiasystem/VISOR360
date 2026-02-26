// src/components/SeccionIndicadores.jsx

import React, { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import dayjs from "dayjs";
import { useDiasLaborables } from "../contexts/DiasLaborablesContext";
import { getRecaudoPorPais, formatPeriodo } from "../services/recaudoApiService";
import apiMain from "../api";
import "./SeccionIndicadores.css";
import { useAuth } from "../contexts/AuthContext";

// 🚀 Importamos los componentes que irán dentro del panel
import ComparativoNPL from "../pages/ComparativoNPL";
import SeccionCampanias from "./SeccionCampanias";
import VisualizacionNPL from "./VisualizacionNPL";
import RecaudoDiario from "./RecaudoDiario";


// Lista completa de indicadores/campañas disponibles en el sistema
// Los nombres deben coincidir con los de la tabla CampanasQA
const TODOS_LOS_INDICADORES = [
  { id: 1, nombre: "NPL COL", region: "COL", idPais: 10025, nombreCampana: "NPL COL" },
  { id: 2, nombre: "ACC COL", region: "COL", idPais: 10028, nombreCampana: "ACC COL" },
  { id: 3, nombre: "NPL PERU", region: "PER", idPais: null, nombreCampana: "NPL PERU" },
  { id: 4, nombre: "NPL CHILE", region: "CHI", idPais: null, nombreCampana: "NPL CHILE" },
];

// Componente interno para cada mes - Usa endpoint /recaudos/pais_by_name
const MesColumna = ({ idPais, nombreCampana, mes, anio, label, isActual, diasRestantes, onClickDias }) => {
  const { user } = useAuth();
  
  // Query al endpoint correcto de recaudo por país
  const { data: recaudoData } = useQuery({
    queryKey: ["recaudo-pais", nombreCampana, mes, anio, user?.id],
    queryFn: async () => {
      if (!nombreCampana) return null;
      const response = await getRecaudoPorPais(nombreCampana, mes, anio, user?.id);
      return response;
    },
    enabled: !!nombreCampana,
    staleTime: 5 * 60 * 1000,
    cacheTime: 10 * 60 * 1000
  });

  // El endpoint devuelve: { total_pais, subcampanas: [...] }
  const recaudoTotal = recaudoData?.total_pais || 0;
  // Obtener meta desde endpoint de metas
  const parseNumber = (v) => {
    if (v == null) return 0;
    if (typeof v === 'number') return v || 0;
    if (typeof v === 'string') {
      const cleaned = v.replace(/\./g, '').replace(/,/g, '.').replace(/\s+/g, '');
      const n = parseFloat(cleaned);
      return isNaN(n) ? 0 : n;
    }
    return 0;
  };

  const { data: metaResp } = useQuery({
    queryKey: ["meta-pais", nombreCampana, mes, anio, user?.id],
    queryFn: async () => {
      if (!nombreCampana) return null;
      try {
        const params = { mes, anio };
        if (user?.id) {
          params.id_usuario = user.id;
        }
        const resp = await apiMain.get(`/metas-campana/pais/${encodeURIComponent(nombreCampana)}`, {
          params
        });
        return resp.data;
      } catch (e) {
        return null;
      }
    },
    enabled: !!nombreCampana,
    staleTime: 5 * 60 * 1000,
    cacheTime: 10 * 60 * 1000
  });

  let metaTotal = 0;
  if (metaResp) {
    metaTotal = parseNumber(metaResp.meta_total ?? metaResp.meta_total_mensual ?? metaResp.metaTotal ?? 0);
    if ((!metaTotal || metaTotal === 0) && Array.isArray(metaResp.metas_subcampanas)) {
      metaTotal = metaResp.metas_subcampanas.reduce((acc, s) => acc + parseNumber(s?.meta_valor ?? s?.meta ?? s?.metaValor ?? 0), 0);
    }
  }
  // Escuchar evento global cuando SeccionCampanias emite el total calculado
  const [metaFromEvent, setMetaFromEvent] = React.useState(null);
  React.useEffect(() => {
    const handler = (ev) => {
      try {
        const d = ev?.detail || {};
        const totals = d.totals || {};
        const key = `${mes}_${anio}`;
        const paisEvent = (d.pais || '').toString();
        if (paisEvent && nombreCampana && nombreCampana.toUpperCase().includes(paisEvent.toUpperCase())) {
          const val = totals[key];
          if (val != null) setMetaFromEvent(val);
        }
      } catch (e) {
        // ignore
      }
    };
    window.addEventListener('metaTotalCalculado', handler);
    return () => window.removeEventListener('metaTotalCalculado', handler);
  }, [nombreCampana, mes, anio]);

  const effectiveMeta = metaFromEvent != null ? metaFromEvent : metaTotal;
  const cumplimiento = metaTotal > 0 ? (recaudoTotal / metaTotal) * 100 : 0;

  const formatCurrency = (val) => {
    return new Intl.NumberFormat("es-CO", { style: "currency", currency: "COP", minimumFractionDigits: 0 }).format(val);
  };

  return (
    <div className="indicador-columna">
      <button className={`mes-boton ${isActual ? 'active' : ''}`}>
        {label} | Meta | %Cum {isActual && diasRestantes ? `| Días: ${diasRestantes}` : ''}
      </button>
      <div className={`indicador-box ${isActual ? 'ultimo' : ''}`}>
      <span>{formatCurrency(recaudoTotal)}</span> · 
      <span>{formatCurrency(effectiveMeta)}</span> · 
      <span className="pct">{(effectiveMeta>0?((recaudoTotal/effectiveMeta)*100):0).toFixed(0)}%</span>
        {isActual && diasRestantes && (
          <span 
            className="dias" 
            onClick={onClickDias}
            style={{ cursor: "pointer", textDecoration: "underline" }}
            title="Click para editar días laborables"
          >
            | {diasRestantes}
          </span>
        )}
      </div>
    </div>
  );
};


const SeccionIndicadores = () => {
  const { user } = useAuth();
  const [openIds, setOpenIds] = useState([]); 
  const [mesesSeleccionados, setMesesSeleccionados] = useState([0, 1, 2]); 
  const [mostrarFiltros, setMostrarFiltros] = useState(true); 
  // Modificado: estado del calendario incluye viewDate para navegar meses
  const [mostrarCalendario, setMostrarCalendario] = useState({ 
    visible: false, 
    campaignId: null, 
    campaignName: null,
    viewDate: dayjs() // Fecha del mes que se está visualizando
  });

  // Filtrar indicadores según las campañas asignadas al usuario
  const indicadores = useMemo(() => {
    const campanasUsuario = user?.campanas || [];
    
    // Debug: ver qué campañas tiene el usuario
    console.log('🔍 SeccionIndicadores - Usuario completo:', user);
    console.log('🔍 SeccionIndicadores - Campañas del usuario:', campanasUsuario);
    
    // Si el usuario no tiene campañas asignadas, no mostrar nada
    if (campanasUsuario.length === 0) {
      console.log('⚠️ Usuario sin campañas asignadas');
      return [];
    }
    
    // Crear un Set de nombres de campañas del usuario (normalizados)
    const campanasPermitidas = new Set(
      campanasUsuario.map(c => (c.nombre || '').toUpperCase().trim())
    );
    
    console.log('🔍 Campañas permitidas (Set):', Array.from(campanasPermitidas));
    
    // Filtrar los indicadores - coincidencia EXACTA
    const indicadoresFiltrados = TODOS_LOS_INDICADORES.filter(indicador => {
      const nombreIndicador = (indicador.nombreCampana || indicador.nombre || '').toUpperCase().trim();
      const tienePermiso = campanasPermitidas.has(nombreIndicador);
      
      console.log(`📋 Indicador "${indicador.nombre}" (${nombreIndicador}): ${tienePermiso ? '✅ PERMITIDO' : '❌ NO PERMITIDO'}`);
      return tienePermiso;
    });
    
    console.log('🎯 Indicadores filtrados finales:', indicadoresFiltrados.map(i => i.nombre));
    return indicadoresFiltrados;
  }, [user?.campanas]);

  const { 
    getDiasFor,
    toggleDiaFor,
    resetDiasFor,
    calcularStats
  } = useDiasLaborables();

  const meses = useMemo(() => {
    const now = dayjs();
    return [
      { 
        mes: now.subtract(2, 'month').month() + 1, 
        anio: now.subtract(2, 'month').year(), 
        label: now.subtract(2, 'month').format('MMM').toLowerCase(), 
        isActual: false 
      },
      { 
        mes: now.subtract(1, 'month').month() + 1, 
        anio: now.subtract(1, 'month').year(), 
        label: now.subtract(1, 'month').format('MMM').toLowerCase(), 
        isActual: false 
      },
      { 
        mes: now.month() + 1, 
        anio: now.year(), 
        label: now.format('MMM').toLowerCase(), 
        isActual: true 
      },
      { // Futuro (próximo mes) para habilitar cálculo si fuera necesario
        mes: now.add(1, 'month').month() + 1,
        anio: now.add(1, 'month').year(),
        label: now.add(1, 'month').format('MMM').toLowerCase(),
        isActual: false 
      }
    ];
  }, []);

  const mesesAMostrar = mesesSeleccionados.map(idx => meses[idx]).filter(Boolean);

  const toggle = (id) => {
    setOpenIds((prev) => 
      prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
    );
  };

  const toggleMes = (idx) => {
    setMesesSeleccionados(prev => 
      prev.includes(idx) ? prev.filter(i => i !== idx) : [...prev, idx].sort()
    );
  };

  // Helper para navegar mes en modal
  const changeModalMonth = (direction) => {
    setMostrarCalendario(prev => ({
      ...prev,
      viewDate: prev.viewDate.add(direction, 'month')
    }));
  };

  return (
    <div className="indicadores-wrapper" style={{ zoom: "0.8" }}>

      {/* Botón Filtros UI... (sin cambios) */}
      {!mostrarFiltros && (
        <button onClick={() => setMostrarFiltros(true)} style={{ position: "fixed", left: "20px", top: "120px", backgroundColor: "#003087", color: "white", border: "none", borderRadius: "8px", padding: "12px 16px", cursor: "pointer", fontSize: "14px", fontWeight: 600, boxShadow: "0 2px 8px rgba(0,0,0,0.2)", zIndex: 100 }}>
          📅 Mostrar Filtros
        </button>
      )}

      {mostrarFiltros && (
        <div style={{ position: "fixed", left: "20px", top: "120px", backgroundColor: "white", padding: "20px", borderRadius: "12px", boxShadow: "0 2px 8px rgba(0,0,0,0.1)", border: "1px solid #e5e7eb", zIndex: 100, width: "200px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
            <div style={{ fontWeight: 600, color: "#003087", fontSize: "14px" }}>Seleccionar meses</div>
            <button onClick={() => setMostrarFiltros(false)} style={{ backgroundColor: "transparent", border: "none", fontSize: "18px", cursor: "pointer", color: "#6b7280", padding: "0", lineHeight: "1" }} title="Ocultar filtros">✕</button>
          </div>
          {meses.slice(0, 3).map((m, idx) => ( // Solo mostrar los 3 primeros en filtro
            <label key={idx} style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "12px", cursor: "pointer", fontSize: "14px", color: "#1f2937" }}>
              <input type="checkbox" checked={mesesSeleccionados.includes(idx)} onChange={() => toggleMes(idx)} style={{ cursor: "pointer", accentColor: "#003087" }} />
              {m.label} {m.anio}
            </label>
          ))}
        </div>
      )}

      <div style={{ marginLeft: "0px" }}>
      {indicadores.map((item) => (
        <div key={item.id} className="indicador-container">
          <div className="indicador-main-row">
            <div className="indicador-badge" onClick={() => toggle(item.id)} style={{ cursor: "pointer" }}>
              <span className={`icon ${openIds.includes(item.id) ? "open" : ""}`}>▲</span> {item.nombre}
            </div>

            {(() => {
              const campKey = item.nombreCampana || item.nombre;
              // Pasamos el ID y la fecha actual para obtener stats del mes en curso
              const diasCamp = getDiasFor(item.id, dayjs()) || [];
              const stats = calcularStats(diasCamp); // Stats del mes actual por defecto
              
              return mesesAMostrar.map((m, idx) => (
                <MesColumna 
                  key={`${item.id}-${m.mes}-${m.anio}`}
                  idPais={item.idPais}
                  nombreCampana={campKey}
                  mes={m.mes}
                  anio={m.anio}
                  label={m.label}
                  isActual={m.isActual}
                  diasRestantes={m.isActual ? stats.diasRestantes : null}
                  onClickDias={() => setMostrarCalendario({ 
                    visible: true, 
                    campaignId: item.id, 
                    campaignName: campKey,
                    viewDate: dayjs() // Inicia en mes actual
                  })}
                />
              ));
            })()}
          </div>

          {openIds.includes(item.id) && (
            <div className="indicador-panel full-width-panel animate-panel">
               {/* Pasar props necesarios a subs */}
               {/* ... componentes internos ... */}
               <SeccionCampanias 
                 idPais={item.idPais} 
                 nombreCampana={item.nombreCampana || item.nombre}
                 idIndicador={item.id}
                 mes={meses[2].mes}
                 anio={meses[2].anio}
                 meses={mesesAMostrar}
               />

               <div className="chart-wrapper" style={{ marginTop: "20px" }}>
                 <ComparativoNPL nombreCampana={item.nombreCampana || item.nombre} />
               </div>
            </div>
          )}
        </div>
      ))}
      </div>

      {/* Modal de Calendario */}
      {mostrarCalendario.visible && (
        <div 
          style={{ position: "fixed", top: 0, left: 0, right: 0, bottom: 0, backgroundColor: "rgba(0,0,0,0.5)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000 }}
          onClick={() => setMostrarCalendario({ visible: false, campaignId: null, campaignName: null, viewDate: dayjs() })}
        >
          <div 
            style={{ backgroundColor: "white", borderRadius: "16px", padding: "24px", maxWidth: "600px", maxHeight: "80vh", overflowY: "auto", boxShadow: "0 4px 24px rgba(0,0,0,0.2)" }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                <button onClick={() => changeModalMonth(-1)} style={{ border:"none", background:"transparent", cursor:"pointer", fontSize:"18px" }}>◀</button>
                <h3 style={{ margin: 0, color: "#003087", fontSize: "18px", fontWeight: 600 }}>
                  {mostrarCalendario.viewDate.format("MMMM YYYY")} - {mostrarCalendario.campaignName}
                </h3>
                <button onClick={() => changeModalMonth(1)} style={{ border:"none", background:"transparent", cursor:"pointer", fontSize:"18px" }}>▶</button>
              </div>
              <button 
                onClick={() => setMostrarCalendario({ visible: false, campaignId: null, campaignName: null, viewDate: dayjs() })}
                style={{ backgroundColor: "transparent", border: "none", fontSize: "24px", cursor: "pointer", color: "#6b7280", padding: "0", lineHeight: "1" }}
              >✕</button>
            </div>

            <p style={{ color: "#6b7280", fontSize: "14px", marginBottom: "20px" }}>
              Selecciona los días laborables. Navega entre meses con las flechas.
            </p>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(7, 1fr)", gap: "8px", textAlign: "center", fontSize: "12px", fontWeight: "bold", color: "#6b7280", marginBottom: "4px" }}>
              <div>Dom</div><div>Lun</div><div>Mar</div><div>Mié</div><div>Jue</div><div>Vie</div><div>Sáb</div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(7, 1fr)", gap: "8px" }}>
              {/* Obtiene días del mes visualizado */}
              {getDiasFor(mostrarCalendario.campaignId, mostrarCalendario.viewDate).map((dia, idx) => {
                // Rellenar huecos si el mes no empieza en domingo?
                // getDiasFor debería retornar días del mes. Si faltan placeholders, el CSS grid los acomoda si usamos col-start?
                // Simplificación: renderizamos botones directos.
                // Si dia.fecha no coincide con grid, podría descuadrar. 
                // Mejor: iterar días del mes calendario completo incluyendo placeholders vacíos si es necesario.
                // Pero por ahora confiamos en que getDiasFor devuelve lista completa secuencial.
                
                const esHoy = dia.fecha === dayjs().format("YYYY-MM-DD");
                
                // Hack para grid start si es el primer día
                const styleExtra = idx === 0 ? { gridColumnStart: dayjs(dia.fecha).day() + 1 } : {};

                return (
                  <button
                    key={dia.fecha}
                    onClick={() => toggleDiaFor(mostrarCalendario.campaignId, dia.fecha)}
                    style={{
                      ...styleExtra,
                      padding: "10px 4px",
                      borderRadius: "8px",
                      border: esHoy ? "2px solid #003087" : dia.activo ? "2px solid #10b981" : "2px solid #e5e7eb",
                      backgroundColor: dia.activo ? (esHoy ? "#003087" : "#10b981") : "white",
                      color: dia.activo ? "white" : "#6b7280",
                      cursor: "pointer",
                      fontSize: "12px",
                      fontWeight: esHoy ? 600 : dia.activo ? 500 : 400,
                      transition: "all 0.2s",
                      textAlign: "center"
                    }}
                    title={dia.activo ? "Click para desactivar" : "Click para activar"}
                  >
                    <div>{dayjs(dia.fecha).format("D")}</div>
                  </button>
                );
              })}

            </div>

            <div style={{ marginTop: "20px", padding: "16px", backgroundColor: "#f3f4f6", borderRadius: "8px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <div style={{ fontSize: "14px", color: "#6b7280", marginBottom: "4px" }}>Días laborables (este mes):</div>
                <div style={{ fontSize: "24px", fontWeight: 700, color: "#003087" }}>
                  {calcularStats(getDiasFor(mostrarCalendario.campaignId, mostrarCalendario.viewDate)).total} días
                </div>
              </div>
              <button
                onClick={() => resetDiasFor(mostrarCalendario.campaignId, mostrarCalendario.viewDate)}
                style={{ padding: "10px 16px", backgroundColor: "#003087", color: "white", border: "none", borderRadius: "8px", cursor: "pointer", fontSize: "14px", fontWeight: 500 }}
              >
                Resetear (L-V)
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};

export default SeccionIndicadores;

