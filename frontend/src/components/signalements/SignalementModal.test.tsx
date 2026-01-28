/**
 * Tests pour SignalementModal
 *
 * Couvre:
 * - Mode creation vs edition
 * - Affichage du formulaire
 * - Saisie des champs
 * - Soumission
 * - Fermeture
 * - Gestion des erreurs
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import SignalementModal from './SignalementModal'
import { createMockSignalement } from '../../fixtures'
import type { Signalement } from '../../types/signalements'

// Mock services
const mockCreateSignalement = vi.fn()
const mockUpdateSignalement = vi.fn()

vi.mock('../../services/signalements', () => ({
  createSignalement: (...args: unknown[]) => mockCreateSignalement(...args),
  updateSignalement: (...args: unknown[]) => mockUpdateSignalement(...args),
}))


describe('SignalementModal', () => {
  const mockOnClose = vi.fn()
  const mockOnSuccess = vi.fn()

  const defaultUsers = [
    { id: 1, nom: 'Jean Dupont' },
    { id: 2, nom: 'Marie Martin' },
  ]

  const defaultProps = {
    isOpen: true,
    onClose: mockOnClose,
    onSuccess: mockOnSuccess,
    chantierId: 1,
    users: defaultUsers,
  }

  beforeEach(() => {
    vi.clearAllMocks()
    mockCreateSignalement.mockResolvedValue(createMockSignalement())
    mockUpdateSignalement.mockResolvedValue(createMockSignalement())
  })

  describe('Rendu conditionnel', () => {
    it('ne rend rien si isOpen est false', () => {
      render(<SignalementModal {...defaultProps} isOpen={false} />)
      expect(screen.queryByText('Nouveau signalement')).not.toBeInTheDocument()
    })

    it('rend le modal si isOpen est true', () => {
      render(<SignalementModal {...defaultProps} />)
      expect(screen.getByText('Nouveau signalement')).toBeInTheDocument()
    })
  })

  describe('Mode creation', () => {
    it('affiche le titre Nouveau signalement', () => {
      render(<SignalementModal {...defaultProps} />)
      expect(screen.getByText('Nouveau signalement')).toBeInTheDocument()
    })

    it('affiche les champs vides', () => {
      render(<SignalementModal {...defaultProps} />)

      expect(screen.getByPlaceholderText('Titre du signalement')).toHaveValue('')
      expect(screen.getByPlaceholderText('Décrivez le problème en détail...')).toHaveValue('')
    })

    it('affiche la priorite par defaut moyenne', () => {
      render(<SignalementModal {...defaultProps} />)

      const prioriteSelect = screen.getByLabelText('Priorité')
      expect(prioriteSelect).toHaveValue('moyenne')
    })

    it('affiche le bouton Creer', () => {
      render(<SignalementModal {...defaultProps} />)
      expect(screen.getByText('Créer')).toBeInTheDocument()
    })
  })

  describe('Mode edition', () => {
    it('affiche le titre Modifier le signalement', () => {
      render(<SignalementModal {...defaultProps} signalement={createMockSignalement()} />)
      expect(screen.getByText('Modifier le signalement')).toBeInTheDocument()
    })

    it('preremplit les champs avec les valeurs existantes', () => {
      render(<SignalementModal {...defaultProps} signalement={createMockSignalement()} />)

      expect(screen.getByDisplayValue('Signalement existant')).toBeInTheDocument()
      expect(screen.getByDisplayValue('Description existante')).toBeInTheDocument()
    })

    it('affiche le bouton Modifier', () => {
      render(<SignalementModal {...defaultProps} signalement={createMockSignalement()} />)
      expect(screen.getByText('Modifier')).toBeInTheDocument()
    })
  })

  describe('Formulaire', () => {
    it('affiche tous les champs requis', () => {
      render(<SignalementModal {...defaultProps} />)

      expect(screen.getByLabelText('Titre *')).toBeInTheDocument()
      expect(screen.getByLabelText('Description *')).toBeInTheDocument()
      expect(screen.getByLabelText('Priorité')).toBeInTheDocument()
      expect(screen.getByLabelText('Assigner à')).toBeInTheDocument()
      expect(screen.getByLabelText('Date de résolution souhaitée')).toBeInTheDocument()
      expect(screen.getByLabelText('Localisation')).toBeInTheDocument()
      expect(screen.getByLabelText('URL de la photo')).toBeInTheDocument()
    })

    it('affiche les utilisateurs dans le selecteur', () => {
      render(<SignalementModal {...defaultProps} />)

      const assigneSelect = screen.getByLabelText('Assigner à')
      expect(assigneSelect).toContainHTML('Jean Dupont')
      expect(assigneSelect).toContainHTML('Marie Martin')
    })

    it('affiche l option Non assigne', () => {
      render(<SignalementModal {...defaultProps} />)

      const assigneSelect = screen.getByLabelText('Assigner à')
      expect(assigneSelect).toContainHTML('Non assigné')
    })
  })

  describe('Saisie des champs', () => {
    it('permet de saisir le titre', async () => {
      const user = userEvent.setup()
      render(<SignalementModal {...defaultProps} />)

      const titreInput = screen.getByPlaceholderText('Titre du signalement')
      await user.type(titreInput, 'Nouveau titre')

      expect(titreInput).toHaveValue('Nouveau titre')
    })

    it('permet de saisir la description', async () => {
      const user = userEvent.setup()
      render(<SignalementModal {...defaultProps} />)

      const descriptionInput = screen.getByPlaceholderText('Décrivez le problème en détail...')
      await user.type(descriptionInput, 'Nouvelle description')

      expect(descriptionInput).toHaveValue('Nouvelle description')
    })

    it('permet de changer la priorite', async () => {
      const user = userEvent.setup()
      render(<SignalementModal {...defaultProps} />)

      const prioriteSelect = screen.getByLabelText('Priorité')
      await user.selectOptions(prioriteSelect, 'critique')

      expect(prioriteSelect).toHaveValue('critique')
    })

    it('permet de saisir la localisation', async () => {
      const user = userEvent.setup()
      render(<SignalementModal {...defaultProps} />)

      const localisationInput = screen.getByPlaceholderText('Ex: Étage 2, Salle B...')
      await user.type(localisationInput, 'Bureau 101')

      expect(localisationInput).toHaveValue('Bureau 101')
    })
  })

  describe('Soumission - Creation', () => {
    it('appelle createSignalement avec les donnees saisies', async () => {
      const user = userEvent.setup()
      render(<SignalementModal {...defaultProps} />)

      await user.type(screen.getByPlaceholderText('Titre du signalement'), 'Mon signalement')
      await user.type(screen.getByPlaceholderText('Décrivez le problème en détail...'), 'Description detaillee')
      await user.selectOptions(screen.getByLabelText('Priorité'), 'haute')
      await user.selectOptions(screen.getByLabelText('Assigner à'), '2')

      await user.click(screen.getByText('Créer'))

      await waitFor(() => {
        expect(mockCreateSignalement).toHaveBeenCalledWith(
          expect.objectContaining({
            chantier_id: 1,
            titre: 'Mon signalement',
            description: 'Description detaillee',
            priorite: 'haute',
            assigne_a: 2,
          })
        )
      })
    })

    it('appelle onSuccess apres creation reussie', async () => {
      const createdSignalement = createMockSignalement({ id: 99, titre: 'Cree' })
      mockCreateSignalement.mockResolvedValueOnce(createdSignalement)

      const user = userEvent.setup()
      render(<SignalementModal {...defaultProps} />)

      await user.type(screen.getByPlaceholderText('Titre du signalement'), 'Titre')
      await user.type(screen.getByPlaceholderText('Décrivez le problème en détail...'), 'Description')

      await user.click(screen.getByText('Créer'))

      await waitFor(() => {
        expect(mockOnSuccess).toHaveBeenCalledWith(createdSignalement)
        expect(mockOnClose).toHaveBeenCalled()
      })
    })
  })

  describe('Soumission - Edition', () => {
    it('appelle updateSignalement avec les donnees modifiees', async () => {
      const user = userEvent.setup()
      render(<SignalementModal {...defaultProps} signalement={createMockSignalement()} />)

      const titreInput = screen.getByDisplayValue('Signalement existant')
      await user.clear(titreInput)
      await user.type(titreInput, 'Titre modifie')

      await user.click(screen.getByText('Modifier'))

      await waitFor(() => {
        expect(mockUpdateSignalement).toHaveBeenCalledWith(
          1,
          expect.objectContaining({
            titre: 'Titre modifie',
          })
        )
      })
    })
  })

  describe('Etat de chargement', () => {
    it('affiche Enregistrement pendant la soumission', async () => {
      mockCreateSignalement.mockImplementation(() => new Promise(() => {}))

      const user = userEvent.setup()
      render(<SignalementModal {...defaultProps} />)

      await user.type(screen.getByPlaceholderText('Titre du signalement'), 'Titre')
      await user.type(screen.getByPlaceholderText('Décrivez le problème en détail...'), 'Description')

      await user.click(screen.getByText('Créer'))

      await waitFor(() => {
        expect(screen.getByText('Enregistrement...')).toBeInTheDocument()
      })
    })

    it('desactive le bouton pendant la soumission', async () => {
      mockCreateSignalement.mockImplementation(() => new Promise(() => {}))

      const user = userEvent.setup()
      render(<SignalementModal {...defaultProps} />)

      await user.type(screen.getByPlaceholderText('Titre du signalement'), 'Titre')
      await user.type(screen.getByPlaceholderText('Décrivez le problème en détail...'), 'Description')

      await user.click(screen.getByText('Créer'))

      await waitFor(() => {
        expect(screen.getByText('Enregistrement...').closest('button')).toBeDisabled()
      })
    })
  })

  describe('Gestion des erreurs', () => {
    it('affiche l erreur en cas d echec', async () => {
      mockCreateSignalement.mockRejectedValueOnce(new Error('Erreur serveur'))

      const user = userEvent.setup()
      render(<SignalementModal {...defaultProps} />)

      await user.type(screen.getByPlaceholderText('Titre du signalement'), 'Titre')
      await user.type(screen.getByPlaceholderText('Décrivez le problème en détail...'), 'Description')

      await user.click(screen.getByText('Créer'))

      await waitFor(() => {
        expect(screen.getByText('Erreur serveur')).toBeInTheDocument()
      })
    })

    it('affiche un message par defaut si pas de message d erreur', async () => {
      mockCreateSignalement.mockRejectedValueOnce({})

      const user = userEvent.setup()
      render(<SignalementModal {...defaultProps} />)

      await user.type(screen.getByPlaceholderText('Titre du signalement'), 'Titre')
      await user.type(screen.getByPlaceholderText('Décrivez le problème en détail...'), 'Description')

      await user.click(screen.getByText('Créer'))

      await waitFor(() => {
        expect(screen.getByText('Une erreur est survenue')).toBeInTheDocument()
      })
    })
  })

  describe('Fermeture', () => {
    it('appelle onClose au clic sur Annuler', async () => {
      const user = userEvent.setup()
      render(<SignalementModal {...defaultProps} />)

      await user.click(screen.getByText('Annuler'))
      expect(mockOnClose).toHaveBeenCalled()
    })

    it('appelle onClose au clic sur le bouton fermer', async () => {
      const user = userEvent.setup()
      render(<SignalementModal {...defaultProps} />)

      await user.click(screen.getByLabelText('Fermer'))
      expect(mockOnClose).toHaveBeenCalled()
    })

    it('appelle onClose au clic sur l overlay', async () => {
      const user = userEvent.setup()
      render(<SignalementModal {...defaultProps} />)

      const overlay = document.querySelector('.bg-gray-500')
      if (overlay) {
        await user.click(overlay)
        expect(mockOnClose).toHaveBeenCalled()
      }
    })
  })
})
