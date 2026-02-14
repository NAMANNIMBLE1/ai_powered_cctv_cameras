import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000'; // Update if your backend runs elsewhere

const api = axios.create({
  baseURL: API_BASE_URL,
});

export const fetchFactoryMetrics = () => api.get('/metrics/factory');
export const fetchWorkerMetrics = () => api.get('/metrics/workers');
export const fetchWorkstationMetrics = () => api.get('/metrics/workstations');
export const seedData = () => api.post('/seed');