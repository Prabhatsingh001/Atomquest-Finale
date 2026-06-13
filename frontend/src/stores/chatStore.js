import { create } from 'zustand';
import api from '../services/api';
import { wsService } from '../services/websocket';

export const useChatStore = create((set, get) => ({
  messages: [],
  typingUsers: {},
  isLoading: false,
  _wsUnsubscribe: null,

  loadHistory: async (sessionId) => {
    set({ isLoading: true });
    try {
      const response = await api.get(`/sessions/${sessionId}/messages`);
      set({ messages: response.data, isLoading: false });
    } catch (error) {
      console.error("Failed to load chat history", error);
      set({ isLoading: false });
    }
  },

  addMessage: (message) => {
    set((state) => {
      if (state.messages.some(m => m.id === message.id)) return state;
      return { messages: [...state.messages, message] };
    });
  },

  addSystemMessage: (content) => {
    const sysMsg = {
      id: `sys-${Date.now()}`,
      content,
      message_type: 'system',
      created_at: new Date().toISOString()
    };
    set((state) => ({ messages: [...state.messages, sysMsg] }));
  },

  setTyping: (userId, name, isTyping) => {
    set((state) => {
      const newTyping = { ...state.typingUsers };
      if (isTyping) {
        newTyping[userId] = { name: name || 'Someone', timestamp: Date.now() };
      } else {
        delete newTyping[userId];
      }
      return { typingUsers: newTyping };
    });
  },

  clearTypingStatus: () => {
    const now = Date.now();
    set((state) => {
      const newTyping = { ...state.typingUsers };
      let changed = false;
      for (const [userId, data] of Object.entries(newTyping)) {
        if (now - data.timestamp > 3000) {
          delete newTyping[userId];
          changed = true;
        }
      }
      return changed ? { typingUsers: newTyping } : state;
    });
  },

  initWebSocketListener: () => {
    if (get()._wsUnsubscribe) return;
    
    const unsubscribe = wsService.onMessage((data) => {
      if (data.type === 'chat' && data.message) {
        get().addMessage(data.message);
      } else if (data.type === 'system') {
        get().addSystemMessage(data.content);
      } else if (data.type === 'typing') {
        get().setTyping(data.user_id, data.name, data.is_typing);
      }
    });
    
    set({ _wsUnsubscribe: unsubscribe });
  },

  cleanup: () => {
    const unsubscribe = get()._wsUnsubscribe;
    if (unsubscribe) unsubscribe();
    set({ messages: [], typingUsers: {}, _wsUnsubscribe: null });
  }
}));

// Background timer to clear typing indicators
setInterval(() => {
  useChatStore.getState().clearTypingStatus();
}, 2000);
