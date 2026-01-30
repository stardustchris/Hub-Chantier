import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import { SecuritySettingsPage } from './SecuritySettingsPage'
import { AuthContext } from '../contexts/AuthContext'
import { ToastContext } from '../contexts/ToastContext'
import { api } from '../services/api'

// Mock API
vi.mock('../services/api', () => ({
  api: {
    post: vi.fn(),
  },
}))

describe('SecuritySettingsPage', () => {
  const mockUser = {
    id: 1,
    email: 'test@example.com',
    prenom: 'Test',
    nom: 'User',
    role: 'admin',
    is_active: true,
    created_at: '2026-01-01T00:00:00Z',
  }

  const mockShowToast = vi.fn()

  const renderWithContext = () => {
    return render(
      <AuthContext.Provider
        value={{
          user: mockUser,
          login: vi.fn(),
          logout: vi.fn(),
          isLoading: false,
        }}
      >
        <ToastContext.Provider value={{ showToast: mockShowToast }}>
          <SecuritySettingsPage />
        </ToastContext.Provider>
      </AuthContext.Provider>
    )
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should render security settings page', () => {
    renderWithContext()

    expect(screen.getByText('Sécurité')).toBeInTheDocument()
    expect(screen.getByText('Changer le mot de passe')).toBeInTheDocument()
  })

  it('should display user information', () => {
    renderWithContext()

    expect(screen.getByText('test@example.com')).toBeInTheDocument()
    expect(screen.getByText(/Actif/)).toBeInTheDocument()
  })

  it('should show password requirements', () => {
    renderWithContext()

    expect(screen.getByText(/Au moins 8 caractères/)).toBeInTheDocument()
    expect(screen.getByText(/Une majuscule/)).toBeInTheDocument()
    expect(screen.getByText(/Une minuscule/)).toBeInTheDocument()
    expect(screen.getByText(/Un chiffre/)).toBeInTheDocument()
    expect(screen.getByText(/Un caractère spécial/)).toBeInTheDocument()
  })

  it('should validate password matching', async () => {
    renderWithContext()

    const oldPasswordInput = screen.getByLabelText(/ancien mot de passe/i)
    const newPasswordInput = screen.getByLabelText(/nouveau mot de passe/i)
    const confirmPasswordInput = screen.getByLabelText(/confirmer/i)

    fireEvent.change(oldPasswordInput, { target: { value: 'OldPassword123!' } })
    fireEvent.change(newPasswordInput, { target: { value: 'NewPassword123!' } })
    fireEvent.change(confirmPasswordInput, { target: { value: 'DifferentPassword123!' } })

    const submitButton = screen.getByText(/modifier le mot de passe/i)
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/Les mots de passe ne correspondent pas/)).toBeInTheDocument()
    })
  })

  it('should validate password strength', async () => {
    renderWithContext()

    const oldPasswordInput = screen.getByLabelText(/ancien mot de passe/i)
    const newPasswordInput = screen.getByLabelText(/nouveau mot de passe/i)
    const confirmPasswordInput = screen.getByLabelText(/confirmer/i)

    fireEvent.change(oldPasswordInput, { target: { value: 'OldPassword123!' } })
    fireEvent.change(newPasswordInput, { target: { value: 'weak' } })
    fireEvent.change(confirmPasswordInput, { target: { value: 'weak' } })

    const submitButton = screen.getByText(/modifier le mot de passe/i)
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/au moins 8 caractères/)).toBeInTheDocument()
    })
  })

  it('should display password strength indicator', () => {
    renderWithContext()

    const newPasswordInput = screen.getByLabelText(/nouveau mot de passe/i)

    // Mot de passe faible
    fireEvent.change(newPasswordInput, { target: { value: 'Weak1!' } })
    expect(screen.getByText('Faible')).toBeInTheDocument()

    // Mot de passe moyen
    fireEvent.change(newPasswordInput, { target: { value: 'Medium123!' } })
    expect(screen.getByText('Moyen')).toBeInTheDocument()

    // Mot de passe fort
    fireEvent.change(newPasswordInput, { target: { value: 'VerySecurePassword123!' } })
    expect(screen.getByText('Fort')).toBeInTheDocument()
  })

  it('should submit password change successfully', async () => {
    vi.mocked(api.post).mockResolvedValue({ data: {} })
    renderWithContext()

    const oldPasswordInput = screen.getByLabelText(/ancien mot de passe/i)
    const newPasswordInput = screen.getByLabelText(/nouveau mot de passe/i)
    const confirmPasswordInput = screen.getByLabelText(/confirmer/i)

    fireEvent.change(oldPasswordInput, { target: { value: 'OldPassword123!' } })
    fireEvent.change(newPasswordInput, { target: { value: 'NewPassword123!' } })
    fireEvent.change(confirmPasswordInput, { target: { value: 'NewPassword123!' } })

    const submitButton = screen.getByText(/modifier le mot de passe/i)
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith('/auth/change-password', {
        old_password: 'OldPassword123!',
        new_password: 'NewPassword123!',
      })
      expect(mockShowToast).toHaveBeenCalledWith(
        'Mot de passe modifié avec succès !',
        'success'
      )
    })
  })

  it('should handle incorrect old password error', async () => {
    vi.mocked(api.post).mockRejectedValue({
      response: {
        status: 400,
      },
    })

    renderWithContext()

    const oldPasswordInput = screen.getByLabelText(/ancien mot de passe/i)
    const newPasswordInput = screen.getByLabelText(/nouveau mot de passe/i)
    const confirmPasswordInput = screen.getByLabelText(/confirmer/i)

    fireEvent.change(oldPasswordInput, { target: { value: 'WrongPassword123!' } })
    fireEvent.change(newPasswordInput, { target: { value: 'NewPassword123!' } })
    fireEvent.change(confirmPasswordInput, { target: { value: 'NewPassword123!' } })

    const submitButton = screen.getByText(/modifier le mot de passe/i)
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/L'ancien mot de passe est incorrect/)).toBeInTheDocument()
    })
  })

  it('should clear form after successful password change', async () => {
    vi.mocked(api.post).mockResolvedValue({ data: {} })
    renderWithContext()

    const oldPasswordInput = screen.getByLabelText(/ancien mot de passe/i) as HTMLInputElement
    const newPasswordInput = screen.getByLabelText(/nouveau mot de passe/i) as HTMLInputElement
    const confirmPasswordInput = screen.getByLabelText(/confirmer/i) as HTMLInputElement

    fireEvent.change(oldPasswordInput, { target: { value: 'OldPassword123!' } })
    fireEvent.change(newPasswordInput, { target: { value: 'NewPassword123!' } })
    fireEvent.change(confirmPasswordInput, { target: { value: 'NewPassword123!' } })

    const submitButton = screen.getByText(/modifier le mot de passe/i)
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(oldPasswordInput.value).toBe('')
      expect(newPasswordInput.value).toBe('')
      expect(confirmPasswordInput.value).toBe('')
    })
  })

  it('should show security recommendations', () => {
    renderWithContext()

    expect(screen.getByText(/Changez votre mot de passe régulièrement/)).toBeInTheDocument()
    expect(screen.getByText(/Utilisez un mot de passe unique/)).toBeInTheDocument()
    expect(screen.getByText(/Ne partagez jamais votre mot de passe/)).toBeInTheDocument()
    expect(screen.getByText(/Déconnectez-vous sur les appareils partagés/)).toBeInTheDocument()
  })

  it('should prevent same old and new password', async () => {
    renderWithContext()

    const oldPasswordInput = screen.getByLabelText(/ancien mot de passe/i)
    const newPasswordInput = screen.getByLabelText(/nouveau mot de passe/i)
    const confirmPasswordInput = screen.getByLabelText(/confirmer/i)

    const samePassword = 'SamePassword123!'
    fireEvent.change(oldPasswordInput, { target: { value: samePassword } })
    fireEvent.change(newPasswordInput, { target: { value: samePassword } })
    fireEvent.change(confirmPasswordInput, { target: { value: samePassword } })

    const submitButton = screen.getByText(/modifier le mot de passe/i)
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/doit être différent de l'ancien/)).toBeInTheDocument()
    })
  })
})
