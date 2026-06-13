import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { sessionsApi } from '../services/sessionsApi';
import { useSessionStore } from '../stores/sessionStore';
import { authApi } from '../services/authApi';
import { useAuthStore } from '../stores/authStore';

export default function Dashboard() {
  const [title, setTitle] = useState('');
  const [loading, setLoading] = useState(false);
  const sessions = useSessionStore(state => state.sessions);
  const setSessions = useSessionStore(state => state.setSessions);
  const addSession = useSessionStore(state => state.addSession);
  const user = useAuthStore(state => state.user);
  const logout = useAuthStore(state => state.logout);
  const navigate = useNavigate();

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      const data = await sessionsApi.listSessions();
      setSessions(data);
    } catch (err) {
      console.error('Failed to load sessions', err);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!title.trim()) return;
    
    setLoading(true);
    try {
      const newSession = await sessionsApi.createSession(title);
      addSession(newSession);
      setTitle('');
    } catch (err) {
      console.error('Failed to create session', err);
      alert('Failed to create session');
    } finally {
      setLoading(false);
    }
  };

  const handleJoin = (id) => {
    navigate(`/session/${id}`);
  };

  const handleCopyLink = async (id) => {
    try {
      const { join_url } = await sessionsApi.getJoinLink(id);
      const fullUrl = `${window.location.origin}${join_url}`;
      await navigator.clipboard.writeText(fullUrl);
      alert('Join link copied to clipboard!');
    } catch (err) {
      console.error('Failed to get join link', err);
    }
  };

  const handleDownloadArchive = async (id) => {
    try {
      const blob = await sessionsApi.downloadArchive(id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `session_${id}_archive.zip`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Failed to download archive', err);
      alert('Failed to download session archive.');
    }
  };

  const handleLogout = async () => {
    try {
      await authApi.logout();
    } catch (e) {
      console.error('Logout API failed', e);
    }
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-slate-50 p-8">
      <div className="max-w-5xl mx-auto">
        <header className="flex flex-col sm:flex-row sm:justify-between items-start sm:items-center gap-4 mb-8 bg-white p-6 rounded-xl shadow-sm">
          <div>
            <h1 className="text-2xl font-bold text-slate-800 break-words w-full">
              Agent Dashboard {user?.name ? `- Welcome, ${user.name}!` : ''}
            </h1>
            <p className="text-slate-500 text-sm">Manage your support sessions</p>
          </div>
          <button 
            onClick={handleLogout}
            className="text-slate-500 hover:text-slate-700 font-medium"
          >
            Logout
          </button>
        </header>

        <div className="grid md:grid-cols-3 gap-8">
          <div className="md:col-span-1">
            <div className="bg-white p-6 rounded-xl shadow-sm">
              <h2 className="text-lg font-semibold mb-4 text-slate-800">Create Session</h2>
              <form onSubmit={handleCreate} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">
                    Session Title
                  </label>
                  <input
                    type="text"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                    placeholder="e.g. Technical Support Call"
                  />
                </div>
                <button
                  type="submit"
                  disabled={loading || !title.trim()}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 rounded-lg transition-colors disabled:opacity-50"
                >
                  {loading ? 'Creating...' : 'Create Room'}
                </button>
              </form>
            </div>
          </div>

          <div className="md:col-span-2">
            <div className="bg-white p-6 rounded-xl shadow-sm">
              <div className="flex flex-col sm:flex-row sm:justify-between items-start sm:items-center mb-4 gap-2">
                <h2 className="text-lg font-semibold text-slate-800">Active & Recent Sessions</h2>
                <button 
                  onClick={() => navigate('/history')}
                  className="text-sm font-medium text-blue-600 hover:text-blue-700 transition"
                >
                  View Full History →
                </button>
              </div>
              {sessions.length === 0 ? (
                <div className="text-center py-10 text-slate-500">
                  No sessions found. Create one to get started.
                </div>
              ) : (
                <div className="space-y-3">
                  {sessions.map(session => (
                    <div key={session.id} className="flex flex-col sm:flex-row items-start sm:items-center justify-between p-4 border border-slate-200 rounded-lg hover:border-blue-300 transition-colors gap-4">
                      <div className="w-full">
                        <h3 className="font-medium text-slate-800 break-words">{session.title}</h3>
                        <div className="flex flex-wrap items-center gap-3 mt-1 text-xs text-slate-500">
                          <span className={`px-2 py-0.5 rounded-full ${session.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-slate-100'}`}>
                            {session.status}
                          </span>
                          <span>Created: {new Date(session.created_at).toLocaleString()}</span>
                        </div>
                      </div>
                      <div className="flex flex-wrap gap-2 items-center w-full sm:w-auto">
                        {session.status !== 'completed' ? (
                          <>
                            <button 
                              onClick={() => handleCopyLink(session.id)}
                              className="px-3 py-1.5 text-sm font-medium text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
                            >
                              Copy Link
                            </button>
                            <button 
                              onClick={() => handleJoin(session.id)}
                              className="px-4 py-1.5 text-sm font-medium text-white bg-slate-800 rounded-lg hover:bg-slate-700 transition-colors"
                            >
                              Join
                            </button>
                          </>
                        ) : (
                          <button 
                            onClick={() => handleDownloadArchive(session.id)}
                            className="w-full sm:w-auto px-4 py-1.5 text-sm font-medium text-green-700 bg-green-100 rounded-lg hover:bg-green-200 transition-colors"
                          >
                            Download Archive
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
