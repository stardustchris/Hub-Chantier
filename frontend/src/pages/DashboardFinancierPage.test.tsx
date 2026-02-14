/**
 * Tests pour DashboardFinancierPage - Module 17 Phase 1
 * CDC FIN-11
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import DashboardFinancierPage from './DashboardFinancierPage'
import type { VueConsolidee } from '../types'

// Mock data
const mockConsolidation: VueConsolidee = {
  kpi_globaux: {
    total_budget_revise: 3450000,
    total_engage: 3190000,
    total_realise: 2970000,
    total_reste_a_depenser: 260000,
    marge_moyenne_pct: 12.5,
    nb_chantiers: 3,
    nb_chantiers_ok: 2,
    nb_chantiers_attention: 0,
    nb_chantiers_depassement: 1,
  },
  chantiers: [
    {
      chantier_id: 1,
      nom_chantier: 'Villa Moderne Duplex',
      montant_revise_ht: 850000,
      total_engage: 720000,
      total_realise: 650000,
      reste_a_depenser: 130000,
      pct_engage: 84.7,
      pct_realise: 76.5,
      marge_estimee_pct: 15.3,
      marge_statut: 'calculee',
      statut: 'ok',
    },
    {
      chantier_id: 2,
      nom_chantier: 'Résidence Les Jardins',
      montant_revise_ht: 2100000,
      total_engage: 1950000,
      total_realise: 1800000,
      reste_a_depenser: 150000,
      pct_engage: 92.9,
      pct_realise: 85.7,
      marge_estimee_pct: 10.2,
      marge_statut: 'calculee',
      statut: 'ok',
    },
    {
      chantier_id: 3,
      nom_chantier: 'École Jean Jaurès',
      montant_revise_ht: 500000,
      total_engage: 520000,
      total_realise: 520000,
      reste_a_depenser: -20000,
      pct_engage: 104.0,
      pct_realise: 104.0,
      marge_estimee_pct: -4.0,
      marge_statut: 'calculee',
      statut: 'depassement',
    },
  ],
  top_rentables: [
    {
      chantier_id: 1,
      nom_chantier: 'Villa Moderne Duplex',
      montant_revise_ht: 850000,
      total_engage: 720000,
      total_realise: 650000,
      reste_a_depenser: 130000,
      pct_engage: 84.7,
      pct_realise: 76.5,
      marge_estimee_pct: 15.3,
      marge_statut: 'calculee',
      statut: 'ok',
    },
  ],
  top_derives: [
    {
      chantier_id: 3,
      nom_chantier: 'École Jean Jaurès',
      montant_revise_ht: 500000,
      total_engage: 520000,
      total_realise: 520000,
      reste_a_depenser: -20000,
      pct_engage: 104.0,
      pct_realise: 104.0,
      marge_estimee_pct: -4.0,
      marge_statut: 'calculee',
      statut: 'depassement',
    },
  ],
}

const mockChantiers = {
  items: [
    { id: 1, nom: 'Villa Moderne Duplex' },
    { id: 2, nom: 'Résidence Les Jardins' },
    { id: 3, nom: 'École Jean Jaurès' },
  ],
  total: 3,
  page: 1,
  size: 100,
}

// Mock services
vi.mock('../services/chantiers', () => ({
  chantiersService: {
    list: vi.fn(() => Promise.resolve(mockChantiers)),
  },
}))

vi.mock('../services/financier', () => ({
  financierService: {
    getConsolidation: vi.fn(() => Promise.resolve(mockConsolidation)),
    getAnalyseIAConsolidee: vi.fn(() => Promise.resolve({
      synthese: 'Situation globale stable',
      alertes: ['École Jean Jaurès en dépassement'],
      recommandations: ['Réviser le budget de l\'école'],
      source: 'regles' as const,
      ai_available: false,
    })),
  },
}))

vi.mock('../services/logger', () => ({
  logger: {
    error: vi.fn(),
    warn: vi.fn(),
    info: vi.fn(),
  },
}))

// Mock Layout component
vi.mock('../components/Layout', () => ({
  default: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="layout">{children}</div>
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
    it('affiche le titre "Dashboard Financier"', async () => {
      renderDashboardFinancierPage()
      expect(screen.getByText('Dashboard Financier')).toBeInTheDocument()
      await waitFor(() => {
        expect(screen.queryByLabelText('Chargement des donnees financieres')).not.toBeInTheDocument()
      })
    })
  })

  describe('KPIs principaux', () => {
    it('affiche le budget total', async () => {
      renderDashboardFinancierPage()
      await waitFor(() => {
        expect(screen.getByText('Budget Total')).toBeInTheDocument()
      })
      expect(screen.getByText(/3\s*450\s*000/)).toBeInTheDocument()
    })

    it('affiche le montant engagé total', async () => {
      renderDashboardFinancierPage()
      await waitFor(() => {
        expect(screen.getByText('Engagé Total')).toBeInTheDocument()
      })
      expect(screen.getByText(/3\s*190\s*000/)).toBeInTheDocument()
    })

    it('affiche le montant déboursé total', async () => {
      renderDashboardFinancierPage()
      await waitFor(() => {
        expect(screen.getByText('Déboursé Total')).toBeInTheDocument()
      })
      expect(screen.getByText(/2\s*970\s*000/)).toBeInTheDocument()
    })

    it('affiche le reste à dépenser', async () => {
      renderDashboardFinancierPage()
      await waitFor(() => {
        expect(screen.getByText('Reste à Dépenser')).toBeInTheDocument()
      })
      expect(screen.getByText(/260\s*000/)).toBeInTheDocument()
    })

    it('affiche la marge moyenne', async () => {
      renderDashboardFinancierPage()
      await waitFor(() => {
        expect(screen.getByText('Marge Moyenne')).toBeInTheDocument()
      })
      // Format français : "12,5 %"
      expect(screen.getByText(/12,5\s*%/)).toBeInTheDocument()
    })
  })

  describe('Compteurs statut', () => {
    it('affiche le nombre de chantiers OK', async () => {
      renderDashboardFinancierPage()
      await waitFor(() => {
        expect(screen.getByText('Chantiers OK')).toBeInTheDocument()
      })
      expect(screen.getByText('2')).toBeInTheDocument()
    })

    it('affiche le nombre de chantiers en dépassement', async () => {
      renderDashboardFinancierPage()
      await waitFor(() => {
        expect(screen.getByText('Chantiers en depassement')).toBeInTheDocument()
      })
      expect(screen.getByText('1')).toBeInTheDocument()
    })
  })

  describe('Détail par chantier', () => {
    it('affiche le titre "Tous les chantiers"', async () => {
      renderDashboardFinancierPage()
      await waitFor(() => {
        expect(screen.getByText('Tous les chantiers')).toBeInTheDocument()
      })
    })

    it('affiche tous les chantiers', async () => {
      renderDashboardFinancierPage()
      await waitFor(() => {
        // Les noms de chantiers sont affichés dans le tableau + les cartes top
        const rows = screen.getAllByText('Villa Moderne Duplex')
        expect(rows.length).toBeGreaterThanOrEqual(1)
      })
    })

    it('affiche les budgets pour chaque chantier', async () => {
      renderDashboardFinancierPage()
      await waitFor(() => {
        // Format EUR français : "850 000" ou "850 000 €"
        // Plusieurs occurrences possibles (tableau + cartes)
        const budgets = screen.getAllByText(/850\s*000/)
        expect(budgets.length).toBeGreaterThanOrEqual(1)
      })
    })

    it('affiche le statut de chaque chantier', async () => {
      renderDashboardFinancierPage()
      await waitFor(() => {
        // "OK" apparaît plusieurs fois : tableau + cartes top rentables/dérivés
        const okElements = screen.getAllByText('OK')
        expect(okElements.length).toBeGreaterThanOrEqual(2)
      })
      // "Depassement" apparaît aussi plusieurs fois
      const depassementElements = screen.getAllByText('Depassement')
      expect(depassementElements.length).toBeGreaterThanOrEqual(1)
    })

    it('affiche le taux de réalisation de chaque chantier', async () => {
      renderDashboardFinancierPage()
      await waitFor(() => {
        // Format français : "76,5 %"
        // Plusieurs occurrences possibles (tableau, cartes)
        const elements = screen.getAllByText(/76,5\s*%/)
        expect(elements.length).toBeGreaterThanOrEqual(1)
      })
      expect(screen.getAllByText(/85,7\s*%/).length).toBeGreaterThanOrEqual(1)
      expect(screen.getAllByText(/104,0\s*%/).length).toBeGreaterThanOrEqual(1)
    })
  })

  describe('Graphiques', () => {
    it('affiche le graphique de répartition par statut', async () => {
      renderDashboardFinancierPage()
      await waitFor(() => {
        expect(screen.getByText('Repartition par statut')).toBeInTheDocument()
      })
    })

    it('affiche le graphique budget/engagé/déboursé', async () => {
      renderDashboardFinancierPage()
      await waitFor(() => {
        expect(screen.getByText('Budget / Engagé / Déboursé par chantier')).toBeInTheDocument()
      })
    })

    it('affiche le graphique des marges', async () => {
      renderDashboardFinancierPage()
      await waitFor(() => {
        expect(screen.getByText('Marges estimees par chantier')).toBeInTheDocument()
      })
    })
  })

  describe('Top chantiers', () => {
    it('affiche le top rentables', async () => {
      renderDashboardFinancierPage()
      await waitFor(() => {
        expect(screen.getByText('Top 3 Rentables')).toBeInTheDocument()
      })
    })

    it('affiche le top dérivés', async () => {
      renderDashboardFinancierPage()
      await waitFor(() => {
        expect(screen.getByText('Top 3 Derives')).toBeInTheDocument()
      })
    })
  })

  describe('Icônes des KPIs', () => {
    it('affiche l\'icône Euro pour le budget total', async () => {
      renderDashboardFinancierPage()
      await waitFor(() => {
        const euroIcons = document.querySelectorAll('.lucide-euro')
        expect(euroIcons.length).toBeGreaterThan(0)
      })
    })

    it('affiche l\'icône Building2 pour chaque chantier', async () => {
      renderDashboardFinancierPage()
      await waitFor(() => {
        const buildingIcons = document.querySelectorAll('.lucide-building-2')
        expect(buildingIcons.length).toBeGreaterThan(0)
      })
    })
  })

  describe('Format des montants', () => {
    it('formate les montants en euros', async () => {
      renderDashboardFinancierPage()
      await waitFor(() => {
        expect(screen.getByText(/3\s*450\s*000/)).toBeInTheDocument()
      })
    })
  })

  describe('Responsive', () => {
    it('utilise grid responsive pour les KPIs', async () => {
      renderDashboardFinancierPage()
      await waitFor(() => {
        const kpisGrid = screen.getByText('Budget Total').closest('.grid')
        expect(kpisGrid?.className).toContain('grid-cols-1')
      })
    })
  })
})
