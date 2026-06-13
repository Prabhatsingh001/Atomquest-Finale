import api from './api';

export const historyApi = {
  getHistory: async (page = 1, perPage = 20) => {
    const response = await api.get(`/sessions?status=completed&page=${page}&per_page=${perPage}`);
    return response.data;
  },
  
  getSessionDetails: async (sessionId) => {
    const response = await api.get(`/sessions/${sessionId}`);
    return response.data;
  },
  
  getSessionMessages: async (sessionId) => {
    const response = await api.get(`/sessions/${sessionId}/messages`);
    return response.data;
  }
};
