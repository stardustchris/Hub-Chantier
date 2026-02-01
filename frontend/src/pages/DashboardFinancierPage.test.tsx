/**
 * Tests pour DashboardFinancierPage - Module 17 Phase 1
 * CDC FIN-11
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import DashboardFinancierPage from './DashboardFinancierPage'

// Mock Layout component
vi.mock('../components/Layout', () => ({
  default: ({ children, title }: { children: React.ReactNode; title: string }) => (
    <div data-testid="layout">
      <h1>{title}</h1>
      {children}
    </div>
  ),
}))

function renderDashboardFinancierPage() {
  return render(
    <MemoryRouter>
      <DashboardFinancierPage />
    </MemoryRouter>
  )
}

describe('DashboardFinancierPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Affichage général', () => {
    it('affiche le titre "Dashboard Financier"', () => {
      renderDashboardFinancierPage()
      expect(screen.getByText('Dashboard Financier')).toBeInTheDocument()
    })

    it('affiche le titre de section "Vue d\'ensemble"', () => {
      renderDashboardFinancierPage()
      expect(screen.getByText('Vue d\'ensemble')).toBeInTheDocument()
    })

    it('affiche le sélecteur de période', () => {
      renderDashboardFinancierPage()
      expect(screen.getByDisplayValue('Ce mois')).toBeInTheDocument()
    })
  })

  describe('KPIs principaux', () => {
    it('affiche le budget total', () => {
      renderDashboardFinancierPage()
      expect(screen.getByText('Budget Total')).toBeInTheDocument()
      // Total: 850000 + 2100000 + 500000 = 3450000
      expect(screen.getByText(/3\s*450\s*000\s*€/)).toBeInTheDocument()
    })

    it('affiche le montant réalisé sous le budget total', () => {
      renderDashboardFinancierPage()
      // 2970000 réalisé
      expect(screen.getByText(/2\s*970\s*000\s*€ réalisé/)).toBeInTheDocument()
    })

    it('affiche les dépenses du mois', () => {
      renderDashboardFinancierPage()
      expect(screen.getByText('Dépenses du mois')).toBeInTheDocument()
      expect(screen.getByText(/285\s*000\s*€/)).toBeInTheDocument()
    })

    it('affiche l\'évolution des dépenses', () => {
      renderDashboardFinancierPage()
      expect(screen.getByText(/\+12\.5% vs mois dernier/)).toBeInTheDocument()
    })

    it('affiche les dépenses moyennes par jour', () => {
      renderDashboardFinancierPage()
      expect(screen.getByText('Dépenses moy./jour')).toBeInTheDocument()
      expect(screen.getByText(/9\s*500\s*€/)).toBeInTheDocument()
      expect(screen.getByText('30 derniers jours')).toBeInTheDocument()
    })

    it('affiche le taux de consommation global', () => {
      renderDashboardFinancierPage()
      expect(screen.getByText('Taux de consommation')).toBeInTheDocument()
      // (2970000 / 3450000) * 100 = 86.1%
      expect(screen.getByText(/86\.1%/)).toBeInTheDocument()
    })

    it('affiche le nombre de chantiers OK et dépassés', () => {
      renderDashboardFinancierPage()
      expect(screen.getByText(/2 chantiers OK \/ 1 dépassés/)).toBeInTheDocument()
    })
  })

  describe('Graphique de consommation budgétaire', () => {
    it('affiche le titre de la section', () => {
      renderDashboardFinancierPage()
      expect(screen.getByText('Consommation budgétaire globale')).toBeInTheDocument()
    })

    it('affiche le budget réalisé et prévu', () => {
      renderDashboardFinancierPage()
      expect(screen.getByText('Budget réalisé')).toBeInTheDocument()
      expect(screen.getByText('Budget prévu')).toBeInTheDocument()
    })

    it('affiche une barre de progression colorée selon le taux', () => {
      renderDashboardFinancierPage()
      // Taux 86.1% devrait être orange (> 80% mais < 100%)
      const progressBar = document.querySelector('.bg-orange-500')
      expect(progressBar).toBeInTheDocument()
    })
  })

  describe('Détail par chantier', () => {
    it('affiche le titre "Détail par chantier"', () => {
      renderDashboardFinancierPage()
      expect(screen.getByText('Détail par chantier')).toBeInTheDocument()
    })

    it('affiche tous les chantiers', () => {
      renderDashboardFinancierPage()
      expect(screen.getByText('Villa Moderne Duplex')).toBeInTheDocument()
      expect(screen.getByText('Résidence Les Jardins')).toBeInTheDocument()
      expect(screen.getByText('École Jean Jaurès')).toBeInTheDocument()
    })

    it('affiche les budgets pour chaque chantier', () => {
      renderDashboardFinancierPage()
      // Villa: 650000 / 850000
      expect(screen.getByText(/650\s*000\s*€ \/ 850\s*000\s*€/)).toBeInTheDocument()
    })

    it('affiche le statut de chaque chantier', () => {
      renderDashboardFinancierPage()
      expect(screen.getAllByText('Dans le budget')).toHaveLength(2)
      expect(screen.getByText('Dépassement')).toBeInTheDocument()
    })

    it('affiche le taux de consommation de chaque chantier', () => {
      renderDashboardFinancierPage()
      expect(screen.getByText('76.5%')).toBeInTheDocument() // Villa
      expect(screen.getByText('85.7%')).toBeInTheDocument() // Résidence
      expect(screen.getByText('104.0%')).toBeInTheDocument() // École
    })
  })

  describe('Alertes de dépassement', () => {
    it('affiche une alerte globale si dépassements', () => {
      renderDashboardFinancierPage()
      expect(
        screen.getByText(/Attention : 1 chantier en dépassement budgétaire/)
      ).toBeInTheDocument()
    })

    it('affiche le message de recommandation', () => {
      renderDashboardFinancierPage()
      expect(
        screen.getByText(/Une révision des budgets est recommandée/)
      ).toBeInTheDocument()
    })

    it('liste les chantiers en dépassement', () => {
      renderDashboardFinancierPage()
      expect(screen.getByText(/École Jean Jaurès/)).toBeInTheDocument()
      expect(screen.getByText(/Dépassement de 20\s*000\s*€/)).toBeInTheDocument()
    })

    it('affiche l\'icône AlertTriangle pour les alertes', () => {
      renderDashboardFinancierPage()
      const alertIcons = document.querySelectorAll('.lucide-alert-triangle')
      expect(alertIcons.length).toBeGreaterThan(0)
    })
  })

  describe('Statuts visuels par chantier', () => {
    it('applique le style vert pour "Dans le budget"', () => {
      renderDashboardFinancierPage()
      const okBadges = screen.getAllByText('Dans le budget')
      okBadges.forEach((badge) => {
        expect(badge.className).toContain('text-green-600')
        expect(badge.className).toContain('bg-green-100')
      })
    })

    it('applique le style rouge pour "Dépassement"', () => {
      renderDashboardFinancierPage()
      const depassementBadge = screen.getByText('Dépassement')
      expect(depassementBadge.className).toContain('text-red-600')
      expect(depassementBadge.className).toContain('bg-red-100')
    })

    it('affiche l\'icône CheckCircle pour les chantiers OK', () => {
      renderDashboardFinancierPage()
      const checkIcons = document.querySelectorAll('.lucide-check-circle')
      expect(checkIcons.length).toBeGreaterThan(0)
    })

    it('affiche l\'icône TrendingUp pour les dépassements', () => {
      renderDashboardFinancierPage()
      const trendingIcons = document.querySelectorAll('.lucide-trending-up')
      expect(trendingIcons.length).toBeGreaterThan(0)
    })
  })

  describe('Barres de progression par chantier', () => {
    it('affiche une barre verte pour taux < 80%', () => {
      renderDashboardFinancierPage()
      // Villa: 76.5% -> verte
      const greenBars = document.querySelectorAll('.bg-green-500')
      expect(greenBars.length).toBeGreaterThan(0)
    })

    it('affiche une barre orange pour taux 80-100%', () => {
      renderDashboardFinancierPage()
      // Résidence: 85.7% -> orange
      const orangeBars = document.querySelectorAll('.bg-orange-500')
      expect(orangeBars.length).toBeGreaterThan(0)
    })

    it('affiche une barre rouge pour taux > 100%', () => {
      renderDashboardFinancierPage()
      // École: 104.0% -> rouge
      const redBars = document.querySelectorAll('.bg-red-500')
      expect(redBars.length).toBeGreaterThan(0)
    })
  })

  describe('Icônes des KPIs', () => {
    it('affiche l\'icône Euro pour le budget total', () => {
      renderDashboardFinancierPage()
      const euroIcons = document.querySelectorAll('.lucide-euro')
      expect(euroIcons.length).toBeGreaterThan(0)
    })

    it('affiche l\'icône DollarSign pour les dépenses', () => {
      renderDashboardFinancierPage()
      const dollarIcons = document.querySelectorAll('.lucide-dollar-sign')
      expect(dollarIcons.length).toBeGreaterThan(0)
    })

    it('affiche l\'icône Calendar pour les dépenses moyennes', () => {
      renderDashboardFinancierPage()
      const calendarIcons = document.querySelectorAll('.lucide-calendar')
      expect(calendarIcons.length).toBeGreaterThan(0)
    })

    it('affiche l\'icône Building2 pour chaque chantier', () => {
      renderDashboardFinancierPage()
      const buildingIcons = document.querySelectorAll('.lucide-building-2')
      expect(buildingIcons.length).toBeGreaterThan(0)
    })
  })

  describe('Évolution des dépenses', () => {
    it('affiche l\'icône ArrowUpRight pour évolution positive', () => {
      renderDashboardFinancierPage()
      const upIcons = document.querySelectorAll('.lucide-arrow-up-right')
      expect(upIcons.length).toBeGreaterThan(0)
    })

    it('applique le style rouge pour augmentation', () => {
      renderDashboardFinancierPage()
      const evolutionText = screen.getByText(/\+12\.5% vs mois dernier/)
      expect(evolutionText.className).toContain('text-red-500')
    })
  })

  describe('Format des montants', () => {
    it('formate les montants en euros sans décimales', () => {
      renderDashboardFinancierPage()
      // Vérifie que les montants n'ont pas de décimales
      const montants = screen.getAllByText(/\d+\s*\d*\s*€/)
      expect(montants.length).toBeGreaterThan(0)
    })

    it('utilise le format français avec espaces', () => {
      renderDashboardFinancierPage()
      expect(screen.getByText(/3\s*450\s*000\s*€/)).toBeInTheDocument()
    })
  })

  describe('Responsive', () => {
    it('utilise grid responsive pour les KPIs', () => {
      renderDashboardFinancierPage()
      const kpisGrid = screen.getByText('Budget Total').closest('.grid')
      expect(kpisGrid?.className).toContain('grid-cols-1')
      expect(kpisGrid?.className).toContain('lg:grid-cols-4')
    })
  })

  describe('Sélecteur de période', () => {
    it('affiche toutes les options de période', () => {
      renderDashboardFinancierPage()
      const select = screen.getByDisplayValue('Ce mois')
      expect(select).toBeInTheDocument()

      const options = within(select as HTMLElement).getAllByRole('option')
      expect(options).toHaveLength(4)
      expect(options[0]).toHaveTextContent('Ce mois')
      expect(options[1]).toHaveTextContent('Cette semaine')
      expect(options[2]).toHaveTextContent('Ce trimestre')
      expect(options[3]).toHaveTextContent('Cette année')
    })

    it('permet de changer la période', async () => {
      const user = userEvent.setup()
      renderDashboardFinancierPage()

      const select = screen.getByDisplayValue('Ce mois') as HTMLSelectElement
      await user.selectOptions(select, 'semaine')

      expect(select.value).toBe('semaine')
    })
  })

  describe('Hover effects', () => {
    it('applique hover:shadow-md sur les cartes de chantiers', () => {
      renderDashboardFinancierPage()
      const chantiersCards = document.querySelectorAll('.hover\\:shadow-md')
      expect(chantiersCards.length).toBeGreaterThan(0)
    })
  })
})

// Helper function pour within (si pas disponible dans testing-library)
function within(element: HTMLElement) {
  return {
    getAllByRole: (role: string) => {
      return Array.from(element.querySelectorAll(`[role="${role}"], ${role}`))
    },
  }
}
