import axios from 'axios';

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
    headers: {
        'Content-Type': 'application/json',
    },
});

// Interceptor to add JWT token to every request
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Interceptor to handle token expiration (401 errors)
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;
            try {
                const refresh = localStorage.getItem('refresh_token');
                if (refresh) {
                    const res = await axios.post(`${api.defaults.baseURL}/api/auth/token/refresh/`, { refresh });
                    const { access } = res.data;
                    localStorage.setItem('access_token', access);
                    originalRequest.headers.Authorization = `Bearer ${access}`;
                    return api(originalRequest);
                }
            } catch (refreshError) {
                // Refresh token expired or invalid - log out user
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                window.location.href = '/login';
            }
        }
        return Promise.reject(error);
    }
);

export const authService = {
    login: (credentials) => api.post('/api/auth/login/', credentials),
    register: (data) => api.post('/api/auth/register/', data), // Ready for when backend adds it
};

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

