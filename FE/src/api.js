import axios from 'axios';

// En DESARROLLO: Apunta directo a 172.17.20.121:8001/api
// En PRODUCCIÓN: IIS reverse proxy maneja /api -> backend
//const API_BASE_URL = import.meta.env.VITE_API_URL ?? 'http://172.17.20.121:8001/api'; //DESARROLLO
const API_BASE_URL = import.meta.env.VITE_API_URL ?? '/api'; // PRODUCCIÓN

const api = axios.create({
  baseURL: API_BASE_URL,
});

export default api;