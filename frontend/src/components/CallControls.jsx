import { useLocalParticipant } from '@livekit/components-react';
import { useAuthStore } from '../stores/authStore';
import { useRecordingStore } from '../stores/recordingStore';

export default function CallControls({ onLeave, onEndSession, sessionId }) {
  const { localParticipant, isCameraEnabled, isMicrophoneEnabled, isScreenShareEnabled } = useLocalParticipant();
  const { user } = useAuthStore();
  const { isRecording, duration, startRecording, stopRecording } = useRecordingStore();

  const toggleCamera = () => localParticipant?.setCameraEnabled(!isCameraEnabled);
  const toggleMicrophone = () => localParticipant?.setMicrophoneEnabled(!isMicrophoneEnabled);
  const toggleScreenShare = () => localParticipant?.setScreenShareEnabled(!isScreenShareEnabled);

  const handleRecordingToggle = async () => {
    if (isRecording) {
      await stopRecording();
    } else {
      await startRecording(sessionId);
    }
  };

  const formatDuration = (seconds) => {
    const m = Math.floor(seconds / 60).toString().padStart(2, '0');
    const s = (seconds % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  };

  return (
    <div className="flex flex-wrap items-center justify-center gap-2 sm:gap-4 py-3 sm:py-4 px-3 sm:px-6 bg-slate-900 rounded-2xl shadow-xl border border-slate-700/50 backdrop-blur-md w-full max-w-full overflow-x-auto">
      <button
        onClick={toggleMicrophone}
        className={`w-12 h-12 rounded-full flex items-center justify-center transition-all ${
          isMicrophoneEnabled ? 'bg-slate-700 hover:bg-slate-600 text-white' : 'bg-red-500 hover:bg-red-600 text-white'
        }`}
        title={isMicrophoneEnabled ? "Mute Microphone" : "Unmute Microphone"}
      >
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          {isMicrophoneEnabled ? (
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
          ) : (
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
          )}
        </svg>
      </button>

      <button
        onClick={toggleCamera}
        className={`w-12 h-12 rounded-full flex items-center justify-center transition-all ${
          isCameraEnabled ? 'bg-slate-700 hover:bg-slate-600 text-white' : 'bg-red-500 hover:bg-red-600 text-white'
        }`}
        title={isCameraEnabled ? "Turn off Camera" : "Turn on Camera"}
      >
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          {isCameraEnabled ? (
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
          ) : (
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
          )}
        </svg>
      </button>

      <button
        onClick={toggleScreenShare}
        className={`w-12 h-12 rounded-full flex items-center justify-center transition-all ${
          isScreenShareEnabled ? 'bg-blue-500 hover:bg-blue-600 text-white' : 'bg-slate-700 hover:bg-slate-600 text-white'
        }`}
        title="Screen Share"
      >
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
      </button>

      <div className="w-px h-8 bg-slate-700 mx-2"></div>

      {user?.role === 'agent' && (
        <>
          <button
            onClick={handleRecordingToggle}
            className={`w-12 h-12 rounded-full flex items-center justify-center transition-all ${
              isRecording ? 'bg-red-500 hover:bg-red-600 animate-pulse' : 'bg-slate-700 hover:bg-slate-600'
            } text-white`}
            title={isRecording ? "Stop Recording" : "Start Recording"}
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
              {isRecording ? (
                <rect x="6" y="6" width="12" height="12" rx="2" />
              ) : (
                <circle cx="12" cy="12" r="6" />
              )}
            </svg>
          </button>
          {isRecording && (
            <span className="text-red-400 font-mono text-sm">{formatDuration(duration)}</span>
          )}
          <div className="w-px h-8 bg-slate-700 mx-2"></div>
        </>
      )}

      <div className="w-full sm:w-auto flex justify-center gap-2 mt-2 sm:mt-0 sm:ml-auto">
        <button
          onClick={onLeave}
          className="px-4 sm:px-6 py-2.5 bg-slate-700 hover:bg-slate-600 text-white font-medium rounded-xl transition-colors shadow-sm text-sm sm:text-base flex-1 sm:flex-none"
        >
          Leave Session
        </button>

        {user?.role === 'agent' && (
          <button
            onClick={onEndSession}
            className="px-4 sm:px-6 py-2.5 bg-red-600 hover:bg-red-700 text-white font-medium rounded-xl transition-colors shadow-lg shadow-red-500/20 text-sm sm:text-base flex-1 sm:flex-none"
          >
            End Session
          </button>
        )}
      </div>
    </div>
  );
}
