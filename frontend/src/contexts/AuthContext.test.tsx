/**
 * Tests unitaires pour AuthContext
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
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

import { authService } from '../services/auth'
import { onSessionExpired, emitLogout } from '../services/authEvents'

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
    sessionStorage.clear()
  })

  afterEach(() => {
    sessionStorage.clear()
  })

  describe('AuthProvider', () => {
    it('demarre en mode loading puis passe a false', async () => {
      // Simuler un delai pour observer isLoading=true
      vi.mocked(authService.getCurrentUser).mockImplementation(
        () =>
          new Promise((resolve) =>
            setTimeout(() => resolve(createMockUser()), 50)
          )
      )
      sessionStorage.setItem('access_token', 'test-token')

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

    it('charge l\'utilisateur si un token existe', async () => {
      const mockUser = createMockUser()
      sessionStorage.setItem('access_token', 'valid-token')
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
    })

    it('supprime le token si getCurrentUser echoue', async () => {
      sessionStorage.setItem('access_token', 'invalid-token')
      vi.mocked(authService.getCurrentUser).mockRejectedValue(new Error('Unauthorized'))

      render(
        <AuthProvider>
          <TestConsumer />
        </AuthProvider>
      )

      await waitFor(() => {
        expect(screen.getByTestId('isAuthenticated').textContent).toBe('false')
        expect(sessionStorage.getItem('access_token')).toBeNull()
      })
    })

    it('reste non authentifie sans token', async () => {
      vi.mocked(authService.getCurrentUser).mockResolvedValue(createMockUser())

      render(
        <AuthProvider>
          <TestConsumer />
        </AuthProvider>
      )

      await waitFor(() => {
        expect(screen.getByTestId('isLoading').textContent).toBe('false')
        expect(screen.getByTestId('isAuthenticated').textContent).toBe('false')
      })

      // getCurrentUser ne doit pas avoir ete appele
      expect(authService.getCurrentUser).not.toHaveBeenCalled()
    })

    it('s\'abonne aux evenements de session expiree', async () => {
      render(
        <AuthProvider>
          <TestConsumer />
        </AuthProvider>
      )

      expect(onSessionExpired).toHaveBeenCalled()
    })
  })

  describe('login', () => {
    it('stocke le token et l\'utilisateur apres login', async () => {
      const user = userEvent.setup()
      const mockUser = createMockUser()
      vi.mocked(authService.login).mockResolvedValue({
        user: mockUser,
        access_token: 'new-token',
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
        expect(sessionStorage.getItem('access_token')).toBe('new-token')
      })
    })

    it('propage l\'erreur si login echoue', async () => {
      const user = userEvent.setup()
      const loginError = new Error('Invalid credentials')
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

      // Attendre que l'erreur soit propagee
      await waitFor(() => {
        expect(onLoginError).toHaveBeenCalledWith(loginError)
      })

      // L'utilisateur doit rester non authentifie
      expect(screen.getByTestId('isAuthenticated').textContent).toBe('false')
    })
  })

  describe('logout', () => {
    it('supprime le token et reset l\'utilisateur', async () => {
      const user = userEvent.setup()
      const mockUser = createMockUser()
      sessionStorage.setItem('access_token', 'valid-token')
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

      expect(screen.getByTestId('isAuthenticated').textContent).toBe('false')
      expect(screen.getByTestId('user').textContent).toBe('null')
      expect(sessionStorage.getItem('access_token')).toBeNull()
    })

    it('emet un evenement de logout pour sync multi-onglets', async () => {
      const user = userEvent.setup()
      const mockUser = createMockUser()
      sessionStorage.setItem('access_token', 'valid-token')
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

      expect(emitLogout).toHaveBeenCalled()
    })
  })

  describe('useAuth hook', () => {
    it('throw si utilise hors du AuthProvider', () => {
      // Supprimer le console.error pour ce test
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

      expect(() => {
        render(<TestConsumer />)
      }).toThrow('useAuth must be used within an AuthProvider')

      consoleSpy.mockRestore()
    })
  })
})
