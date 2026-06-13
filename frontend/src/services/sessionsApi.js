import api from './api';

export const sessionsApi = {
  createSession: async (title) => {
    const response = await api.post('/sessions', { title });
    return response.data;
  },
  
  listSessions: async (page = 1, perPage = 20) => {
    const response = await api.get(`/sessions?page=${page}&per_page=${perPage}`);
    return response.data;
  },
  
  getSession: async (id) => {
    const response = await api.get(`/sessions/${id}`);
    return response.data;
  },
  
  getJoinLink: async (id) => {
    const response = await api.get(`/sessions/${id}/link`);
    return response.data;
  },
  
  agentJoin: async (id) => {
    const response = await api.post(`/participants/session/${id}/join`);
    return response.data;
  },
  
  customerJoin: async (token, name) => {
    const response = await api.post(`/participants/join/${token}`, { name });
    return response.data;
  },

  endSession: async (id) => {
    const response = await api.post(`/sessions/${id}/end`);
    return response.data;
  },

  downloadArchive: async (id) => {
    // We use responseType 'blob' to handle binary file downloads
    const response = await api.get(`/sessions/${id}/archive`, {
      responseType: 'blob',
    });
    return response.data;
  }
};
