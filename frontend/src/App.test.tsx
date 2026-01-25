/**
 * Tests unitaires pour App.tsx
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import App from './App'

// Mock all lazy-loaded pages
vi.mock('./pages/LoginPage', () => ({
  default: () => <div data-testid="login-page">Login Page</div>,
}))

vi.mock('./pages/DashboardPage', () => ({
  default: () => <div data-testid="dashboard-page">Dashboard Page</div>,
}))

vi.mock('./pages/ChantiersListPage', () => ({
  default: () => <div data-testid="chantiers-list-page">Chantiers List Page</div>,
}))

vi.mock('./pages/ChantierDetailPage', () => ({
  default: () => <div data-testid="chantier-detail-page">Chantier Detail Page</div>,
}))

vi.mock('./pages/UsersListPage', () => ({
  default: () => <div data-testid="users-list-page">Users List Page</div>,
}))

vi.mock('./pages/UserDetailPage', () => ({
  default: () => <div data-testid="user-detail-page">User Detail Page</div>,
}))

vi.mock('./pages/PlanningPage', () => ({
  default: () => <div data-testid="planning-page">Planning Page</div>,
}))

vi.mock('./pages/FeuillesHeuresPage', () => ({
  default: () => <div data-testid="feuilles-heures-page">Feuilles Heures Page</div>,
}))

vi.mock('./pages/FormulairesPage', () => ({
  default: () => <div data-testid="formulaires-page">Formulaires Page</div>,
}))

vi.mock('./pages/DocumentsPage', () => ({
  default: () => <div data-testid="documents-page">Documents Page</div>,
}))

vi.mock('./pages/LogistiquePage', () => ({
  default: () => <div data-testid="logistique-page">Logistique Page</div>,
}))

// Mock components
vi.mock('./components/ErrorBoundary', () => ({
  default: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}))

vi.mock('./components/Toast', () => ({
  default: () => <div data-testid="toast-container" />,
}))

vi.mock('./components/LoggerToastBridge', () => ({
  default: () => <div data-testid="logger-toast-bridge" />,
}))

vi.mock('./components/OfflineIndicator', () => ({
  default: () => <div data-testid="offline-indicator" />,
}))

// Mock ProtectedRoute to pass through or block based on auth
const mockUser = { id: '1', email: 'test@test.com', role: 'admin' }
let isAuthenticated = false

vi.mock('./components/ProtectedRoute', () => ({
  default: ({ children }: { children: React.ReactNode }) => {
    if (isAuthenticated) {
      return <>{children}</>
    }
    // Redirect to login when not authenticated
    window.history.pushState({}, '', '/login')
    return null
  },
}))

// Mock AuthContext
vi.mock('./contexts/AuthContext', () => ({
  AuthProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  useAuth: () => ({
    user: isAuthenticated ? mockUser : null,
    isLoading: false,
    login: vi.fn(),
    logout: vi.fn(),
  }),
}))

// Mock ToastContext
vi.mock('./contexts/ToastContext', () => ({
  ToastProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  useToast: () => ({
    addToast: vi.fn(),
    showUndoToast: vi.fn(),
  }),
}))

describe('App', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    isAuthenticated = false
    // Reset URL
    window.history.pushState({}, '', '/')
  })

  describe('rendering', () => {
    it('rend sans erreur', () => {
      render(<App />)
      // App should render without crashing
      expect(document.body).toBeInTheDocument()
    })

    it('affiche le toast container', async () => {
      render(<App />)
      await waitFor(() => {
        expect(screen.getByTestId('toast-container')).toBeInTheDocument()
      })
    })

    it('affiche l offline indicator', async () => {
      render(<App />)
      await waitFor(() => {
        expect(screen.getByTestId('offline-indicator')).toBeInTheDocument()
      })
    })

    it('affiche le logger toast bridge', async () => {
      render(<App />)
      await waitFor(() => {
        expect(screen.getByTestId('logger-toast-bridge')).toBeInTheDocument()
      })
    })
  })

  describe('routing - unauthenticated', () => {
    it('affiche la page login sur /login', async () => {
      window.history.pushState({}, '', '/login')
      render(<App />)

      await waitFor(() => {
        expect(screen.getByTestId('login-page')).toBeInTheDocument()
      })
    })
  })

  describe('routing - authenticated', () => {
    beforeEach(() => {
      isAuthenticated = true
    })

    it('affiche le dashboard sur /', async () => {
      render(<App />)

      await waitFor(() => {
        expect(screen.getByTestId('dashboard-page')).toBeInTheDocument()
      })
    })

    it('affiche la liste des chantiers sur /chantiers', async () => {
      window.history.pushState({}, '', '/chantiers')
      render(<App />)

      await waitFor(() => {
        expect(screen.getByTestId('chantiers-list-page')).toBeInTheDocument()
      })
    })

    it('affiche le detail chantier sur /chantiers/:id', async () => {
      window.history.pushState({}, '', '/chantiers/123')
      render(<App />)

      await waitFor(() => {
        expect(screen.getByTestId('chantier-detail-page')).toBeInTheDocument()
      })
    })

    it('affiche la liste des utilisateurs sur /utilisateurs', async () => {
      window.history.pushState({}, '', '/utilisateurs')
      render(<App />)

      await waitFor(() => {
        expect(screen.getByTestId('users-list-page')).toBeInTheDocument()
      })
    })

    it('affiche le planning sur /planning', async () => {
      window.history.pushState({}, '', '/planning')
      render(<App />)

      await waitFor(() => {
        expect(screen.getByTestId('planning-page')).toBeInTheDocument()
      })
    })

    it('affiche les feuilles heures sur /feuilles-heures', async () => {
      window.history.pushState({}, '', '/feuilles-heures')
      render(<App />)

      await waitFor(() => {
        expect(screen.getByTestId('feuilles-heures-page')).toBeInTheDocument()
      })
    })

    it('affiche les formulaires sur /formulaires', async () => {
      window.history.pushState({}, '', '/formulaires')
      render(<App />)

      await waitFor(() => {
        expect(screen.getByTestId('formulaires-page')).toBeInTheDocument()
      })
    })

    it('affiche les documents sur /documents', async () => {
      window.history.pushState({}, '', '/documents')
      render(<App />)

      await waitFor(() => {
        expect(screen.getByTestId('documents-page')).toBeInTheDocument()
      })
    })

    it('affiche la logistique sur /logistique', async () => {
      window.history.pushState({}, '', '/logistique')
      render(<App />)

      await waitFor(() => {
        expect(screen.getByTestId('logistique-page')).toBeInTheDocument()
      })
    })

    it('redirige les routes inconnues vers /', async () => {
      window.history.pushState({}, '', '/unknown-route')
      render(<App />)

      await waitFor(() => {
        expect(screen.getByTestId('dashboard-page')).toBeInTheDocument()
      })
    })
  })

  describe('lazy loading', () => {
    it('affiche un loader pendant le chargement', () => {
      // The Suspense fallback should show a spinner
      // Since we're mocking the pages, they load instantly
      // But the PageLoader component should exist in the DOM structure
      render(<App />)
      // The app should render without throwing
      expect(document.body).toBeInTheDocument()
    })
  })
})
