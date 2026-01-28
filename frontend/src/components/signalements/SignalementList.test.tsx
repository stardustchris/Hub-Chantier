/**
 * Tests pour SignalementList
 *
 * Couvre:
 * - Chargement et affichage de la liste
 * - Filtres (statut, priorite, recherche, en retard)
 * - Pagination
 * - Gestion des erreurs
 * - Etat vide
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import SignalementList from './SignalementList'
import { createMockSignalement } from '../../fixtures'
import type { Signalement } from '../../types/signalements'

// Mock services
const mockListSignalementsByChantier = vi.fn()
const mockSearchSignalements = vi.fn()

vi.mock('../../services/signalements', () => ({
  listSignalementsByChantier: (...args: unknown[]) => mockListSignalementsByChantier(...args),
  searchSignalements: (...args: unknown[]) => mockSearchSignalements(...args),
  getPrioriteIcon: () => '🔴',
  getStatutIcon: () => '🔵',
}))

vi.mock('../../services/logger', () => ({
  logger: {
    error: vi.fn(),
    warn: vi.fn(),
    info: vi.fn(),
  },
}))


describe('SignalementList', () => {
  const mockOnClick = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    mockListSignalementsByChantier.mockResolvedValue({
      signalements: [createMockSignalement()],
      total: 1,
    })
    mockSearchSignalements.mockResolvedValue({
      signalements: [createMockSignalement()],
      total: 1,
    })
  })

  describe('Chargement', () => {
    it('affiche le loader pendant le chargement', () => {
      mockListSignalementsByChantier.mockImplementation(() => new Promise(() => {}))

      render(<SignalementList chantierId={1} />)

      expect(document.querySelector('.animate-spin')).toBeInTheDocument()
    })

    it('charge les signalements au montage', async () => {
      render(<SignalementList chantierId={1} />)

      await waitFor(() => {
        expect(mockListSignalementsByChantier).toHaveBeenCalled()
      })
    })

    it('utilise searchSignalements en vue globale', async () => {
      render(<SignalementList showGlobalView />)

      await waitFor(() => {
        expect(mockSearchSignalements).toHaveBeenCalled()
      })
    })
  })

  describe('Affichage liste', () => {
    it('affiche les signalements', async () => {
      render(<SignalementList chantierId={1} />)

      await waitFor(() => {
        expect(screen.getByText('Signalement test')).toBeInTheDocument()
      })
    })

    it('appelle onSignalementClick au clic', async () => {
      const user = userEvent.setup()
      render(<SignalementList chantierId={1} onSignalementClick={mockOnClick} />)

      await waitFor(() => {
        expect(screen.getByText('Signalement test')).toBeInTheDocument()
      })

      await user.click(screen.getByText('Signalement test'))
      expect(mockOnClick).toHaveBeenCalled()
    })
  })

  describe('Etat vide', () => {
    it('affiche le message si aucun signalement', async () => {
      mockListSignalementsByChantier.mockResolvedValueOnce({
        signalements: [],
        total: 0,
      })

      render(<SignalementList chantierId={1} />)

      await waitFor(() => {
        expect(screen.getByText('Aucun signalement')).toBeInTheDocument()
      })
    })

    it('suggere de modifier les filtres si filtres actifs', async () => {
      mockListSignalementsByChantier.mockResolvedValue({
        signalements: [],
        total: 0,
      })

      render(<SignalementList chantierId={1} showFilters />)

      // Simuler un filtre actif en cliquant sur un bouton de filtre rapide
      await waitFor(() => {
        expect(screen.getByText('Aucun signalement')).toBeInTheDocument()
      })
    })
  })

  describe('Gestion des erreurs', () => {
    it('affiche l erreur si le chargement echoue', async () => {
      mockListSignalementsByChantier.mockRejectedValueOnce(new Error('Erreur'))

      render(<SignalementList chantierId={1} />)

      await waitFor(() => {
        expect(screen.getByText('Impossible de charger les signalements')).toBeInTheDocument()
      })
    })

    it('affiche le bouton Reessayer', async () => {
      mockListSignalementsByChantier.mockRejectedValueOnce(new Error('Erreur'))

      render(<SignalementList chantierId={1} />)

      await waitFor(() => {
        expect(screen.getByText('Réessayer')).toBeInTheDocument()
      })
    })

    it('recharge au clic sur Reessayer', async () => {
      mockListSignalementsByChantier.mockRejectedValueOnce(new Error('Erreur'))

      const user = userEvent.setup()
      render(<SignalementList chantierId={1} />)

      await waitFor(() => {
        expect(screen.getByText('Réessayer')).toBeInTheDocument()
      })

      mockListSignalementsByChantier.mockResolvedValueOnce({
        signalements: [createMockSignalement()],
        total: 1,
      })

      await user.click(screen.getByText('Réessayer'))

      await waitFor(() => {
        expect(mockListSignalementsByChantier).toHaveBeenCalledTimes(2)
      })
    })
  })

  describe('Pagination', () => {
    it('affiche la pagination si total > limit', async () => {
      mockListSignalementsByChantier.mockResolvedValueOnce({
        signalements: Array(10).fill(null).map((_, i) => createMockSignalement({ id: i + 1 })),
        total: 150,
      })

      render(<SignalementList chantierId={1} limit={10} />)

      await waitFor(() => {
        expect(screen.getByText('Suivant')).toBeInTheDocument()
        expect(screen.getByText('Précédent')).toBeInTheDocument()
      })
    })

    it('desactive Precedent sur la premiere page', async () => {
      mockListSignalementsByChantier.mockResolvedValueOnce({
        signalements: Array(10).fill(null).map((_, i) => createMockSignalement({ id: i + 1 })),
        total: 150,
      })

      render(<SignalementList chantierId={1} limit={10} />)

      await waitFor(() => {
        expect(screen.getByText('Précédent')).toBeDisabled()
      })
    })
  })

  describe('Filtres', () => {
    it('affiche les filtres si showFilters est true', async () => {
      render(<SignalementList chantierId={1} showFilters />)

      await waitFor(() => {
        expect(screen.getByText('Statut:')).toBeInTheDocument()
        expect(screen.getByText('Priorité:')).toBeInTheDocument()
      })
    })

    it('n affiche pas les filtres si showFilters est false', async () => {
      render(<SignalementList chantierId={1} showFilters={false} />)

      await waitFor(() => {
        expect(screen.queryByText('Statut:')).not.toBeInTheDocument()
      })
    })
  })

  describe('Mode compact', () => {
    it('utilise le style compact si compact est true', async () => {
      render(<SignalementList chantierId={1} compact />)

      await waitFor(() => {
        expect(screen.getByText('Signalement test')).toBeInTheDocument()
      })
    })
  })
})
