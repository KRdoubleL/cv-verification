import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import VerifierDashboard from './pages/VerifierDashboard'
import CandidatePage from './pages/CandidatePage'
import UploadPage from './pages/UploadPage'

function ProtectedRoute({ children, roles }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="min-h-screen flex items-center justify-center"><div className="text-gray-500 text-sm">Loading...</div></div>
  if (!user) return <Navigate to="/login" replace />
  if (roles && !roles.includes(user.role)) return <Navigate to="/dashboard" replace />
  return children
}

function AppRoutes() {
  const { user } = useAuth()
  const defaultDash = user?.role === 'verifier' ? '/verify' : '/dashboard'

  return (
    <Routes>
      <Route path="/login" element={user ? <Navigate to={defaultDash} replace /> : <LoginPage />} />
      <Route path="/dashboard" element={
        <ProtectedRoute roles={['recruiter', 'admin']}>
          <DashboardPage />
        </ProtectedRoute>
      } />
      <Route path="/verify" element={
        <ProtectedRoute roles={['verifier', 'admin']}>
          <VerifierDashboard />
        </ProtectedRoute>
      } />
      <Route path="/upload" element={
        <ProtectedRoute roles={['recruiter', 'admin']}>
          <UploadPage />
        </ProtectedRoute>
      } />
      <Route path="/candidate/:id" element={
        <ProtectedRoute>
          <CandidatePage />
        </ProtectedRoute>
      } />
      <Route path="*" element={<Navigate to={defaultDash} replace />} />
    </Routes>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </AuthProvider>
  )
}