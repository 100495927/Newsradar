import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import RegisterPage from './pages/RegisterPage'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import SummaryPage from './pages/SummaryPage'
import AlertsPage from './pages/AlertsPage'
import SourcesPage from './pages/SourcesPage'
import ProfilePage from './pages/ProfilePage'
import ForgotPasswordPage from './pages/ForgotPasswordPage'
import NotificationsPage from './pages/NotificationsPage'

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<RegisterPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
          <Route path="/summary" element={<ProtectedRoute><SummaryPage /></ProtectedRoute>} />
          <Route path="/alerts" element={<ProtectedRoute><AlertsPage /></ProtectedRoute>} />
          <Route path="/sources" element={<ProtectedRoute><SourcesPage /></ProtectedRoute>} />
          <Route path="/notifications" element={<ProtectedRoute><NotificationsPage /></ProtectedRoute>} />
          <Route path="/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App
