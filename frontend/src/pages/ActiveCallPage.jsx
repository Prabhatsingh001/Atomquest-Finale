import { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useSessionStore } from '../stores/sessionStore';
import { useAuthStore } from '../stores/authStore';
import { sessionsApi } from '../services/sessionsApi';
import VideoRoom from '../components/VideoRoom';

export default function ActiveCallPage() {
  const { id } = useParams(); // id could be session.id (for agents) or join_token (for customers)
  const navigate = useNavigate();
  
  const { activeSession, setActiveSession, clearActiveSession } = useSessionStore();
  const { user } = useAuthStore();
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const initRef = useRef(false);

  useEffect(() => {
    // Prevent running more than once for the same session
    if (initRef.current) return;
    initRef.current = true;

    async function initSession() {
      // If we already have an active session with a token, just use it
      if (activeSession && activeSession.livekitToken) {
        setLoading(false);
        return;
      }

      // If no active session but user is an agent, try to join as agent
      if (user && (user.role === 'agent' || user.role === 'admin')) {
        try {
          const response = await sessionsApi.agentJoin(id);
          setActiveSession({
            livekitToken: response.livekit_token,
            roomName: response.room_name,
            identity: response.identity,
            sessionId: response.session_id,
            isAgent: true
          });
        } catch (err) {
          setError('Failed to join session as agent. Make sure you own this session.');
        }
      } else {
        // Customer who lost their state — redirect back to join page
        navigate(`/join/${id}`);
        return;
      }
      setLoading(false);
    }

    initSession();
  }, [id]);

  const handleLeave = () => {
    clearActiveSession();
    if (user && (user.role === 'agent' || user.role === 'admin')) {
      navigate('/dashboard');
    } else {
      navigate('/login');
    }
  };

  const handleEndSession = async () => {
    try {
      if (activeSession?.sessionId) {
        await sessionsApi.endSession(activeSession.sessionId);
      }
    } catch (err) {
      console.error("Failed to end session", err);
    } finally {
      handleLeave();
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen bg-slate-900 text-white">Loading session...</div>;
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-slate-900 text-white">
        <p className="text-red-400 mb-4">{error}</p>
        <button onClick={handleLeave} className="px-4 py-2 bg-slate-700 rounded hover:bg-slate-600 transition">
          Return
        </button>
      </div>
    );
  }

  return (
    <div className="w-full h-screen bg-black overflow-hidden">
      {activeSession && activeSession.livekitToken ? (
        <VideoRoom 
          token={activeSession.livekitToken} 
          roomName={activeSession.roomName} 
          sessionId={activeSession.sessionId}
          onLeave={handleLeave}
          onEndSession={handleEndSession}
        />
      ) : (
        <div className="flex items-center justify-center h-full text-white">
          Failed to load room
        </div>
      )}
    </div>
  );
}

