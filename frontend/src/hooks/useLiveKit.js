import { useRoomContext, useParticipants, useTracks } from '@livekit/components-react';
import { Track } from 'livekit-client';

export function useLiveKit() {
  const room = useRoomContext();
  const participants = useParticipants();
  const tracks = useTracks([
    { source: Track.Source.Camera, withPlaceholder: true },
    { source: Track.Source.Microphone, withPlaceholder: true },
    { source: Track.Source.ScreenShare, withPlaceholder: false },
  ]);

  const toggleCamera = async () => {
    if (!room.localParticipant) return;
    await room.localParticipant.setCameraEnabled(!room.localParticipant.isCameraEnabled);
  };

  const toggleMicrophone = async () => {
    if (!room.localParticipant) return;
    await room.localParticipant.setMicrophoneEnabled(!room.localParticipant.isMicrophoneEnabled);
  };

  const toggleScreenShare = async () => {
    if (!room.localParticipant) return;
    await room.localParticipant.setScreenShareEnabled(!room.localParticipant.isScreenShareEnabled);
  };

  return { 
    room, 
    participants, 
    tracks, 
    toggleCamera, 
    toggleMicrophone, 
    toggleScreenShare 
  };
}
