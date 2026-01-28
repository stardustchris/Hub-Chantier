/**
 * Tests pour SignalementCard
 *
 * Couvre:
 * - Mode normal et compact
 * - Affichage des informations
 * - Badge en retard
 * - Barre de progression
 * - Actions (traiter, cloturer)
 * - Callbacks onClick
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import SignalementCard from './SignalementCard'
import { createMockSignalement } from '../../fixtures'
import type { Signalement } from '../../types/signalements'

// Mock services
vi.mock('../../services/signalements', () => ({
  getPrioriteIcon: (priorite: string) => priorite === 'critique' ? '🔴' : '🟡',
  getStatutIcon: (statut: string) => statut === 'cloture' ? '✅' : '🔵',
}))

vi.mock('../../utils/dates', () => ({
  formatDateDayMonthYearTime: () => '15/01/2024 10:00',
}))

// Using shared fixture from ../../fixtures

describe('SignalementCard', () => {
  const mockOnClick = vi.fn()
  const mockOnTraiter = vi.fn()
  const mockOnCloturer = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Mode normal', () => {
    it('affiche le titre du signalement', () => {
      render(<SignalementCard signalement={createMockSignalement()} />)
      expect(screen.getByText('Fuite eau')).toBeInTheDocument()
    })

    it('affiche la description', () => {
      render(<SignalementCard signalement={createMockSignalement()} />)
      expect(screen.getByText('Il y a une fuite au plafond')).toBeInTheDocument()
    })

    it('affiche le badge de priorite', () => {
      render(<SignalementCard signalement={createMockSignalement()} />)
      expect(screen.getByText('Haute')).toBeInTheDocument()
    })

    it('affiche le badge de statut', () => {
      render(<SignalementCard signalement={createMockSignalement()} />)
      expect(screen.getByText(/Ouvert/)).toBeInTheDocument()
    })

    it('affiche le createur', () => {
      render(<SignalementCard signalement={createMockSignalement()} />)
      expect(screen.getByText('Jean Dupont')).toBeInTheDocument()
    })

    it('affiche l assignation', () => {
      render(<SignalementCard signalement={createMockSignalement()} />)
      expect(screen.getByText('Marie Martin')).toBeInTheDocument()
    })

    it('affiche Non assigne si pas d assignation', () => {
      render(<SignalementCard signalement={createMockSignalement({ assigne_a: null, assigne_a_nom: undefined })} />)
      expect(screen.getByText('Non assigné')).toBeInTheDocument()
    })

    it('affiche le nombre de reponses', () => {
      render(<SignalementCard signalement={createMockSignalement({ nb_reponses: 3 })} />)
      expect(screen.getByText(/3 réponse/)).toBeInTheDocument()
    })

    it('affiche les escalades si presentes', () => {
      render(<SignalementCard signalement={createMockSignalement({ nb_escalades: 2 })} />)
      expect(screen.getByText(/2 escalades/)).toBeInTheDocument()
    })
  })

  describe('Badge EN RETARD', () => {
    it('affiche le badge EN RETARD si en retard', () => {
      render(<SignalementCard signalement={createMockSignalement({ est_en_retard: true })} />)
      expect(screen.getByText('EN RETARD')).toBeInTheDocument()
    })

    it('n affiche pas le badge si pas en retard', () => {
      render(<SignalementCard signalement={createMockSignalement({ est_en_retard: false })} />)
      expect(screen.queryByText('EN RETARD')).not.toBeInTheDocument()
    })
  })

  describe('Barre de progression', () => {
    it('affiche le pourcentage de temps ecoule', () => {
      render(<SignalementCard signalement={createMockSignalement({ pourcentage_temps: 50 })} />)
      expect(screen.getByText(/50%/)).toBeInTheDocument()
    })

    it('affiche le temps restant', () => {
      render(<SignalementCard signalement={createMockSignalement({ temps_restant: '2j 5h' })} />)
      expect(screen.getByText('2j 5h')).toBeInTheDocument()
    })

    it('n affiche pas la barre pour signalement cloture', () => {
      render(<SignalementCard signalement={createMockSignalement({ statut: 'cloture' })} />)
      expect(screen.queryByText(/Temps ecoule/)).not.toBeInTheDocument()
    })
  })

  describe('Mode compact', () => {
    it('affiche le titre en mode compact', () => {
      render(<SignalementCard signalement={createMockSignalement()} compact />)
      expect(screen.getByText('Fuite eau')).toBeInTheDocument()
    })

    it('n affiche pas la description en mode compact', () => {
      render(<SignalementCard signalement={createMockSignalement()} compact />)
      expect(screen.queryByText('Il y a une fuite au plafond')).not.toBeInTheDocument()
    })

    it('affiche En retard en mode compact si applicable', () => {
      render(<SignalementCard signalement={createMockSignalement({ est_en_retard: true })} compact />)
      expect(screen.getByText('En retard')).toBeInTheDocument()
    })
  })

  describe('Actions', () => {
    it('affiche le bouton Traiter pour signalement ouvert', () => {
      render(<SignalementCard signalement={createMockSignalement({ statut: 'ouvert' })} onTraiter={mockOnTraiter} />)
      expect(screen.getByText('Traiter')).toBeInTheDocument()
    })

    it('affiche le bouton Traiter pour signalement en_cours', () => {
      render(<SignalementCard signalement={createMockSignalement({ statut: 'en_cours' })} onTraiter={mockOnTraiter} />)
      expect(screen.getByText('Traiter')).toBeInTheDocument()
    })

    it('affiche le bouton Cloturer pour signalement traite', () => {
      render(<SignalementCard signalement={createMockSignalement({ statut: 'traite' })} onCloturer={mockOnCloturer} />)
      expect(screen.getByText('Clôturer')).toBeInTheDocument()
    })

    it('appelle onTraiter au clic sur Traiter', async () => {
      const user = userEvent.setup()
      render(<SignalementCard signalement={createMockSignalement()} onTraiter={mockOnTraiter} />)

      await user.click(screen.getByText('Traiter'))

      expect(mockOnTraiter).toHaveBeenCalled()
    })

    it('appelle onCloturer au clic sur Cloturer', async () => {
      const user = userEvent.setup()
      render(<SignalementCard signalement={createMockSignalement({ statut: 'traite' })} onCloturer={mockOnCloturer} />)

      await user.click(screen.getByText('Clôturer'))

      expect(mockOnCloturer).toHaveBeenCalled()
    })

    it('n appelle pas onClick au clic sur les boutons d action', async () => {
      const user = userEvent.setup()
      render(
        <SignalementCard
          signalement={createMockSignalement()}
          onClick={mockOnClick}
          onTraiter={mockOnTraiter}
        />
      )

      await user.click(screen.getByText('Traiter'))

      expect(mockOnTraiter).toHaveBeenCalled()
      expect(mockOnClick).not.toHaveBeenCalled()
    })
  })

  describe('Callback onClick', () => {
    it('appelle onClick au clic sur la carte', async () => {
      const user = userEvent.setup()
      render(<SignalementCard signalement={createMockSignalement()} onClick={mockOnClick} />)

      await user.click(screen.getByText('Fuite eau'))

      expect(mockOnClick).toHaveBeenCalledWith(expect.objectContaining({ id: 1, titre: 'Fuite eau' }))
    })
  })

  describe('Localisation', () => {
    it('affiche la localisation si presente', () => {
      render(<SignalementCard signalement={createMockSignalement({ localisation: 'Etage 2, Bureau 205' })} />)
      expect(screen.getByText('Etage 2, Bureau 205')).toBeInTheDocument()
    })
  })
})
