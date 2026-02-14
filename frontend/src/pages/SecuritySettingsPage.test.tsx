import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import { SecuritySettingsPage } from './SecuritySettingsPage'

// Mock user and toast
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

// Mock useAuth
vi.mock('../contexts/AuthContext', () => ({
  useAuth: () => ({
    user: mockUser,
    login: vi.fn(),
    logout: vi.fn(),
    isLoading: false,
  }),
}))

// Mock useToast
vi.mock('../contexts/ToastContext', () => ({
  useToast: () => ({
    showToast: mockShowToast,
  }),
}))

// Mock API
const mockApiPost = vi.fn()
vi.mock('../services/api', () => ({
  default: {
    post: (...args: unknown[]) => mockApiPost(...args),
  },
}))

describe('SecuritySettingsPage', () => {
  const renderWithContext = () => {
    return render(<SecuritySettingsPage />)
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

    const oldPasswordInput = screen.getByLabelText('Ancien mot de passe')
    const newPasswordInput = screen.getByLabelText('Nouveau mot de passe')
    const confirmPasswordInput = screen.getByLabelText('Confirmer le nouveau mot de passe')

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

    const oldPasswordInput = screen.getByLabelText('Ancien mot de passe')
    const newPasswordInput = screen.getByLabelText('Nouveau mot de passe')
    const confirmPasswordInput = screen.getByLabelText('Confirmer le nouveau mot de passe')

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

    const newPasswordInput = screen.getByLabelText('Nouveau mot de passe')

    // Mot de passe faible (8 caractères, seulement minuscules = strength 2)
    fireEvent.change(newPasswordInput, { target: { value: 'weakpass' } })
    expect(screen.getByText('Faible')).toBeInTheDocument()

    // Mot de passe moyen (8 caractères avec 4 critères: >=8, minuscules, majuscule, chiffre)
    fireEvent.change(newPasswordInput, { target: { value: 'Medium123' } })
    expect(screen.getByText('Moyen')).toBeInTheDocument()

    // Mot de passe fort (12+ caractères avec tous les critères)
    fireEvent.change(newPasswordInput, { target: { value: 'VerySecurePassword123!' } })
    expect(screen.getByText('Fort')).toBeInTheDocument()
  })

  it('should submit password change successfully', async () => {
    mockApiPost.mockResolvedValue({ data: {} })
    renderWithContext()

    const oldPasswordInput = screen.getByLabelText('Ancien mot de passe')
    const newPasswordInput = screen.getByLabelText('Nouveau mot de passe')
    const confirmPasswordInput = screen.getByLabelText('Confirmer le nouveau mot de passe')

    fireEvent.change(oldPasswordInput, { target: { value: 'OldPassword123!' } })
    fireEvent.change(newPasswordInput, { target: { value: 'NewPassword123!' } })
    fireEvent.change(confirmPasswordInput, { target: { value: 'NewPassword123!' } })

    const submitButton = screen.getByText(/modifier le mot de passe/i)
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(mockApiPost).toHaveBeenCalledWith('/auth/change-password', {
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
    mockApiPost.mockRejectedValue({
      response: {
        status: 400,
      },
    })

    renderWithContext()

    const oldPasswordInput = screen.getByLabelText('Ancien mot de passe')
    const newPasswordInput = screen.getByLabelText('Nouveau mot de passe')
    const confirmPasswordInput = screen.getByLabelText('Confirmer le nouveau mot de passe')

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
    mockApiPost.mockResolvedValue({ data: {} })
    renderWithContext()

    const oldPasswordInput = screen.getByLabelText('Ancien mot de passe') as HTMLInputElement
    const newPasswordInput = screen.getByLabelText('Nouveau mot de passe') as HTMLInputElement
    const confirmPasswordInput = screen.getByLabelText('Confirmer le nouveau mot de passe') as HTMLInputElement

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

    const oldPasswordInput = screen.getByLabelText('Ancien mot de passe')
    const newPasswordInput = screen.getByLabelText('Nouveau mot de passe')
    const confirmPasswordInput = screen.getByLabelText('Confirmer le nouveau mot de passe')

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
