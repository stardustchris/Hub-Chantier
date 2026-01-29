/**
 * Tests pour SignalementDetail
 *
 * Couvre:
 * - Chargement et affichage du signalement
 * - Affichage des metadonnees (priorite, statut, dates)
 * - Affichage de la photo
 * - Actions (traiter, cloturer, reouvrir)
 * - Gestion des erreurs
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import SignalementDetail from './SignalementDetail'
import { createMockSignalement } from '../../fixtures'
import type { Reponse } from '../../types/signalements'

// Mock services
const mockGetSignalement = vi.fn()
const mockListReponses = vi.fn()
const mockMarquerTraite = vi.fn()
const mockCloturerSignalement = vi.fn()
const mockReouvrirSignalement = vi.fn()

vi.mock('../../services/signalements', () => ({
  getSignalement: (...args: unknown[]) => mockGetSignalement(...args),
  listReponses: (...args: unknown[]) => mockListReponses(...args),
  createReponse: vi.fn(),
  marquerTraite: (...args: unknown[]) => mockMarquerTraite(...args),
  cloturerSignalement: (...args: unknown[]) => mockCloturerSignalement(...args),
  reouvrirSignalement: (...args: unknown[]) => mockReouvrirSignalement(...args),
  getPrioriteIcon: (priorite: string) => priorite === 'critique' ? '🔴' : '🟡',
  getStatutIcon: (statut: string) => statut === 'cloture' ? '✅' : '🔵',
}))


const createMockReponse = (overrides: Partial<Reponse> = {}): Reponse => ({
  id: 1,
  signalement_id: 1,
  contenu: 'Je vais verifier',
  auteur_id: 2,
  auteur_nom: 'Marie Martin',
  photo_url: null,
  created_at: '2024-01-15T11:00:00',
  updated_at: '2024-01-15T11:00:00',
  est_resolution: false,
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
    mockGetSignalement.mockResolvedValue(createMockSignalement())
    mockListReponses.mockResolvedValue({ reponses: [createMockReponse()] })
  })

  describe('Chargement', () => {
    it('affiche un loader pendant le chargement', () => {
      mockGetSignalement.mockImplementation(() => new Promise(() => {}))

      render(<SignalementDetail {...defaultProps} />)

      expect(screen.getByText('Chargement...')).toBeInTheDocument()
    })

    it('charge le signalement au montage', async () => {
      render(<SignalementDetail {...defaultProps} />)

      await waitFor(() => {
        expect(mockGetSignalement).toHaveBeenCalledWith(1)
        expect(mockListReponses).toHaveBeenCalledWith(1)
      })
    })

    it('affiche une erreur si le chargement echoue', async () => {
      mockGetSignalement.mockRejectedValueOnce(new Error('Erreur reseau'))

      render(<SignalementDetail {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Erreur reseau')).toBeInTheDocument()
      })
    })
  })

  describe('Affichage', () => {
    it('affiche le titre du signalement', async () => {
      render(<SignalementDetail {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Signalement Test')).toBeInTheDocument()
      })
    })

    it('affiche la description', async () => {
      render(<SignalementDetail {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Description')).toBeInTheDocument()
        expect(screen.getByText('Description du signalement')).toBeInTheDocument()
      })
    })

    it('affiche le badge de priorite', async () => {
      render(<SignalementDetail {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Moyenne')).toBeInTheDocument()
      })
    })

    it('affiche le badge EN RETARD si applicable', async () => {
      mockGetSignalement.mockResolvedValueOnce(createMockSignalement({ est_en_retard: true }))

      render(<SignalementDetail {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('EN RETARD')).toBeInTheDocument()
      })
    })

    it('affiche les informations de creation', async () => {
      render(<SignalementDetail {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Jean Dupont')).toBeInTheDocument()
      })
    })

    it('affiche l assignation', async () => {
      render(<SignalementDetail {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Marie Martin')).toBeInTheDocument()
      })
    })

    it('affiche Non assigne si pas d assignation', async () => {
      mockGetSignalement.mockResolvedValueOnce(createMockSignalement({ assigne_a: null, assigne_a_nom: undefined }))

      render(<SignalementDetail {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Non assigné')).toBeInTheDocument()
      })
    })
  })

  describe('Photo', () => {
    it('affiche la photo si presente', async () => {
      mockGetSignalement.mockResolvedValueOnce(createMockSignalement({
        photo_url: 'https://example.com/photo.jpg',
      }))

      render(<SignalementDetail {...defaultProps} />)

      await waitFor(() => {
        const img = screen.getByRole('img', { name: 'Photo du signalement' })
        expect(img).toHaveAttribute('src', 'https://example.com/photo.jpg')
      })
    })
  })

  describe('Barre de progression', () => {
    it('affiche le pourcentage de temps ecoule', async () => {
      mockGetSignalement.mockResolvedValueOnce(createMockSignalement({ pourcentage_temps: 30, temps_restant: '2j 5h' }))
      render(<SignalementDetail {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText(/30%/)).toBeInTheDocument()
      })
    })

    it('affiche le temps restant', async () => {
      mockGetSignalement.mockResolvedValueOnce(createMockSignalement({ pourcentage_temps: 30, temps_restant: '2j 5h' }))
      render(<SignalementDetail {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('2j 5h')).toBeInTheDocument()
      })
    })
  })

  describe('Actions', () => {
    it('affiche le bouton Traiter pour signalement ouvert', async () => {
      render(<SignalementDetail {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Marquer comme traité')).toBeInTheDocument()
      })
    })

    it('affiche le bouton Cloturer pour signalement traite', async () => {
      mockGetSignalement.mockResolvedValueOnce(createMockSignalement({ statut: 'traite' }))

      render(<SignalementDetail {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Clôturer')).toBeInTheDocument()
      })
    })

    it('affiche le bouton Reouvrir pour signalement cloture', async () => {
      mockGetSignalement.mockResolvedValueOnce(createMockSignalement({ statut: 'cloture' }))

      render(<SignalementDetail {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Réouvrir')).toBeInTheDocument()
      })
    })

    it('affiche le bouton Modifier si canEdit', async () => {
      render(<SignalementDetail {...defaultProps} canEdit={true} />)

      await waitFor(() => {
        expect(screen.getByText('Modifier')).toBeInTheDocument()
      })
    })
  })

  describe('Cloture', () => {
    it('appelle cloturerSignalement au clic', async () => {
      mockGetSignalement.mockResolvedValueOnce(createMockSignalement({ statut: 'traite' }))
      const cloture = createMockSignalement({ statut: 'cloture' })
      mockCloturerSignalement.mockResolvedValueOnce(cloture)

      const user = userEvent.setup()
      render(<SignalementDetail {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Clôturer')).toBeInTheDocument()
      })

      await user.click(screen.getByText('Clôturer'))

      await waitFor(() => {
        expect(mockCloturerSignalement).toHaveBeenCalledWith(1)
        expect(mockOnUpdate).toHaveBeenCalledWith(cloture)
      })
    })
  })

  describe('Reouverture', () => {
    it('appelle reouvrirSignalement au clic', async () => {
      mockGetSignalement.mockResolvedValueOnce(createMockSignalement({ statut: 'cloture' }))
      const reouvert = createMockSignalement({ statut: 'ouvert' })
      mockReouvrirSignalement.mockResolvedValueOnce(reouvert)

      const user = userEvent.setup()
      render(<SignalementDetail {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Réouvrir')).toBeInTheDocument()
      })

      await user.click(screen.getByText('Réouvrir'))

      await waitFor(() => {
        expect(mockReouvrirSignalement).toHaveBeenCalledWith(1)
        expect(mockOnUpdate).toHaveBeenCalledWith(reouvert)
      })
    })
  })

  describe('Fermeture', () => {
    it('appelle onClose au clic sur le bouton fermer', async () => {
      const user = userEvent.setup()
      render(<SignalementDetail {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Signalement Test')).toBeInTheDocument()
      })

      await user.click(screen.getByLabelText('Fermer'))
      expect(mockOnClose).toHaveBeenCalled()
    })
  })

  describe('Commentaire de traitement', () => {
    it('affiche le commentaire si present', async () => {
      mockGetSignalement.mockResolvedValueOnce(createMockSignalement({
        statut: 'traite',
        commentaire_traitement: 'Probleme resolu par le plombier',
      }))

      render(<SignalementDetail {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Commentaire de traitement')).toBeInTheDocument()
        expect(screen.getByText('Probleme resolu par le plombier')).toBeInTheDocument()
      })
    })
  })

  describe('Localisation', () => {
    it('affiche la localisation si presente', async () => {
      mockGetSignalement.mockResolvedValueOnce(createMockSignalement({
        localisation: 'Etage 2, Bureau 205',
      }))

      render(<SignalementDetail {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Etage 2, Bureau 205')).toBeInTheDocument()
      })
    })
  })
})
