import api from './api';

export const adminApi = {
  getAdminSessions: async (page = 1, perPage = 20, status = '') => {
    const params = new URLSearchParams({ page, per_page: perPage });
    if (status) params.append('status_filter', status);
    const response = await api.get(`/admin/sessions?${params.toString()}`);
    return response.data;
  },

  forceEndSession: async (sessionId) => {
    const response = await api.post('/admin/end-session', { session_id: sessionId });
    return response.data;
  },

  getMetrics: async () => {
    const response = await api.get('/admin/metrics');
    return response.data;
  }
};
