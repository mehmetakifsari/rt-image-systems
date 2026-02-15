import React from 'react';
import './i18n';
import './index.css';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'sonner';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { OfflineProvider } from './contexts/OfflineContext';
import { ThemeProvider, useTheme } from './contexts/ThemeContext';

// Pages
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import HomePage from './pages/HomePage';
import NewRecordPage from './pages/NewRecordPage';
import RecordDetailPage from './pages/RecordDetailPage';
import AdminPage from './pages/AdminPage';

// Protected Route wrapper
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen bg-[#09090b] flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-[#FACC15] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }
  
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  
  return children;
};

// Public Route wrapper (redirect to home if logged in)
const PublicRoute = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen bg-[#09090b] flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-[#FACC15] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }
  
  if (user) {
    return <Navigate to="/" replace />;
  }
  
  return children;
};

function AppRoutes() {
  return (
    <Routes>
      {/* Public Landing Page */}
      <Route path="/welcome" element={<LandingPage />} />
      
      <Route 
        path="/login" 
        element={
          <PublicRoute>
            <LoginPage />
          </PublicRoute>
        } 
      />
      <Route 
        path="/" 
        element={
          <ProtectedRoute>
            <HomePage />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/new" 
        element={
          <ProtectedRoute>
            <NewRecordPage />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/record/:id" 
        element={
          <ProtectedRoute>
            <RecordDetailPage />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/admin" 
        element={
          <ProtectedRoute>
            <AdminPage />
          </ProtectedRoute>
        } 
      />
      <Route path="*" element={<Navigate to="/welcome" replace />} />
    </Routes>
  );
}

// Themed Toaster Component
const ThemedToaster = () => {
  const { theme } = useTheme();
  
  return (
    <Toaster 
      position="top-center"
      toastOptions={{
        style: theme === 'dark' 
          ? {
              background: '#18181b',
              border: '1px solid #27272a',
              color: '#fafafa'
            }
          : {
              background: '#ffffff',
              border: '1px solid #e5e7eb',
              color: '#111827'
            }
      }}
    />
  );
};

function App() {
  return (
    <BrowserRouter>
      <ThemeProvider>
        <AuthProvider>
          <OfflineProvider>
            <AppRoutes />
            <ThemedToaster />
          </OfflineProvider>
        </AuthProvider>
      </ThemeProvider>
    </BrowserRouter>
  );
}

export default App;
