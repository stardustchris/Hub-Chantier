/**
 * Tests pour SignalementModal
 *
 * Couvre:
 * - Mode création vs édition
 * - Initialisation du formulaire
 * - Sélection de priorité et assignation
 * - Validation et soumission
 * - Gestion des erreurs
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import SignalementModal from './SignalementModal'
import type { Signalement } from '../../types/signalements'

// Mock des services
vi.mock('../../services/signalements', () => ({
  createSignalement: vi.fn(),
  updateSignalement: vi.fn(),
}))

import { createSignalement, updateSignalement } from '../../services/signalements'

const createMockSignalement = (overrides: Partial<Signalement> = {}): Signalement => ({
  id: 1,
  chantier_id: 'ch-1',
  titre: 'Signalement Test',
  description: 'Description du signalement',
  priorite: 'haute',
  priorite_label: 'Haute',
  statut: 'ouvert',
  statut_label: 'Ouvert',
  cree_par: 'user-1',
  cree_par_nom: 'Jean Dupont',
  created_at: '2024-01-15T10:00:00',
  updated_at: '2024-01-15T10:00:00',
  est_en_retard: false,
  pourcentage_temps: 25,
  temps_restant: '3 jours',
  ...overrides,
})

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
  })

  describe('Rendu conditionnel', () => {
    it('ne rend rien quand isOpen est false', () => {
      render(<SignalementModal {...defaultProps} isOpen={false} />)
      expect(screen.queryByText('Nouveau signalement')).not.toBeInTheDocument()
    })

    it('rend le modal quand isOpen est true', () => {
      render(<SignalementModal {...defaultProps} />)
      expect(screen.getByText('Nouveau signalement')).toBeInTheDocument()
    })
  })

  describe('Mode création', () => {
    it('affiche le titre "Nouveau signalement"', () => {
      render(<SignalementModal {...defaultProps} />)
      expect(screen.getByText('Nouveau signalement')).toBeInTheDocument()
    })

    it('affiche le bouton Créer', () => {
      render(<SignalementModal {...defaultProps} />)
      expect(screen.getByRole('button', { name: 'Créer' })).toBeInTheDocument()
    })

    it('initialise le formulaire vide', () => {
      render(<SignalementModal {...defaultProps} />)

      expect(screen.getByLabelText(/titre/i)).toHaveValue('')
      expect(screen.getByLabelText(/description/i)).toHaveValue('')
      expect(screen.getByLabelText(/priorité/i)).toHaveValue('moyenne')
    })
  })

  describe('Mode édition', () => {
    const editSignalement = createMockSignalement({
      titre: 'Mon Signalement',
      description: 'Ma description',
      priorite: 'haute',
      localisation: 'Étage 2',
      photo_url: 'https://example.com/photo.jpg',
      assigne_a: 1,
      date_resolution_souhaitee: '2024-02-15T00:00:00',
    })

    it('affiche le titre "Modifier le signalement"', () => {
      render(<SignalementModal {...defaultProps} signalement={editSignalement} />)
      expect(screen.getByText('Modifier le signalement')).toBeInTheDocument()
    })

    it('affiche le bouton Modifier', () => {
      render(<SignalementModal {...defaultProps} signalement={editSignalement} />)
      expect(screen.getByRole('button', { name: 'Modifier' })).toBeInTheDocument()
    })

    it('initialise le formulaire avec les données du signalement', () => {
      render(<SignalementModal {...defaultProps} signalement={editSignalement} />)

      expect(screen.getByLabelText(/titre/i)).toHaveValue('Mon Signalement')
      expect(screen.getByLabelText(/description/i)).toHaveValue('Ma description')
      expect(screen.getByLabelText(/priorité/i)).toHaveValue('haute')
      expect(screen.getByLabelText(/localisation/i)).toHaveValue('Étage 2')
      expect(screen.getByLabelText(/url de la photo/i)).toHaveValue('https://example.com/photo.jpg')
    })

    it('initialise l\'assignation', () => {
      render(<SignalementModal {...defaultProps} signalement={editSignalement} />)

      expect(screen.getByLabelText(/assigner à/i)).toHaveValue('1')
    })

    it('initialise la date de résolution', () => {
      render(<SignalementModal {...defaultProps} signalement={editSignalement} />)

      expect(screen.getByLabelText(/date de résolution/i)).toHaveValue('2024-02-15')
    })
  })

  describe('Formulaire', () => {
    it('affiche tous les champs requis', () => {
      render(<SignalementModal {...defaultProps} />)

      expect(screen.getByLabelText(/titre/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/description/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/priorité/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/assigner à/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/date de résolution/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/localisation/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/url de la photo/i)).toBeInTheDocument()
    })

    it('affiche les options de priorité', () => {
      render(<SignalementModal {...defaultProps} />)

      const prioriteSelect = screen.getByLabelText(/priorité/i)
      expect(prioriteSelect).toContainHTML('Basse')
      expect(prioriteSelect).toContainHTML('Moyenne')
      expect(prioriteSelect).toContainHTML('Haute')
      expect(prioriteSelect).toContainHTML('Critique')
    })

    it('affiche la liste des utilisateurs dans le sélecteur', () => {
      render(<SignalementModal {...defaultProps} />)

      expect(screen.getByText('Jean Dupont')).toBeInTheDocument()
      expect(screen.getByText('Marie Martin')).toBeInTheDocument()
    })

    it('affiche l\'option "Non assigné"', () => {
      render(<SignalementModal {...defaultProps} />)

      expect(screen.getByText('Non assigné')).toBeInTheDocument()
    })

    it('permet de saisir le titre', async () => {
      const user = userEvent.setup()
      render(<SignalementModal {...defaultProps} />)

      const titreInput = screen.getByLabelText(/titre/i)
      await user.type(titreInput, 'Mon nouveau signalement')

      expect(titreInput).toHaveValue('Mon nouveau signalement')
    })

    it('permet de saisir la description', async () => {
      const user = userEvent.setup()
      render(<SignalementModal {...defaultProps} />)

      const descInput = screen.getByLabelText(/description/i)
      await user.type(descInput, 'Ma description détaillée')

      expect(descInput).toHaveValue('Ma description détaillée')
    })

    it('permet de sélectionner la priorité', async () => {
      const user = userEvent.setup()
      render(<SignalementModal {...defaultProps} />)

      const prioriteSelect = screen.getByLabelText(/priorité/i)
      await user.selectOptions(prioriteSelect, 'critique')

      expect(prioriteSelect).toHaveValue('critique')
    })

    it('permet d\'assigner à un utilisateur', async () => {
      const user = userEvent.setup()
      render(<SignalementModal {...defaultProps} />)

      const assigneSelect = screen.getByLabelText(/assigner à/i)
      await user.selectOptions(assigneSelect, '2')

      expect(assigneSelect).toHaveValue('2')
    })
  })

  describe('Soumission en création', () => {
    it('appelle createSignalement avec les données', async () => {
      const user = userEvent.setup()
      const newSignalement = createMockSignalement()
      vi.mocked(createSignalement).mockResolvedValueOnce(newSignalement)

      render(<SignalementModal {...defaultProps} />)

      await user.type(screen.getByLabelText(/titre/i), 'Nouveau signalement')
      await user.type(screen.getByLabelText(/description/i), 'Description test')
      await user.selectOptions(screen.getByLabelText(/priorité/i), 'haute')

      await user.click(screen.getByRole('button', { name: 'Créer' }))

      await waitFor(() => {
        expect(createSignalement).toHaveBeenCalledWith(
          expect.objectContaining({
            chantier_id: 1,
            titre: 'Nouveau signalement',
            description: 'Description test',
            priorite: 'haute',
          })
        )
      })
    })

    it('appelle onSuccess après création réussie', async () => {
      const user = userEvent.setup()
      const newSignalement = createMockSignalement()
      vi.mocked(createSignalement).mockResolvedValueOnce(newSignalement)

      render(<SignalementModal {...defaultProps} />)

      await user.type(screen.getByLabelText(/titre/i), 'Nouveau signalement')
      await user.type(screen.getByLabelText(/description/i), 'Description test')

      await user.click(screen.getByRole('button', { name: 'Créer' }))

      await waitFor(() => {
        expect(mockOnSuccess).toHaveBeenCalledWith(newSignalement)
      })
    })

    it('ferme le modal après création réussie', async () => {
      const user = userEvent.setup()
      vi.mocked(createSignalement).mockResolvedValueOnce(createMockSignalement())

      render(<SignalementModal {...defaultProps} />)

      await user.type(screen.getByLabelText(/titre/i), 'Nouveau signalement')
      await user.type(screen.getByLabelText(/description/i), 'Description test')

      await user.click(screen.getByRole('button', { name: 'Créer' }))

      await waitFor(() => {
        expect(mockOnClose).toHaveBeenCalled()
      })
    })
  })

  describe('Soumission en édition', () => {
    const editSignalement = createMockSignalement({ id: 1 })

    it('appelle updateSignalement avec les données', async () => {
      const user = userEvent.setup()
      const updatedSignalement = createMockSignalement({ titre: 'Titre modifié' })
      vi.mocked(updateSignalement).mockResolvedValueOnce(updatedSignalement)

      render(<SignalementModal {...defaultProps} signalement={editSignalement} />)

      const titreInput = screen.getByLabelText(/titre/i)
      await user.clear(titreInput)
      await user.type(titreInput, 'Titre modifié')

      await user.click(screen.getByRole('button', { name: 'Modifier' }))

      await waitFor(() => {
        expect(updateSignalement).toHaveBeenCalledWith(
          1,
          expect.objectContaining({
            titre: 'Titre modifié',
          })
        )
      })
    })

    it('appelle onSuccess après modification réussie', async () => {
      const user = userEvent.setup()
      const updatedSignalement = createMockSignalement({ titre: 'Titre modifié' })
      vi.mocked(updateSignalement).mockResolvedValueOnce(updatedSignalement)

      render(<SignalementModal {...defaultProps} signalement={editSignalement} />)

      await user.click(screen.getByRole('button', { name: 'Modifier' }))

      await waitFor(() => {
        expect(mockOnSuccess).toHaveBeenCalledWith(updatedSignalement)
      })
    })
  })

  describe('États de chargement', () => {
    it('affiche "Enregistrement..." pendant la soumission', async () => {
      const user = userEvent.setup()
      vi.mocked(createSignalement).mockImplementation(
        () => new Promise((resolve) => setTimeout(() => resolve(createMockSignalement()), 1000))
      )

      render(<SignalementModal {...defaultProps} />)

      await user.type(screen.getByLabelText(/titre/i), 'Test')
      await user.type(screen.getByLabelText(/description/i), 'Test')

      await user.click(screen.getByRole('button', { name: 'Créer' }))

      expect(screen.getByText('Enregistrement...')).toBeInTheDocument()
    })

    it('désactive le bouton pendant le chargement', async () => {
      const user = userEvent.setup()
      vi.mocked(createSignalement).mockImplementation(
        () => new Promise((resolve) => setTimeout(() => resolve(createMockSignalement()), 1000))
      )

      render(<SignalementModal {...defaultProps} />)

      await user.type(screen.getByLabelText(/titre/i), 'Test')
      await user.type(screen.getByLabelText(/description/i), 'Test')

      await user.click(screen.getByRole('button', { name: 'Créer' }))

      expect(screen.getByRole('button', { name: 'Enregistrement...' })).toBeDisabled()
    })
  })

  describe('Gestion des erreurs', () => {
    it('affiche l\'erreur si la création échoue', async () => {
      const user = userEvent.setup()
      vi.mocked(createSignalement).mockRejectedValueOnce(new Error('Erreur de création'))

      render(<SignalementModal {...defaultProps} />)

      await user.type(screen.getByLabelText(/titre/i), 'Test')
      await user.type(screen.getByLabelText(/description/i), 'Test')

      await user.click(screen.getByRole('button', { name: 'Créer' }))

      await waitFor(() => {
        expect(screen.getByText('Erreur de création')).toBeInTheDocument()
      })
    })

    it('affiche un message générique pour les erreurs non-Error', async () => {
      const user = userEvent.setup()
      vi.mocked(createSignalement).mockRejectedValueOnce('Something went wrong')

      render(<SignalementModal {...defaultProps} />)

      await user.type(screen.getByLabelText(/titre/i), 'Test')
      await user.type(screen.getByLabelText(/description/i), 'Test')

      await user.click(screen.getByRole('button', { name: 'Créer' }))

      await waitFor(() => {
        expect(screen.getByText('Une erreur est survenue')).toBeInTheDocument()
      })
    })

    it('ne ferme pas le modal si une erreur survient', async () => {
      const user = userEvent.setup()
      vi.mocked(createSignalement).mockRejectedValueOnce(new Error('Erreur'))

      render(<SignalementModal {...defaultProps} />)

      await user.type(screen.getByLabelText(/titre/i), 'Test')
      await user.type(screen.getByLabelText(/description/i), 'Test')

      await user.click(screen.getByRole('button', { name: 'Créer' }))

      await waitFor(() => {
        expect(mockOnClose).not.toHaveBeenCalled()
      })
    })
  })

  describe('Fermeture du modal', () => {
    it('appelle onClose au clic sur X', async () => {
      const user = userEvent.setup()
      render(<SignalementModal {...defaultProps} />)

      const closeButton = screen.getByLabelText('Fermer')
      await user.click(closeButton)

      expect(mockOnClose).toHaveBeenCalled()
    })

    it('appelle onClose au clic sur Annuler', async () => {
      const user = userEvent.setup()
      render(<SignalementModal {...defaultProps} />)

      const cancelButton = screen.getByRole('button', { name: 'Annuler' })
      await user.click(cancelButton)

      expect(mockOnClose).toHaveBeenCalled()
    })

    it('appelle onClose au clic sur l\'overlay', async () => {
      const user = userEvent.setup()
      const { container } = render(<SignalementModal {...defaultProps} />)

      const overlay = container.querySelector('.bg-gray-500')
      await user.click(overlay!)

      expect(mockOnClose).toHaveBeenCalled()
    })
  })

  describe('Réinitialisation', () => {
    it('réinitialise le formulaire quand on ferme et rouvre', () => {
      const { rerender } = render(<SignalementModal {...defaultProps} />)

      // Fermer le modal
      rerender(<SignalementModal {...defaultProps} isOpen={false} />)

      // Rouvrir le modal
      rerender(<SignalementModal {...defaultProps} isOpen={true} />)

      expect(screen.getByLabelText(/titre/i)).toHaveValue('')
      expect(screen.getByLabelText(/description/i)).toHaveValue('')
    })

    it('réinitialise l\'erreur quand on rouvre', () => {
      const { rerender } = render(<SignalementModal {...defaultProps} />)

      // Simuler une erreur en rerenderant avec un signalement différent
      rerender(<SignalementModal {...defaultProps} signalement={createMockSignalement()} />)

      expect(screen.queryByText(/erreur/i)).not.toBeInTheDocument()
    })
  })

  describe('Validation', () => {
    it('requiert le titre', () => {
      render(<SignalementModal {...defaultProps} />)

      const titreInput = screen.getByLabelText(/titre/i)
      expect(titreInput).toHaveAttribute('required')
    })

    it('requiert la description', () => {
      render(<SignalementModal {...defaultProps} />)

      const descInput = screen.getByLabelText(/description/i)
      expect(descInput).toHaveAttribute('required')
    })

    it('a une limite de 200 caractères pour le titre', () => {
      render(<SignalementModal {...defaultProps} />)

      const titreInput = screen.getByLabelText(/titre/i)
      expect(titreInput).toHaveAttribute('maxLength', '200')
    })

    it('a une limite de 100 caractères pour la localisation', () => {
      render(<SignalementModal {...defaultProps} />)

      const locInput = screen.getByLabelText(/localisation/i)
      expect(locInput).toHaveAttribute('maxLength', '100')
    })
  })
})
