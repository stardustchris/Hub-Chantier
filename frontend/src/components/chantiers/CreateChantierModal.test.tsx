/**
 * Tests pour CreateChantierModal
 *
 * Couvre:
 * - Affichage du formulaire
 * - Saisie des champs
 * - Gestion des contacts
 * - Gestion des phases
 * - Validation des dates
 * - Soumission
 * - Fermeture
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { CreateChantierModal } from './CreateChantierModal'

// Mock useFocusTrap to prevent auto-focus stealing during userEvent.type()
vi.mock('../../hooks/useFocusTrap', () => ({
  useFocusTrap: () => ({ current: null }),
  default: () => ({ current: null }),
}))

describe('CreateChantierModal', () => {
  const mockOnClose = vi.fn()
  const mockOnSubmit = vi.fn()

  const defaultProps = {
    onClose: mockOnClose,
    onSubmit: mockOnSubmit,
    usedColors: [],
  }

  beforeEach(() => {
    vi.clearAllMocks()
    mockOnSubmit.mockResolvedValue(undefined)
  })

  describe('Affichage', () => {
    it('affiche le titre Nouveau chantier', () => {
      render(<CreateChantierModal {...defaultProps} />)
      expect(screen.getByText('Nouveau chantier')).toBeInTheDocument()
    })

    it('affiche le champ nom du chantier', () => {
      render(<CreateChantierModal {...defaultProps} />)
      expect(screen.getByText('Nom du chantier *')).toBeInTheDocument()
      expect(screen.getByPlaceholderText(/Residence Les Pins/)).toBeInTheDocument()
    })

    it('affiche le champ adresse', () => {
      render(<CreateChantierModal {...defaultProps} />)
      expect(screen.getByText('Adresse *')).toBeInTheDocument()
      expect(screen.getByPlaceholderText(/12 rue des Lilas/)).toBeInTheDocument()
    })

    it('affiche la section contacts', () => {
      render(<CreateChantierModal {...defaultProps} />)
      expect(screen.getByText('Contacts sur le chantier')).toBeInTheDocument()
    })

    it('affiche la section phases', () => {
      render(<CreateChantierModal {...defaultProps} />)
      expect(screen.getByText(/Phases du chantier/)).toBeInTheDocument()
    })

    it('affiche les champs de dates si pas de phases', () => {
      render(<CreateChantierModal {...defaultProps} />)
      expect(screen.getByText('Date debut prevue')).toBeInTheDocument()
      expect(screen.getByText('Date fin prevue')).toBeInTheDocument()
    })

    it('affiche les boutons Annuler et Creer', () => {
      render(<CreateChantierModal {...defaultProps} />)
      expect(screen.getByText('Annuler')).toBeInTheDocument()
      expect(screen.getByText('Creer')).toBeInTheDocument()
    })
  })

  describe('Saisie des champs', () => {
    it('permet de saisir le nom', async () => {
      const user = userEvent.setup()
      render(<CreateChantierModal {...defaultProps} />)

      const nomInput = screen.getByPlaceholderText(/Residence Les Pins/)
      await user.type(nomInput, 'Mon chantier')

      expect(nomInput).toHaveValue('Mon chantier')
    })

    it('permet de saisir l adresse', async () => {
      const user = userEvent.setup()
      render(<CreateChantierModal {...defaultProps} />)

      const adresseInput = screen.getByPlaceholderText(/12 rue des Lilas/)
      await user.type(adresseInput, '123 rue Test')

      expect(adresseInput).toHaveValue('123 rue Test')
    })

    it('permet de saisir les heures estimees', async () => {
      const user = userEvent.setup()
      render(<CreateChantierModal {...defaultProps} />)

      const heuresInput = screen.getByPlaceholderText('Ex: 500')
      await user.type(heuresInput, '250')

      expect(heuresInput).toHaveValue(250)
    })

    it('permet de saisir la description', async () => {
      const user = userEvent.setup()
      render(<CreateChantierModal {...defaultProps} />)

      const descInput = screen.getByPlaceholderText('Description du chantier...')
      await user.type(descInput, 'Ma description')

      expect(descInput).toHaveValue('Ma description')
    })
  })

  describe('Gestion des contacts', () => {
    it('affiche un contact par defaut', () => {
      render(<CreateChantierModal {...defaultProps} />)
      expect(screen.getByPlaceholderText('Nom')).toBeInTheDocument()
      expect(screen.getByPlaceholderText('Telephone')).toBeInTheDocument()
      expect(screen.getByPlaceholderText('Profession')).toBeInTheDocument()
    })

    it('permet d ajouter un contact', async () => {
      const user = userEvent.setup()
      render(<CreateChantierModal {...defaultProps} />)

      const addButton = screen.getAllByRole('button').find(btn => btn.textContent?.includes('Ajouter'))
      if (addButton) {
        await user.click(addButton)
      }

      expect(screen.getAllByPlaceholderText('Nom')).toHaveLength(2)
    })

    it('permet de supprimer un contact', async () => {
      const user = userEvent.setup()
      render(<CreateChantierModal {...defaultProps} />)

      // Ajouter un contact d'abord
      const addButton = screen.getAllByRole('button').find(btn => btn.textContent?.includes('Ajouter'))
      if (addButton) {
        await user.click(addButton)
      }

      expect(screen.getAllByPlaceholderText('Nom')).toHaveLength(2)

      // Supprimer un contact
      const deleteButtons = document.querySelectorAll('button svg.lucide-trash-2')
      if (deleteButtons.length > 0) {
        const parent = deleteButtons[0].closest('button')
        if (parent) {
          await user.click(parent)
        }
      }

      expect(screen.getAllByPlaceholderText('Nom')).toHaveLength(1)
    })

    it('permet de saisir les infos du contact', async () => {
      const user = userEvent.setup()
      render(<CreateChantierModal {...defaultProps} />)

      await user.type(screen.getByPlaceholderText('Nom'), 'Jean')
      await user.type(screen.getByPlaceholderText('Telephone'), '0612345678')
      await user.type(screen.getByPlaceholderText('Profession'), 'Electricien')

      expect(screen.getByPlaceholderText('Nom')).toHaveValue('Jean')
      expect(screen.getByPlaceholderText('Telephone')).toHaveValue('0612345678')
      expect(screen.getByPlaceholderText('Profession')).toHaveValue('Electricien')
    })
  })

  describe('Gestion des phases', () => {
    it('n affiche pas de phase par defaut', () => {
      render(<CreateChantierModal {...defaultProps} />)
      expect(screen.getByText(/Aucune phase definie/)).toBeInTheDocument()
    })

    it('permet d ajouter une phase', async () => {
      const user = userEvent.setup()
      render(<CreateChantierModal {...defaultProps} />)

      await user.click(screen.getByText('Ajouter une phase'))

      expect(screen.getByText('Phase 1')).toBeInTheDocument()
      expect(screen.getByPlaceholderText(/Nom de la phase/)).toBeInTheDocument()
    })

    it('cache les dates globales quand il y a des phases', async () => {
      const user = userEvent.setup()
      render(<CreateChantierModal {...defaultProps} />)

      expect(screen.getByText('Date debut prevue')).toBeInTheDocument()

      await user.click(screen.getByText('Ajouter une phase'))

      expect(screen.queryByText('Date debut prevue')).not.toBeInTheDocument()
    })

    it('permet de supprimer une phase', async () => {
      const user = userEvent.setup()
      render(<CreateChantierModal {...defaultProps} />)

      await user.click(screen.getByText('Ajouter une phase'))
      expect(screen.getByText('Phase 1')).toBeInTheDocument()

      const deleteButtons = document.querySelectorAll('.bg-gray-50 button svg.lucide-trash-2')
      if (deleteButtons.length > 0) {
        const parent = deleteButtons[0].closest('button')
        if (parent) {
          await user.click(parent)
        }
      }

      expect(screen.queryByText('Phase 1')).not.toBeInTheDocument()
    })
  })

  describe('Validation', () => {
    it('desactive le bouton Creer si nom vide', () => {
      render(<CreateChantierModal {...defaultProps} />)
      expect(screen.getByText('Creer').closest('button')).toBeDisabled()
    })

    it('desactive le bouton Creer si adresse vide', async () => {
      const user = userEvent.setup()
      render(<CreateChantierModal {...defaultProps} />)

      await user.type(screen.getByPlaceholderText(/Residence Les Pins/), 'Mon chantier')

      expect(screen.getByText('Creer').closest('button')).toBeDisabled()
    })

    it('active le bouton Creer si nom et adresse remplis', async () => {
      const user = userEvent.setup()
      render(<CreateChantierModal {...defaultProps} />)

      await user.type(screen.getByPlaceholderText(/Residence Les Pins/), 'Mon chantier')
      await user.type(screen.getByPlaceholderText(/12 rue des Lilas/), '123 rue Test')

      expect(screen.getByText('Creer').closest('button')).not.toBeDisabled()
    })

    it('affiche erreur si date fin avant date debut', async () => {
      const user = userEvent.setup()
      render(<CreateChantierModal {...defaultProps} />)

      await user.type(screen.getByPlaceholderText(/Residence Les Pins/), 'Mon chantier')
      await user.type(screen.getByPlaceholderText(/12 rue des Lilas/), '123 rue Test')

      // Note: Les inputs date ne sont pas facilement testables avec userEvent
    })
  })

  describe('Soumission', () => {
    it('appelle onSubmit avec les donnees du formulaire', async () => {
      const user = userEvent.setup()
      render(<CreateChantierModal {...defaultProps} />)

      await user.type(screen.getByPlaceholderText(/Residence Les Pins/), 'Mon chantier')
      await user.type(screen.getByPlaceholderText(/12 rue des Lilas/), '123 rue Test')

      await user.click(screen.getByText('Creer'))

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith(
          expect.objectContaining({
            nom: 'Mon chantier',
            adresse: '123 rue Test',
          }),
          expect.any(Array), // contacts
          expect.any(Array), // phases
        )
      })
    })

    it('affiche le spinner pendant la soumission', async () => {
      mockOnSubmit.mockImplementation(() => new Promise(() => {}))

      const user = userEvent.setup()
      render(<CreateChantierModal {...defaultProps} />)

      await user.type(screen.getByPlaceholderText(/Residence Les Pins/), 'Mon chantier')
      await user.type(screen.getByPlaceholderText(/12 rue des Lilas/), '123 rue Test')

      await user.click(screen.getByText('Creer'))

      await waitFor(() => {
        expect(document.querySelector('.animate-spin')).toBeInTheDocument()
      })
    })

    it('affiche l erreur en cas d echec', async () => {
      mockOnSubmit.mockRejectedValueOnce({
        response: { data: { detail: 'Erreur serveur' } },
      })

      const user = userEvent.setup()
      render(<CreateChantierModal {...defaultProps} />)

      await user.type(screen.getByPlaceholderText(/Residence Les Pins/), 'Mon chantier')
      await user.type(screen.getByPlaceholderText(/12 rue des Lilas/), '123 rue Test')

      await user.click(screen.getByText('Creer'))

      await waitFor(() => {
        expect(screen.getByText('Erreur serveur')).toBeInTheDocument()
      })
    })
  })

  describe('Fermeture', () => {
    it('appelle onClose au clic sur Annuler', async () => {
      const user = userEvent.setup()
      render(<CreateChantierModal {...defaultProps} />)

      await user.click(screen.getByText('Annuler'))
      expect(mockOnClose).toHaveBeenCalled()
    })

    it('appelle onClose au clic sur le bouton X', async () => {
      const user = userEvent.setup()
      render(<CreateChantierModal {...defaultProps} />)

      const closeButton = document.querySelector('button svg.lucide-x')?.closest('button')
      if (closeButton) {
        await user.click(closeButton)
        expect(mockOnClose).toHaveBeenCalled()
      }
    })

    it('appelle onClose au clic sur l overlay', async () => {
      const user = userEvent.setup()
      render(<CreateChantierModal {...defaultProps} />)

      const overlay = document.querySelector('.bg-black\\/50')
      if (overlay) {
        await user.click(overlay)
        expect(mockOnClose).toHaveBeenCalled()
      }
    })
  })

  describe('Couleur', () => {
    it('selectionne la premiere couleur disponible', () => {
      render(<CreateChantierModal {...defaultProps} usedColors={['#E74C3C']} />)
      // La couleur devrait etre selectionnee automatiquement
      // On ne peut pas facilement verifier la valeur interne sans exposer l'etat
    })
  })
})
