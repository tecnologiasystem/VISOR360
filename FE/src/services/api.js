import axios from 'axios';

export const api = axios.create({
  baseURL: 'http://172.18.73.118:8002',
});

export default api;
