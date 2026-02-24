import axios from 'axios';

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
    headers: {
        'Content-Type': 'application/json',
    },
});

export const analyticsService = {
    getStatistics: () => api.get('/api/analytics/statistics/'),
    getSeverityByDay: () => api.get('/api/analytics/severity-by-day/'),
    getHourlyCalls: () => api.get('/api/analytics/hourly/'),
};

export const incidentService = {
    getIncidents: (params) => api.get('/api/incidents/', { params }),
    predictSeverity: (data) => api.post('/api/predictions/predict/', data),
};

export default api;
