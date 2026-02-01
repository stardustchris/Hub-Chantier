/**
 * Tests pour BudgetsPage - Module 17 Phase 1
 * CDC FIN-01, FIN-02
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import BudgetsPage from './BudgetsPage'

// Mock Layout component
vi.mock('../components/Layout', () => ({
  default: ({ children, title }: { children: React.ReactNode; title: string }) => (
    <div data-testid="layout">
      <h1>{title}</h1>
      {children}
    </div>
  ),
}))

function renderBudgetsPage() {
  return render(
    <MemoryRouter>
      <BudgetsPage />
    </MemoryRouter>
  )
}

describe('BudgetsPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Affichage général', () => {
    it('affiche le titre "Budgets"', () => {
      renderBudgetsPage()
      expect(screen.getByText('Budgets')).toBeInTheDocument()
    })

    it('affiche les statistiques globales', () => {
      renderBudgetsPage()
      expect(screen.getByText('Budget Prévisionnel')).toBeInTheDocument()
      expect(screen.getByText('Engagé')).toBeInTheDocument()
      expect(screen.getByText('Réalisé')).toBeInTheDocument()
    })

    it('affiche le bouton "Nouveau budget"', () => {
      renderBudgetsPage()
      expect(screen.getByText('Nouveau budget')).toBeInTheDocument()
    })

    it('affiche le bouton "Filtrer"', () => {
      renderBudgetsPage()
      expect(screen.getByText('Filtrer')).toBeInTheDocument()
    })

    it('affiche le champ de recherche', () => {
      renderBudgetsPage()
      expect(screen.getByPlaceholderText('Rechercher un chantier...')).toBeInTheDocument()
    })
  })

  describe('Statistiques globales', () => {
    it('affiche le budget prévisionnel total', () => {
      renderBudgetsPage()
      // Total: 850000 + 2100000 + 500000 = 3450000
      expect(screen.getByText(/3\s*450\s*000/)).toBeInTheDocument()
    })

    it('affiche le montant engagé total', () => {
      renderBudgetsPage()
      // Total engagé: 720000 + 1950000 + 520000 = 3190000
      expect(screen.getByText(/3\s*190\s*000/)).toBeInTheDocument()
    })

    it('affiche le montant réalisé total', () => {
      renderBudgetsPage()
      // Total réalisé: 650000 + 1800000 + 480000 = 2930000
      expect(screen.getByText(/2\s*930\s*000/)).toBeInTheDocument()
    })

    it('affiche le pourcentage d\'engagement', () => {
      renderBudgetsPage()
      // (3190000 / 3450000) * 100 = 92.5%
      expect(screen.getByText(/92\.5% du prévu/)).toBeInTheDocument()
    })

    it('affiche le pourcentage de réalisation', () => {
      renderBudgetsPage()
      // (2930000 / 3450000) * 100 = 84.9%
      expect(screen.getByText(/84\.9% du prévu/)).toBeInTheDocument()
    })
  })

  describe('Liste des budgets', () => {
    it('affiche tous les chantiers par défaut', () => {
      renderBudgetsPage()
      expect(screen.getByText('Villa Moderne Duplex')).toBeInTheDocument()
      expect(screen.getByText('Résidence Les Jardins')).toBeInTheDocument()
      expect(screen.getByText('École Jean Jaurès')).toBeInTheDocument()
    })

    it('affiche les montants pour chaque chantier', () => {
      renderBudgetsPage()
      // Villa Moderne Duplex
      expect(screen.getByText(/850\s*000\s*€/)).toBeInTheDocument()
      expect(screen.getByText(/720\s*000\s*€/)).toBeInTheDocument()
      expect(screen.getByText(/650\s*000\s*€/)).toBeInTheDocument()
    })

    it('affiche les dates pour chaque chantier', () => {
      renderBudgetsPage()
      expect(screen.getByText(/15\/01\/2026/)).toBeInTheDocument()
      expect(screen.getByText(/30\/08\/2026/)).toBeInTheDocument()
    })

    it('affiche le statut de chaque chantier', () => {
      renderBudgetsPage()
      expect(screen.getAllByText('Actif')).toHaveLength(2)
      expect(screen.getByText('Dépassé')).toBeInTheDocument()
    })

    it('affiche le taux de consommation pour chaque chantier', () => {
      renderBudgetsPage()
      expect(screen.getByText('76.5%')).toBeInTheDocument() // Villa
      expect(screen.getByText('85.7%')).toBeInTheDocument() // Résidence
      expect(screen.getByText('104.0%')).toBeInTheDocument() // École
    })

    it('affiche le taux d\'engagement pour chaque chantier', () => {
      renderBudgetsPage()
      // Taux engagement = (engagé / prévu) * 100
      // Villa: (720000 / 850000) * 100 = 84.7%
      expect(screen.getByText('84.7%')).toBeInTheDocument()
    })
  })

  describe('Recherche', () => {
    it('filtre les chantiers par nom', async () => {
      const user = userEvent.setup()
      renderBudgetsPage()

      const searchInput = screen.getByPlaceholderText('Rechercher un chantier...')
      await user.type(searchInput, 'Villa')

      expect(screen.getByText('Villa Moderne Duplex')).toBeInTheDocument()
      expect(screen.queryByText('Résidence Les Jardins')).not.toBeInTheDocument()
      expect(screen.queryByText('École Jean Jaurès')).not.toBeInTheDocument()
    })

    it('est insensible à la casse', async () => {
      const user = userEvent.setup()
      renderBudgetsPage()

      const searchInput = screen.getByPlaceholderText('Rechercher un chantier...')
      await user.type(searchInput, 'villa')

      expect(screen.getByText('Villa Moderne Duplex')).toBeInTheDocument()
    })

    it('affiche un message si aucun résultat', async () => {
      const user = userEvent.setup()
      renderBudgetsPage()

      const searchInput = screen.getByPlaceholderText('Rechercher un chantier...')
      await user.type(searchInput, 'Inexistant')

      expect(screen.getByText('Aucun budget trouvé')).toBeInTheDocument()
    })

    it('réaffiche tous les chantiers si le champ est vidé', async () => {
      const user = userEvent.setup()
      renderBudgetsPage()

      const searchInput = screen.getByPlaceholderText('Rechercher un chantier...')
      await user.type(searchInput, 'Villa')
      expect(screen.queryByText('Résidence Les Jardins')).not.toBeInTheDocument()

      await user.clear(searchInput)
      expect(screen.getByText('Résidence Les Jardins')).toBeInTheDocument()
    })
  })

  describe('Alertes de dépassement', () => {
    it('affiche une alerte pour les chantiers dépassés', () => {
      renderBudgetsPage()
      expect(screen.getByText('Budget dépassé')).toBeInTheDocument()
    })

    it('affiche le montant du dépassement', () => {
      renderBudgetsPage()
      // École: 520000 - 500000 = 20000 EUR
      expect(screen.getByText(/Dépassement de/)).toBeInTheDocument()
      expect(screen.getByText(/20\s*000\s*€/)).toBeInTheDocument()
    })

    it('n\'affiche pas d\'alerte pour les chantiers dans le budget', () => {
      renderBudgetsPage()
      const alerts = screen.getAllByText(/Budget dépassé/)
      expect(alerts).toHaveLength(1) // Seulement École Jean Jaurès
    })
  })

  describe('Barres de progression', () => {
    it('affiche une barre verte pour consommation < 80%', () => {
      renderBudgetsPage()
      const progressBars = document.querySelectorAll('.bg-green-500')
      expect(progressBars.length).toBeGreaterThan(0)
    })

    it('affiche une barre orange pour consommation 80-100%', () => {
      renderBudgetsPage()
      const progressBars = document.querySelectorAll('.bg-orange-500')
      expect(progressBars.length).toBeGreaterThan(0)
    })

    it('affiche une barre rouge pour consommation > 100%', () => {
      renderBudgetsPage()
      const progressBars = document.querySelectorAll('.bg-red-500')
      expect(progressBars.length).toBeGreaterThan(0)
    })
  })

  describe('Statuts visuels', () => {
    it('applique le style vert pour statut "actif"', () => {
      renderBudgetsPage()
      const actifBadges = screen.getAllByText('Actif')
      actifBadges.forEach((badge) => {
        expect(badge.className).toContain('bg-green-100')
        expect(badge.className).toContain('text-green-800')
      })
    })

    it('applique le style rouge pour statut "depasse"', () => {
      renderBudgetsPage()
      const depasseBadge = screen.getByText('Dépassé')
      expect(depasseBadge.className).toContain('bg-red-100')
      expect(depasseBadge.className).toContain('text-red-800')
    })
  })

  describe('Format des montants', () => {
    it('formate les montants en euros', () => {
      renderBudgetsPage()
      // Tous les montants doivent avoir le symbole € et être formatés
      const montants = screen.getAllByText(/\d+\s*\d*\s*€/)
      expect(montants.length).toBeGreaterThan(0)
    })

    it('utilise le format français (espaces pour milliers)', () => {
      renderBudgetsPage()
      // 850000 devrait être affiché comme "850 000 €"
      expect(screen.getByText(/850\s*000\s*€/)).toBeInTheDocument()
    })
  })

  describe('Icônes', () => {
    it('affiche l\'icône Euro pour le budget prévisionnel', () => {
      renderBudgetsPage()
      const euroIcons = document.querySelectorAll('.lucide-euro')
      expect(euroIcons.length).toBeGreaterThan(0)
    })

    it('affiche l\'icône Building2 pour chaque chantier', () => {
      renderBudgetsPage()
      const buildingIcons = document.querySelectorAll('.lucide-building-2')
      expect(buildingIcons.length).toBeGreaterThan(0)
    })

    it('affiche l\'icône Calendar pour les dates', () => {
      renderBudgetsPage()
      const calendarIcons = document.querySelectorAll('.lucide-calendar')
      expect(calendarIcons.length).toBeGreaterThan(0)
    })
  })

  describe('Responsive', () => {
    it('utilise grid-cols-1 sur mobile et grid-cols-3 sur desktop pour les stats', () => {
      renderBudgetsPage()
      const statsGrid = screen.getByText('Budget Prévisionnel').closest('.grid')
      expect(statsGrid?.className).toContain('grid-cols-1')
      expect(statsGrid?.className).toContain('md:grid-cols-3')
    })
  })
})
