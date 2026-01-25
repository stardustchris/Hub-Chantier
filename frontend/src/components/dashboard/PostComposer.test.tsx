/**
 * Tests pour PostComposer
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import PostComposer from './PostComposer'

// Mock MentionInput
vi.mock('../common/MentionInput', () => ({
  default: ({ value, onChange, placeholder }: any) => (
    <textarea
      data-testid="mention-input"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
    />
  ),
}))

describe('PostComposer', () => {
  const mockOnSubmit = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    mockOnSubmit.mockResolvedValue(undefined)
  })

  const renderComposer = (props = {}) => {
    return render(
      <PostComposer
        onSubmit={mockOnSubmit}
        {...props}
      />
    )
  }

  describe('rendering', () => {
    it('affiche le champ de saisie', () => {
      renderComposer()
      expect(screen.getByTestId('mention-input')).toBeInTheDocument()
    })

    it('affiche le bouton Publier', () => {
      renderComposer()
      expect(screen.getByText('Publier')).toBeInTheDocument()
    })

    it('affiche le bouton Photo', () => {
      renderComposer()
      expect(screen.getByText('Photo')).toBeInTheDocument()
    })

    it('affiche le placeholder standard', () => {
      renderComposer()
      expect(screen.getByPlaceholderText(/Quoi de neuf/)).toBeInTheDocument()
    })
  })

  describe('mode compagnon', () => {
    it('affiche le placeholder compagnon', () => {
      renderComposer({ isCompagnon: true })
      expect(screen.getByPlaceholderText(/Partager une photo/)).toBeInTheDocument()
    })

    it('affiche Prendre une photo au lieu de Photo', () => {
      renderComposer({ isCompagnon: true })
      expect(screen.getByText('Prendre une photo')).toBeInTheDocument()
    })

    it('n affiche pas les options de ciblage', () => {
      renderComposer({ isCompagnon: true })
      expect(screen.queryByText('Tout le monde')).not.toBeInTheDocument()
    })

    it('n affiche pas le bouton Urgent', () => {
      renderComposer({ isCompagnon: true })
      expect(screen.queryByText('Urgent')).not.toBeInTheDocument()
    })
  })

  describe('ciblage (non compagnon)', () => {
    it('affiche le bouton de ciblage par defaut', () => {
      renderComposer()
      expect(screen.getByText('Tout le monde')).toBeInTheDocument()
    })

    it('ouvre le menu de ciblage au clic', async () => {
      const user = userEvent.setup()
      renderComposer()

      await user.click(screen.getByLabelText('Choisir le ciblage'))

      await waitFor(() => {
        expect(screen.getByText('📢 Tout le monde')).toBeInTheDocument()
        expect(screen.getByText('🏗️ Chantiers spécifiques')).toBeInTheDocument()
        expect(screen.getByText('👥 Personnes spécifiques')).toBeInTheDocument()
      })
    })

    it('change le ciblage au clic sur une option', async () => {
      const user = userEvent.setup()
      renderComposer()

      await user.click(screen.getByLabelText('Choisir le ciblage'))
      await user.click(screen.getByText('🏗️ Chantiers spécifiques'))

      expect(screen.getByText('Chantiers')).toBeInTheDocument()
    })
  })

  describe('marquage urgent', () => {
    it('affiche le bouton Urgent', () => {
      renderComposer()
      expect(screen.getByText('Urgent')).toBeInTheDocument()
    })

    it('toggle le marquage urgent au clic', async () => {
      const user = userEvent.setup()
      renderComposer()

      const urgentButton = screen.getByLabelText('Marquer comme urgent')
      await user.click(urgentButton)

      expect(screen.getByLabelText('Retirer le marquage urgent')).toBeInTheDocument()
    })
  })

  describe('soumission', () => {
    it('desactive Publier si contenu vide', () => {
      renderComposer()
      expect(screen.getByText('Publier')).toBeDisabled()
    })

    it('active Publier si contenu present', async () => {
      const user = userEvent.setup()
      renderComposer()

      await user.type(screen.getByTestId('mention-input'), 'Mon post')
      expect(screen.getByText('Publier')).not.toBeDisabled()
    })

    it('appelle onSubmit avec les bonnes donnees', async () => {
      const user = userEvent.setup()
      renderComposer()

      await user.type(screen.getByTestId('mention-input'), 'Mon nouveau post')
      await user.click(screen.getByText('Publier'))

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith({
          content: 'Mon nouveau post',
          target_type: 'everyone',
          is_urgent: false,
          chantier_ids: undefined,
        })
      })
    })

    it('vide le contenu apres soumission', async () => {
      const user = userEvent.setup()
      renderComposer()

      await user.type(screen.getByTestId('mention-input'), 'Mon post')
      await user.click(screen.getByText('Publier'))

      await waitFor(() => {
        expect(screen.getByTestId('mention-input')).toHaveValue('')
      })
    })

    it('inclut le chantier par defaut si fourni', async () => {
      const user = userEvent.setup()
      renderComposer({ defaultChantier: 42 })

      await user.type(screen.getByTestId('mention-input'), 'Post chantier')
      await user.click(screen.getByText('Publier'))

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith(
          expect.objectContaining({
            chantier_ids: [42],
          })
        )
      })
    })

    it('inclut is_urgent true si marque urgent', async () => {
      const user = userEvent.setup()
      renderComposer()

      await user.type(screen.getByTestId('mention-input'), 'Post urgent')
      await user.click(screen.getByLabelText('Marquer comme urgent'))
      await user.click(screen.getByText('Publier'))

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith(
          expect.objectContaining({
            is_urgent: true,
          })
        )
      })
    })
  })

  describe('avatar', () => {
    it('affiche l avatar avec emoji', () => {
      renderComposer()
      expect(screen.getByText('👤')).toBeInTheDocument()
    })
  })
})
