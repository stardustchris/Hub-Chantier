/**
 * Tests unitaires pour RessourceCard
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import RessourceCard from './RessourceCard'
import type { Ressource } from '../../types/logistique'

// Mock de l'api logistique
vi.mock('../../api/logistique', () => ({
  formatPlageHoraire: (debut: string, fin: string) => `${debut} - ${fin}`,
}))

// Mock des types logistique
vi.mock('../../types/logistique', () => ({
  CATEGORIES_RESSOURCES: {
    materiel: { label: 'Matériel', color: '#3498DB' },
    vehicule: { label: 'Véhicule', color: '#27AE60' },
    espace: { label: 'Espace', color: '#9B59B6' },
    humain: { label: 'Humain', color: '#E67E22' },
  },
}))

const createMockRessource = (overrides: Partial<Ressource> = {}): Ressource => ({
  id: 1,
  code: 'GRU-01',
  nom: 'Grue à tour 45m',
  description: 'Grue de chantier pour levage lourd',
  categorie: 'engin_levage',
  categorie_label: 'Engin de levage',
  couleur: '#E74C3C',
  actif: true,
  validation_requise: true,
  heure_debut_defaut: '08:00',
  heure_fin_defaut: '18:00',
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
  ...overrides,
})

describe('RessourceCard', () => {
  describe('rendering', () => {
    it('affiche le code de la ressource', () => {
      render(<RessourceCard ressource={createMockRessource()} />)
      expect(screen.getByText('[GRU-01]')).toBeInTheDocument()
    })

    it('affiche le nom de la ressource', () => {
      render(<RessourceCard ressource={createMockRessource()} />)
      expect(screen.getByText('Grue à tour 45m')).toBeInTheDocument()
    })

    it('affiche la description', () => {
      render(<RessourceCard ressource={createMockRessource()} />)
      expect(screen.getByText('Grue de chantier pour levage lourd')).toBeInTheDocument()
    })

    it('affiche la plage horaire', () => {
      render(<RessourceCard ressource={createMockRessource()} />)
      expect(screen.getByText('08:00 - 18:00')).toBeInTheDocument()
    })

    it('affiche le badge validation requise', () => {
      render(<RessourceCard ressource={createMockRessource({ validation_requise: true })} />)
      expect(screen.getByText('Validation N+1')).toBeInTheDocument()
    })

    it('affiche le badge sans validation', () => {
      render(<RessourceCard ressource={createMockRessource({ validation_requise: false })} />)
      expect(screen.getByText('Sans validation')).toBeInTheDocument()
    })
  })

  describe('photo et avatar', () => {
    it('affiche la photo si disponible', () => {
      render(<RessourceCard ressource={createMockRessource({ photo_url: 'https://example.com/grue.jpg' })} />)
      expect(screen.getByAltText('Grue à tour 45m')).toHaveAttribute('src', 'https://example.com/grue.jpg')
    })

    it('affiche un avatar avec les initiales du code si pas de photo', () => {
      render(<RessourceCard ressource={createMockRessource({ photo_url: undefined })} />)
      expect(screen.getByText('GR')).toBeInTheDocument()
    })
  })

  describe('etat actif/inactif', () => {
    it('applique l opacite reduite si inactif', () => {
      const { container } = render(<RessourceCard ressource={createMockRessource({ actif: false })} />)
      expect(container.firstChild).toHaveClass('opacity-60')
    })

    it('affiche le badge Inactif', () => {
      render(<RessourceCard ressource={createMockRessource({ actif: false })} />)
      expect(screen.getByText('Inactif')).toBeInTheDocument()
    })

    it('n affiche pas le badge si actif', () => {
      render(<RessourceCard ressource={createMockRessource({ actif: true })} />)
      expect(screen.queryByText('Inactif')).not.toBeInTheDocument()
    })
  })

  describe('selection', () => {
    it('applique le style selectionne', () => {
      const { container } = render(<RessourceCard ressource={createMockRessource()} selected />)
      expect(container.firstChild).toHaveClass('border-blue-500')
    })

    it('n applique pas le style si non selectionne', () => {
      const { container } = render(<RessourceCard ressource={createMockRessource()} selected={false} />)
      expect(container.firstChild).toHaveClass('border-gray-200')
    })
  })

  describe('interactions', () => {
    it('appelle onSelect au clic', () => {
      const handleSelect = vi.fn()
      render(<RessourceCard ressource={createMockRessource()} onSelect={handleSelect} />)

      fireEvent.click(screen.getByText('Grue à tour 45m'))

      expect(handleSelect).toHaveBeenCalledWith(expect.objectContaining({ id: '1' }))
    })

    it('affiche le bouton editer si onEdit fourni', () => {
      render(<RessourceCard ressource={createMockRessource()} onEdit={vi.fn()} />)
      expect(screen.getByRole('button')).toBeInTheDocument()
    })

    it('n affiche pas le bouton editer si onEdit non fourni', () => {
      render(<RessourceCard ressource={createMockRessource()} />)
      expect(screen.queryByRole('button')).not.toBeInTheDocument()
    })

    it('appelle onEdit au clic sur le bouton editer', () => {
      const handleEdit = vi.fn()
      render(<RessourceCard ressource={createMockRessource()} onEdit={handleEdit} />)

      fireEvent.click(screen.getByRole('button'))

      expect(handleEdit).toHaveBeenCalledWith(expect.objectContaining({ id: '1' }))
    })

    it('empeche la propagation du clic sur editer', () => {
      const handleEdit = vi.fn()
      const handleSelect = vi.fn()
      render(<RessourceCard ressource={createMockRessource()} onEdit={handleEdit} onSelect={handleSelect} />)

      fireEvent.click(screen.getByRole('button'))

      expect(handleEdit).toHaveBeenCalled()
      expect(handleSelect).not.toHaveBeenCalled()
    })
  })

  describe('couleur', () => {
    it('affiche la barre de couleur', () => {
      const { container } = render(<RessourceCard ressource={createMockRessource({ couleur: '#FF5733' })} />)
      const colorBar = container.querySelector('.h-2.rounded-t-lg')
      expect(colorBar).toHaveStyle({ backgroundColor: '#FF5733' })
    })
  })

  describe('description optionnelle', () => {
    it('n affiche pas la description si absente', () => {
      render(<RessourceCard ressource={createMockRessource({ description: undefined })} />)
      expect(screen.queryByText('Grue de chantier pour levage lourd')).not.toBeInTheDocument()
    })
  })
})
