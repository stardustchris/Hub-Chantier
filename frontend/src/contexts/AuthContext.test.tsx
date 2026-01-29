/**
 * Tests unitaires pour AuthContext
 *
 * Architecture: cookies HttpOnly (withCredentials: true)
 * - L'authentification repose sur un cookie HttpOnly positionné par le serveur
 * - getCurrentUser est toujours appelé au mount (le cookie est envoyé automatiquement)
 * - Pas de sessionStorage/localStorage pour les tokens
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { AuthProvider, useAuth } from './AuthContext'

// Mock des services
vi.mock('../services/auth', () => ({
  authService: {
    login: vi.fn(),
    getCurrentUser: vi.fn(),
  },
}))

vi.mock('../services/authEvents', () => ({
  onSessionExpired: vi.fn(() => vi.fn()),
  emitLogout: vi.fn(),
}))

vi.mock('../services/api', () => ({
  default: {
    post: vi.fn().mockResolvedValue({}),
  },
}))

vi.mock('../services/csrf', () => ({
  clearCsrfToken: vi.fn(),
}))

import { authService } from '../services/auth'
import { onSessionExpired, emitLogout } from '../services/authEvents'
import { clearCsrfToken } from '../services/csrf'

// Mock user complet pour eviter les erreurs TS
const createMockUser = (overrides = {}) => ({
  id: '1',
  email: 'test@example.com',
  nom: 'Test',
  prenom: 'User',
  role: 'admin' as const,
  is_active: true,
  type_utilisateur: 'employe' as const,
  created_at: '2026-01-01T00:00:00Z',
  ...overrides,
})

// Composant de test pour acceder au contexte
function TestConsumer({ onLoginError }: { onLoginError?: (error: Error) => void }) {
  const { user, isLoading, isAuthenticated, login, logout } = useAuth()
  return (
    <div>
      <div data-testid="isLoading">{isLoading.toString()}</div>
      <div data-testid="isAuthenticated">{isAuthenticated.toString()}</div>
      <div data-testid="user">{user ? user.email : 'null'}</div>
      <button
        onClick={() =>
          login('test@example.com', 'password').catch((e) => {
            onLoginError?.(e)
          })
        }
      >
        Login
      </button>
      <button onClick={logout}>Logout</button>
    </div>
  )
}

describe('AuthContext', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('AuthProvider', () => {
    it('demarre en mode loading puis passe a false', async () => {
      vi.mocked(authService.getCurrentUser).mockImplementation(
        () =>
          new Promise((resolve) =>
            setTimeout(() => resolve(createMockUser()), 50)
          )
      )

      render(
        <AuthProvider>
          <TestConsumer />
        </AuthProvider>
      )

      // Pendant le chargement, isLoading devrait etre true
      expect(screen.getByTestId('isLoading').textContent).toBe('true')

      // Apres le chargement, isLoading devrait etre false
      await waitFor(() => {
        expect(screen.getByTestId('isLoading').textContent).toBe('false')
      })
    })

    it('charge l\'utilisateur si le cookie HttpOnly est valide', async () => {
      const mockUser = createMockUser()
      vi.mocked(authService.getCurrentUser).mockResolvedValue(mockUser)

      render(
        <AuthProvider>
          <TestConsumer />
        </AuthProvider>
      )

      await waitFor(() => {
        expect(screen.getByTestId('isAuthenticated').textContent).toBe('true')
        expect(screen.getByTestId('user').textContent).toBe('test@example.com')
      })

      // getCurrentUser est appelé au mount (cookie envoyé automatiquement)
      expect(authService.getCurrentUser).toHaveBeenCalled()
    })

    it('reste non authentifie si getCurrentUser echoue (pas de cookie valide)', async () => {
      vi.mocked(authService.getCurrentUser).mockRejectedValue(new Error('Unauthorized'))

      render(
        <AuthProvider>
          <TestConsumer />
        </AuthProvider>
      )

      await waitFor(() => {
        expect(screen.getByTestId('isLoading').textContent).toBe('false')
        expect(screen.getByTestId('isAuthenticated').textContent).toBe('false')
      })

      expect(authService.getCurrentUser).toHaveBeenCalled()
    })

    it('s\'abonne aux evenements de session expiree', async () => {
      vi.mocked(authService.getCurrentUser).mockRejectedValue(new Error('Unauthorized'))

      render(
        <AuthProvider>
          <TestConsumer />
        </AuthProvider>
      )

      expect(onSessionExpired).toHaveBeenCalled()
    })
  })

  describe('login', () => {
    it('met a jour l\'utilisateur apres login reussi', async () => {
      const user = userEvent.setup()
      const mockUser = createMockUser()
      vi.mocked(authService.getCurrentUser).mockRejectedValue(new Error('Unauthorized'))
      vi.mocked(authService.login).mockResolvedValue({
        user: mockUser,
        access_token: 'token-in-cookie',
        token_type: 'bearer',
      })

      render(
        <AuthProvider>
          <TestConsumer />
        </AuthProvider>
      )

      await waitFor(() => {
        expect(screen.getByTestId('isLoading').textContent).toBe('false')
      })

      await user.click(screen.getByText('Login'))

      await waitFor(() => {
        expect(screen.getByTestId('isAuthenticated').textContent).toBe('true')
      })

      // Le token est dans le cookie HttpOnly, pas dans sessionStorage
      expect(sessionStorage.getItem('access_token')).toBeNull()
    })

    it('propage l\'erreur si login echoue', async () => {
      const user = userEvent.setup()
      const loginError = new Error('Invalid credentials')
      vi.mocked(authService.getCurrentUser).mockRejectedValue(new Error('Unauthorized'))
      vi.mocked(authService.login).mockRejectedValue(loginError)

      const onLoginError = vi.fn()

      render(
        <AuthProvider>
          <TestConsumer onLoginError={onLoginError} />
        </AuthProvider>
      )

      await waitFor(() => {
        expect(screen.getByTestId('isLoading').textContent).toBe('false')
      })

      await user.click(screen.getByText('Login'))

      await waitFor(() => {
        expect(onLoginError).toHaveBeenCalledWith(loginError)
      })

      expect(screen.getByTestId('isAuthenticated').textContent).toBe('false')
    })
  })

  describe('logout', () => {
    it('appelle l\'API logout et reset l\'utilisateur', async () => {
      const user = userEvent.setup()
      const mockUser = createMockUser()
      vi.mocked(authService.getCurrentUser).mockResolvedValue(mockUser)

      render(
        <AuthProvider>
          <TestConsumer />
        </AuthProvider>
      )

      await waitFor(() => {
        expect(screen.getByTestId('isAuthenticated').textContent).toBe('true')
      })

      await user.click(screen.getByText('Logout'))

      await waitFor(() => {
        expect(screen.getByTestId('isAuthenticated').textContent).toBe('false')
        expect(screen.getByTestId('user').textContent).toBe('null')
      })

      // Le cookie est supprimé côté serveur via POST /api/auth/logout
      // Le token CSRF est nettoyé
      expect(clearCsrfToken).toHaveBeenCalled()
    })

    it('emet un evenement de logout pour sync multi-onglets', async () => {
      const user = userEvent.setup()
      const mockUser = createMockUser()
      vi.mocked(authService.getCurrentUser).mockResolvedValue(mockUser)

      render(
        <AuthProvider>
          <TestConsumer />
        </AuthProvider>
      )

      await waitFor(() => {
        expect(screen.getByTestId('isAuthenticated').textContent).toBe('true')
      })

      await user.click(screen.getByText('Logout'))

      await waitFor(() => {
        expect(emitLogout).toHaveBeenCalled()
      })
    })
  })

  describe('useAuth hook', () => {
    it('throw si utilise hors du AuthProvider', () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

      expect(() => {
        render(<TestConsumer />)
      }).toThrow('useAuth must be used within an AuthProvider')

      consoleSpy.mockRestore()
    })
  })
})
