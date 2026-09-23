// Servicio del modulo "Analisis Financiero" (Dashboard Unit Economics).
//
// Reutiliza el apiClient compartido (axios + interceptor JWT): NO crea una
// instancia nueva, para heredar el token y el manejo de 401 del resto de VISOR360.
//
// Assumption: ApiClient no comparte datos con SQL Server. Los endpoints leen el
// mismo Excel de siempre, embebido en VISOR360 a traves de BE/app/financiero.
import { apiClient } from './apiService';

const BASE = '/financiero';

export const financieroService = {
  // Valores validos para los selectores (negocios, monedas, periodos, meses).
  getCatalogo: () => apiClient.get(`${BASE}/catalogo`),

  // Metadatos del Excel vigente (nombre, ubicacion, fecha de actualizacion).
  getExcel: () => apiClient.get(`${BASE}/excel`),

  // Snapshot de la vista Business Unit.
  getSnapshot: (params) => apiClient.get(`${BASE}/snapshot`, { params }),

  // Vista Performance: composicion de costos, top terceros, CRxM.
  getPerformance: (params) => apiClient.get(`${BASE}/performance`, { params }),

  // Vista Budget & Goals: presupuesto mensual y anual.
  getBudget: (params) => apiClient.get(`${BASE}/budget`, { params }),

  // Sube un Excel nuevo (multipart). El backend valida las 12 hojas antes de
  // reemplazar; si falta alguna, no toca el vigente.
  subirExcel: (file) => {
    const formData = new FormData();
    formData.append('archivo', file);
    return apiClient.post(`${BASE}/upload-excel`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};

export default financieroService;
