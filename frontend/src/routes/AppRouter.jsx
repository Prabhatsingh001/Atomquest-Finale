import { Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from '../pages/LoginPage';
import SignupPage from '../pages/SignupPage';
import Dashboard from '../pages/Dashboard';
import JoinSessionPage from '../pages/JoinSessionPage';
import ActiveCallPage from '../pages/ActiveCallPage';
import HistoryPage from '../pages/HistoryPage';
import AdminDashboardPage from '../pages/AdminDashboardPage';
import ProtectedRoute from '../components/ProtectedRoute';

function AppRouter() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/signup" element={<SignupPage />} />
      <Route path="/join/:token" element={<JoinSessionPage />} />
      <Route path="/session/:id" element={<ActiveCallPage />} />

      {/* Protected Agent routes */}
      <Route 
        path="/dashboard" 
        element={
          <ProtectedRoute requiredRoles={['agent']}>
            <Dashboard />
          </ProtectedRoute>
        } 
      />
      
      <Route 
        path="/history" 
        element={
          <ProtectedRoute requiredRoles={['agent']}>
            <HistoryPage />
          </ProtectedRoute>
        } 
      />

      {/* Protected Admin-only routes */}
      <Route 
        path="/admin" 
        element={
          <ProtectedRoute requiredRoles={['admin']}>
            <AdminDashboardPage />
          </ProtectedRoute>
        } 
      />


      {/* Catch-all */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default AppRouter;
