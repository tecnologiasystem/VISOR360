import React, { useState, useEffect } from "react";
import "./SeccionCampanias.css";
import { recaudoApi } from "../services/recaudoApiService";
import apiMain from "../api";
import { Spin, Tooltip, Modal, Popover } from "antd";
import { CalendarOutlined, RiseOutlined, FallOutlined, MinusOutlined, InfoCircleOutlined, LeftOutlined, RightOutlined, CheckCircleFilled } from "@ant-design/icons";
import dayjs from "dayjs";
import { useDiasLaborables } from "../contexts/DiasLaborablesContext";
import { useAuth } from "../contexts/AuthContext";

const fmt = (v) => {
  if (!v) return "$0";
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    maximumFractionDigits: 0
  }).format(v);
};

const fmtPercent = (v) => {
  if (!v && v !== 0) return "0%";
  return `${Math.round(v * 100)}%`;
};

const fmtVariacion = (v) => {
  if (!v && v !== 0) return "0%";
  const pct = Math.round(v * 100);
  return `${pct > 0 ? '+' : ''}${pct}%`;
};

// Helper: parse numbers robustly (handles formatted strings like '1.234.567,00')
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

// Mini Calendario Visual
const MiniCalendario = ({ diasHabiles, diaHabilActual, diaSeleccionado, onSelectDia, mesVista, onCambiarMes }) => {
  const diasSemana = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'];
  const fechaVista = mesVista || dayjs();
  const mesActual = fechaVista.month();
  const anioActual = fechaVista.year();
  const primerDiaMes = fechaVista.startOf('month');
  const ultimoDiaMes = fechaVista.endOf('month');
  const diasEnMes = ultimoDiaMes.date();
  const primerDiaSemana = primerDiaMes.day();

  const esMesActual = dayjs().isSame(fechaVista, 'month');
  const puedeRetroceder = fechaVista.isAfter(dayjs().subtract(6, 'months'));

  // Crear mapa de fecha -> número de día hábil
  const fechaADiaHabil = {};
  diasHabiles.forEach((dia) => {
    const fecha = dayjs(dia.fecha).format('YYYY-MM-DD');
    fechaADiaHabil[fecha] = dia.dia_habil;
  });

  // Generar todas las celdas del calendario
  const celdas = [];

  // Celdas vacías al inicio
  for (let i = 0; i < primerDiaSemana; i++) {
    celdas.push({ tipo: 'vacio', key: `vacio-${i}` });
  }

  // Días del mes
  for (let dia = 1; dia <= diasEnMes; dia++) {
    const fecha = fechaVista.date(dia);
    const fechaStr = fecha.format('YYYY-MM-DD');
    const numDiaHabil = fechaADiaHabil[fechaStr];
    const esHoy = fecha.isSame(dayjs(), 'day');
    const esFuturo = fecha.isAfter(dayjs(), 'day');
    const esSeleccionado = numDiaHabil === diaSeleccionado;
    const esHabil = !!numDiaHabil;
    const habilitado = esHabil && (esMesActual ? numDiaHabil <= diaHabilActual : true);

    celdas.push({
      tipo: 'dia',
      dia,
      fecha: fechaStr,
      numDiaHabil,
      esHoy,
      esFuturo,
      esSeleccionado,
      esHabil,
      habilitado,
      key: `dia-${dia}`
    });
  }

  return (
    <div className="mini-calendario">
      <div className="calendario-titulo">
        <button
          className="mes-nav-btn"
          onClick={() => onCambiarMes(fechaVista.subtract(1, 'month'))}
          disabled={!puedeRetroceder}
        >
          <LeftOutlined />
        </button>
        <span className="mes-nombre">{fechaVista.format('MMMM YYYY')}</span>
        <button
          className="mes-nav-btn"
          onClick={() => onCambiarMes(fechaVista.add(1, 'month'))}
          disabled={fechaVista.isSame(dayjs(), 'month') || fechaVista.isAfter(dayjs(), 'month')}
        >
          <RightOutlined />
        </button>
      </div>

      <div className="calendario-grid">
        {/* Encabezados de días de semana */}
        {diasSemana.map(d => (
          <div key={d} className="calendario-header-dia">{d}</div>
        ))}

        {/* Celdas del calendario */}
        {celdas.map(celda => {
          if (celda.tipo === 'vacio') {
            return <div key={celda.key} className="calendario-celda vacia"></div>;
          }

          const clases = ['calendario-celda'];
          if (celda.esHoy) clases.push('hoy');
          if (celda.esSeleccionado) clases.push('seleccionado');
          if (celda.esHabil) clases.push('habil');
          if (!celda.habilitado) clases.push('deshabilitado');
          if (celda.esFuturo) clases.push('futuro');

          return (
            <div
              key={celda.key}
              className={clases.join(' ')}
              onClick={() => celda.habilitado && onSelectDia(celda.numDiaHabil)}
              title={celda.esHabil ? `Día hábil ${celda.numDiaHabil}` : 'No es día hábil'}
            >
              <span className="celda-numero">{celda.dia}</span>
              {celda.esHabil && (
                <span className="celda-dia-habil">D{celda.numDiaHabil}</span>
              )}
              {celda.esSeleccionado && <CheckCircleFilled className="celda-check" />}
            </div>
          );
        })}
      </div>

      <div className="calendario-leyenda">
        <div className="leyenda-item">
          <span className="leyenda-color habil"></span>
          <span>Día hábil</span>
        </div>
        <div className="leyenda-item">
          <span className="leyenda-color seleccionado"></span>
          <span>Seleccionado</span>
        </div>
        <div className="leyenda-item">
          <span className="leyenda-color hoy"></span>
          <span>Hoy</span>
        </div>
      </div>
    </div>
  );
};

// Modal de detalle de subcampaña
const DetalleModal = ({ visible, onClose, subcampana, comparacionData, diaHabil, mesComparar, anioComparar, nombreCampana }) => {
  const monthNames = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
  const [historicoLoading, setHistoricoLoading] = React.useState(false);
  const [historicoData, setHistoricoData] = React.useState([]);

  // Usar mesComparar y anioComparar si están disponibles
  const mesActualNum = comparacionData?.mes_actual?.mes || dayjs().month() + 1;
  const anioActual = comparacionData?.mes_actual?.anio || dayjs().year();
  const mesAnteriorNum = mesComparar || (mesActualNum === 1 ? 12 : mesActualNum - 1);
  const anioAnterior = anioComparar || (mesActualNum === 1 ? anioActual - 1 : anioActual);
  const mesActualNombre = monthNames[mesActualNum - 1];
  const mesAnteriorNombre = monthNames[mesAnteriorNum - 1];

  // Función helper para buscar en el objeto por_campana de forma flexible
  const buscarValor = (dataObj, nombreBuscado) => {
    if (!dataObj?.por_campana || !nombreBuscado) return 0;

    const map = dataObj.por_campana;
    // 1. Intento exacto
    if (map[nombreBuscado] !== undefined) return map[nombreBuscado];

    // 2. Intento case-insensitive
    const nombreBuscadoUpper = nombreBuscado.toUpperCase();
    const keys = Object.keys(map);
    const keyMatch = keys.find(k => k.toUpperCase() === nombreBuscadoUpper);
    if (keyMatch) return map[keyMatch];

    // 3. Intento con alias conocidos
    if (nombreBuscadoUpper === 'PRAGROUP' || nombreBuscadoUpper === 'PRA GROUP') {
      const praKey = keys.find(k => k.toUpperCase() === 'PRA');
      if (praKey) return map[praKey];
    }

    return 0;
  };

  const recaudoActual = buscarValor(comparacionData?.mes_actual, subcampana?.nombre_campana);
  const recaudoAnterior = buscarValor(comparacionData?.mes_comparar, subcampana?.nombre_campana);
  const variacion = recaudoAnterior > 0 ? (recaudoActual - recaudoAnterior) / recaudoAnterior : 0;
  const variacionAbs = recaudoActual - recaudoAnterior;

  // Cargar histórico de días hábiles cuando se abre el modal
  React.useEffect(() => {
    const cargarHistorico = async () => {
      if (!visible || !nombreCampana || !diaHabil) return;

      setHistoricoLoading(true);
      try {
        // Calcular los 4 meses anteriores al mes comparado
        const meses = [];
        let mesTmp = mesAnteriorNum;
        let anioTmp = anioAnterior;
        for (let i = 0; i < 4; i++) {
          meses.unshift({ mes: mesTmp, anio: anioTmp });
          mesTmp = mesTmp === 1 ? 12 : mesTmp - 1;
          anioTmp = mesTmp === 12 ? anioTmp - 1 : anioTmp;
        }

        // Hacer llamadas para cada mes
        const promesas = meses.map(async ({ mes, anio }) => {
          try {
            const mesAnt = mes === 1 ? 12 : mes - 1;
            const anioAnt = mes === 1 ? anio - 1 : anio;

            const mapaNombres = {
              'ACC COL': 'ACC',
              'ACC': 'ACC',
              'NPL COL': 'NPL COL',
              'NPL PER': 'NPL PER',
              'NPL CHILE': 'NPL CHILE'
            };
            const nombreCampanaApi = mapaNombres[nombreCampana] || nombreCampana;

            const resp = await recaudoApi.get(
              `/dias-habiles/recaudo-comparativo/${encodeURIComponent(nombreCampanaApi)}`,
              {
                params: {
                  mes_actual: mes,
                  anio_actual: anio,
                  mes_comparar: mesAnt,
                  anio_comparar: anioAnt,
                  hasta_dia_habil: diaHabil
                }
              }
            );

            return {
              mes,
              anio,
              recaudo: buscarValor(resp.data?.mes_actual, subcampana?.nombre_campana)
            };
          } catch (e) {
            console.error(`Error cargando ${mes}/${anio}:`, e);
            return { mes, anio, recaudo: 0 };
          }
        });

        const resultados = await Promise.all(promesas);
        setHistoricoData(resultados);
      } catch (e) {
        console.error('Error cargando histórico:', e);
      } finally {
        setHistoricoLoading(false);
      }
    };

    cargarHistorico();
  }, [visible, nombreCampana, diaHabil, subcampana?.nombre_campana, mesAnteriorNum, anioAnterior]);

  if (!subcampana) return null;

  return (
    <Modal
      open={visible}
      onCancel={onClose}
      footer={null}
      title={
        <div className="modal-title">
          <span className="modal-campana-name">{subcampana.nombre_campana}</span>
          <span className="modal-subtitle">Comparativo por Día Hábil {diaHabil}</span>
        </div>
      }
      width={650}
      className="detalle-modal"
    >
      <div className="modal-content">
        {/* Comparación principal */}
        <div className="modal-comparacion-principal">
          <div className="modal-mes-card actual">
            <div className="mes-label">{mesActualNombre} {dayjs().year()}</div>
            <div className="mes-fecha">Corte: {comparacionData?.mes_actual?.fecha_corte || '-'}</div>
            <div className="mes-valor">{fmt(recaudoActual)}</div>
          </div>

          <div className="modal-vs">
            <div className={`variacion-grande ${variacion >= 0 ? 'positiva' : 'negativa'}`}>
              {variacion > 0 ? <RiseOutlined /> : variacion < 0 ? <FallOutlined /> : <MinusOutlined />}
              <span>{fmtVariacion(variacion)}</span>
            </div>
            <div className="variacion-absoluta">
              {variacionAbs >= 0 ? '+' : ''}{fmt(variacionAbs)}
            </div>
          </div>

          <div className="modal-mes-card anterior">
            <div className="mes-label">{mesAnteriorNombre} {anioAnterior}</div>
            <div className="mes-fecha">Corte: {comparacionData?.mes_comparar?.fecha_corte || '-'}</div>
            <div className="mes-valor">{fmt(recaudoAnterior)}</div>
          </div>
        </div>

        {/* Histórico de días hábiles - recaudo hasta día hábil N */}
        <div className="modal-historico">
          <h4>📊 Histórico hasta Día Hábil {diaHabil} (Meses Anteriores)</h4>
          {historicoLoading ? (
            <div style={{ textAlign: 'center', padding: '20px' }}>
              <Spin />
            </div>
          ) : (
            <div className="historico-grid historico-compacto">
              {historicoData.map((item, idx) => (
                <div className="historico-item-compacto" key={idx}>
                  <div className="historico-mes-compacto">
                    {monthNames[item.mes - 1]} {item.anio}
                  </div>
                  <div className="historico-valor-grande">
                    {fmt(item.recaudo)}
                  </div>
                  <div className="historico-label-dia">
                    Hasta día hábil {diaHabil}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Info adicional */}
        <div className="modal-info">
          <InfoCircleOutlined />
          <span>
            Comparación basada en día hábil {diaHabil}.
            Los días hábiles excluyen fines de semana y festivos de Colombia.
          </span>
        </div>
      </div>
    </Modal>
  );
};

export default function SeccionCampanias({ idPais, mes, anio, nombreCampana, meses, idIndicador }) {

  const { user } = useAuth();
  const [subcampanas, setSubcampanas] = useState([]);
  const [loading, setLoading] = useState(false);
  const [metasPorMes, setMetasPorMes] = useState({});


  // Estado para comparación por día hábil
  const [diaHabilInfo, setDiaHabilInfo] = useState(null);
  const [diasHabilesMes, setDiasHabilesMes] = useState([]);
  const [diaHabilSeleccionado, setDiaHabilSeleccionado] = useState(null);
  const [comparacionData, setComparacionData] = useState(null);
  const [loadingComparacion, setLoadingComparacion] = useState(false);

  // Modal de detalle
  const [modalVisible, setModalVisible] = useState(false);
  const [subcampanaSeleccionada, setSubcampanaSeleccionada] = useState(null);

  // Popover del calendario
  const [calendarioVisible, setCalendarioVisible] = useState(false);
  const [mesVistaCalendario, setMesVistaCalendario] = useState(dayjs());
  const [mesComparar, setMesComparar] = useState(null);
  const [anioComparar, setAnioComparar] = useState(null);

  const monthNames = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];

  const { getDiasFor, diasPorCampana, toggleDiaFor, resetDiasFor, calcularStats } = useDiasLaborables();

  // Si el calendario por campaña cambia en el contexto, actualizar diaHabilSeleccionado
  useEffect(() => {
    const campKey = nombreCampana || '';
    const diasCamp = getDiasFor(campKey) || [];
    if (diasCamp && diasCamp.length > 0) {
      const hoy = dayjs().format('YYYY-MM-DD');
      const diaHabilActualCtx = diasCamp.filter(d => d.activo && d.fecha <= hoy).length;
      setDiaHabilSeleccionado(diaHabilActualCtx);
    }
  }, [diasPorCampana, nombreCampana, getDiasFor]);

  // Cargar info del día hábil actual y días del mes
  useEffect(() => {
    const cargarDiaHabil = async () => {
      try {
        const resp = await recaudoApi.get('/dias-habiles/info-hoy', { params: { id_campana: idIndicador } });
        // Normalizar campos: el backend puede devolver `dia_habil` o `dia_habil_actual`
        const info = resp.data || {};
        const diaActual = info.dia_habil ?? info.dia_habil_actual ?? info.dia ?? null;
        const normalized = {
          ...info,
          dia_habil: info.dia_habil ?? info.dia_habil_actual ?? diaActual,
          dia_habil_actual: info.dia_habil_actual ?? info.dia_habil ?? diaActual,
        };
        setDiaHabilInfo(normalized);
        // Preferir calendario específico de la campaña si existe
        const campKey = nombreCampana || '';
        const diasCamp = getDiasFor(campKey) || [];
        if (diasCamp && diasCamp.length > 0) {
          const hoy = dayjs().format('YYYY-MM-DD');
          const diaHabilActualCtx = diasCamp.filter(d => d.activo && d.fecha <= hoy).length;
          if (diaHabilActualCtx > 0) {
            setDiaHabilSeleccionado(diaHabilActualCtx);
          } else {
            setDiaHabilSeleccionado(normalized.dia_habil ?? normalized.dia_habil_actual ?? null);
          }
        } else {
          setDiaHabilSeleccionado(normalized.dia_habil ?? normalized.dia_habil_actual ?? null);
        }

        // Inicializar mes a comparar como el anterior
        const mesActual = dayjs().month() + 1;
        const anioActual = dayjs().year();
        const mesAnt = mesActual === 1 ? 12 : mesActual - 1;
        const anioAnt = mesActual === 1 ? anioActual - 1 : anioActual;
        setMesComparar(mesAnt);
        setAnioComparar(anioAnt);

        // Cargar todos los días hábiles del mes actual para el calendario
        const respMes = await recaudoApi.get(`/dias-habiles/mes/${anioActual}/${mesActual}`, { params: { id_campana: idIndicador } });
        setDiasHabilesMes(respMes.data.dias || []);
      } catch (e) {
        console.error('Error cargando día hábil:', e);
        setDiaHabilInfo({ dia_habil: 8, dia_habil_actual: 8, total_dias_habiles_mes: 21 });
        setDiaHabilSeleccionado(8);
      }
    };
    cargarDiaHabil();
  }, [idIndicador]);

  // Cargar días del mes cuando cambia la vista del calendario
  useEffect(() => {
    const cargarDiasMes = async () => {
      try {
        const mes = mesVistaCalendario.month() + 1;
        const anio = mesVistaCalendario.year();
        const respMes = await recaudoApi.get(`/dias-habiles/mes/${anio}/${mes}`, { params: { id_campana: idIndicador } });
        setDiasHabilesMes(respMes.data.dias || []);
      } catch (e) {
        console.error('Error cargando días del mes:', e);
      }
    };
    cargarDiasMes();
  }, [mesVistaCalendario, idIndicador]);

  // Cargar comparación cuando cambie el día hábil seleccionado o el mes a comparar
  useEffect(() => {
    const cargarComparacion = async () => {
      if (!diaHabilSeleccionado || !nombreCampana || !mesComparar || !anioComparar) return;

      setLoadingComparacion(true);
      try {
        const mesActual = mesVistaCalendario.month() + 1;
        const anioActual = mesVistaCalendario.year();


        // Normalizar nombre de campaña para el API
        const mapaNombres = {
          'ACC COL': 'ACC',
          'ACC': 'ACC',
          'NPL COL': 'NPL COL',
          'NPL PER': 'NPL PER',
          'NPL CHILE': 'NPL CHILE'
        };
        const nombreCampanaApi = mapaNombres[nombreCampana] || nombreCampana;

        const resp = await recaudoApi.get(
          `/dias-habiles/recaudo-comparativo/${encodeURIComponent(nombreCampanaApi)}`,
          {
            params: {
              mes_actual: mesActual,
              anio_actual: anioActual,
              mes_comparar: mesComparar,
              anio_comparar: anioComparar,
              hasta_dia_habil: diaHabilSeleccionado
            }
          }
        );
        setComparacionData(resp.data);
      } catch (e) {
        console.error('Error cargando comparación:', e);
        setComparacionData(null);
      } finally {
        setLoadingComparacion(false);
      }
    };
    cargarComparacion();
  }, [diaHabilSeleccionado, nombreCampana, mesComparar, anioComparar, mesVistaCalendario]);

  // Cargar subcampañas
  useEffect(() => {
    const cargarSubcampanas = async () => {
      const months = Array.isArray(meses) && meses.length ? meses : [{ mes, anio }];
      if ((!idPais && !nombreCampana) || !months.length) return;

      setLoading(true);
      try {
        // Cargar metas para cada mes
        const metasResponses = await Promise.all(months.map(async (m) => {
          try {
            if (nombreCampana) {
              const paisName = encodeURIComponent(nombreCampana);
              const resp = await apiMain.get(`/metas-campana/pais/${paisName}`, {
                params: {
                  mes: m.mes,
                  anio: m.anio,
                  ...(user?.id && { id_usuario: user.id })
                }
              });
              return { mes: m.mes, anio: m.anio, metas: resp.data.metas_subcampanas || [] };
            }
            return { mes: m.mes, anio: m.anio, metas: [] };
          } catch (e) {
            return { mes: m.mes, anio: m.anio, metas: [] };
          }
        }));

        const metasMap = {};
        metasResponses.forEach(({ mes: m, anio: a, metas }) => {
          const key = `${m}_${a}`;
          metasMap[key] = {};
          metas.forEach((meta) => {
            const raw = meta?.meta_valor ?? meta?.meta ?? meta?.metaValor ?? 0;
            metasMap[key][meta.nombre_campana] = parseNumber(raw);
          });
        });
        // Calcular suma total de metas por mes y emitir evento para otros componentes
        const totalMetasPorMes = {};
        Object.keys(metasMap).forEach((k) => {
          const entries = Object.values(metasMap[k] || {});
          const sum = entries.reduce((acc, v) => acc + parseNumber(v), 0);
          totalMetasPorMes[k] = sum;
        });

        try {
          const eventDetail = {
            pais: nombreCampana || idPais,
            totals: totalMetasPorMes
          };
          window.dispatchEvent(new CustomEvent('metaTotalCalculado', { detail: eventDetail }));
          console.log('ℹ️ SeccionCampanias dispatched metaTotalCalculado', eventDetail);
        } catch (e) {
          console.warn('No se pudo dispatch metaTotalCalculado', e);
        }
        setMetasPorMes(metasMap);

        const responsesByMonth = await Promise.all(months.map(async (m) => {
          try {
            if (nombreCampana) {
              const paisName = encodeURIComponent(nombreCampana);
              const resp = await recaudoApi.get(`/recaudos/pais_by_name/${paisName}`, {
                params: {
                  mes: m.mes,
                  anio: m.anio,
                  id_usuario: user?.id  // Agregar id_usuario para filtrar por permisos
                }
              });
              return { mes: m.mes, anio: m.anio, data: resp.data };
            } else {
              const resp = await recaudoApi.get(`/recaudos/pais/${idPais}`, {
                params: {
                  mes: m.mes,
                  anio: m.anio,
                  id_usuario: user?.id  // Agregar id_usuario para filtrar por permisos
                }
              });
              return { mes: m.mes, anio: m.anio, data: resp.data };
            }
          } catch (e) {
            return { mes: m.mes, anio: m.anio, data: { subcampanas: [] } };
          }
        }));

        const subcampanasMap = new Map();
        responsesByMonth.forEach((monthResp, idx) => {
          const subcamps = monthResp.data?.subcampanas || [];
          subcamps.forEach((sub) => {
            const name = sub.nombre_campana || sub.nombre || sub.name || '';
            if (!subcampanasMap.has(name)) {
              subcampanasMap.set(name, new Array(months.length).fill(0));
            }
            subcampanasMap.get(name)[idx] = sub.total || sub.recaudo_total || 0;
          });
        });

        const result = Array.from(subcampanasMap.entries())
          .map(([name, totals]) => ({
            nombre_campana: name,
            totals_by_month: totals
          }))
          .filter(sub => sub.totals_by_month.some(total => total > 0));

        // Filter by user's permitted inversionistas
        let filteredResult = result;
        if (user?.inversionistas && Array.isArray(user.inversionistas) && user.inversionistas.length > 0) {
          const permittedInversionistas = new Set(
            user.inversionistas.map(inv => inv.nombre_inversionista?.toUpperCase())
          );
          console.log('🔍 Inversionistas permitidos:', Array.from(permittedInversionistas));
          console.log('📊 Subcampañas antes de filtrar:', result.map(r => r.nombre_campana));

          filteredResult = result.filter(sub => {
            const subNombre = sub.nombre_campana?.toUpperCase();
            return permittedInversionistas.has(subNombre);
          });

          console.log('✅ Subcampañas después de filtrar:', filteredResult.map(r => r.nombre_campana));
        }

        setSubcampanas(filteredResult);
      } catch (error) {
        console.error('Error al cargar subcampañas:', error);
        setSubcampanas([]);
      } finally {
        setLoading(false);
      }
    };

    cargarSubcampanas();
  }, [idPais, nombreCampana, meses, mes, anio]);

  if (loading) {
    return <div style={{ textAlign: 'center', padding: '20px' }}><Spin /></div>;
  }

  const monthsArr = Array.isArray(meses) && meses.length ? meses : [{ mes, anio }];

  const mesActualNum = dayjs().month() + 1;
  const mesAnteriorNum = mesActualNum === 1 ? 12 : mesActualNum - 1;
  const mesActualNombre = monthNames[mesActualNum - 1];
  const mesAnteriorNombre = monthNames[mesAnteriorNum - 1];

  const getComparacionSubcampana = (nombreSubcampana) => {
    if (!comparacionData) return null;

    // Función helper para buscar en el objeto por_campana de forma flexible
    const buscarValor = (dataObj, nombreBuscado) => {
      if (!dataObj?.por_campana) return 0;

      const map = dataObj.por_campana;
      // 1. Intento exacto
      if (map[nombreBuscado] !== undefined) return map[nombreBuscado];

      // 2. Intento case-insensitive
      const nombreBuscadoUpper = nombreBuscado.toUpperCase();
      const keys = Object.keys(map);
      const keyMatch = keys.find(k => k.toUpperCase() === nombreBuscadoUpper);
      if (keyMatch) return map[keyMatch];

      // 3. Intento con alias conocidos o parciales
      // PRAGROUP -> PRA
      if (nombreBuscadoUpper === 'PRAGROUP' || nombreBuscadoUpper === 'PRA GROUP') {
        const praKey = keys.find(k => k.toUpperCase() === 'PRA');
        if (praKey) return map[praKey];
      }

      return 0;
    };

    const recaudoActual = buscarValor(comparacionData.mes_actual, nombreSubcampana);
    const recaudoAnterior = buscarValor(comparacionData.mes_comparar, nombreSubcampana);
    const variacion = recaudoAnterior > 0 ? (recaudoActual - recaudoAnterior) / recaudoAnterior : 0;

    return { recaudoActual, recaudoAnterior, variacion };
  };

  const handleRowClick = (sub) => {
    setSubcampanaSeleccionada(sub);
    setModalVisible(true);
  };

  const handleSelectDiaCalendario = (numDiaHabil) => {
    // Encontrar la fecha asociada al día hábil y actualizar el calendario por campaña
    const fecha = diasHabilesMes.find(d => d.dia_habil === numDiaHabil)?.fecha;
    const campKey = nombreCampana || '';
    if (fecha) {
      toggleDiaFor(campKey, fecha);
    }
    setDiaHabilSeleccionado(numDiaHabil);
    // Actualizar mes a comparar basado en el mes vista - 1
    const mesVista = mesVistaCalendario.month() + 1;
    const anioVista = mesVistaCalendario.year();
    const mesComp = mesVista === 1 ? 12 : mesVista - 1;
    const anioComp = mesVista === 1 ? anioVista - 1 : anioVista;
    setMesComparar(mesComp);
    setAnioComparar(anioComp);
    setCalendarioVisible(false);
  };

  const handleCambiarMes = (nuevaFecha) => {
    setMesVistaCalendario(nuevaFecha);
  };

  // Encontrar la fecha del día hábil seleccionado
  const fechaSeleccionada = diasHabilesMes.find(d => d.dia_habil === diaHabilSeleccionado)?.fecha;

  return (
    <div className="campanias-wrapper">
      {/* Resumen de metas por mes (totales calculados) */}
      {/* metas-resumen removed - totals now shown in blue header boxes */}
      {/* === TITULO Y SELECTOR === */}
      <div className="campanias-header-container">
        <div className="campanias-title">Campaña</div>

        <div className="dia-habil-selector">
          <Popover
            content={
              <MiniCalendario
                diasHabiles={diasHabilesMes}
                diaHabilActual={diaHabilInfo?.dia_habil_actual || 8}
                diaSeleccionado={diaHabilSeleccionado}
                onSelectDia={handleSelectDiaCalendario}
                mesVista={mesVistaCalendario}
                onCambiarMes={handleCambiarMes}
              />
            }
            title={null}
            trigger="click"
            open={calendarioVisible}
            onOpenChange={setCalendarioVisible}
            placement="bottomRight"
          >
            <button className="calendario-trigger" disabled={loadingComparacion}>
              <CalendarOutlined style={{ color: '#f5a623', fontSize: 18 }} />
              <span className="trigger-text">
                {fechaSeleccionada
                  ? `${dayjs(fechaSeleccionada).format('DD MMM')} (Día ${diaHabilSeleccionado})`
                  : `Día hábil ${diaHabilSeleccionado ?? '-'} `
                }
              </span>
              {loadingComparacion && <Spin size="small" style={{ marginLeft: 8 }} />}
            </button>
          </Popover>

          {(() => {
            const campKey = nombreCampana || '';
            const diasCamp = getDiasFor(campKey) || [];
            if (diasCamp && diasCamp.length > 0) {
              const stats = calcularStats(diasCamp);
              const diaActual = (stats.transcurridos || 0) + 1;
              return (
                <span className="dia-habil-info">
                  Hoy: día hábil {diaActual} de {stats.total}
                </span>
              );
            }
            return diaHabilInfo ? (
              <span className="dia-habil-info">
                Hoy: día hábil {diaHabilInfo.dia_habil ?? diaHabilInfo.dia_habil_actual} de {diaHabilInfo.total_dias_habiles_mes}
              </span>
            ) : null;
          })()}
        </div>
      </div>

      {/* === ENCABEZADO CON MESES === */}
      <div className="campanias-header-row con-comparacion">
        <div className="campanias-header-spacer"></div>
        {monthsArr.map((m, idx) => (
          <div className="campanias-header-month" key={idx}>
            {monthNames[m.mes - 1]} {m.anio}
          </div>
        ))}
        <div className="campanias-header-month comparacion-header">
          📊 {mesActualNombre} vs {mesAnteriorNombre} (Día {diaHabilSeleccionado})
        </div>
      </div>

      {/* === TABLA === */}
      <div className="campanias-table">
        {subcampanas.map((sub, i) => {
          const totals = sub.totals_by_month || [];
          const comp = getComparacionSubcampana(sub.nombre_campana);

          return (
            <div
              className="campania-row con-comparacion clickable"
              key={i}
              onClick={() => handleRowClick(sub)}
            >
              <div className="campania-nombre">
                {sub.nombre_campana}
                <InfoCircleOutlined className="info-icon" />
              </div>

              {monthsArr.map((m, j) => {
                const recaudo = totals[j] || 0;
                const metaKey = `${m.mes}_${m.anio}`;
                let meta = metasPorMes[metaKey]?.[sub.nombre_campana] || 0;
                if (!meta && metasPorMes[metaKey]) {
                  const entry = Object.entries(metasPorMes[metaKey]).find(
                    ([k]) => k.toLowerCase() === sub.nombre_campana.toLowerCase()
                  );
                  meta = entry ? entry[1] : 0;
                }
                const cumplimiento = meta > 0 ? recaudo / meta : null;

                return (
                  <div className="campania-block" key={j}>
                    <span className="blue">{fmt(recaudo)}</span>
                    <span className="blue">{meta > 0 ? fmt(meta) : '-'}</span>
                    <span className="orange">{cumplimiento !== null ? fmtPercent(cumplimiento) : '-'}</span>
                  </div>
                );
              })}

              {/* COLUMNA DE COMPARACIÓN */}
              <div className="campania-block comparacion-block">
                {loadingComparacion ? (
                  <Spin size="small" />
                ) : comp ? (
                  <div className="comparacion-inline">
                    <div className="comp-valores">
                      <span className="comp-actual">{fmt(comp.recaudoActual)}</span>
                      <span className="comp-separator">vs</span>
                      <span className="comp-anterior">{fmt(comp.recaudoAnterior)}</span>
                    </div>
                    <div className={`variacion-badge ${comp.variacion >= 0 ? 'positiva' : 'negativa'}`}>
                      {comp.variacion > 0 ? <RiseOutlined /> : comp.variacion < 0 ? <FallOutlined /> : <MinusOutlined />}
                      <span>{fmtVariacion(comp.variacion)}</span>
                    </div>
                  </div>
                ) : (
                  <span className="no-data">-</span>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {comparacionData && (
        <div className="comparacion-footer">
          📅 {mesActualNombre}: {comparacionData.mes_actual?.fecha_corte} vs {mesAnteriorNombre}: {comparacionData.mes_comparar?.fecha_corte}
          <span className="footer-hint"> | Click en una campaña para más detalles</span>
        </div>
      )}

      {/* Modal de detalle */}
      <DetalleModal
        visible={modalVisible}
        onClose={() => setModalVisible(false)}
        subcampana={subcampanaSeleccionada}
        comparacionData={comparacionData}
        diaHabil={diaHabilSeleccionado}
        mesComparar={mesComparar}
        anioComparar={anioComparar}
        nombreCampana={nombreCampana}
      />
    </div>
  );
}
