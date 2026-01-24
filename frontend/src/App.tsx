import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import { ToastProvider } from './contexts/ToastContext'
import ErrorBoundary from './components/ErrorBoundary'
import ToastContainer from './components/Toast'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import ChantiersListPage from './pages/ChantiersListPage'
import ChantierDetailPage from './pages/ChantierDetailPage'
import UsersListPage from './pages/UsersListPage'
import UserDetailPage from './pages/UserDetailPage'
import PlanningPage from './pages/PlanningPage'
import FeuillesHeuresPage from './pages/FeuillesHeuresPage'
import FormulairesPage from './pages/FormulairesPage'
import DocumentsPage from './pages/DocumentsPage'
import LogistiquePage from './pages/LogistiquePage'
import ProtectedRoute from './components/ProtectedRoute'

function App() {
  return (
    <ErrorBoundary>
    <BrowserRouter>
      <AuthProvider>
        <ToastProvider>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<LoginPage />} />

          {/* Protected routes */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/chantiers"
            element={
              <ProtectedRoute>
                <ChantiersListPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/chantiers/:id"
            element={
              <ProtectedRoute>
                <ChantierDetailPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/utilisateurs"
            element={
              <ProtectedRoute>
                <UsersListPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/utilisateurs/:id"
            element={
              <ProtectedRoute>
                <UserDetailPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/planning"
            element={
              <ProtectedRoute>
                <PlanningPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/feuilles-heures"
            element={
              <ProtectedRoute>
                <FeuillesHeuresPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/formulaires"
            element={
              <ProtectedRoute>
                <FormulairesPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/documents"
            element={
              <ProtectedRoute>
                <DocumentsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/logistique"
            element={
              <ProtectedRoute>
                <LogistiquePage />
              </ProtectedRoute>
            }
          />

          {/* Catch all - redirect to dashboard */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
        <ToastContainer />
        </ToastProvider>
      </AuthProvider>
    </BrowserRouter>
    </ErrorBoundary>
  )
}

export default App
