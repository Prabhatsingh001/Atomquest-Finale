import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export const useSessionStore = create(
  persist(
    (set) => ({
      sessions: [],
      activeSession: null,
      joinLink: null,
      
      setSessions: (sessions) => set({ sessions }),
      addSession: (session) => set((state) => ({ sessions: [session, ...state.sessions] })),
      setActiveSession: (session) => set({ activeSession: session }),
      setJoinLink: (joinLink) => set({ joinLink }),
      clearActiveSession: () => set({ activeSession: null, joinLink: null }),
    }),
    {
      name: 'session-storage',
      partialize: (state) => ({ activeSession: state.activeSession }),
    }
  )
)
