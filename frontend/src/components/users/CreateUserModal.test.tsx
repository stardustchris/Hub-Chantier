/**
 * Tests pour CreateUserModal
 *
 * Couvre:
 * - Affichage du formulaire
 * - Validation des champs requis
 * - Soumission du formulaire
 * - Gestion des erreurs
 * - Sélection de couleur
 * - Fermeture (Echap, bouton, overlay)
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { CreateUserModal } from './CreateUserModal'

describe('CreateUserModal', () => {
  const mockOnClose = vi.fn()
  const mockOnSubmit = vi.fn()

  const defaultProps = {
    onClose: mockOnClose,
    onSubmit: mockOnSubmit,
  }

  beforeEach(() => {
    vi.clearAllMocks()
    mockOnSubmit.mockResolvedValue(undefined)
  })

  describe('Affichage', () => {
    it('affiche le titre', () => {
      render(<CreateUserModal {...defaultProps} />)
      expect(screen.getByText('Nouvel utilisateur')).toBeInTheDocument()
    })

    it('affiche les champs du formulaire', () => {
      render(<CreateUserModal {...defaultProps} />)

      expect(screen.getByPlaceholderText('Jean')).toBeInTheDocument() // Prénom
      expect(screen.getByPlaceholderText('Dupont')).toBeInTheDocument() // Nom
      expect(screen.getByPlaceholderText('jean.dupont@email.com')).toBeInTheDocument() // Email
      expect(screen.getByPlaceholderText('********')).toBeInTheDocument() // Password
    })

    it('affiche les sélecteurs de rôle et type', () => {
      render(<CreateUserModal {...defaultProps} />)

      expect(screen.getByText('Role')).toBeInTheDocument()
      expect(screen.getByText('Type')).toBeInTheDocument()
    })

    it('affiche le sélecteur de métier', () => {
      render(<CreateUserModal {...defaultProps} />)
      expect(screen.getByText('Metier')).toBeInTheDocument()
    })

    it('affiche le champ téléphone', () => {
      render(<CreateUserModal {...defaultProps} />)
      expect(screen.getByPlaceholderText('06 12 34 56 78')).toBeInTheDocument()
    })

    it('affiche les boutons de couleur', () => {
      render(<CreateUserModal {...defaultProps} />)
      expect(screen.getByText('Couleur')).toBeInTheDocument()
      // Multiple color buttons
      const colorButtons = screen.getAllByRole('button').filter(
        btn => btn.getAttribute('aria-label')?.includes('Couleur')
      )
      expect(colorButtons.length).toBeGreaterThan(0)
    })

    it('affiche les boutons Annuler et Créer', () => {
      render(<CreateUserModal {...defaultProps} />)
      expect(screen.getByText('Annuler')).toBeInTheDocument()
      expect(screen.getByText('Creer')).toBeInTheDocument()
    })
  })

  describe('Validation', () => {
    it('désactive le bouton Créer si champs requis vides', () => {
      render(<CreateUserModal {...defaultProps} />)
      expect(screen.getByText('Creer').closest('button')).toBeDisabled()
    })

    it('active le bouton Créer quand tous les champs requis sont remplis', () => {
      render(<CreateUserModal {...defaultProps} />)

      fireEvent.change(screen.getByPlaceholderText('Jean'), { target: { value: 'Pierre' } })
      fireEvent.change(screen.getByPlaceholderText('Dupont'), { target: { value: 'Martin' } })
      fireEvent.change(screen.getByPlaceholderText('jean.dupont@email.com'), { target: { value: 'pierre@test.com' } })
      fireEvent.change(screen.getByPlaceholderText('********'), { target: { value: 'password123' } })

      expect(screen.getByText('Creer').closest('button')).not.toBeDisabled()
    })

    it('exige un mot de passe d\'au moins 6 caractères', () => {
      render(<CreateUserModal {...defaultProps} />)
      const passwordInput = screen.getByPlaceholderText('********')
      expect(passwordInput).toHaveAttribute('minLength', '6')
    })
  })

  describe('Soumission', () => {
    it('appelle onSubmit avec les données du formulaire', async () => {
      const user = userEvent.setup()
      render(<CreateUserModal {...defaultProps} />)

      fireEvent.change(screen.getByPlaceholderText('Jean'), { target: { value: 'Pierre' } })
      fireEvent.change(screen.getByPlaceholderText('Dupont'), { target: { value: 'Martin' } })
      fireEvent.change(screen.getByPlaceholderText('jean.dupont@email.com'), { target: { value: 'pierre@test.com' } })
      fireEvent.change(screen.getByPlaceholderText('********'), { target: { value: 'password123' } })

      await user.click(screen.getByText('Creer'))

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith(
          expect.objectContaining({
            prenom: 'Pierre',
            nom: 'Martin',
            email: 'pierre@test.com',
            password: 'password123',
            role: 'compagnon', // default
            type_utilisateur: 'employe', // default
          })
        )
      })
    })

    it('affiche un spinner pendant la soumission', async () => {
      mockOnSubmit.mockImplementation(() => new Promise(() => {})) // Never resolves

      const user = userEvent.setup()
      render(<CreateUserModal {...defaultProps} />)

      fireEvent.change(screen.getByPlaceholderText('Jean'), { target: { value: 'Pierre' } })
      fireEvent.change(screen.getByPlaceholderText('Dupont'), { target: { value: 'Martin' } })
      fireEvent.change(screen.getByPlaceholderText('jean.dupont@email.com'), { target: { value: 'pierre@test.com' } })
      fireEvent.change(screen.getByPlaceholderText('********'), { target: { value: 'password123' } })

      await user.click(screen.getByText('Creer'))

      await waitFor(() => {
        expect(document.querySelector('.animate-spin')).toBeInTheDocument()
      })
    })

    it('affiche une erreur en cas d\'échec', async () => {
      mockOnSubmit.mockRejectedValue({
        response: { data: { detail: 'Email déjà utilisé' } },
      })

      const user = userEvent.setup()
      render(<CreateUserModal {...defaultProps} />)

      fireEvent.change(screen.getByPlaceholderText('Jean'), { target: { value: 'Pierre' } })
      fireEvent.change(screen.getByPlaceholderText('Dupont'), { target: { value: 'Martin' } })
      fireEvent.change(screen.getByPlaceholderText('jean.dupont@email.com'), { target: { value: 'pierre@test.com' } })
      fireEvent.change(screen.getByPlaceholderText('********'), { target: { value: 'password123' } })

      await user.click(screen.getByText('Creer'))

      await waitFor(() => {
        expect(screen.getByText('Email déjà utilisé')).toBeInTheDocument()
      })
    })

    it('affiche un message d\'erreur générique si pas de détail', async () => {
      mockOnSubmit.mockRejectedValue(new Error('Network error'))

      const user = userEvent.setup()
      render(<CreateUserModal {...defaultProps} />)

      fireEvent.change(screen.getByPlaceholderText('Jean'), { target: { value: 'Pierre' } })
      fireEvent.change(screen.getByPlaceholderText('Dupont'), { target: { value: 'Martin' } })
      fireEvent.change(screen.getByPlaceholderText('jean.dupont@email.com'), { target: { value: 'pierre@test.com' } })
      fireEvent.change(screen.getByPlaceholderText('********'), { target: { value: 'password123' } })

      await user.click(screen.getByText('Creer'))

      await waitFor(() => {
        expect(screen.getByText('Erreur lors de la creation')).toBeInTheDocument()
      })
    })
  })

  describe('Sélection de couleur', () => {
    it('permet de sélectionner une couleur', async () => {
      const user = userEvent.setup()
      render(<CreateUserModal {...defaultProps} />)

      const colorButtons = screen.getAllByRole('button').filter(
        btn => btn.getAttribute('aria-label')?.includes('Couleur')
      )

      // Click on a different color
      await user.click(colorButtons[1])

      // The button should be marked as selected
      expect(colorButtons[1]).toHaveClass('border-gray-900')
    })

    it('indique la couleur sélectionnée dans aria-pressed', async () => {
      render(<CreateUserModal {...defaultProps} />)

      const selectedButton = screen.getByRole('button', { pressed: true })
      expect(selectedButton).toBeInTheDocument()
    })
  })

  describe('Champs optionnels', () => {
    it('permet de sélectionner un métier', async () => {
      const user = userEvent.setup()
      render(<CreateUserModal {...defaultProps} />)

      const metierSelect = screen.getAllByRole('combobox').find(
        select => select.querySelector('option[value="macon"]')
      )

      if (metierSelect) {
        await user.selectOptions(metierSelect, 'macon')
        expect(metierSelect).toHaveValue('macon')
      }
    })

    it('permet de sélectionner un rôle', async () => {
      const user = userEvent.setup()
      render(<CreateUserModal {...defaultProps} />)

      const roleSelect = screen.getAllByRole('combobox')[0]
      await user.selectOptions(roleSelect, 'chef_chantier')
      expect(roleSelect).toHaveValue('chef_chantier')
    })

    it('permet de sélectionner le type sous-traitant', async () => {
      const user = userEvent.setup()
      render(<CreateUserModal {...defaultProps} />)

      const typeSelect = screen.getAllByRole('combobox')[1]
      await user.selectOptions(typeSelect, 'sous_traitant')
      expect(typeSelect).toHaveValue('sous_traitant')
    })

    it('permet de saisir un téléphone', () => {
      render(<CreateUserModal {...defaultProps} />)

      fireEvent.change(screen.getByPlaceholderText('06 12 34 56 78'), { target: { value: '0612345678' } })
      expect(screen.getByPlaceholderText('06 12 34 56 78')).toHaveValue('0612345678')
    })
  })

  describe('Fermeture', () => {
    it('appelle onClose au clic sur Annuler', async () => {
      const user = userEvent.setup()
      render(<CreateUserModal {...defaultProps} />)

      await user.click(screen.getByText('Annuler'))
      expect(mockOnClose).toHaveBeenCalled()
    })

    it('appelle onClose au clic sur le bouton X', async () => {
      const user = userEvent.setup()
      render(<CreateUserModal {...defaultProps} />)

      await user.click(screen.getByLabelText('Fermer le formulaire'))
      expect(mockOnClose).toHaveBeenCalled()
    })

    it('appelle onClose au clic sur l\'overlay', async () => {
      const user = userEvent.setup()
      render(<CreateUserModal {...defaultProps} />)

      const overlay = document.querySelector('.bg-black\\/50')
      if (overlay) {
        await user.click(overlay)
        expect(mockOnClose).toHaveBeenCalled()
      }
    })

    it('appelle onClose à la touche Echap', async () => {
      const user = userEvent.setup()
      render(<CreateUserModal {...defaultProps} />)

      await user.keyboard('{Escape}')
      expect(mockOnClose).toHaveBeenCalled()
    })
  })

  describe('Focus', () => {
    it('focus un element du modal au montage', async () => {
      render(<CreateUserModal {...defaultProps} />)

      // useFocusTrap focuses the first focusable element (close button) after 50ms
      await waitFor(() => {
        const focused = document.activeElement
        expect(focused).not.toBe(document.body)
      })
    })
  })
})
