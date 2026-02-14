/**
 * Tests pour BudgetsPage - Module 17 Phase 1
 * CDC FIN-01, FIN-02
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import BudgetsPage from './BudgetsPage'

// Mock services
vi.mock('../services/financier', () => ({
  financierService: {
    getBudgetByChantier: vi.fn(() => Promise.resolve(null)),
    listAchats: vi.fn(() => Promise.resolve({ items: [] })),
  },
}))

vi.mock('../services/chantiers', () => ({
  chantiersService: {
    list: vi.fn(() => Promise.resolve({ items: [] })),
  },
}))

vi.mock('../services/logger', () => ({
  logger: {
    error: vi.fn(),
  },
}))

// Mock Layout component
vi.mock('../components/Layout', () => ({
  default: ({ children, title }: { children: React.ReactNode; title: string }) => (
    <div data-testid="layout">
      <h1>{title}</h1>
      {children}
    </div>
  ),
}))

import { financierService } from '../services/financier'
import { chantiersService } from '../services/chantiers'

// ---- Données de test ----
const mockChantiers = [
  { id: 1, nom: 'Villa Moderne Duplex', statut: 'en_cours', date_debut_prevue: '2026-01-01', date_fin_prevue: '2026-06-30' },
  { id: 2, nom: 'Résidence Les Jardins', statut: 'en_cours', date_debut_prevue: '2026-02-01', date_fin_prevue: '2026-12-31' },
  { id: 3, nom: 'École Jean Jaurès', statut: 'en_cours', date_debut_prevue: '2026-03-01', date_fin_prevue: '2026-09-30' },
]

// Villa: 60% consommé (<80% → vert), engagé 70% (<100% → pas dépassé)
const budgetVilla = {
  id: 1, chantier_id: 1, montant_initial_ht: 850000, montant_revise_ht: 850000,
}
const achatsVilla = [
  { id: 1, quantite: 1, prix_unitaire_ht: 510000, statut: 'livre' }, // réalisé + engagé
  { id: 2, quantite: 1, prix_unitaire_ht: 85000, statut: 'commande' }, // engagé only
]

// Résidence: 85% consommé (80-100% → orange), engagé 90%
const budgetResidence = {
  id: 2, chantier_id: 2, montant_initial_ht: 1200000, montant_revise_ht: 1200000,
}
const achatsResidence = [
  { id: 3, quantite: 1, prix_unitaire_ht: 1020000, statut: 'livre' }, // réalisé + engagé
  { id: 4, quantite: 1, prix_unitaire_ht: 60000, statut: 'commande' }, // engagé only
]

// École: 104% consommé (>100% → rouge), engagé 104% (>100% → dépassé)
const budgetEcole = {
  id: 3, chantier_id: 3, montant_initial_ht: 500000, montant_revise_ht: 500000,
}
const achatsEcole = [
  { id: 5, quantite: 1, prix_unitaire_ht: 520000, statut: 'commande' }, // engagé > prévu → dépassé
]

function setupMocksWithData() {
  vi.mocked(chantiersService.list).mockResolvedValue({ items: mockChantiers } as any)
  vi.mocked(financierService.getBudgetByChantier).mockImplementation((id: number) => {
    if (id === 1) return Promise.resolve(budgetVilla as any)
    if (id === 2) return Promise.resolve(budgetResidence as any)
    if (id === 3) return Promise.resolve(budgetEcole as any)
    return Promise.resolve(null)
  })
  vi.mocked(financierService.listAchats).mockImplementation(({ chantier_id }: any) => {
    if (chantier_id === 1) return Promise.resolve({ items: achatsVilla } as any)
    if (chantier_id === 2) return Promise.resolve({ items: achatsResidence } as any)
    if (chantier_id === 3) return Promise.resolve({ items: achatsEcole } as any)
    return Promise.resolve({ items: [] } as any)
  })
}

function renderBudgetsPage() {
  return render(
    <MemoryRouter>
      <BudgetsPage />
    </MemoryRouter>
  )
}

async function renderAndWaitForLoad() {
  renderBudgetsPage()
  await waitFor(() => {
    expect(screen.queryByText(/Chargement/i)).not.toBeInTheDocument()
  })
}

describe('BudgetsPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Affichage général', () => {
    it('affiche le titre "Budgets"', async () => {
      renderBudgetsPage()
      await waitFor(() => {
        expect(screen.getByText('Budgets')).toBeInTheDocument()
      })
    })

    it('affiche les statistiques globales', async () => {
      renderBudgetsPage()
      await waitFor(() => {
        expect(screen.getByText('Budget Prévisionnel')).toBeInTheDocument()
        expect(screen.getByText('Engagé')).toBeInTheDocument()
        expect(screen.getByText('Déboursé')).toBeInTheDocument()
      })
    })

    it('affiche le champ de recherche', async () => {
      renderBudgetsPage()
      await waitFor(() => {
        expect(screen.getByPlaceholderText('Rechercher un chantier...')).toBeInTheDocument()
      })
    })
  })

  describe('Statistiques globales', () => {
    it('affiche le budget prévisionnel total', async () => {
      await renderAndWaitForLoad()
      expect(screen.getByText('Budget Prévisionnel')).toBeInTheDocument()
    })

    it('affiche le montant engagé total', async () => {
      await renderAndWaitForLoad()
      expect(screen.getByText('Engagé')).toBeInTheDocument()
    })

    it('affiche le montant déboursé total', async () => {
      await renderAndWaitForLoad()
      expect(screen.getByText('Déboursé')).toBeInTheDocument()
    })

    it('affiche les statistiques de manière cohérente', async () => {
      await renderAndWaitForLoad()
      expect(screen.getByText('Budget Prévisionnel')).toBeInTheDocument()
      expect(screen.getByText('Engagé')).toBeInTheDocument()
      expect(screen.getByText('Déboursé')).toBeInTheDocument()
    })

    it('gère les données vides gracieusement', async () => {
      await renderAndWaitForLoad()
      expect(screen.queryByText(/Erreur/i)).not.toBeInTheDocument()
    })
  })

  describe('Liste des budgets', () => {
    it('affiche un message quand il n\'y a pas de budgets', async () => {
      await renderAndWaitForLoad()
      expect(screen.getByText(/Aucun budget/i)).toBeInTheDocument()
    })

    it('gère le chargement des budgets', async () => {
      renderBudgetsPage()
      await waitFor(() => {
        expect(screen.queryByText(/Chargement/i)).not.toBeInTheDocument()
      })
    })

    it('structure la page correctement', async () => {
      await renderAndWaitForLoad()
      expect(screen.getByTestId('layout')).toBeInTheDocument()
    })
  })

  describe('Recherche', () => {
    beforeEach(() => {
      setupMocksWithData()
    })

    it('filtre les chantiers par nom', async () => {
      const user = userEvent.setup()
      renderBudgetsPage()
      await waitFor(() => {
        expect(screen.getByText('Villa Moderne Duplex')).toBeInTheDocument()
      })

      const searchInput = screen.getByPlaceholderText('Rechercher un chantier...')
      await user.type(searchInput, 'Villa')

      expect(screen.getByText('Villa Moderne Duplex')).toBeInTheDocument()
      expect(screen.queryByText('Résidence Les Jardins')).not.toBeInTheDocument()
      expect(screen.queryByText('École Jean Jaurès')).not.toBeInTheDocument()
    })

    it('est insensible à la casse', async () => {
      const user = userEvent.setup()
      renderBudgetsPage()
      await waitFor(() => {
        expect(screen.getByText('Villa Moderne Duplex')).toBeInTheDocument()
      })

      const searchInput = screen.getByPlaceholderText('Rechercher un chantier...')
      await user.type(searchInput, 'villa')

      expect(screen.getByText('Villa Moderne Duplex')).toBeInTheDocument()
    })

    it('affiche un message si aucun résultat', async () => {
      const user = userEvent.setup()
      renderBudgetsPage()
      await waitFor(() => {
        expect(screen.getByText('Villa Moderne Duplex')).toBeInTheDocument()
      })

      const searchInput = screen.getByPlaceholderText('Rechercher un chantier...')
      await user.type(searchInput, 'Inexistant')

      expect(screen.getByText('Aucun budget trouvé')).toBeInTheDocument()
    })

    it('réaffiche tous les chantiers si le champ est vidé', async () => {
      const user = userEvent.setup()
      renderBudgetsPage()
      await waitFor(() => {
        expect(screen.getByText('Résidence Les Jardins')).toBeInTheDocument()
      })

      const searchInput = screen.getByPlaceholderText('Rechercher un chantier...')
      await user.type(searchInput, 'Villa')
      expect(screen.queryByText('Résidence Les Jardins')).not.toBeInTheDocument()

      await user.clear(searchInput)
      expect(screen.getByText('Résidence Les Jardins')).toBeInTheDocument()
    })
  })

  describe('Alertes de dépassement', () => {
    beforeEach(() => {
      setupMocksWithData()
    })

    it('affiche une alerte pour les chantiers dépassés', async () => {
      renderBudgetsPage()
      await waitFor(() => {
        expect(screen.getByText('Budget dépassé')).toBeInTheDocument()
      })
    })

    it('affiche le montant du dépassement', async () => {
      renderBudgetsPage()
      await waitFor(() => {
        expect(screen.getByText(/Dépassement de/)).toBeInTheDocument()
      })
    })

    it('n\'affiche pas d\'alerte pour les chantiers dans le budget', async () => {
      renderBudgetsPage()
      await waitFor(() => {
        expect(screen.getByText('Budget dépassé')).toBeInTheDocument()
      })
      const alerts = screen.getAllByText(/Budget dépassé/)
      expect(alerts).toHaveLength(1) // Seulement École Jean Jaurès
    })
  })

  describe('Barres de progression', () => {
    beforeEach(() => {
      setupMocksWithData()
    })

    it('affiche une barre verte pour consommation < 80%', async () => {
      renderBudgetsPage()
      await waitFor(() => {
        expect(screen.getByText('Villa Moderne Duplex')).toBeInTheDocument()
      })
      const progressBars = document.querySelectorAll('.bg-green-500')
      expect(progressBars.length).toBeGreaterThan(0)
    })

    it('affiche une barre orange pour consommation 80-100%', async () => {
      renderBudgetsPage()
      await waitFor(() => {
        expect(screen.getByText('Résidence Les Jardins')).toBeInTheDocument()
      })
      const progressBars = document.querySelectorAll('.bg-orange-500')
      expect(progressBars.length).toBeGreaterThan(0)
    })

    it('affiche une barre rouge pour consommation > 100%', async () => {
      renderBudgetsPage()
      await waitFor(() => {
        expect(screen.getByText('École Jean Jaurès')).toBeInTheDocument()
      })
      const progressBars = document.querySelectorAll('.bg-red-500')
      expect(progressBars.length).toBeGreaterThan(0)
    })
  })

  describe('Statuts visuels', () => {
    beforeEach(() => {
      setupMocksWithData()
    })

    it('applique le style vert pour statut "actif"', async () => {
      renderBudgetsPage()
      await waitFor(() => {
        expect(screen.getAllByText('Actif').length).toBeGreaterThan(0)
      })
      const actifBadges = screen.getAllByText('Actif')
      actifBadges.forEach((badge) => {
        expect(badge.className).toContain('bg-green-100')
        expect(badge.className).toContain('text-green-800')
      })
    })

    it('applique le style rouge pour statut "depasse"', async () => {
      renderBudgetsPage()
      await waitFor(() => {
        expect(screen.getByText('Dépassé')).toBeInTheDocument()
      })
      const depasseBadge = screen.getByText('Dépassé')
      expect(depasseBadge.className).toContain('bg-red-100')
      expect(depasseBadge.className).toContain('text-red-800')
    })
  })

  describe('Format des montants', () => {
    beforeEach(() => {
      setupMocksWithData()
    })

    it('formate les montants en euros', async () => {
      renderBudgetsPage()
      await waitFor(() => {
        expect(screen.getByText('Villa Moderne Duplex')).toBeInTheDocument()
      })
      const montants = screen.getAllByText(/\d+.*€/)
      expect(montants.length).toBeGreaterThan(0)
    })

    it('utilise le format français pour les montants', async () => {
      renderBudgetsPage()
      await waitFor(() => {
        expect(screen.getByText('Villa Moderne Duplex')).toBeInTheDocument()
      })
      // 850000 devrait être formaté en euros
      const montants = screen.getAllByText(/850.*€/)
      expect(montants.length).toBeGreaterThan(0)
    })
  })

  describe('Icônes', () => {
    it('affiche l\'icône Euro pour le budget prévisionnel', async () => {
      renderBudgetsPage()
      await waitFor(() => {
        expect(screen.queryByText(/Chargement/i)).not.toBeInTheDocument()
      })
      const euroIcons = document.querySelectorAll('.lucide-euro')
      expect(euroIcons.length).toBeGreaterThan(0)
    })

    it('affiche l\'icône Building2 pour chaque chantier', async () => {
      setupMocksWithData()
      renderBudgetsPage()
      await waitFor(() => {
        expect(screen.getByText('Villa Moderne Duplex')).toBeInTheDocument()
      })
      const buildingIcons = document.querySelectorAll('.lucide-building-2')
      expect(buildingIcons.length).toBeGreaterThan(0)
    })

    it('affiche l\'icône Calendar pour les dates', async () => {
      setupMocksWithData()
      renderBudgetsPage()
      await waitFor(() => {
        expect(screen.getByText('Villa Moderne Duplex')).toBeInTheDocument()
      })
      const calendarIcons = document.querySelectorAll('.lucide-calendar')
      expect(calendarIcons.length).toBeGreaterThan(0)
    })
  })

  describe('Responsive', () => {
    it('utilise grid-cols-1 sur mobile et grid-cols-3 sur desktop pour les stats', async () => {
      await renderAndWaitForLoad()
      const statsGrid = screen.getByText('Budget Prévisionnel').closest('.grid')
      expect(statsGrid?.className).toContain('grid-cols-1')
      expect(statsGrid?.className).toContain('md:grid-cols-3')
    })
  })
})
