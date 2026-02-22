import { lazy, Suspense, useState } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClientProvider } from '@tanstack/react-query'
import { queryClient } from './lib/queryClient'
import { AuthProvider } from './contexts/AuthContext'
import { ToastProvider } from './contexts/ToastContext'
import { DemoProvider, useDemo } from './contexts/DemoContext'
import ErrorBoundary from './components/ErrorBoundary'
import ToastContainer from './components/Toast'
import LoggerToastBridge from './components/LoggerToastBridge'
import ProtectedRoute from './components/ProtectedRoute'
import OfflineIndicator from './components/OfflineIndicator'
import { GDPRBanner } from './components/common/GDPRBanner'
import CommandPalette from './components/common/CommandPalette'
import KeyboardShortcutsHelp from './components/common/KeyboardShortcutsHelp'
import { useRouteChangeReset } from './hooks/useRouteChangeReset'
import { useKeyboardShortcuts } from './hooks/useKeyboardShortcuts'
import { AlertCircle } from 'lucide-react'

// Lazy load pages for code splitting
const LoginPage = lazy(() => import('./pages/LoginPage'))
const DashboardPage = lazy(() => import('./pages/DashboardPage'))
const ChantiersListPage = lazy(() => import('./pages/ChantiersListPage'))
const ChantierDetailPage = lazy(() => import('./pages/ChantierDetailPage'))
const UsersListPage = lazy(() => import('./pages/UsersListPage'))
const UserDetailPage = lazy(() => import('./pages/UserDetailPage'))
const APIKeysPage = lazy(() => import('./pages/APIKeysPage'))
const WebhooksPage = lazy(() => import('./pages/WebhooksPage'))
const PlanningPage = lazy(() => import('./pages/PlanningPage'))
const FeuillesHeuresPage = lazy(() => import('./pages/FeuillesHeuresPage'))
const FormulairesPage = lazy(() => import('./pages/FormulairesPage'))
const DocumentsPage = lazy(() => import('./pages/DocumentsPage'))
const LogistiquePage = lazy(() => import('./pages/LogistiquePage'))
const SecuritySettingsPage = lazy(() => import('./pages/SecuritySettingsPage'))
const AcceptInvitationPage = lazy(() => import('./pages/AcceptInvitationPage'))
const ResetPasswordPage = lazy(() => import('./pages/ResetPasswordPage'))
const ForgotPasswordPage = lazy(() => import('./pages/ForgotPasswordPage'))
const FournisseursPage = lazy(() => import('./pages/FournisseursPage'))
const BudgetsPage = lazy(() => import('./pages/BudgetsPage'))
const AchatsPage = lazy(() => import('./pages/AchatsPage'))
const DashboardFinancierPage = lazy(() => import('./pages/DashboardFinancierPage'))
const DevisListPage = lazy(() => import('./pages/DevisListPage'))
const DevisDetailPage = lazy(() => import('./pages/DevisDetailPage'))
const DevisGeneratorPage = lazy(() => import('./pages/DevisGeneratorPage'))
const DevisDashboardPage = lazy(() => import('./pages/DevisDashboardPage'))
const ArticlesPage = lazy(() => import('./pages/ArticlesPage'))
const DevisPreviewPage = lazy(() => import('./pages/DevisPreviewPage'))
const PennylaneIntegrationPage = lazy(() => import('./pages/PennylaneIntegrationPage'))
const ParametresEntreprisePage = lazy(() => import('./pages/ParametresEntreprisePage'))

// CSS-only loading spinner (no lucide-react dependency)
function PageLoader() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="w-8 h-8 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin" />
    </div>
  )
}

// Wrapper component to use route change reset hook
function RouteChangeHandler() {
  useRouteChangeReset()
  return null
}

// Wrapper pour les raccourcis clavier (doit être dans <BrowserRouter> — react-router-dom v7)
function KeyboardShortcutsHandler({ onShowHelp }: { onShowHelp: () => void }) {
  useKeyboardShortcuts({ onShowHelp })
  return null
}

// Bandeau mode démo
function DemoBanner() {
  const { isDemoMode, disableDemoMode } = useDemo()

  if (!isDemoMode) return null

  return (
    <div className="fixed top-0 left-0 right-0 z-[9997] bg-yellow-500 text-yellow-900 py-2 px-4 shadow-lg">
      <div className="max-w-7xl mx-auto flex items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <span className="font-medium text-sm">
            Mode démonstration — Les données ne sont pas sauvegardées
          </span>
        </div>
        <button
          onClick={disableDemoMode}
          className="px-3 py-1 bg-yellow-700 hover:bg-yellow-800 text-white rounded-lg text-sm font-medium transition-colors flex-shrink-0"
        >
          Quitter
        </button>
      </div>
    </div>
  )
}

function App() {
  const [showShortcutsHelp, setShowShortcutsHelp] = useState(false)

  return (
    <ErrorBoundary>
    <BrowserRouter>
      <RouteChangeHandler />
      <KeyboardShortcutsHandler onShowHelp={() => setShowShortcutsHelp(true)} />
      <AuthProvider>
        <DemoProvider>
        <ToastProvider>
        <QueryClientProvider client={queryClient}>
        <DemoBanner />
        <Suspense fallback={<PageLoader />}>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          <Route path="/accept-invitation" element={<AcceptInvitationPage />} />
          <Route path="/reset-password" element={<ResetPasswordPage />} />

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
            path="/api-keys"
            element={
              <ProtectedRoute>
                <APIKeysPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/webhooks"
            element={
              <ProtectedRoute>
                <WebhooksPage />
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
          <Route
            path="/fournisseurs"
            element={
              <ProtectedRoute>
                <FournisseursPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/budgets"
            element={
              <ProtectedRoute>
                <BudgetsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/achats"
            element={
              <ProtectedRoute>
                <AchatsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/finances"
            element={
              <ProtectedRoute>
                <DashboardFinancierPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/security"
            element={
              <ProtectedRoute>
                <SecuritySettingsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/devis/dashboard"
            element={
              <ProtectedRoute>
                <DevisDashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/devis/articles"
            element={
              <ProtectedRoute>
                <ArticlesPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/devis/:id/preview"
            element={
              <ProtectedRoute>
                <DevisPreviewPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/devis/:id/legacy"
            element={
              <ProtectedRoute>
                <DevisDetailPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/devis/:id"
            element={
              <ProtectedRoute>
                <DevisGeneratorPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/devis"
            element={
              <ProtectedRoute>
                <DevisListPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/financier/pennylane"
            element={
              <ProtectedRoute>
                <PennylaneIntegrationPage />
              </ProtectedRoute>
            }
          />

          <Route
            path="/parametres-entreprise"
            element={
              <ProtectedRoute>
                <ParametresEntreprisePage />
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
        <CommandPalette />
        <KeyboardShortcutsHelp
          isOpen={showShortcutsHelp}
          onClose={() => setShowShortcutsHelp(false)}
        />
        </QueryClientProvider>
        </ToastProvider>
        </DemoProvider>
      </AuthProvider>
    </BrowserRouter>
    </ErrorBoundary>
  )
}

export default App
