import { useRoomContext } from '@livekit/components-react';
import { ConnectionState } from 'livekit-client';
import { useEffect, useState } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';

export default function ConnectionStatus({ sessionId }) {
  const room = useRoomContext();
  const [livekitState, setLivekitState] = useState(room.state);
  const { isConnected: wsConnected } = useWebSocket(sessionId);

  useEffect(() => {
    const handleStateChange = (state) => setLivekitState(state);
    room.on('connected', () => handleStateChange(ConnectionState.Connected));
    room.on('disconnected', () => handleStateChange(ConnectionState.Disconnected));
    room.on('reconnecting', () => handleStateChange(ConnectionState.Reconnecting));
    
    return () => {
      room.off('connected', handleStateChange);
      room.off('disconnected', handleStateChange);
      room.off('reconnecting', handleStateChange);
    };
  }, [room]);

  let status = 'connected';
  let colorClass = 'bg-green-500';
  let text = 'Connected';

  if (livekitState === ConnectionState.Reconnecting || !wsConnected) {
    status = 'reconnecting';
    colorClass = 'bg-yellow-500 animate-pulse';
    text = 'Reconnecting...';
  } else if (livekitState === ConnectionState.Disconnected) {
    status = 'disconnected';
    colorClass = 'bg-red-500';
    text = 'Disconnected';
  }

  return (
    <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-800/80 rounded-full border border-slate-700/50 backdrop-blur-sm">
      <div className={`w-2.5 h-2.5 rounded-full ${colorClass}`} />
      <span className="text-xs font-medium text-slate-200">{text}</span>
    </div>
  );
}
