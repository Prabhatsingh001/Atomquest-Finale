import api from './api';

export const fileApi = {
  uploadFile: async (sessionId, file) => {
    const formData = new FormData();
    formData.append('session_id', sessionId);
    formData.append('file', file);
    
    // api defaults to application/json usually, but when we pass FormData, 
    // axios will automatically set Content-Type to multipart/form-data with the correct boundary.
    const response = await api.post('/uploads', formData);
    return response.data;
  },

  getSessionFiles: async (sessionId) => {
    const response = await api.get(`/uploads/session/${sessionId}`);
    return response.data;
  }
};
