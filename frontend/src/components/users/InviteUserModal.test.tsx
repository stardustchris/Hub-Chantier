import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import { InviteUserModal } from './InviteUserModal'

describe('InviteUserModal', () => {
  const mockOnClose = vi.fn()
  const mockOnSubmit = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should render the modal with all fields', () => {
    render(<InviteUserModal onClose={mockOnClose} onSubmit={mockOnSubmit} />)

    expect(screen.getByText('Inviter un utilisateur')).toBeInTheDocument()
    expect(screen.getByLabelText(/prénom/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/nom/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/rôle/i)).toBeInTheDocument()
  })

  it('should display invitation info message', () => {
    render(<InviteUserModal onClose={mockOnClose} onSubmit={mockOnSubmit} />)

    expect(
      screen.getByText(/Un email d'invitation sera envoyé/)
    ).toBeInTheDocument()
  })

  it('should call onClose when clicking cancel', () => {
    render(<InviteUserModal onClose={mockOnClose} onSubmit={mockOnSubmit} />)

    const cancelButton = screen.getByText('Annuler')
    fireEvent.click(cancelButton)

    expect(mockOnClose).toHaveBeenCalledTimes(1)
  })

  it('should call onClose when clicking X button', () => {
    render(<InviteUserModal onClose={mockOnClose} onSubmit={mockOnSubmit} />)

    const closeButton = screen.getByRole('button', { name: /fermer/i })
    fireEvent.click(closeButton)

    expect(mockOnClose).toHaveBeenCalledTimes(1)
  })

  it('should call onClose when pressing Escape', () => {
    render(<InviteUserModal onClose={mockOnClose} onSubmit={mockOnSubmit} />)

    fireEvent.keyDown(document, { key: 'Escape' })

    expect(mockOnClose).toHaveBeenCalledTimes(1)
  })

  it('should submit with valid data', async () => {
    mockOnSubmit.mockResolvedValue(undefined)
    render(<InviteUserModal onClose={mockOnClose} onSubmit={mockOnSubmit} />)

    // Remplir le formulaire
    fireEvent.change(screen.getByLabelText(/prénom/i), {
      target: { value: 'Jean' },
    })
    fireEvent.change(screen.getByLabelText(/nom/i), {
      target: { value: 'Dupont' },
    })
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'jean.dupont@test.com' },
    })

    // Soumettre
    const submitButton = screen.getByText(/envoyer l'invitation/i)
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith({
        prenom: 'Jean',
        nom: 'Dupont',
        email: 'jean.dupont@test.com',
        role: 'compagnon', // Valeur par défaut
      })
    })
  })

  it('should disable submit button when fields are empty', () => {
    render(<InviteUserModal onClose={mockOnClose} onSubmit={mockOnSubmit} />)

    const submitButton = screen.getByText(/envoyer l'invitation/i)
    expect(submitButton).toBeDisabled()
  })

  it('should enable submit button when all required fields are filled', () => {
    render(<InviteUserModal onClose={mockOnClose} onSubmit={mockOnSubmit} />)

    fireEvent.change(screen.getByLabelText(/prénom/i), {
      target: { value: 'Jean' },
    })
    fireEvent.change(screen.getByLabelText(/nom/i), {
      target: { value: 'Dupont' },
    })
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'jean.dupont@test.com' },
    })

    const submitButton = screen.getByText(/envoyer l'invitation/i)
    expect(submitButton).not.toBeDisabled()
  })

  it('should display error message on submit failure', async () => {
    const errorMessage = 'Email déjà utilisé'
    mockOnSubmit.mockRejectedValue({
      response: {
        data: {
          detail: errorMessage,
        },
      },
    })

    render(<InviteUserModal onClose={mockOnClose} onSubmit={mockOnSubmit} />)

    // Remplir le formulaire
    fireEvent.change(screen.getByLabelText(/prénom/i), {
      target: { value: 'Jean' },
    })
    fireEvent.change(screen.getByLabelText(/nom/i), {
      target: { value: 'Dupont' },
    })
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'jean.dupont@test.com' },
    })

    // Soumettre
    const submitButton = screen.getByText(/envoyer l'invitation/i)
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(errorMessage)).toBeInTheDocument()
    })
  })

  it('should allow changing role', () => {
    render(<InviteUserModal onClose={mockOnClose} onSubmit={mockOnSubmit} />)

    const roleSelect = screen.getByLabelText(/rôle/i)
    fireEvent.change(roleSelect, { target: { value: 'chef' } })

    expect(roleSelect).toHaveValue('chef')
  })

  it('should focus first input on mount', () => {
    render(<InviteUserModal onClose={mockOnClose} onSubmit={mockOnSubmit} />)

    const prenomInput = screen.getByLabelText(/prénom/i)
    expect(prenomInput).toHaveFocus()
  })

  it('should show loading state during submit', async () => {
    mockOnSubmit.mockImplementation(
      () => new Promise((resolve) => setTimeout(resolve, 100))
    )

    render(<InviteUserModal onClose={mockOnClose} onSubmit={mockOnSubmit} />)

    // Remplir le formulaire
    fireEvent.change(screen.getByLabelText(/prénom/i), {
      target: { value: 'Jean' },
    })
    fireEvent.change(screen.getByLabelText(/nom/i), {
      target: { value: 'Dupont' },
    })
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'jean.dupont@test.com' },
    })

    // Soumettre
    const submitButton = screen.getByText(/envoyer l'invitation/i)
    fireEvent.click(submitButton)

    // Vérifier l'état de chargement
    await waitFor(() => {
      expect(submitButton).toBeDisabled()
    })
  })
})
