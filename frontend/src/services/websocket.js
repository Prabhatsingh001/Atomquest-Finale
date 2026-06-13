class WebSocketService {
  constructor() {
    this.ws = null;
    this.sessionId = null;
    this.token = null;
    this.listeners = [];
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectTimeoutId = null;
    this.isConnected = false;
  }

  connect(sessionId, token) {
    if (this.ws) {
      if (this.sessionId === sessionId && this.isConnected) return;
      this.disconnect();
    }

    this.sessionId = sessionId;
    this.token = token;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const url = `${protocol}//${window.location.host}/api/ws/${sessionId}?token=${token}`;
    
    try {
      this.ws = new WebSocket(url);

      this.ws.onopen = () => {
        this.isConnected = true;
        this.reconnectAttempts = 0;
        this.notifyListeners({ type: '_connection', status: 'connected' });
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.notifyListeners(data);
        } catch (e) {
          console.error("Failed to parse websocket message", e);
        }
      };

      this.ws.onclose = () => {
        this.isConnected = false;
        this.notifyListeners({ type: '_connection', status: 'disconnected' });
        this.ws = null;
        this.scheduleReconnect();
      };

      this.ws.onerror = (error) => {
        console.error("WebSocket error", error);
      };
    } catch (e) {
      console.error("Failed to initialize WebSocket", e);
      this.scheduleReconnect();
    }
  }

  scheduleReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) return;
    
    clearTimeout(this.reconnectTimeoutId);
    this.reconnectAttempts++;
    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 15000);
    
    this.reconnectTimeoutId = setTimeout(() => {
      if (this.sessionId && this.token) {
        this.connect(this.sessionId, this.token);
      }
    }, delay);
  }

  sendMessage(message) {
    if (this.ws && this.isConnected) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.error("WebSocket is not connected");
    }
  }

  onMessage(callback) {
    this.listeners.push(callback);
    return () => {
      this.listeners = this.listeners.filter(cb => cb !== callback);
    };
  }

  notifyListeners(data) {
    this.listeners.forEach(cb => cb(data));
  }

  disconnect() {
    clearTimeout(this.reconnectTimeoutId);
    this.sessionId = null;
    this.token = null;
    
    if (this.ws) {
      this.ws.onclose = null; // Prevent reconnect
      this.ws.close();
      this.ws = null;
    }
    this.isConnected = false;
    this.notifyListeners({ type: '_connection', status: 'disconnected' });
  }
}

export const wsService = new WebSocketService();
