import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { sessionsApi } from '../services/sessionsApi';
import { useSessionStore } from '../stores/sessionStore';
import { useAuthStore } from '../stores/authStore';

export default function JoinSessionPage() {
  const { token } = useParams();
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const setActiveSession = useSessionStore(state => state.setActiveSession);

  const handleJoin = async (e) => {
    e.preventDefault();
    if (!name.trim()) return;

    setLoading(true);
    setError('');
    
    try {
      const response = await sessionsApi.customerJoin(token, name);
      
      // Store backend authentication for the ephemeral customer
      useAuthStore.getState().login(
        { id: response.user_id, name: name, role: 'customer' },
        response.backend_token
      );

      // Store session and redirect to session view
      // Note: We use the join_token as the id in URL for customers
      setActiveSession({
        livekitToken: response.livekit_token,
        roomName: response.room_name,
        identity: response.identity,
        sessionId: response.session_id,
        isAgent: false
      });
      navigate(`/session/${token}`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to join session. The link might be invalid or expired.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-slate-50 px-4">
      <div className="w-full max-w-md bg-white rounded-xl shadow-lg p-8">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-slate-900">Join Support Call</h1>
          <p className="text-slate-500 mt-2">Enter your name to join the session</p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 text-red-600 rounded-lg text-sm border border-red-200">
            {error}
          </div>
        )}

        <form onSubmit={handleJoin} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Your Name
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition-colors"
              placeholder="e.g. Jane Doe"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading || !name.trim()}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 rounded-lg transition-colors disabled:opacity-70 text-lg shadow-sm"
          >
            {loading ? 'Joining...' : 'Join Call'}
          </button>
        </form>
      </div>
    </div>
  );
}
