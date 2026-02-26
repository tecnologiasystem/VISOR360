import React, { useState, useEffect } from "react";
import "./KpiTablero.css";
import dayjs from "dayjs";
import "dayjs/locale/es";
dayjs.locale("es");
import { Select, DatePicker, Button, Space, Spin, Modal, message } from "antd";
import ComparativoNPL from "./ComparativoNPL";
import SeccionCampanias from "../components/SeccionCampanias";
import SeccionIndicadores from "../components/SeccionIndicadores";
import HistoricoCumplimiento from "../components/HistoricoCumplimiento";
import { Collapse } from "antd";
import { useAuth } from "../contexts/AuthContext";
import { useDiasLaborables } from "../contexts/DiasLaborablesContext";
import { apiClient } from "../services/apiService";
import { recaudoApi } from "../services/recaudoApiService";
import api from "../api";

const { Option } = Select;

const META = {
  CLIENTES_TOTALES: { label: "Clientes asignados", agg: "last", fmt: "num" },
  CLIENTES_GESTIONABLES: { label: "Clientes con acuerdo", agg: "last", fmt: "num" },
  RECAUDO_Q: { label: "Recaudo a la fecha", agg: "sum", fmt: "num" },
  META: { label: "Meta", agg: "last", fmt: "money0" },
  CLIENTES_CONTACTADOS: { label: "Clientes contactados", agg: "sum", fmt: "num" },
  TICKET_CONTACTO: { label: "Ticket Promedio día", agg: "last", fmt: "money0" },
  ACUERDOS_Q: { label: "Total acuerdos", agg: "sum", fmt: "num" },
  ACUERDOS_DOLAR: { label: "Acuerdos $", agg: "sum", fmt: "money0" },
  TICKET_ACUERDOS: { label: "Monto Prom x Acuerdo", agg: "last", fmt: "money0" },
  EFECTIVIDAD: { label: "Efectividad", agg: "last", fmt: "percent2" },
  PLANTA: { label: "Planta", agg: "last", fmt: "num" },
};

const fmt = {
  num: (v) => (v == null ? "0" : Intl.NumberFormat('es-CO').format(v)),
  money0: (v) => v == null ? "$0" : Intl.NumberFormat('es-CO', {
    style: "currency", currency: "COP", maximumFractionDigits: 0
  }).format(v),
  percent2: (v) => v == null ? "0%" : Intl.NumberFormat('es-CO', {
    style: "percent", maximumFractionDigits: 2
  }).format(v),
};

function workdaysInMonth(d) {
  const start = d.startOf("month"), end = d.endOf("month");
  let n = 0;
  for (let cur = start; cur.isBefore(end) || cur.isSame(end, "day"); cur = cur.add(1, "day")) {
    const dow = cur.day();
    if (dow !== 0 && dow !== 6) n++;
  }
  return n;
}

function workIndexUpTo(d) {
  const start = d.startOf("month");
  let n = 0;
  for (let cur = start; cur.isBefore(d) || cur.isSame(d, "day"); cur = cur.add(1, "day")) {
    const dow = cur.day();
    if (dow !== 0 && dow !== 6) n++;
  }
  return n;
}

const KpiTablero = () => {
  const { user } = useAuth();
  const { diasRestantes: daysToGo, totalDiasLaborables } = useDiasLaborables();
  const now = dayjs();
  // Por defecto mostrar el mes actual
  const [monthState, setMonthState] = useState(now.startOf('month'));
  
  // Generar los últimos 3 meses para el selector de meses
  const ultimos3Meses = Array.from({ length: 3 }, (_, i) => 
    now.subtract(i, 'month').startOf('month')
  ).reverse();
  const [activeTab, setActiveTab] = useState("actual");
  const [campanaId, setCampanaId] = useState(user?.campanas?.[0]?.id || null);
  const [selectedMonth, setSelectedMonth] = useState("Ago");
  const [recaudoData, setRecaudoData] = useState(null);
  const [loadingRecaudo, setLoadingRecaudo] = useState(false);
  const [dailySeries, setDailySeries] = useState([]);
  const [showPowerBI, setShowPowerBI] = useState(false);
  const [metaTotal, setMetaTotal] = useState(0);
  const [tanqueData, setTanqueData] = useState({ total: 0, cantidad: 0 });
  const [loadingTanque, setLoadingTanque] = useState(false);

  // Obtener campañas del usuario
  const campanas = user?.campanas || [];
  
  // Debug: verificar qué campañas tiene el usuario
  useEffect(() => {
    console.log('🔍 Usuario completo:', user);
    console.log('🔍 Campañas del usuario:', campanas);
  }, [user, campanas]);

  // Función para cargar las metas
  const cargarMeta = async () => {
    if (!campanaId) return;
    
    const campanaSeleccionada = campanas.find(c => c.id === campanaId);
    if (!campanaSeleccionada) return;
    
    const name = campanaSeleccionada.nombre || '';
    if (/npl|acc/i.test(name)) {
      try {
        const mes = monthState.month() + 1;
        const anio = monthState.year();
        const paisName = encodeURIComponent(name);
        const response = await api.get(`/metas-campana/pais/${paisName}`, {
          params: { mes, anio }
        });
          console.log('📌 cargarMeta response for', name, response.data);
          const respData = response.data || {};

          // Helper: parse numbers robustly (handles formatted strings like '1.234.567,00')
          const parseNumber = (v) => {
            if (v == null) return 0;
            if (typeof v === 'number') return v || 0;
            if (typeof v === 'string') {
              // Remove thousand separators and convert comma-decimal to dot
              const cleaned = v.replace(/\./g, '').replace(/,/g, '.').replace(/\s+/g, '');
              const n = parseFloat(cleaned);
              return isNaN(n) ? 0 : n;
            }
            return 0;
          };

          // Prefer explicit meta_total fields; otherwise sum metas_subcampanas
          let mt = parseNumber(respData.meta_total ?? respData.meta_total_mensual ?? respData.metaTotal ?? 0);

          if ((!mt || mt === 0) && Array.isArray(respData.metas_subcampanas)) {
            const sum = respData.metas_subcampanas.reduce((acc, s) => {
              const raw = s?.meta_valor ?? s?.meta ?? s?.metaValor ?? 0;
              return acc + parseNumber(raw);
            }, 0);
            mt = sum;
            console.log('ℹ️ meta_total missing/zero, computed sum from metas_subcampanas:', mt, respData.metas_subcampanas.length);
          }

          // If still zero but there are metas under a different key, try common alternatives
          if ((!mt || mt === 0) && respData.subcampanas && Array.isArray(respData.subcampanas)) {
            const sum2 = respData.subcampanas.reduce((acc, s) => acc + parseNumber(s.total_meta || s.meta_valor || s.meta || 0), 0);
            mt = sum2;
            console.log('ℹ️ computed from respData.subcampanas fallback:', mt);
          }

          setMetaTotal(mt || 0);
      } catch (error) {
        console.error('Error al cargar meta:', error);
        setMetaTotal(0);
      }
    }
  };

  // Función para cargar el recaudo
  const cargarRecaudo = async () => {
    if (!campanaId) return;
    
    // Buscar el nombre de la campaña seleccionada
    const campanaSeleccionada = campanas.find(c => c.id === campanaId);
    if (!campanaSeleccionada) return;
    
    setLoadingRecaudo(true);
    try {
      const mes = monthState.month() + 1; // dayjs months are 0-indexed
      const anio = monthState.year();
      
      // Si es "Al día de hoy", agregar parámetro hasta_hoy=true
      const params = { mes, anio };
      if (activeTab === 'actual') {
        params.hasta_hoy = 'true';
      }
      
      // Agregar ID del usuario para filtrar por permisos
      if (user?.id) {
        params.id_usuario = user.id;
      }
      
      // If the selected campaign is a "campaign-grande" (NPL, ACC, etc.) request by country name
      const name = campanaSeleccionada.nombre || '';
      if (/npl|acc/i.test(name)) {
        const paisName = encodeURIComponent(name);
        const resp = await recaudoApi.get(`/recaudos/pais_by_name/${paisName}`, { params: { mes, anio, ...(user?.id && { id_usuario: user.id }) } });
        setRecaudoData(resp.data);
        // fetch daily series
        try {
          const resp2 = await recaudoApi.get(`/recaudos/pais_by_name/${paisName}/diario`, { params: { mes, anio } });
          setDailySeries(resp2.data || []);
        } catch (e) {
          setDailySeries([]);
        }
      } else {
        const response = await recaudoApi.get(`/recaudos/campana/${campanaSeleccionada.nombre}`, {
          params
        });
        setRecaudoData(response.data);
        setDailySeries([]);
      }
    } catch (error) {
      console.error('Error al cargar recaudo:', error);
      setRecaudoData({ recaudo_total: 0, cantidad_recaudos: 0 });
      setDailySeries([]);
    } finally {
      setLoadingRecaudo(false);
    }
  };

  // Función para cargar recaudo del tanque (sin identificar)
  const cargarTanque = async () => {
    if (!campanaId) return;
    
    const campanaSeleccionada = campanas.find(c => c.id === campanaId);
    if (!campanaSeleccionada) return;
    
    setLoadingTanque(true);
    try {
      const mes = monthState.month() + 1;
      const anio = monthState.year();
      const params = { mes, anio };
      
      if (activeTab === 'actual') {
        params.hasta_hoy = 'true';
      }
      
      const name = campanaSeleccionada.nombre || '';
      
      // Usar el endpoint de portafolio para tanque
      if (/npl|acc/i.test(name)) {
        const paisName = encodeURIComponent(name);
        const resp = await api.get(`/portafolio/tanque/pais/${paisName}`, { params });
        setTanqueData({
          total: resp.data?.total || 0,
          cantidad: resp.data?.cantidad || 0
        });
      } else {
        // Para campañas específicas, usar el endpoint por campaña
        const resp = await api.get(`/portafolio/tanque/campana/${encodeURIComponent(name)}`, { params });
        setTanqueData({
          total: resp.data?.total || 0,
          cantidad: resp.data?.cantidad || 0
        });
      }
    } catch (error) {
      console.error('Error al cargar tanque:', error);
      setTanqueData({ total: 0, cantidad: 0 });
    } finally {
      setLoadingTanque(false);
    }
  };

  // Cargar recaudo cuando cambie la campaña, el mes o el filtro de tiempo
  useEffect(() => {
    cargarRecaudo();
    cargarMeta();
    cargarTanque();
  }, [campanaId, monthState, activeTab]);

  // Escuchar eventos de actualización de metas
  useEffect(() => {
    const handleMetasActualizadas = async (event) => {
      const detail = event?.detail || {};
      console.log('🔔 Metas actualizadas, detalle:', detail);

      const paisActualizado = detail.pais;

      // Buscar si la campaña actualmente visible corresponde al país actualizado
      const campanaSeleccionada = campanas.find(c => c.id === campanaId);
      const nombreVisible = (campanaSeleccionada?.nombre || '').toUpperCase();
      const paisUpper = (paisActualizado || '').toUpperCase();

      // Si el país del evento coincide con la vista actual, recargar datos
      if (paisActualizado && nombreVisible.includes(paisUpper)) {
        try {
          // Si recibimos meta_total en el evento, usarlo directamente para evitar latencia
          if (detail.meta_total != null) {
            console.log('ℹ️ Evento trae meta_total, aplicando directamente y omitiendo recarga de metas para no sobrescribirlo');
            setMetaTotal(detail.meta_total);
          } else {
            await cargarMeta();
          }
          await cargarRecaudo();
          message.success(`Metas actualizadas para ${paisActualizado}. Datos refrescados.`);
        } catch (e) {
          console.error('Error refrescando datos tras metasActualizadas:', e);
        }
      } else if (paisActualizado) {
        // No coincide con la vista actual: avisar al usuario que hay cambios para otro país
        message.info(`Metas actualizadas para ${paisActualizado}. Selecciona esa campaña para ver los cambios.`);
        // Evitar que una recarga inválida sobrescriba un meta_total recibido en el evento
        if (detail.meta_total != null) {
          console.log('ℹ️ Evento trae meta_total para otro país; aplicando en background sin forzar recarga de metas');
          setMetaTotal(detail.meta_total);
        } else {
          cargarMeta();
        }
        cargarRecaudo();
      } else {
        // Sin detalle, recargar por seguridad
        cargarMeta();
        cargarRecaudo();
      }
    };

    window.addEventListener('metasActualizadas', handleMetasActualizadas);
    // Escuchar evento calculado desde SeccionCampanias con suma de metas por mes
    const handleMetaTotalCalculado = (event) => {
      try {
        const d = event?.detail || {};
        console.log('🔔 metaTotalCalculado received:', d);
        const pais = (d.pais || '').toString();
        const name = (campanas.find(c => c.id === campanaId)?.nombre || '').toString();
        // Si el evento corresponde a la campaña visible, aplicar el total del mes seleccionado
        if (pais && name && name.toUpperCase().includes(pais.toUpperCase())) {
          const key = `${monthState.month() + 1}_${monthState.year()}`;
          const totals = d.totals || d.totals || {};
          const value = totals[key] ?? 0;
          if (value && value > 0) {
            console.log('ℹ️ Aplicando metaTotal desde metaTotalCalculado:', value);
            setMetaTotal(value);
          }
        }
      } catch (e) {
        console.error('Error handling metaTotalCalculado:', e);
      }
    };
    window.addEventListener('metaTotalCalculado', handleMetaTotalCalculado);
    
    return () => {
      window.removeEventListener('metasActualizadas', handleMetasActualizadas);
      window.removeEventListener('metaTotalCalculado', handleMetaTotalCalculado);
    };
  }, [campanaId, monthState, campanas]);

  // Usar el recaudo real o mock si está cargando
  const recaudoActual = recaudoData?.recaudo_total || recaudoData?.total_pais || 0;

  const mockKpiData = {
    CLIENTES_TOTALES: 0, CLIENTES_GESTIONABLES: 0, RECAUDO_Q: recaudoActual,
    META: metaTotal || 0, CLIENTES_CONTACTADOS: 0, TICKET_CONTACTO: 0,
    ACUERDOS_Q: 0, ACUERDOS_DOLAR: 0, TICKET_ACUERDOS: 0,
    EFECTIVIDAD: 0.0, PLANTA: 0
  };

  // Timeline mock data (días del mes)
  // If we have a daily series from the API use it; otherwise fall back to mock
  const timelineData = (dailySeries && dailySeries.length > 0) ?
    dailySeries.map((item, idx) => ({
      day: idx + 1,
      date: dayjs(item.fecha).format('DD/MM'),
      value: item.total
    })) :
    Array.from({ length: 20 }, (_, i) => ({
      day: i + 1,
      date: monthState.date(i + 1).format("DD/MM"),
      value: Math.floor(Math.random() * 50000) + 20000
    }));

  const metaDelMes = mockKpiData.META;
  
  // Verificar si el mes seleccionado es el actual o futuro
  const mesSeleccionado = monthState.startOf('month');
  const mesActual = now.startOf('month');
  const esMesActualOFuturo = mesSeleccionado.isSame(mesActual) || mesSeleccionado.isAfter(mesActual);
  const esMesPasado = mesSeleccionado.isBefore(mesActual);
  
  // Calcular progreso usando días del contexto
  const diasTranscurridos = esMesActualOFuturo ? (totalDiasLaborables - daysToGo) : totalDiasLaborables;
  const progressRatio = totalDiasLaborables > 0 ? diasTranscurridos / totalDiasLaborables : 1;
  
  const recaudoPonderado = progressRatio > 0 
    ? recaudoActual / progressRatio
    : 0;
  const cumplimientoMeta = metaDelMes > 0 ? recaudoActual / metaDelMes : 0;

  // Calcular "por día" según el tipo de mes
  let porDiaValor = 0;
  let porDiaLabel = '';
  let diasRestantesCalculo = 0;
  
  if (esMesPasado) {
    // Mes pasado: mostrar recaudo promedio por día laborable
    porDiaValor = totalDiasLaborables > 0 ? recaudoActual / totalDiasLaborables : 0;
    porDiaLabel = `Promedio por día (${totalDiasLaborables} días):`;
    diasRestantesCalculo = 0;
  } else {
    // Mes actual o futuro: mostrar lo que falta por día
    diasRestantesCalculo = daysToGo;
    porDiaValor = diasRestantesCalculo > 0 ? (metaDelMes - recaudoActual) / diasRestantesCalculo : 0;
    porDiaLabel = `Por día (${diasRestantesCalculo} restantes):`;
  }
  
  const recaudoCard = {
    actual: recaudoActual, 
    ponderado: recaudoPonderado, 
    meta: metaDelMes,
    cumplimiento: cumplimientoMeta, 
    porDia: porDiaValor,
    porDiaLabel: porDiaLabel,
    mostrarPorDia: esMesPasado || diasRestantesCalculo > 0
  };

  // DEBUG: inspeccionar meta antes del render
  console.log('🔎 DEBUG KpiTablero metaTotal state:', metaTotal, 'type:', typeof metaTotal, 'metaDelMes (used):', metaDelMes);

  const scrollTimeline = (direction) => {
    const track = document.querySelector('.timeline-track');
    if (track) {
      const scrollAmount = 300;
      track.scrollBy({ left: direction === 'left' ? -scrollAmount : scrollAmount, behavior: 'smooth' });
    }
  };

  const scrollDays = (dir) => {
    const track = document.querySelector(".kpi-days-track");

    if (track) {
      track.scrollBy({
        left: dir === "left" ? -300 : 300,
        behavior: "smooth",
      });
    }
  };

  const { Panel } = Collapse;


  return (
    <div className="kpi-dashboard">

      {/* ===================== HEADER ===================== */}
      <div className="dashboard-header">
        <h1 className="dashboard-title">Torre de Control</h1>
        <div className="dashboard-subtitle">Monitoreo KPI, Metas, OKR y Logros</div>
      </div>

      {/* ===================== FILTROS SUPERIORES ===================== */}
      <div className="filter-bar">
        <Space size="middle" wrap align="center">
          <label>Campaña:</label>
          <Select 
            value={campanaId} 
            onChange={setCampanaId} 
            style={{ width: 200 }}
            placeholder="Seleccione una campaña"
          >
            {campanas.map((c) => (
              <Option key={c.id} value={c.id}>
                {c.nombre}
              </Option>
            ))}
          </Select>

          <label>Mes:</label>
          <DatePicker
            picker="month"
            value={monthState}
            onChange={(v) => v && setMonthState(v)}
            format="MMMM YYYY"
            allowClear={false}
          />

          {/* Acciones superiores (sin botón Tesorería — movido al menú) */}
          <div className="filter-actions" />
        </Space>
      </div>

      {/* ===================== PROGRESS BAR ===================== */}
      <div className="progress-strip">
        <div className="progress-track">
          <div className="progress-fill" style={{ width: `${progressRatio * 100}%` }} />
        </div>
      </div>

      {/* ======================================================== */}
      {/* =============== SECCIÓN PRINCIPAL DEL GRID ============= */}
      {/* ======================================================== */}

      <div className="main-grid">

        {/* Tarjeta Recaudo Principal */}
        <div className="recaudo-card kpi-card">
          <div className="recaudo-main">
            <div className="recaudo-inner">
              <div className="recaudo-label">Recaudo a la Fecha</div>
              <div className="recaudo-value">
                {loadingRecaudo ? <Spin size="small" /> : fmt.money0(recaudoCard.actual)}
              </div>
            </div>

            {/* Tarjeta Recaudo Tanque (Sin Identificar) - DENTRO DEL MAIN */}
            <div className="recaudo-inner tanque-inner">
              <div className="recaudo-label">Recaudo a la Fecha Tanque</div>
              <div className="recaudo-value">
                {loadingTanque ? <Spin size="small" /> : fmt.money0(tanqueData.total)}
              </div>
              <div className="tanque-cantidad">
                {fmt.num(tanqueData.cantidad)} recaudos sin identificar
              </div>
            </div>

            <div className="meta-box">
              <div className="meta-label">Meta del Mes</div>
              <div className="meta-value">{fmt.money0(recaudoCard.meta)}</div>
            </div>
          </div>

          <div className="recaudo-metrics">
            <div className="metric-item">
              <div className="metric-label">Cumplimiento:</div>
              <div className="metric-value" style={{ color: recaudoCard.cumplimiento >= 1 ? '#10B981' : '#F59E0B' }}>
                {fmt.percent2(recaudoCard.cumplimiento)}
              </div>
            </div>

            {recaudoCard.mostrarPorDia && (
              <div className="metric-item">
                <div className="metric-label">{recaudoCard.porDiaLabel}</div>
                <div className="metric-value">{fmt.money0(recaudoCard.porDia)}</div>
              </div>
            )}
          </div>
        </div>

      </div>
      {/* ← ← ← ESTE CIERRE ES EL QUE TE FALTABA */}

      {/* ======================================================== */}
      {/* =============== SECCIÓN KPI AVANZADO =================== */}
      {/* ======================================================== */}

      {/* ======================================================== */}
      {/* ========================= NOTA ========================= */}
      {/* ======================================================== */}


      <SeccionIndicadores />

      {/* ======================================================== */}
      {/* =============== COMPARATIVO POR DÍA HÁBIL ============== */}
      <HistoricoCumplimiento />




    </div>

  );
};

export default KpiTablero;
