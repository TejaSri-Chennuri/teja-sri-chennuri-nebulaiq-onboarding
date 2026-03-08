import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

// Attach token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('zentra_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('zentra_token');
      localStorage.removeItem('zentra_user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ─── Auth ────────────────────────────────────────────────────────────────────
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (email, password) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    return axios.post(`${API_BASE}/auth/login`, formData);
  },
  getMe: () => api.get('/auth/me'),
  updateProfile: (data) => api.put('/auth/me', data),
  gmailAuthorize: () => api.get('/auth/gmail/authorize'),
};

// ─── Subscriptions ───────────────────────────────────────────────────────────
export const subscriptionAPI = {
  list: (params) => api.get('/subscriptions', { params }),
  get: (id) => api.get(`/subscriptions/${id}`),
  create: (data) => api.post('/subscriptions', data),
  update: (id, data) => api.put(`/subscriptions/${id}`, data),
  delete: (id) => api.delete(`/subscriptions/${id}`),
  cancel: (id) => api.post(`/subscriptions/${id}/cancel`),
  logUsage: (id, data) => api.post(`/subscriptions/${id}/log-usage`, data),
  scanGmail: () => api.post('/subscriptions/scan/gmail'),
  scanBank: () => api.post('/subscriptions/scan/bank'),
};

// ─── Analytics ───────────────────────────────────────────────────────────────
export const analyticsAPI = {
  dashboard: () => api.get('/analytics/dashboard'),
  summary: () => api.get('/analytics/summary'),
  categoryBreakdown: () => api.get('/analytics/category-breakdown'),
  monthlyTrend: (months) => api.get('/analytics/monthly-trend', { params: { months } }),
  upcomingRenewals: (days) => api.get('/analytics/upcoming-renewals', { params: { days } }),
  savingsPotential: () => api.get('/analytics/savings-potential'),
  recommendations: () => api.get('/analytics/recommendations'),
  insights: () => api.get('/analytics/insights'),
};

// ─── Notifications ───────────────────────────────────────────────────────────
export const notificationAPI = {
  list: (params) => api.get('/notifications', { params }),
  unreadCount: () => api.get('/notifications/unread-count'),
  markRead: (id) => api.put(`/notifications/${id}/read`),
  markAllRead: () => api.put('/notifications/mark-all-read'),
  getPreferences: () => api.get('/notifications/preferences'),
  updatePreferences: (data) => api.put('/notifications/preferences', data),
};

export default api;
