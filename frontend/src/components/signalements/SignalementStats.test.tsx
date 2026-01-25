/**
 * Tests unitaires pour SignalementStats
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import SignalementStats from './SignalementStats'
import * as signalementsService from '../../services/signalements'

vi.mock('../../services/signalements', () => ({
  getStatistiques: vi.fn(),
}))

const mockStats = {
  total: 50,
  en_retard: 5,
  traites_cette_semaine: 12,
  taux_resolution: 75.5,
  temps_moyen_resolution: 48,
  par_statut: {
    ouvert: 15,
    en_cours: 10,
    traite: 8,
    cloture: 17,
  },
  par_priorite: {
    critique: 5,
    haute: 12,
    moyenne: 20,
    basse: 13,
  },
}

describe('SignalementStats', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(signalementsService.getStatistiques).mockResolvedValue(mockStats)
  })

  describe('chargement', () => {
    it('affiche le message de chargement initialement', () => {
      vi.mocked(signalementsService.getStatistiques).mockImplementation(() => new Promise(() => {}))
      render(<SignalementStats />)

      expect(screen.getByText(/Chargement des statistiques/i)).toBeInTheDocument()
    })

    it('charge les statistiques au montage', async () => {
      render(<SignalementStats />)

      await waitFor(() => {
        expect(signalementsService.getStatistiques).toHaveBeenCalled()
      })
    })

    it('passe les parametres de filtre', async () => {
      render(<SignalementStats chantierId={5} dateDebut="2026-01-01" dateFin="2026-01-31" />)

      await waitFor(() => {
        expect(signalementsService.getStatistiques).toHaveBeenCalledWith(5, '2026-01-01', '2026-01-31')
      })
    })
  })

  describe('affichage des statistiques', () => {
    it('affiche le total de signalements', async () => {
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
      })
    })

    it('affiche les traites cette semaine', async () => {
      render(<SignalementStats />)

      await waitFor(() => {
        expect(screen.getByText('Traités cette semaine')).toBeInTheDocument()
      })
    })

    it('affiche le taux de resolution', async () => {
      render(<SignalementStats />)

      await waitFor(() => {
        expect(screen.getByText('Taux de résolution')).toBeInTheDocument()
        expect(screen.getByText('76%')).toBeInTheDocument()
      })
    })

    it('affiche la repartition par statut', async () => {
      render(<SignalementStats />)

      await waitFor(() => {
        expect(screen.getByText('Par statut')).toBeInTheDocument()
      })
    })

    it('affiche la repartition par priorite', async () => {
      render(<SignalementStats />)

      await waitFor(() => {
        expect(screen.getByText('Par priorité')).toBeInTheDocument()
      })
    })
  })

  describe('alerte en retard', () => {
    it('affiche l alerte si signalements en retard', async () => {
      render(<SignalementStats />)

      await waitFor(() => {
        expect(screen.getByText(/5 signalements en retard/i)).toBeInTheDocument()
      })
    })

    it('n affiche pas l alerte si aucun retard', async () => {
      vi.mocked(signalementsService.getStatistiques).mockResolvedValue({
        ...mockStats,
        en_retard: 0,
      })

      render(<SignalementStats />)

      await waitFor(() => {
        expect(screen.queryByText(/signalements en retard/i)).not.toBeInTheDocument()
      })
    })

    it('affiche singulier pour 1 retard', async () => {
      vi.mocked(signalementsService.getStatistiques).mockResolvedValue({
        ...mockStats,
        en_retard: 1,
      })

      render(<SignalementStats />)

      await waitFor(() => {
        expect(screen.getByText(/1 signalement en retard/i)).toBeInTheDocument()
      })
    })
  })

  describe('gestion des erreurs', () => {
    it('affiche l erreur en cas d echec', async () => {
      vi.mocked(signalementsService.getStatistiques).mockRejectedValue(new Error('Erreur serveur'))

      render(<SignalementStats />)

      await waitFor(() => {
        expect(screen.getByText('Erreur serveur')).toBeInTheDocument()
      })
    })

    it('affiche le bouton reessayer en cas d erreur', async () => {
      vi.mocked(signalementsService.getStatistiques).mockRejectedValue(new Error('Erreur'))

      render(<SignalementStats />)

      await waitFor(() => {
        expect(screen.getByText('Réessayer')).toBeInTheDocument()
      })
    })

    it('recharge au clic sur reessayer', async () => {
      vi.mocked(signalementsService.getStatistiques)
        .mockRejectedValueOnce(new Error('Erreur'))
        .mockResolvedValueOnce(mockStats)

      render(<SignalementStats />)

      await waitFor(() => {
        expect(screen.getByText('Réessayer')).toBeInTheDocument()
      })

      fireEvent.click(screen.getByText('Réessayer'))

      await waitFor(() => {
        expect(signalementsService.getStatistiques).toHaveBeenCalledTimes(2)
      })
    })
  })

  describe('rafraichissement', () => {
    it('recharge quand refreshTrigger change', async () => {
      const { rerender } = render(<SignalementStats refreshTrigger={1} />)

      await waitFor(() => {
        expect(signalementsService.getStatistiques).toHaveBeenCalledTimes(1)
      })

      rerender(<SignalementStats refreshTrigger={2} />)

      await waitFor(() => {
        expect(signalementsService.getStatistiques).toHaveBeenCalledTimes(2)
      })
    })
  })

  describe('formatage du temps', () => {
    it('affiche le temps en heures', async () => {
      vi.mocked(signalementsService.getStatistiques).mockResolvedValue({
        ...mockStats,
        temps_moyen_resolution: 5.5,
      })

      render(<SignalementStats />)

      await waitFor(() => {
        expect(screen.getByText(/5\.5h/)).toBeInTheDocument()
      })
    })

    it('affiche le temps en jours si plus de 24h', async () => {
      vi.mocked(signalementsService.getStatistiques).mockResolvedValue({
        ...mockStats,
        temps_moyen_resolution: 48,
      })

      render(<SignalementStats />)

      await waitFor(() => {
        expect(screen.getByText(/2j 0h/)).toBeInTheDocument()
      })
    })

    it('affiche le temps en minutes si moins d une heure', async () => {
      vi.mocked(signalementsService.getStatistiques).mockResolvedValue({
        ...mockStats,
        temps_moyen_resolution: 0.5,
      })

      render(<SignalementStats />)

      await waitFor(() => {
        expect(screen.getByText(/30 min/)).toBeInTheDocument()
      })
    })

    it('affiche tiret si pas de temps', async () => {
      vi.mocked(signalementsService.getStatistiques).mockResolvedValue({
        ...mockStats,
        temps_moyen_resolution: null,
      })

      render(<SignalementStats />)

      await waitFor(() => {
        expect(screen.getByText(/Temps moyen: -/)).toBeInTheDocument()
      })
    })
  })

  describe('resume performance', () => {
    it('affiche le resume des statuts', async () => {
      render(<SignalementStats />)

      await waitFor(() => {
        expect(screen.getByText('Résumé performance')).toBeInTheDocument()
        expect(screen.getByText(/Ouverts:/)).toBeInTheDocument()
        expect(screen.getByText(/En cours:/)).toBeInTheDocument()
        expect(screen.getByText(/Traités:/)).toBeInTheDocument()
        expect(screen.getByText(/Clôturés:/)).toBeInTheDocument()
      })
    })
  })
})
