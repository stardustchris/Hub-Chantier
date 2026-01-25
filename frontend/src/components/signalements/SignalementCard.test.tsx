/**
 * Tests unitaires pour SignalementCard
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import SignalementCard from './SignalementCard'
import type { Signalement } from '../../types/signalements'

// Mock des services
vi.mock('../../services/signalements', () => ({
  getPrioriteIcon: (priorite: string) => priorite === 'haute' ? '🔴' : priorite === 'moyenne' ? '🟡' : '🟢',
  getStatutIcon: (statut: string) => statut === 'ouvert' ? '📌' : statut === 'traite' ? '✅' : '🔒',
}))

const createMockSignalement = (overrides: Partial<Signalement> = {}): Signalement => ({
  id: '1',
  titre: 'Signalement Test',
  description: 'Description du signalement test',
  priorite: 'moyenne',
  priorite_label: 'Moyenne',
  statut: 'ouvert',
  statut_label: 'Ouvert',
  cree_par: '1',
  cree_par_nom: 'Jean Dupont',
  assigne_a: '2',
  assigne_a_nom: 'Marie Martin',
  chantier_id: '1',
  chantier_nom: 'Chantier A',
  localisation: 'Zone B',
  created_at: '2026-01-20T10:00:00Z',
  updated_at: '2026-01-20T10:00:00Z',
  est_en_retard: false,
  pourcentage_temps: 30,
  temps_restant: '2 jours',
  nb_reponses: 3,
  nb_escalades: 0,
  ...overrides,
})

describe('SignalementCard', () => {
  describe('mode normal', () => {
    it('affiche le titre du signalement', () => {
      render(<SignalementCard signalement={createMockSignalement()} />)
      expect(screen.getByText('Signalement Test')).toBeInTheDocument()
    })

    it('affiche la description', () => {
      render(<SignalementCard signalement={createMockSignalement()} />)
      expect(screen.getByText('Description du signalement test')).toBeInTheDocument()
    })

    it('affiche le label de priorite', () => {
      render(<SignalementCard signalement={createMockSignalement()} />)
      expect(screen.getByText('Moyenne')).toBeInTheDocument()
    })

    it('affiche le label de statut', () => {
      render(<SignalementCard signalement={createMockSignalement()} />)
      expect(screen.getByText(/Ouvert/)).toBeInTheDocument()
    })

    it('affiche le createur', () => {
      render(<SignalementCard signalement={createMockSignalement()} />)
      expect(screen.getByText(/Jean Dupont/)).toBeInTheDocument()
    })

    it('affiche l assignation', () => {
      render(<SignalementCard signalement={createMockSignalement()} />)
      expect(screen.getByText(/Marie Martin/)).toBeInTheDocument()
    })

    it('affiche la localisation', () => {
      render(<SignalementCard signalement={createMockSignalement()} />)
      expect(screen.getByText(/Zone B/)).toBeInTheDocument()
    })

    it('affiche le nombre de reponses', () => {
      render(<SignalementCard signalement={createMockSignalement()} />)
      expect(screen.getByText(/3 réponses/)).toBeInTheDocument()
    })

    it('affiche la barre de progression', () => {
      const { container } = render(<SignalementCard signalement={createMockSignalement({ pourcentage_temps: 30 })} />)
      const progressBar = container.querySelector('[style*="width: 30%"]')
      expect(progressBar).toBeInTheDocument()
    })
  })

  describe('etat en retard', () => {
    it('affiche le badge EN RETARD', () => {
      render(<SignalementCard signalement={createMockSignalement({ est_en_retard: true })} />)
      expect(screen.getByText('EN RETARD')).toBeInTheDocument()
    })

    it('applique le style de bordure rouge', () => {
      const { container } = render(<SignalementCard signalement={createMockSignalement({ est_en_retard: true })} />)
      expect(container.firstChild).toHaveClass('border-red-300')
    })
  })

  describe('progression du temps', () => {
    it('affiche une barre verte sous 50%', () => {
      const { container } = render(<SignalementCard signalement={createMockSignalement({ pourcentage_temps: 30 })} />)
      const progressBar = container.querySelector('.bg-green-500')
      expect(progressBar).toBeInTheDocument()
    })

    it('affiche une barre orange entre 50% et 100%', () => {
      const { container } = render(<SignalementCard signalement={createMockSignalement({ pourcentage_temps: 75 })} />)
      const progressBar = container.querySelector('.bg-orange-500')
      expect(progressBar).toBeInTheDocument()
    })

    it('affiche une barre rouge a 100%+', () => {
      const { container } = render(<SignalementCard signalement={createMockSignalement({ pourcentage_temps: 120 })} />)
      const progressBar = container.querySelector('.bg-red-500')
      expect(progressBar).toBeInTheDocument()
    })
  })

  describe('interactions', () => {
    it('appelle onClick au clic sur la carte', () => {
      const handleClick = vi.fn()
      render(<SignalementCard signalement={createMockSignalement()} onClick={handleClick} />)

      fireEvent.click(screen.getByText('Signalement Test'))
      expect(handleClick).toHaveBeenCalledWith(expect.objectContaining({ id: '1' }))
    })

    it('affiche le bouton Traiter pour statut ouvert', () => {
      render(<SignalementCard signalement={createMockSignalement({ statut: 'ouvert' })} onTraiter={vi.fn()} />)
      expect(screen.getByText('Traiter')).toBeInTheDocument()
    })

    it('affiche le bouton Traiter pour statut en_cours', () => {
      render(<SignalementCard signalement={createMockSignalement({ statut: 'en_cours' })} onTraiter={vi.fn()} />)
      expect(screen.getByText('Traiter')).toBeInTheDocument()
    })

    it('appelle onTraiter au clic', () => {
      const handleTraiter = vi.fn()
      render(<SignalementCard signalement={createMockSignalement()} onTraiter={handleTraiter} />)

      fireEvent.click(screen.getByText('Traiter'))
      expect(handleTraiter).toHaveBeenCalledWith(expect.objectContaining({ id: '1' }))
    })

    it('affiche le bouton Cloturer pour statut traite', () => {
      render(<SignalementCard signalement={createMockSignalement({ statut: 'traite' })} onCloturer={vi.fn()} />)
      expect(screen.getByText('Clôturer')).toBeInTheDocument()
    })

    it('appelle onCloturer au clic', () => {
      const handleCloturer = vi.fn()
      render(<SignalementCard signalement={createMockSignalement({ statut: 'traite' })} onCloturer={handleCloturer} />)

      fireEvent.click(screen.getByText('Clôturer'))
      expect(handleCloturer).toHaveBeenCalledWith(expect.objectContaining({ id: '1' }))
    })
  })

  describe('mode compact', () => {
    it('affiche une version simplifiee', () => {
      render(<SignalementCard signalement={createMockSignalement()} compact />)
      expect(screen.getByText('Signalement Test')).toBeInTheDocument()
      // En mode compact, pas de description
      expect(screen.queryByText('Description du signalement test')).not.toBeInTheDocument()
    })

    it('affiche En retard pour signalement en retard', () => {
      render(<SignalementCard signalement={createMockSignalement({ est_en_retard: true })} compact />)
      expect(screen.getByText('En retard')).toBeInTheDocument()
    })

    it('applique le style compact en retard', () => {
      const { container } = render(<SignalementCard signalement={createMockSignalement({ est_en_retard: true })} compact />)
      expect(container.firstChild).toHaveClass('border-red-300')
      expect(container.firstChild).toHaveClass('bg-red-50')
    })
  })

  describe('cas limites', () => {
    it('affiche Non assigne si pas d assignation', () => {
      render(<SignalementCard signalement={createMockSignalement({ assigne_a: null, assigne_a_nom: null })} />)
      expect(screen.getByText(/Non assigné/)).toBeInTheDocument()
    })

    it('cache la barre de progression pour statut cloture', () => {
      const { container } = render(<SignalementCard signalement={createMockSignalement({ statut: 'cloture' })} />)
      expect(container.querySelector('.bg-gray-200')).not.toBeInTheDocument()
    })

    it('affiche les escalades si presentes', () => {
      render(<SignalementCard signalement={createMockSignalement({ nb_escalades: 2 })} />)
      expect(screen.getByText(/2 escalades/)).toBeInTheDocument()
    })

    it('affiche Delai depasse si pas de temps restant', () => {
      render(<SignalementCard signalement={createMockSignalement({ temps_restant: '' })} />)
      expect(screen.getByText('Délai dépassé')).toBeInTheDocument()
    })
  })
})
