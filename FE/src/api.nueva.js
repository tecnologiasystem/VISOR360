import axios from 'axios';

// API hardcodeada para puerto 8003 (Nueva Data)
const api = axios.create({
  baseURL: 'http://172.18.73.118:8003/api',
});

export default api;
