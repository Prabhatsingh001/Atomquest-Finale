import { create } from 'zustand';
import { recordingApi } from '../services/recordingApi';

export const useRecordingStore = create((set, get) => ({
  isRecording: false,
  recordingId: null,
  duration: 0,
  timerInterval: null,

  startRecording: async (sessionId) => {
    try {
      const response = await recordingApi.startRecording(sessionId);
      
      const timer = setInterval(() => {
        set((state) => ({ duration: state.duration + 1 }));
      }, 1000);

      set({
        isRecording: true,
        recordingId: response.id,
        duration: 0,
        timerInterval: timer,
      });
      return response;
    } catch (error) {
      console.error('Failed to start recording', error);
      throw error;
    }
  },

  stopRecording: async () => {
    const { recordingId, timerInterval } = get();
    if (!recordingId) return;

    try {
      const response = await recordingApi.stopRecording(recordingId);
      
      if (timerInterval) clearInterval(timerInterval);

      set({
        isRecording: false,
        recordingId: null,
        duration: 0,
        timerInterval: null,
      });
      return response;
    } catch (error) {
      console.error('Failed to stop recording', error);
      throw error;
    }
  },
}));
