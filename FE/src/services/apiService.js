import axios from 'axios';

// En DESARROLLO: Apunta directo a 172.17.20.121:8001/api
// En PRODUCCIÓN: IIS reverse proxy maneja /api -> backend
const API_BASE_URL = import.meta.env.VITE_API_URL ?? 'http://172.17.20.121:8001/api';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar token JWT
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor para manejar errores de autenticación
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Servicios por microservicio
export const kpiService = {
  getDefiniciones: () => apiClient.get('/kpi/definiciones'),
  getValores: (params) => apiClient.get('/kpi/valores', { params }),
  getMetas: (params) => apiClient.get('/kpi/metas', { params }),
  getAsignaciones: (params) => apiClient.get('/kpi/asignaciones', { params }),
};

export const financeService = {
  getBalanceScorecard: () => apiClient.get('/finance/balance-scorecard'),
  getIngresos: (params) => apiClient.get('/finance/ingresos', { params }),
  getGastos: (params) => apiClient.get('/finance/gastos', { params }),
  getPFG: () => apiClient.get('/finance/pfg'),
};

export const hrService = {
  getTalentoMetrics: () => apiClient.get('/hr/talento-metrics'),
  getEmpleados: () => apiClient.get('/hr/empleados'),
  getRotacion: () => apiClient.get('/hr/rotacion'),
};

export const areasService = {
  getAreas: () => apiClient.get('/areas'),
};

export default apiClient;
