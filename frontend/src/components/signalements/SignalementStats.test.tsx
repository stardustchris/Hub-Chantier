/**
 * Tests pour SignalementStats
 *
 * Couvre:
 * - Chargement et affichage des statistiques
 * - Affichage des indicateurs principaux
 * - Affichage par statut et priorite
 * - Alertes en retard
 * - Gestion des erreurs
 * - Formatage des durees
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import SignalementStats from './SignalementStats'
import type { SignalementStatsResponse } from '../../types/signalements'

// Mock services
const mockGetStatistiques = vi.fn()

vi.mock('../../services/signalements', () => ({
  getStatistiques: (...args: unknown[]) => mockGetStatistiques(...args),
}))

const createMockStats = (overrides: Partial<SignalementStatsResponse> = {}): SignalementStatsResponse => ({
  total: 50,
  en_retard: 3,
  traites_cette_semaine: 12,
  taux_resolution: 75.5,
  temps_moyen_resolution: 48,
  par_statut: {
    ouvert: 10,
    en_cours: 15,
    traite: 20,
    cloture: 5,
  },
  par_priorite: {
    critique: 5,
    haute: 15,
    moyenne: 20,
    basse: 10,
  },
  ...overrides,
})

describe('SignalementStats', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockGetStatistiques.mockResolvedValue(createMockStats())
  })

  describe('Chargement', () => {
    it('affiche le message de chargement', () => {
      mockGetStatistiques.mockImplementation(() => new Promise(() => {}))

      render(<SignalementStats />)

      expect(screen.getByText('Chargement des statistiques...')).toBeInTheDocument()
    })

    it('charge les statistiques au montage', async () => {
      render(<SignalementStats />)

      await waitFor(() => {
        expect(mockGetStatistiques).toHaveBeenCalled()
      })
    })

    it('passe les parametres au service', async () => {
      render(
        <SignalementStats
          chantierId={1}
          dateDebut="2024-01-01"
          dateFin="2024-12-31"
        />
      )

      await waitFor(() => {
        expect(mockGetStatistiques).toHaveBeenCalledWith(1, '2024-01-01', '2024-12-31')
      })
    })
  })

  describe('Indicateurs principaux', () => {
    it('affiche le total des signalements', async () => {
      render(<SignalementStats />)

      await waitFor(() => {
        expect(screen.getByText('Total signalements')).toBeInTheDocument()
        expect(screen.getByText('50')).toBeInTheDocument()
      })
    })

    it('affiche le nombre en retard', async () => {
      render(<SignalementStats />)

      await waitFor(() => {
        expect(screen.getByText('En retard')).toBeInTheDocument()
        expect(screen.getByText('3')).toBeInTheDocument()
      })
    })

    it('affiche les traites cette semaine', async () => {
      render(<SignalementStats />)

      await waitFor(() => {
        expect(screen.getByText('Traités cette semaine')).toBeInTheDocument()
        expect(screen.getByText('12')).toBeInTheDocument()
      })
    })

    it('affiche le taux de resolution', async () => {
      render(<SignalementStats />)

      await waitFor(() => {
        expect(screen.getByText('Taux de résolution')).toBeInTheDocument()
        expect(screen.getByText('76%')).toBeInTheDocument()
      })
    })
  })

  describe('Repartition par statut', () => {
    it('affiche la section par statut', async () => {
      render(<SignalementStats />)

      await waitFor(() => {
        expect(screen.getByText('Par statut')).toBeInTheDocument()
      })
    })

    it('affiche les compteurs par statut', async () => {
      render(<SignalementStats />)

      await waitFor(() => {
        // Les valeurs sont affichees (peuvent apparaitre plusieurs fois)
        expect(screen.getAllByText('10').length).toBeGreaterThanOrEqual(1) // ouvert
        expect(screen.getAllByText('15').length).toBeGreaterThanOrEqual(1) // en_cours
        expect(screen.getAllByText('20').length).toBeGreaterThanOrEqual(1) // traite
        expect(screen.getAllByText('5').length).toBeGreaterThanOrEqual(1) // cloture
      })
    })
  })

  describe('Repartition par priorite', () => {
    it('affiche la section par priorite', async () => {
      render(<SignalementStats />)

      await waitFor(() => {
        expect(screen.getByText('Par priorité')).toBeInTheDocument()
      })
    })
  })

  describe('Alertes', () => {
    it('affiche l alerte si signalements en retard', async () => {
      mockGetStatistiques.mockResolvedValueOnce(createMockStats({ en_retard: 5 }))

      render(<SignalementStats />)

      await waitFor(() => {
        expect(screen.getByText('5 signalements en retard')).toBeInTheDocument()
      })
    })

    it('n affiche pas l alerte si aucun en retard', async () => {
      mockGetStatistiques.mockResolvedValueOnce(createMockStats({ en_retard: 0 }))

      render(<SignalementStats />)

      await waitFor(() => {
        expect(screen.queryByText(/signalement.* en retard/)).not.toBeInTheDocument()
      })
    })
  })

  describe('Resume performance', () => {
    it('affiche le resume performance', async () => {
      render(<SignalementStats />)

      await waitFor(() => {
        expect(screen.getByText('Résumé performance')).toBeInTheDocument()
      })
    })
  })

  describe('Gestion des erreurs', () => {
    it('affiche l erreur si le chargement echoue', async () => {
      mockGetStatistiques.mockRejectedValueOnce(new Error('Erreur reseau'))

      render(<SignalementStats />)

      await waitFor(() => {
        expect(screen.getByText('Erreur reseau')).toBeInTheDocument()
      })
    })

    it('affiche le bouton Reessayer', async () => {
      mockGetStatistiques.mockRejectedValueOnce(new Error('Erreur'))

      render(<SignalementStats />)

      await waitFor(() => {
        expect(screen.getByText('Réessayer')).toBeInTheDocument()
      })
    })

    it('recharge les stats au clic sur Reessayer', async () => {
      mockGetStatistiques.mockRejectedValueOnce(new Error('Erreur'))

      const user = userEvent.setup()
      render(<SignalementStats />)

      await waitFor(() => {
        expect(screen.getByText('Réessayer')).toBeInTheDocument()
      })

      mockGetStatistiques.mockResolvedValueOnce(createMockStats())
      await user.click(screen.getByText('Réessayer'))

      await waitFor(() => {
        expect(mockGetStatistiques).toHaveBeenCalledTimes(2)
      })
    })
  })

  describe('Formatage durees', () => {
    it('formate les heures en jours et heures', async () => {
      mockGetStatistiques.mockResolvedValueOnce(createMockStats({ temps_moyen_resolution: 48 }))

      render(<SignalementStats />)

      await waitFor(() => {
        expect(screen.getByText(/2j 0h/)).toBeInTheDocument()
      })
    })

    it('formate les petites durees en heures', async () => {
      mockGetStatistiques.mockResolvedValueOnce(createMockStats({ temps_moyen_resolution: 5.5 }))

      render(<SignalementStats />)

      await waitFor(() => {
        expect(screen.getByText(/5.5h/)).toBeInTheDocument()
      })
    })
  })

  describe('Refresh trigger', () => {
    it('recharge les stats quand refreshTrigger change', async () => {
      const { rerender } = render(<SignalementStats refreshTrigger={0} />)

      await waitFor(() => {
        expect(mockGetStatistiques).toHaveBeenCalledTimes(1)
      })

      rerender(<SignalementStats refreshTrigger={1} />)

      await waitFor(() => {
        expect(mockGetStatistiques).toHaveBeenCalledTimes(2)
      })
    })
  })
})
