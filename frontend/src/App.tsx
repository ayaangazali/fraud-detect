import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Login from './pages/Login';
import DashboardPage from './pages/dashboard/DashboardPage';
import UploadPage from './pages/screening/UploadPage';
import ScreeningQueuePage from './pages/screening/ScreeningQueuePage';
import CheckerReviewPage from './pages/review/CheckerReviewPage';
import FinalizerReviewPage from './pages/review/FinalizerReviewPage';
import ReportsPage from './pages/reports/ReportsPage';
import AuditLogsPage from './pages/audit/AuditLogsPage';
import SettingsPage from './pages/SettingsPage';
import ProtectedRoute from './components/auth/ProtectedRoute';
import RealTimeProvider from './components/providers/RealTimeProvider';
import { useAuthStore } from './stores/authStore';

const App: React.FC = () => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  return (
    <BrowserRouter>
      <RealTimeProvider>
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#333',
              color: '#fff',
            },
            success: {
              duration: 3000,
              iconTheme: {
                primary: '#10b981',
                secondary: '#fff',
              },
            },
            error: {
              duration: 4000,
              iconTheme: {
                primary: '#ef4444',
                secondary: '#fff',
              },
            },
          }}
        />
        <Routes>
          <Route
            path="/"
            element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <Login />}
          />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/upload"
            element={
              <ProtectedRoute requireRole="screener">
                <UploadPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/screening"
            element={
              <ProtectedRoute requireRole="screener">
                <ScreeningQueuePage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/checker"
            element={
              <ProtectedRoute requireRole="checker">
                <CheckerReviewPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/finalizer"
            element={
              <ProtectedRoute requireRole="finalizer">
                <FinalizerReviewPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/reports"
            element={
              <ProtectedRoute>
                <ReportsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/audit"
            element={
              <ProtectedRoute requireRole={['checker', 'finalizer']}>
                <AuditLogsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings"
            element={
              <ProtectedRoute>
                <SettingsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="*"
            element={<Navigate to={isAuthenticated ? '/dashboard' : '/'} replace />}
          />
        </Routes>
      </RealTimeProvider>
    </BrowserRouter>
  );
};

export default App;
