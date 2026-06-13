import { useEffect, useState } from 'react';
import { historyApi } from '../services/historyApi';
import { useNavigate } from 'react-router-dom';

export default function HistoryPage() {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const navigate = useNavigate();

  useEffect(() => {
    async function load() {
      try {
        const data = await historyApi.getHistory(page, 20);
        setSessions(data);
      } catch (err) {
        console.error("Failed to load history", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [page]);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 p-8 flex justify-center items-center">
        <div className="text-slate-500">Loading history...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 p-8">
      <div className="max-w-5xl mx-auto">
        <header className="flex flex-col sm:flex-row sm:justify-between items-start sm:items-center gap-4 mb-8 bg-white p-6 rounded-xl shadow-sm">
          <div className="w-full break-words">
            <h1 className="text-2xl font-bold text-slate-800">Session History</h1>
            <p className="text-slate-500 text-sm">Review your past support sessions</p>
          </div>
          <button 
            onClick={() => navigate('/dashboard')}
            className="text-sm font-medium text-blue-600 hover:text-blue-700 transition"
          >
            ← Back to Dashboard
          </button>
        </header>
        
        <div className="bg-white rounded-xl shadow-sm overflow-hidden border border-slate-200">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead className="bg-slate-50 border-b border-slate-200 text-sm text-slate-500 uppercase tracking-wider">
                <tr>
                  <th className="px-6 py-4 font-medium">Title</th>
                  <th className="px-6 py-4 font-medium">Date</th>
                  <th className="px-6 py-4 font-medium">Duration</th>
                  <th className="px-6 py-4 font-medium">Status</th>
                  <th className="px-6 py-4 font-medium text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {sessions.map(session => (
                  <tr key={session.id} className="hover:bg-slate-50/50 transition-colors">
                    <td className="px-6 py-4 font-medium text-slate-900">{session.title}</td>
                    <td className="px-6 py-4 text-slate-500 text-sm">{new Date(session.created_at).toLocaleString()}</td>
                    <td className="px-6 py-4 text-slate-500 text-sm">{session.duration_seconds || 0}s</td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${
                        session.status === 'active' ? 'bg-green-100 text-green-700' :
                        session.status === 'waiting' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-slate-100 text-slate-700'
                      }`}>
                        {session.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right flex justify-end gap-3">
                      <button 
                        onClick={async () => {
                          try {
                            const { sessionsApi } = await import('../services/sessionsApi');
                            const blob = await sessionsApi.downloadArchive(session.id);
                            const url = window.URL.createObjectURL(blob);
                            const a = document.createElement('a');
                            a.href = url;
                            a.download = `session_${session.id}_archive.zip`;
                            document.body.appendChild(a);
                            a.click();
                            window.URL.revokeObjectURL(url);
                            document.body.removeChild(a);
                          } catch (err) {
                            console.error('Failed to download archive', err);
                            alert('Failed to download session archive.');
                          }
                        }}
                        className="text-sm font-medium text-green-600 hover:text-green-700 transition-colors"
                      >
                        Download Archive
                      </button>
                    </td>
                  </tr>
                ))}
                {sessions.length === 0 && (
                  <tr>
                    <td colSpan="5" className="px-6 py-10 text-center text-slate-500">
                      No ended sessions found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
          
          <div className="flex justify-between items-center px-6 py-4 bg-slate-50 border-t border-slate-200">
            <button 
              disabled={page === 1} 
              onClick={() => setPage(p => p - 1)}
              className="px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 disabled:opacity-50 transition-colors"
            >
              Previous
            </button>
            <span className="text-sm text-slate-500">Page {page}</span>
            <button 
              disabled={sessions.length < 20}
              onClick={() => setPage(p => p + 1)}
              className="px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 disabled:opacity-50 transition-colors"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
