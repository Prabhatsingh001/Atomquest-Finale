import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAdminStore } from '../stores/adminStore';
import { authApi } from '../services/authApi';
import { useAuthStore } from '../stores/authStore';

export default function AdminDashboardPage() {
  const { user, logout } = useAuthStore();
  const { sessions, metrics, isLoading, fetchSessions, fetchMetrics, forceEndSession } = useAdminStore();
  const navigate = useNavigate();

  useEffect(() => {
    fetchMetrics();
    fetchSessions();
    
    // Auto-refresh every 10 seconds
    const interval = setInterval(() => {
      fetchMetrics();
      fetchSessions();
    }, 10000);
    
    return () => clearInterval(interval);
  }, []);

  const handleForceEnd = async (sessionId) => {
    if (window.confirm("Are you sure you want to forcibly terminate this session?")) {
      await forceEndSession(sessionId);
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

  if (!metrics) {
    return <div className="p-8 text-slate-500">Loading admin data...</div>;
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8 flex flex-col sm:flex-row sm:justify-between items-start sm:items-end gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 tracking-tight">System Admin</h1>
          <p className="mt-2 text-slate-500">Monitor platform health and active sessions.</p>
        </div>
        <div className="flex flex-col items-start sm:items-end gap-2 w-full sm:w-auto">
          <div className="flex gap-4">
            <button 
              onClick={() => window.open('/api/metrics', '_blank')}
              className="text-blue-600 hover:text-blue-800 font-medium"
            >
              Raw Metrics
            </button>
            <button 
              onClick={handleLogout}
              className="text-slate-500 hover:text-slate-700 font-medium"
            >
              Logout
            </button>
          </div>
          <div className="text-sm text-slate-500">
            Auto-refreshing every 10s
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-10">
        <MetricCard title="Active Sessions" value={metrics.active_sessions} />
        <MetricCard title="Active Participants" value={metrics.active_participants} />
        <MetricCard title="Total Sessions" value={metrics.total_sessions} />
        <MetricCard title="WS Connections" value={metrics.websocket_connections} />
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
        <div className="px-6 py-5 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
          <h2 className="text-lg font-semibold text-slate-800">All Sessions</h2>
        </div>
        
        {isLoading && sessions.length === 0 ? (
          <div className="p-8 text-center text-slate-500">Loading sessions...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-sm text-slate-500 uppercase tracking-wider">
                  <th className="px-6 py-4 font-medium">Session ID</th>
                  <th className="px-6 py-4 font-medium">Title</th>
                  <th className="px-6 py-4 font-medium">Status</th>
                  <th className="px-6 py-4 font-medium">Participants</th>
                  <th className="px-6 py-4 font-medium text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {sessions.map((session) => (
                  <tr key={session.id} className="hover:bg-slate-50/50 transition-colors">
                    <td className="px-6 py-4 text-slate-600 font-mono text-sm">#{session.id}</td>
                    <td className="px-6 py-4 font-medium text-slate-900">{session.title}</td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${
                        session.status === 'active' ? 'bg-green-100 text-green-700' :
                        session.status === 'waiting' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-slate-100 text-slate-700'
                      }`}>
                        {session.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-slate-500 text-sm">
                      {session.participants?.length || 0}
                    </td>
                    <td className="px-6 py-4 text-right">
                      {session.status === 'active' || session.status === 'waiting' ? (
                        <button
                          onClick={() => handleForceEnd(session.id)}
                          className="text-red-600 hover:text-red-800 text-sm font-medium transition-colors"
                        >
                          Force End
                        </button>
                      ) : (
                        <span className="text-slate-400 text-sm">Ended</span>
                      )}
                    </td>
                  </tr>
                ))}
                {sessions.length === 0 && (
                  <tr>
                    <td colSpan="5" className="px-6 py-10 text-center text-slate-500">
                      No sessions found in the system.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

function MetricCard({ title, value }) {
  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 flex flex-col items-center justify-center">
      <div className="text-sm font-medium text-slate-500 uppercase tracking-wider mb-2">{title}</div>
      <div className="text-4xl font-bold text-slate-900">{value}</div>
    </div>
  );
}
