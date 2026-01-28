import { lazy, Suspense } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import { ToastProvider } from './contexts/ToastContext'
import ErrorBoundary from './components/ErrorBoundary'
import ToastContainer from './components/Toast'
import LoggerToastBridge from './components/LoggerToastBridge'
import ProtectedRoute from './components/ProtectedRoute'
import OfflineIndicator from './components/OfflineIndicator'
import { GDPRBanner } from './components/common/GDPRBanner'

// Lazy load pages for code splitting
const LoginPage = lazy(() => import('./pages/LoginPage'))
const DashboardPage = lazy(() => import('./pages/DashboardPage'))
const ChantiersListPage = lazy(() => import('./pages/ChantiersListPage'))
const ChantierDetailPage = lazy(() => import('./pages/ChantierDetailPage'))
const UsersListPage = lazy(() => import('./pages/UsersListPage'))
const UserDetailPage = lazy(() => import('./pages/UserDetailPage'))
const PlanningPage = lazy(() => import('./pages/PlanningPage'))
const FeuillesHeuresPage = lazy(() => import('./pages/FeuillesHeuresPage'))
const FormulairesPage = lazy(() => import('./pages/FormulairesPage'))
const DocumentsPage = lazy(() => import('./pages/DocumentsPage'))
const LogistiquePage = lazy(() => import('./pages/LogistiquePage'))

// CSS-only loading spinner (no lucide-react dependency)
function PageLoader() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="w-8 h-8 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin" />
    </div>
  )
}

function App() {
  return (
    <ErrorBoundary>
    <BrowserRouter>
      <AuthProvider>
        <ToastProvider>
        <Suspense fallback={<PageLoader />}>
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
        </Suspense>
        <LoggerToastBridge />
        <ToastContainer />
        <GDPRBanner />
        <OfflineIndicator />
        </ToastProvider>
      </AuthProvider>
    </BrowserRouter>
    </ErrorBoundary>
  )
}

export default App
