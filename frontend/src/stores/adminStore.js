import { create } from 'zustand';
import { adminApi } from '../services/adminApi';

export const useAdminStore = create((set) => ({
  sessions: [],
  metrics: null,
  isLoading: false,

  fetchSessions: async (page = 1, perPage = 20, status = '') => {
    set({ isLoading: true });
    try {
      const data = await adminApi.getAdminSessions(page, perPage, status);
      set({ sessions: data, isLoading: false });
    } catch (error) {
      console.error('Failed to fetch admin sessions', error);
      set({ isLoading: false });
    }
  },

  fetchMetrics: async () => {
    try {
      const data = await adminApi.getMetrics();
      set({ metrics: data });
    } catch (error) {
      console.error('Failed to fetch admin metrics', error);
    }
  },

  forceEndSession: async (sessionId) => {
    try {
      await adminApi.forceEndSession(sessionId);
      // Immediately remove from sessions or update status
      set((state) => ({
        sessions: state.sessions.map((s) => 
          s.id === sessionId ? { ...s, status: 'completed' } : s
        )
      }));
    } catch (error) {
      console.error('Failed to force end session', error);
      throw error;
    }
  }
}));
