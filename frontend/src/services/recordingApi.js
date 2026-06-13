import api from './api';

export const recordingApi = {
  startRecording: async (sessionId) => {
    const response = await api.post('/recordings/start', { session_id: sessionId });
    return response.data;
  },

  stopRecording: async (recordingId) => {
    const response = await api.post('/recordings/stop', { recording_id: recordingId });
    return response.data;
  },

  getRecording: async (recordingId) => {
    const response = await api.get(`/recordings/${recordingId}`);
    return response.data;
  },

  listSessionRecordings: async (sessionId) => {
    const response = await api.get(`/recordings/session/${sessionId}`);
    return response.data;
  }
};
