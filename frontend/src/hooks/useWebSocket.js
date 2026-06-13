import { useEffect, useState, useCallback } from 'react';
import { wsService } from '../services/websocket';
import { useAuthStore } from '../stores/authStore';
import { useChatStore } from '../stores/chatStore';

export function useWebSocket(sessionId) {
  const { token } = useAuthStore();
  const [isConnected, setIsConnected] = useState(wsService.isConnected);
  const initWebSocketListener = useChatStore(state => state.initWebSocketListener);
  const cleanup = useChatStore(state => state.cleanup);

  useEffect(() => {
    if (!sessionId || !token) return;

    wsService.connect(sessionId, token);
    initWebSocketListener();

    const unsubscribe = wsService.onMessage((data) => {
      if (data.type === '_connection') {
        setIsConnected(data.status === 'connected');
      }
      if (data.type === 'recording_started') {
        alert('This session is now being recorded.');
      }
      if (data.type === 'session_ended') {
        alert('This session has ended.');
        const userStr = localStorage.getItem('atomquest-auth');
        let role = 'customer';
        try {
          if (userStr) {
             const parsed = JSON.parse(userStr);
             role = parsed.state.user?.role || 'customer';
          }
        } catch (e) {}
        
        if (role === 'agent' || role === 'admin') {
          window.location.href = '/dashboard';
        } else {
          window.location.href = '/login';
        }
      }
    });

    return () => {
      unsubscribe();
      wsService.disconnect();
      cleanup();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId, token]);

  const sendMessage = useCallback((content) => {
    wsService.sendMessage({ type: 'chat', content });
  }, []);

  const sendTyping = useCallback((isTyping = true) => {
    wsService.sendMessage({ type: 'typing', is_typing: isTyping });
  }, []);

  return { isConnected, sendMessage, sendTyping };
}
