import { LiveKitRoom, GridLayout, ParticipantTile, useTracks, RoomAudioRenderer } from '@livekit/components-react';
import { Track } from 'livekit-client';
import '@livekit/components-styles';
import CallControls from './CallControls';
import { ChatPanel } from "./ChatPanel";
import ConnectionStatus from './ConnectionStatus';

function VideoGrid() {
  const tracks = useTracks(
    [
      { source: Track.Source.Camera, withPlaceholder: true },
      { source: Track.Source.ScreenShare, withPlaceholder: false },
    ],
    { onlySubscribed: false }
  );
  
  return (
    <GridLayout tracks={tracks} className="w-full h-full">
      <ParticipantTile />
    </GridLayout>
  );
}

export default function VideoRoom({ token, roomName, sessionId, onLeave, onEndSession }) {
  // Use current origin for LiveKit WebSocket connection if served behind same proxy,
  // or explicitly use the backend LiveKit URL if configured.
  const serverUrl = import.meta.env.VITE_LIVEKIT_URL || `ws://${window.location.hostname}:7880`;

  if (!token) {
    return <div>Loading room...</div>;
  }

  return (
    <LiveKitRoom
      video={true}
      audio={true}
      token={token}
      serverUrl={serverUrl}
      data-lk-theme="default"
      className="h-full flex flex-col"
    >
      <div className="flex-1 flex flex-col lg:flex-row overflow-hidden">
        {/* Video Area */}
        <div className="flex-1 relative bg-slate-950 flex flex-col min-h-0">
          <div className="absolute top-4 left-4 z-10">
            <ConnectionStatus sessionId={sessionId} />
          </div>
          <div className="flex-1 overflow-hidden p-4 flex items-center justify-center">
            <VideoGrid />
            <RoomAudioRenderer />
          </div>
          
          {/* Controls Area */}
          <div className="h-24 bg-slate-900 border-t border-slate-800 flex items-center justify-center">
            <CallControls onLeave={onLeave} onEndSession={onEndSession} sessionId={sessionId} />
          </div>
        </div>

        {/* Chat Panel */}
        <div className="w-full h-1/3 lg:h-auto lg:w-80 bg-slate-900 border-t lg:border-t-0 lg:border-l border-slate-800 flex flex-col">
          <ChatPanel sessionId={sessionId} />
        </div>
      </div>
    </LiveKitRoom>
  );
}
