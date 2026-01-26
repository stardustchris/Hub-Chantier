/**
 * Tests pour SignalementDetail
 *
 * Couvre:
 * - Chargement des données
 * - Affichage des informations du signalement
 * - Actions (traiter, clôturer, réouvrir)
 * - Gestion des réponses
 * - Gestion des erreurs
 * - Affichage conditionnel selon les permissions
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import SignalementDetail from './SignalementDetail'
import type { Signalement, Reponse } from '../../types/signalements'

// Mock des services
vi.mock('../../services/signalements', () => ({
  getSignalement: vi.fn(),
  listReponses: vi.fn(),
  createReponse: vi.fn(),
  marquerTraite: vi.fn(),
  cloturerSignalement: vi.fn(),
  reouvrirSignalement: vi.fn(),
  getPrioriteIcon: vi.fn((priorite: string) => {
    const icons: Record<string, string> = {
      critique: '🔴',
      haute: '🟠',
      moyenne: '🟡',
      basse: '🟢',
    }
    return icons[priorite] || '⚪'
  }),
  getStatutIcon: vi.fn((statut: string) => {
    const icons: Record<string, string> = {
      ouvert: '📋',
      en_cours: '🔧',
      traite: '✅',
      cloture: '🔒',
    }
    return icons[statut] || '❓'
  }),
}))

vi.mock('../../utils/dates', () => ({
  formatDateDayMonthYearTime: vi.fn((date: string) => `Formatted: ${date}`),
}))

vi.mock('./TraiterModal', () => ({
  default: vi.fn(({ isOpen, onClose, onConfirm, isLoading }) =>
    isOpen ? (
      <div data-testid="traiter-modal">
        <button onClick={() => onConfirm('Commentaire test')} disabled={isLoading}>
          Confirmer
        </button>
        <button onClick={onClose}>Annuler</button>
      </div>
    ) : null
  ),
}))

vi.mock('./ReponsesSection', () => ({
  default: vi.fn(({ reponses, canReply, onAddReponse }) => (
    <div data-testid="reponses-section">
      <span>Réponses: {reponses.length}</span>
      {canReply && (
        <button onClick={() => onAddReponse('Nouvelle réponse')}>Ajouter réponse</button>
      )}
    </div>
  )),
}))

import {
  getSignalement,
  listReponses,
  createReponse,
  marquerTraite,
  cloturerSignalement,
  reouvrirSignalement,
} from '../../services/signalements'

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

const createMockReponse = (overrides: Partial<Reponse> = {}): Reponse => ({
  id: 1,
  signalement_id: 1,
  contenu: 'Contenu de la réponse',
  auteur_id: 'user-1',
  auteur_nom: 'Jean Dupont',
  created_at: '2024-01-15T11:00:00',
  ...overrides,
})

describe('SignalementDetail', () => {
  const mockOnClose = vi.fn()
  const mockOnUpdate = vi.fn()
  const mockOnEdit = vi.fn()

  const defaultProps = {
    signalementId: 1,
    onClose: mockOnClose,
    onUpdate: mockOnUpdate,
    onEdit: mockOnEdit,
  }

  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(getSignalement).mockResolvedValue(createMockSignalement())
    vi.mocked(listReponses).mockResolvedValue({ reponses: [] })
  })

  describe('Chargement', () => {
    it('affiche le texte de chargement', () => {
      vi.mocked(getSignalement).mockImplementation(() => new Promise(() => {}))
      render(<SignalementDetail {...defaultProps} />)

      expect(screen.getByText('Chargement...')).toBeInTheDocument()
    })

    it('charge le signalement et les réponses', async () => {
      render(<SignalementDetail {...defaultProps} />)

      await waitFor(() => {
        expect(getSignalement).toHaveBeenCalledWith(1)
        expect(listReponses).toHaveBeenCalledWith(1)
      })
    })

    it('affiche une erreur si le chargement échoue', async () => {
      vi.mocked(getSignalement).mockRejectedValueOnce(new Error('Erreur de chargement'))

      render(<SignalementDetail {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Erreur de chargement')).toBeInTheDocument()
      })
    })
  })

  describe('Affichage des informations', () => {
    it('affiche le titre du signalement', async () => {
      render(<SignalementDetail {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Signalement Test')).toBeInTheDocument()
      })
    })

    it('affiche la description', async () => {
      render(<SignalementDetail {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Description du signalement')).toBeInTheDocument()
      })
    })

    it('affiche le label de priorité', async () => {
      render(<SignalementDetail {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Haute')).toBeInTheDocument()
      })
    })

    it('affiche le label de statut', async () => {
      render(<SignalementDetail {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText(/Ouvert/)).toBeInTheDocument()
      })
    })

    it('affiche le badge EN RETARD si applicable', async () => {
      vi.mocked(getSignalement).mockResolvedValueOnce(
        createMockSignalement({ est_en_retard: true })
      )

      render(<SignalementDetail {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('EN RETARD')).toBeInTheDocument()
      })
    })

    it('affiche le créateur', async () => {
      render(<SignalementDetail {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Jean Dupont')).toBeInTheDocument()
      })
    })

    it('affiche l\'assigné', async () => {
      vi.mocked(getSignalement).mockResolvedValueOnce(
        createMockSignalement({ assigne_a: 'user-2', assigne_a_nom: 'Marie Martin' })
      )

      render(<SignalementDetail {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Marie Martin')).toBeInTheDocument()
      })
    })

    it('affiche "Non assigné" si pas d\'assigné', async () => {
      render(<SignalementDetail {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Non assigné')).toBeInTheDocument()
      })
    })

    it('affiche la localisation si présente', async () => {
      vi.mocked(getSignalement).mockResolvedValueOnce(
        createMockSignalement({ localisation: 'Bâtiment A, 2ème étage' })
      )

      render(<SignalementDetail {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Bâtiment A, 2ème étage')).toBeInTheDocument()
      })
    })

    it('affiche la photo si présente', async () => {
      vi.mocked(getSignalement).mockResolvedValueOnce(
        createMockSignalement({ photo_url: 'https://example.com/photo.jpg' })
      )

      render(<SignalementDetail {...defaultProps} />)

      await waitFor(() => {
        const img = screen.getByAltText('Photo du signalement')
        expect(img).toHaveAttribute('src', 'https://example.com/photo.jpg')
      })
    })

    it('affiche le commentaire de traitement si présent', async () => {
      vi.mocked(getSignalement).mockResolvedValueOnce(
        createMockSignalement({
          commentaire_traitement: 'Problème résolu',
          statut: 'traite',
        })
      )

      render(<SignalementDetail {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Commentaire de traitement')).toBeInTheDocument()
        expect(screen.getByText('Problème résolu')).toBeInTheDocument()
      })
    })

    it('affiche la barre de progression du temps', async () => {
      vi.mocked(getSignalement).mockResolvedValueOnce(
        createMockSignalement({ pourcentage_temps: 50 })
      )

      render(<SignalementDetail {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Temps écoulé: 50%')).toBeInTheDocument()
      })
    })

    it('n\'affiche pas la barre de progression pour les signalements clôturés', async () => {
      vi.mocked(getSignalement).mockResolvedValueOnce(
        createMockSignalement({ statut: 'cloture' })
      )

      render(<SignalementDetail {...defaultProps} />)

      await waitFor(() => {
        expect(screen.queryByText(/Temps écoulé/)).not.toBeInTheDocument()
      })
    })
  })

  describe('Actions', () => {
    it('affiche le bouton Modifier si canEdit=true et statut != cloture', async () => {
      render(<SignalementDetail {...defaultProps} canEdit={true} />)

      await waitFor(() => {
        expect(screen.getByText('Modifier')).toBeInTheDocument()
      })
    })

    it('n\'affiche pas le bouton Modifier si canEdit=false', async () => {
      render(<SignalementDetail {...defaultProps} canEdit={false} />)

      await waitFor(() => {
        expect(screen.queryByText('Modifier')).not.toBeInTheDocument()
      })
    })

    it('n\'affiche pas le bouton Modifier si statut=cloture', async () => {
      vi.mocked(getSignalement).mockResolvedValueOnce(
        createMockSignalement({ statut: 'cloture' })
      )

      render(<SignalementDetail {...defaultProps} canEdit={true} />)

      await waitFor(() => {
        expect(screen.queryByText('Modifier')).not.toBeInTheDocument()
      })
    })

    it('affiche le bouton "Marquer comme traité" pour les statuts ouvert/en_cours', async () => {
      render(<SignalementDetail {...defaultProps} canTraiter={true} />)

      await waitFor(() => {
        expect(screen.getByText('Marquer comme traité')).toBeInTheDocument()
      })
    })

    it('affiche le bouton "Clôturer" pour le statut traité', async () => {
      vi.mocked(getSignalement).mockResolvedValueOnce(
        createMockSignalement({ statut: 'traite' })
      )

      render(<SignalementDetail {...defaultProps} canCloturer={true} />)

      await waitFor(() => {
        expect(screen.getByText('Clôturer')).toBeInTheDocument()
      })
    })

    it('affiche le bouton "Réouvrir" pour le statut cloture', async () => {
      vi.mocked(getSignalement).mockResolvedValueOnce(
        createMockSignalement({ statut: 'cloture' })
      )

      render(<SignalementDetail {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Réouvrir')).toBeInTheDocument()
      })
    })
  })

  describe('Marquer comme traité', () => {
    it('ouvre le modal de traitement au clic', async () => {
      const user = userEvent.setup()
      render(<SignalementDetail {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Marquer comme traité')).toBeInTheDocument()
      })

      await user.click(screen.getByText('Marquer comme traité'))

      expect(screen.getByTestId('traiter-modal')).toBeInTheDocument()
    })

    it('appelle marquerTraite à la confirmation', async () => {
      const user = userEvent.setup()
      const updatedSignalement = createMockSignalement({ statut: 'traite' })
      vi.mocked(marquerTraite).mockResolvedValueOnce(updatedSignalement)

      render(<SignalementDetail {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Marquer comme traité')).toBeInTheDocument()
      })

      await user.click(screen.getByText('Marquer comme traité'))
      await user.click(screen.getByText('Confirmer'))

      await waitFor(() => {
        expect(marquerTraite).toHaveBeenCalledWith(1, 'Commentaire test')
        expect(mockOnUpdate).toHaveBeenCalledWith(updatedSignalement)
      })
    })
  })

  describe('Clôturer', () => {
    it('appelle cloturerSignalement au clic', async () => {
      const user = userEvent.setup()
      vi.mocked(getSignalement).mockResolvedValueOnce(
        createMockSignalement({ statut: 'traite' })
      )
      const updatedSignalement = createMockSignalement({ statut: 'cloture' })
      vi.mocked(cloturerSignalement).mockResolvedValueOnce(updatedSignalement)

      render(<SignalementDetail {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Clôturer')).toBeInTheDocument()
      })

      await user.click(screen.getByText('Clôturer'))

      await waitFor(() => {
        expect(cloturerSignalement).toHaveBeenCalledWith(1)
        expect(mockOnUpdate).toHaveBeenCalledWith(updatedSignalement)
      })
    })
  })

  describe('Réouvrir', () => {
    it('appelle reouvrirSignalement au clic', async () => {
      const user = userEvent.setup()
      vi.mocked(getSignalement).mockResolvedValueOnce(
        createMockSignalement({ statut: 'cloture' })
      )
      const updatedSignalement = createMockSignalement({ statut: 'ouvert' })
      vi.mocked(reouvrirSignalement).mockResolvedValueOnce(updatedSignalement)

      render(<SignalementDetail {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Réouvrir')).toBeInTheDocument()
      })

      await user.click(screen.getByText('Réouvrir'))

      await waitFor(() => {
        expect(reouvrirSignalement).toHaveBeenCalledWith(1)
        expect(mockOnUpdate).toHaveBeenCalledWith(updatedSignalement)
      })
    })
  })

  describe('Réponses', () => {
    it('affiche la section réponses', async () => {
      vi.mocked(listReponses).mockResolvedValueOnce({
        reponses: [createMockReponse(), createMockReponse({ id: 2 })],
      })

      render(<SignalementDetail {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByTestId('reponses-section')).toBeInTheDocument()
        expect(screen.getByText('Réponses: 2')).toBeInTheDocument()
      })
    })

    it('permet d\'ajouter une réponse si non clôturé', async () => {
      const user = userEvent.setup()
      const newReponse = createMockReponse({ id: 3, contenu: 'Nouvelle réponse' })
      vi.mocked(createReponse).mockResolvedValueOnce(newReponse)

      render(<SignalementDetail {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Ajouter réponse')).toBeInTheDocument()
      })

      await user.click(screen.getByText('Ajouter réponse'))

      await waitFor(() => {
        expect(createReponse).toHaveBeenCalledWith(1, { contenu: 'Nouvelle réponse' })
      })
    })

    it('ne permet pas d\'ajouter une réponse si clôturé', async () => {
      vi.mocked(getSignalement).mockResolvedValueOnce(
        createMockSignalement({ statut: 'cloture' })
      )

      render(<SignalementDetail {...defaultProps} />)

      await waitFor(() => {
        expect(screen.queryByText('Ajouter réponse')).not.toBeInTheDocument()
      })
    })
  })

  describe('Fermeture', () => {
    it('appelle onClose au clic sur le bouton fermer', async () => {
      const user = userEvent.setup()
      render(<SignalementDetail {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByLabelText('Fermer')).toBeInTheDocument()
      })

      await user.click(screen.getByLabelText('Fermer'))

      expect(mockOnClose).toHaveBeenCalled()
    })
  })

  describe('Édition', () => {
    it('appelle onEdit au clic sur Modifier', async () => {
      const user = userEvent.setup()
      const signalement = createMockSignalement()
      vi.mocked(getSignalement).mockResolvedValueOnce(signalement)

      render(<SignalementDetail {...defaultProps} canEdit={true} />)

      await waitFor(() => {
        expect(screen.getByText('Modifier')).toBeInTheDocument()
      })

      await user.click(screen.getByText('Modifier'))

      expect(mockOnEdit).toHaveBeenCalledWith(signalement)
    })
  })

  describe('Gestion des erreurs d\'action', () => {
    it('affiche une erreur si marquerTraite échoue', async () => {
      const user = userEvent.setup()
      // Le message d'erreur affiché sera err.message si c'est une instance de Error
      vi.mocked(marquerTraite).mockRejectedValueOnce(new Error('Erreur de traitement'))

      render(<SignalementDetail {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Marquer comme traité')).toBeInTheDocument()
      })

      await user.click(screen.getByText('Marquer comme traité'))
      await user.click(screen.getByText('Confirmer'))

      await waitFor(() => {
        expect(screen.getByText('Erreur de traitement')).toBeInTheDocument()
      })
    })

    it('affiche une erreur si cloturerSignalement échoue', async () => {
      const user = userEvent.setup()
      vi.mocked(getSignalement).mockResolvedValueOnce(
        createMockSignalement({ statut: 'traite' })
      )
      // Le message d'erreur affiché sera err.message
      vi.mocked(cloturerSignalement).mockRejectedValueOnce(new Error('Erreur de clôture'))

      render(<SignalementDetail {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Clôturer')).toBeInTheDocument()
      })

      await user.click(screen.getByText('Clôturer'))

      await waitFor(() => {
        expect(screen.getByText('Erreur de clôture')).toBeInTheDocument()
      })
    })
  })
})
