import { VideoTrack, AudioTrack, useParticipant } from '@livekit/components-react';

export default function ParticipantTile({ participant }) {
  const { cameraTrack, microphoneTrack, isSpeaking } = useParticipant(participant);

  return (
    <div className={`relative rounded-xl overflow-hidden bg-slate-800 border-2 transition-colors ${isSpeaking ? 'border-blue-500' : 'border-transparent'} shadow-md h-full min-h-[200px] flex items-center justify-center`}>
      {cameraTrack?.publication?.isMuted || !cameraTrack ? (
        <div className="w-20 h-20 bg-slate-700 rounded-full flex items-center justify-center text-2xl font-bold text-slate-300">
          {participant.identity.substring(0, 2).toUpperCase()}
        </div>
      ) : (
        <VideoTrack trackRef={cameraTrack} className="w-full h-full object-cover" />
      )}
      
      {microphoneTrack && !microphoneTrack.publication?.isMuted && (
         <AudioTrack trackRef={microphoneTrack} />
      )}

      {/* Overlay */}
      <div className="absolute bottom-2 left-2 bg-black/60 backdrop-blur-sm px-3 py-1.5 rounded-lg flex items-center gap-2">
        <span className="text-white text-sm font-medium truncate max-w-[120px]">
          {participant.name || participant.identity}
        </span>
        {microphoneTrack?.publication?.isMuted ? (
          <div className="w-2 h-2 rounded-full bg-red-500" title="Muted" />
        ) : (
          <div className={`w-2 h-2 rounded-full ${isSpeaking ? 'bg-green-400 animate-pulse' : 'bg-slate-400'}`} />
        )}
      </div>
    </div>
  );
}
