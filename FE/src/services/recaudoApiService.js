/**
 * API Service para Recaudo Meta (microservicio puerto 8001)
 * Este servicio conecta con el backend de metas y recaudo por campaña e inversionista
 * 
 * En DESARROLLO: Apunta directo a localhost:8001
 * En PRODUCCIÓN: IIS reverse proxy maneja la redirección (usar VITE_RECAUDO_API_URL vacío)
 */
import axios from 'axios';

// En desarrollo apuntamos directo al BE.
// En producción preferimos usar una URL relativa ('/api') para pasar por el proxy HTTPS (IIS)
// Dejar VITE_RECAUDO_API_URL vacío o no definido hará que use la ruta relativa.
const RECAUDO_API_URL = import.meta.env.VITE_RECAUDO_API_URL || 'https://visor360.systemgroupglobal.com:8443/api';

const recaudoApi = axios.create({
  baseURL: RECAUDO_API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para logging en desarrollo
recaudoApi.interceptors.request.use(
  (config) => {
    if (import.meta.env.DEV) {
      console.log(`[RecaudoAPI] ${config.method?.toUpperCase()} ${config.url}`, config.params || '');
    }
    return config;
  },
  (error) => Promise.reject(error)
);

recaudoApi.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('[RecaudoAPI] Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// ==================== CAMPAÑAS ====================

/**
 * Obtener todas las campañas
 */
export const getCampanas = async () => {
  const response = await recaudoApi.get('/campanas/');
  return response.data;
};

/**
 * Obtener campaña por ID
 */
export const getCampanaById = async (idCampana) => {
  const response = await recaudoApi.get(`/campanas/${idCampana}`);
  return response.data;
};

/**
 * Obtener campañas con sus inversionistas
 */
export const getCampanasConInversionistas = async () => {
  const response = await recaudoApi.get('/campanas/con-inversionistas/');
  return response.data;
};

// ==================== INVERSIONISTAS ====================

/**
 * Obtener todos los inversionistas
 */
export const getInversionistas = async (soloActivos = true) => {
  const response = await recaudoApi.get('/inversionistas/', {
    params: { solo_activos: soloActivos }
  });
  return response.data;
};

/**
 * Obtener inversionistas por campaña
 */
export const getInversionistasPorCampana = async (idCampana, soloActivos = true) => {
  const response = await recaudoApi.get(`/inversionistas/por-campana/${idCampana}`, {
    params: { solo_activos: soloActivos }
  });
  return response.data;
};

// ==================== RECAUDO ====================

/**
 * Obtener recaudo diario (para gráficos)
 * Usa SP_CampanasRecaudoQA_ConsultaFE con TipoResumen=1
 * 
 * @param {Object} params - Parámetros de filtro
 * @param {number} params.idCampana - ID de campaña (opcional)
 * @param {number} params.idInversionista - ID de inversionista (opcional)
 * @param {string} params.anioMes - Periodo específico YYYY-MM (opcional)
 * @param {string} params.anioMesDesde - Periodo desde YYYY-MM (opcional)
 * @param {string} params.anioMesHasta - Periodo hasta YYYY-MM (opcional)
 */
export const getRecaudoDiario = async (params = {}) => {
  const response = await recaudoApi.get('/recaudo/diario', {
    params: {
      id_campana: params.idCampana,
      id_inversionista: params.idInversionista,
      anio_mes: params.anioMes,
      anio_mes_desde: params.anioMesDesde,
      anio_mes_hasta: params.anioMesHasta,
      solo_activos: params.soloActivos ?? true
    }
  });
  return response.data;
};

/**
 * Obtener recaudo mensual/diario (para gráficos)
 * Usa endpoint /calculo/recaudo/por-mes
 */
export const getRecaudoMensual = async (params = {}) => {
  const response = await recaudoApi.get('/calculo/recaudo/por-mes');
  return response.data;
};

/**
 * Obtener recaudo por país y mes (para indicadores principales)
 * Usa endpoint /recaudos/pais_by_name/{pais_name}
 * 
 * @param {string} paisName - Nombre del país (NPL COL, ACC, etc.)
 * @param {number} mes - Mes (1-12)
 * @param {number} anio - Año
 * @returns {Object} { id_pais, mes, anio, total_pais, cantidad_pais, subcampanas, modo }
 */
export const getRecaudoPorPais = async (paisName, mes, anio, id_usuario = null) => {
  const params = { mes, anio };
  if (id_usuario) {
    params.id_usuario = id_usuario;
  }
  const response = await recaudoApi.get(`/recaudos/pais_by_name/${encodeURIComponent(paisName)}`, {
    params
  });
  return response.data;
};

/**
 * Obtener resumen por campaña para un mes
 */
export const getResumenPorCampana = async (anioMes, idCampana = null) => {
  const response = await recaudoApi.get('/recaudo/resumen/por-campana', {
    params: { anio_mes: anioMes, id_campana: idCampana }
  });
  return response.data;
};

/**
 * Obtener resumen por inversionista para un mes
 */
export const getResumenPorInversionista = async (anioMes, idCampana = null) => {
  const response = await recaudoApi.get('/recaudo/resumen/por-inversionista', {
    params: { anio_mes: anioMes, id_campana: idCampana }
  });
  return response.data;
};

/**
 * Obtener acumulado diario (para gráficos de línea)
 */
export const getAcumuladoDiario = async (anioMes, idCampana = null, idInversionista = null) => {
  const response = await recaudoApi.get('/recaudo/acumulado-diario', {
    params: {
      anio_mes: anioMes,
      id_campana: idCampana,
      id_inversionista: idInversionista
    }
  });
  return response.data;
};

// ==================== CARGAS ====================

/**
 * Ejecutar carga desde staging
 */
export const ejecutarCargaDesdeStaging = async (datos) => {
  const response = await recaudoApi.post('/recaudo/carga-excel', datos);
  return response.data;
};

/**
 * Obtener historial de cargas
 */
export const getHistorialCargas = async (params = {}) => {
  const response = await recaudoApi.get('/cargas/', {
    params: {
      id_usuario: params.idUsuario,
      fecha_desde: params.fechaDesde,
      fecha_hasta: params.fechaHasta,
      limite: params.limite || 100
    }
  });
  return response.data;
};

/**
 * Obtener auditoría de cambios
 */
export const getAuditoria = async (params = {}) => {
  const response = await recaudoApi.get('/cargas/auditoria/', {
    params: {
      id_recaudo: params.idRecaudo,
      id_carga: params.idCarga,
      fecha_desde: params.fechaDesde,
      fecha_hasta: params.fechaHasta,
      limite: params.limite || 100
    }
  });
  return response.data;
};

// ==================== HELPERS ====================

/**
 * Mapeo de nombres de campaña del FE a IDs del backend
 * Ajustar según los IDs reales de la BD
 */
export const CAMPANA_MAP = {
  'NPL COL': 1,
  'ACC': 2,
  'ACC COL': 2,
  'NPL PER': 3,
  'NPL PERU': 3,
  'NPL CHILE': 4,
};

/**
 * Obtener ID de campaña por nombre
 */
export const getCampanaIdByName = (nombre) => {
  return CAMPANA_MAP[nombre] || null;
};

/**
 * Formatear periodo YYYY-MM desde mes y año
 */
export const formatPeriodo = (mes, anio) => {
  return `${anio}-${String(mes).padStart(2, '0')}`;
};

/**
 * Health check del servicio
 */
export const healthCheck = async () => {
  const response = await recaudoApi.get('/health');
  return response.data;
};

// ==================== DÍAS HÁBILES ====================

/**
 * Obtener información del día hábil actual
 * Retorna: fecha, dia_habil, total_dias_habiles_mes, dias_habiles_restantes, festivos_mes
 */
export const getInfoDiaHabilActual = async () => {
  const response = await recaudoApi.get('/dias-habiles/info-hoy');
  return response.data;
};

/**
 * Obtener días hábiles de un mes
 */
export const getDiasHabilesMes = async (anio, mes) => {
  const response = await recaudoApi.get(`/dias-habiles/mes/${anio}/${mes}`);
  return response.data;
};

/**
 * Obtener festivos de un año
 */
export const getFestivosAnio = async (anio) => {
  const response = await recaudoApi.get(`/dias-habiles/festivos/${anio}`);
  return response.data;
};

/**
 * Comparar días hábiles entre dos meses
 * Retorna el mapeo de días hábiles entre ambos meses
 */
export const compararDiasHabiles = async (mesActual, anioActual, mesComparar, anioComparar, hastaDiaHabil = null) => {
  const params = {
    mes_actual: mesActual,
    anio_actual: anioActual,
    mes_comparar: mesComparar,
    anio_comparar: anioComparar
  };
  if (hastaDiaHabil) {
    params.hasta_dia_habil = hastaDiaHabil;
  }
  const response = await recaudoApi.get('/dias-habiles/comparar', { params });
  return response.data;
};

/**
 * Obtener recaudo comparativo por día hábil entre dos meses
 * Compara el recaudo acumulado hasta el día hábil N en ambos meses
 */
export const getRecaudoComparativoDiaHabil = async (pais, mesActual, anioActual, mesComparar, anioComparar, hastaDiaHabil = null) => {
  const params = {
    mes_actual: mesActual,
    anio_actual: anioActual,
    mes_comparar: mesComparar,
    anio_comparar: anioComparar
  };
  if (hastaDiaHabil) {
    params.hasta_dia_habil = hastaDiaHabil;
  }
  const response = await recaudoApi.get(`/dias-habiles/recaudo-comparativo/${encodeURIComponent(pais)}`, { params });
  return response.data;
};

/**
 * Obtener recaudo detallado por día hábil para graficar comparativas
 */
export const getRecaudoComparativoDetallado = async (pais, mesActual, anioActual, mesComparar, anioComparar) => {
  const params = {
    mes_actual: mesActual,
    anio_actual: anioActual,
    mes_comparar: mesComparar,
    anio_comparar: anioComparar
  };
  const response = await recaudoApi.get(`/dias-habiles/recaudo-comparativo-detallado/${encodeURIComponent(pais)}`, { params });
  return response.data;
};

// Export named para compatibilidad
export { recaudoApi };

export default recaudoApi;
