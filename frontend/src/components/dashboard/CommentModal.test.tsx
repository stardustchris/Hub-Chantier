/**
 * Tests pour CommentModal
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import CommentModal from './CommentModal'
import { dashboardService } from '../../services/dashboard'

// Mock du service dashboard
vi.mock('../../services/dashboard', () => ({
  dashboardService: {
    addComment: vi.fn(),
  },
}))

// Mock de MentionInput (composant complexe)
vi.mock('../common/MentionInput', () => ({
  default: ({ value, onChange, placeholder, disabled }: { value: string; onChange: (v: string) => void; placeholder?: string; disabled?: boolean }) => (
    <textarea
      data-testid="mention-input"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      disabled={disabled}
    />
  ),
}))

describe('CommentModal', () => {
  const defaultProps = {
    isOpen: true,
    onClose: vi.fn(),
    postId: 123,
    postAuthor: 'Jean Dupont',
    onCommentAdded: vi.fn(),
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('ne rend rien si isOpen est false', () => {
    const { container } = render(<CommentModal {...defaultProps} isOpen={false} />)

    expect(container).toBeEmptyDOMElement()
  })

  it('affiche le modal si isOpen est true', () => {
    render(<CommentModal {...defaultProps} />)

    expect(screen.getByText('Repondre a Jean Dupont')).toBeInTheDocument()
  })

  it('affiche le nom de l\'auteur du post', () => {
    render(<CommentModal {...defaultProps} postAuthor="Marie Martin" />)

    expect(screen.getByText('Repondre a Marie Martin')).toBeInTheDocument()
  })

  it('affiche le bouton Annuler', () => {
    render(<CommentModal {...defaultProps} />)

    expect(screen.getByText('Annuler')).toBeInTheDocument()
  })

  it('affiche le bouton Envoyer', () => {
    render(<CommentModal {...defaultProps} />)

    expect(screen.getByText('Envoyer')).toBeInTheDocument()
  })

  it('appelle onClose au clic sur Annuler', () => {
    const onClose = vi.fn()
    render(<CommentModal {...defaultProps} onClose={onClose} />)

    fireEvent.click(screen.getByText('Annuler'))

    expect(onClose).toHaveBeenCalled()
  })

  it('appelle onClose au clic sur le bouton fermer', () => {
    const onClose = vi.fn()
    render(<CommentModal {...defaultProps} onClose={onClose} />)

    // Le bouton X
    const closeButton = screen.getByRole('button', { name: '' })
    fireEvent.click(closeButton)

    expect(onClose).toHaveBeenCalled()
  })

  it('appelle onClose au clic sur l\'overlay', () => {
    const onClose = vi.fn()
    render(<CommentModal {...defaultProps} onClose={onClose} />)

    // Clic sur l'overlay (premier div avec bg-black)
    const overlay = document.querySelector('.bg-black')
    if (overlay) {
      fireEvent.click(overlay)
    }

    expect(onClose).toHaveBeenCalled()
  })

  it('desactive le bouton Envoyer si le contenu est vide', () => {
    render(<CommentModal {...defaultProps} />)

    const submitButton = screen.getByText('Envoyer').closest('button')
    expect(submitButton).toBeDisabled()
  })

  it('active le bouton Envoyer si le contenu n\'est pas vide', () => {
    render(<CommentModal {...defaultProps} />)

    const textarea = screen.getByTestId('mention-input')
    fireEvent.change(textarea, { target: { value: 'Mon commentaire' } })

    const submitButton = screen.getByText('Envoyer').closest('button')
    expect(submitButton).not.toBeDisabled()
  })

  it('affiche une erreur si le commentaire est vide lors de la soumission', async () => {
    render(<CommentModal {...defaultProps} />)

    // Forcer la soumission avec un contenu vide (contourner le disabled)
    const form = document.querySelector('form')
    if (form) {
      fireEvent.submit(form)
    }

    await waitFor(() => {
      expect(screen.getByText('Le commentaire ne peut pas etre vide')).toBeInTheDocument()
    })
  })

  it('appelle dashboardService.addComment lors de la soumission', async () => {
    vi.mocked(dashboardService.addComment).mockResolvedValue(undefined as never)

    render(<CommentModal {...defaultProps} />)

    const textarea = screen.getByTestId('mention-input')
    fireEvent.change(textarea, { target: { value: 'Mon commentaire' } })

    const submitButton = screen.getByText('Envoyer').closest('button')
    fireEvent.click(submitButton!)

    await waitFor(() => {
      expect(dashboardService.addComment).toHaveBeenCalledWith('123', { contenu: 'Mon commentaire' })
    })
  })

  it('appelle onCommentAdded apres un ajout reussi', async () => {
    vi.mocked(dashboardService.addComment).mockResolvedValue(undefined as never)
    const onCommentAdded = vi.fn()

    render(<CommentModal {...defaultProps} onCommentAdded={onCommentAdded} />)

    const textarea = screen.getByTestId('mention-input')
    fireEvent.change(textarea, { target: { value: 'Mon commentaire' } })

    const submitButton = screen.getByText('Envoyer').closest('button')
    fireEvent.click(submitButton!)

    await waitFor(() => {
      expect(onCommentAdded).toHaveBeenCalled()
    })
  })

  it('appelle onClose apres un ajout reussi', async () => {
    vi.mocked(dashboardService.addComment).mockResolvedValue(undefined as never)
    const onClose = vi.fn()

    render(<CommentModal {...defaultProps} onClose={onClose} />)

    const textarea = screen.getByTestId('mention-input')
    fireEvent.change(textarea, { target: { value: 'Mon commentaire' } })

    const submitButton = screen.getByText('Envoyer').closest('button')
    fireEvent.click(submitButton!)

    await waitFor(() => {
      expect(onClose).toHaveBeenCalled()
    })
  })

  it('affiche une erreur si l\'ajout echoue', async () => {
    vi.mocked(dashboardService.addComment).mockRejectedValue(new Error('Network error'))

    render(<CommentModal {...defaultProps} />)

    const textarea = screen.getByTestId('mention-input')
    fireEvent.change(textarea, { target: { value: 'Mon commentaire' } })

    const submitButton = screen.getByText('Envoyer').closest('button')
    fireEvent.click(submitButton!)

    await waitFor(() => {
      expect(screen.getByText("Erreur lors de l'ajout du commentaire")).toBeInTheDocument()
    })
  })

  it('affiche le loader pendant l\'envoi', async () => {
    vi.mocked(dashboardService.addComment).mockImplementation(
      () => new Promise((resolve) => setTimeout(resolve, 100))
    )

    render(<CommentModal {...defaultProps} />)

    const textarea = screen.getByTestId('mention-input')
    fireEvent.change(textarea, { target: { value: 'Mon commentaire' } })

    const submitButton = screen.getByText('Envoyer').closest('button')
    fireEvent.click(submitButton!)

    expect(screen.getByText('Envoi...')).toBeInTheDocument()
  })

  it('desactive les boutons pendant l\'envoi', async () => {
    vi.mocked(dashboardService.addComment).mockImplementation(
      () => new Promise((resolve) => setTimeout(resolve, 100))
    )

    render(<CommentModal {...defaultProps} />)

    const textarea = screen.getByTestId('mention-input')
    fireEvent.change(textarea, { target: { value: 'Mon commentaire' } })

    const submitButton = screen.getByText('Envoyer').closest('button')
    fireEvent.click(submitButton!)

    expect(screen.getByText('Annuler').closest('button')).toBeDisabled()
  })

  it('trim le contenu avant envoi', async () => {
    vi.mocked(dashboardService.addComment).mockResolvedValue(undefined as never)

    render(<CommentModal {...defaultProps} />)

    const textarea = screen.getByTestId('mention-input')
    fireEvent.change(textarea, { target: { value: '  Mon commentaire  ' } })

    const submitButton = screen.getByText('Envoyer').closest('button')
    fireEvent.click(submitButton!)

    await waitFor(() => {
      expect(dashboardService.addComment).toHaveBeenCalledWith('123', { contenu: 'Mon commentaire' })
    })
  })
})
