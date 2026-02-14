/**
 * Tests pour BudgetTab - Onglet principal Budget avec sections Phase 3
 *
 * Couvre :
 * - Section A : Top 5 Lots les plus consommes
 * - Section B : Dernieres Operations (achats + situations)
 * - Section C : Actions rapides
 * - Comportement callback onDashboardLoaded
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import BudgetTab from './BudgetTab'
import { financierService } from '../../services/financier'
import type { Budget, DashboardFinancier, KPIFinancier, RepartitionLot, Achat, SituationTravaux } from '../../types'

// Mock all services
vi.mock('../../services/financier', () => ({
  financierService: {
    getBudgetByChantier: vi.fn(),
    getDashboardFinancier: vi.fn(),
    listAlertes: vi.fn(),
    listSituations: vi.fn(),
    createBudget: vi.fn(),
  },
}))

vi.mock('../../services/logger', () => ({
  logger: {
    error: vi.fn(),
    warn: vi.fn(),
    info: vi.fn(),
  },
}))

// Mock AuthContext
const mockUser = { role: 'admin', id: 1, email: 'admin@test.com', nom: 'Admin', prenom: 'Test' }
vi.mock('../../contexts/AuthContext', () => ({
  useAuth: () => ({ user: mockUser }),
}))

// Mock ToastContext
const mockAddToast = vi.fn()
vi.mock('../../contexts/ToastContext', () => ({
  useToast: () => ({ addToast: mockAddToast }),
}))

// Mock child components to isolate BudgetTab logic
vi.mock('./BudgetDashboard', () => ({
  default: ({ onDashboardLoaded, chantierId }: { onDashboardLoaded?: (d: DashboardFinancier) => void; chantierId: number }) => {
    // Simulate the callback being called when component mounts
    const { useEffect } = require('react')
    useEffect(() => {
      // Retrieve dashboard from the service mock to simulate real behavior
      financierService.getDashboardFinancier(chantierId).then((data: DashboardFinancier) => {
        onDashboardLoaded?.(data)
      }).catch(() => {})
    }, [chantierId, onDashboardLoaded])
    return <div data-testid="budget-dashboard">BudgetDashboard</div>
  },
}))

vi.mock('./SuggestionsPanel', () => ({
  default: () => <div data-testid="suggestions-panel">SuggestionsPanel</div>,
}))

vi.mock('./LotsBudgetairesTable', () => ({
  default: () => <div data-testid="lots-table">LotsBudgetairesTable</div>,
}))

vi.mock('./AchatsList', () => ({
  default: () => <div data-testid="achats-list">AchatsList</div>,
}))

vi.mock('./JournalFinancier', () => ({
  default: () => <div data-testid="journal-financier">JournalFinancier</div>,
}))

vi.mock('./AvenantsList', () => ({
  default: () => <div data-testid="avenants-list">AvenantsList</div>,
}))

vi.mock('./SituationsList', () => ({
  default: () => <div data-testid="situations-list">SituationsList</div>,
}))

vi.mock('./FacturesList', () => ({
  default: () => <div data-testid="factures-list">FacturesList</div>,
}))

vi.mock('./CoutsMainOeuvrePanel', () => ({
  default: () => <div data-testid="couts-mo">CoutsMainOeuvrePanel</div>,
}))

vi.mock('./CoutsMaterielPanel', () => ({
  default: () => <div data-testid="couts-mat">CoutsMaterielPanel</div>,
}))

vi.mock('./AlertesPanel', () => ({
  default: () => <div data-testid="alertes-panel">AlertesPanel</div>,
}))

vi.mock('./ChartTooltip', () => ({
  formatEUR: (v: number) =>
    new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(v),
}))

const createMockBudget = (overrides: Partial<Budget> = {}): Budget => ({
  id: 1,
  chantier_id: 100,
  montant_initial_ht: 500000,
  montant_avenants_ht: 50000,
  montant_revise_ht: 550000,
  retenue_garantie_pct: 5,
  seuil_alerte_pct: 80,
  seuil_validation_achat: 5000,
  notes: null,
  created_at: '2026-01-01',
  ...overrides,
})

const createMockKPI = (overrides: Partial<KPIFinancier> = {}): KPIFinancier => ({
  montant_revise_ht: 550000,
  total_engage: 200000,
  total_realise: 100000,
  reste_a_depenser: 350000,
  marge_estimee: 63.64,
  pct_engage: 36.36,
  pct_realise: 18.18,
  pct_reste: 63.64,
  ...overrides,
})

const createMockRepartitionLots = (): RepartitionLot[] => [
  { lot_id: 1, code_lot: 'GO-01', libelle: 'Gros oeuvre', total_prevu_ht: 200000, engage: 150000, realise: 100000 },
  { lot_id: 2, code_lot: 'SEC-01', libelle: 'Second oeuvre', total_prevu_ht: 100000, engage: 80000, realise: 60000 },
  { lot_id: 3, code_lot: 'ELEC-01', libelle: 'Electricite', total_prevu_ht: 80000, engage: 70000, realise: 40000 },
  { lot_id: 4, code_lot: 'PLOMB-01', libelle: 'Plomberie', total_prevu_ht: 50000, engage: 20000, realise: 10000 },
  { lot_id: 5, code_lot: 'PEIN-01', libelle: 'Peinture', total_prevu_ht: 30000, engage: 15000, realise: 5000 },
  { lot_id: 6, code_lot: 'TERR-01', libelle: 'Terrassement', total_prevu_ht: 40000, engage: 10000, realise: 5000 },
]

const createMockAchats = (): Achat[] => [
  {
    id: 1, chantier_id: 100, fournisseur_id: 1, lot_budgetaire_id: 1,
    type_achat: 'materiel' as const, libelle: 'Ciment Portland', quantite: 100,
    unite: 'kg' as const, prix_unitaire_ht: 15, taux_tva: 20,
    total_ht: 1500, montant_tva: 300, total_ttc: 1800,
    date_commande: '2026-01-10', date_livraison_prevue: '2026-01-15',
    statut: 'valide' as const, numero_facture: null, motif_refus: null,
    commentaire: null, demandeur_id: 1, valideur_id: null, validated_at: null,
    fournisseur_nom: 'Lafarge', statut_label: 'Valide', statut_couleur: '#10B981',
    created_at: '2026-01-10', updated_at: '2026-01-10',
  },
  {
    id: 2, chantier_id: 100, fournisseur_id: 2, lot_budgetaire_id: 2,
    type_achat: 'materiel' as const, libelle: 'Sable fin', quantite: 50,
    unite: 'kg' as const, prix_unitaire_ht: 8, taux_tva: 20,
    total_ht: 400, montant_tva: 80, total_ttc: 480,
    date_commande: '2026-01-12', date_livraison_prevue: null,
    statut: 'demande' as const, numero_facture: null, motif_refus: null,
    commentaire: null, demandeur_id: 1, valideur_id: null, validated_at: null,
    statut_label: 'Demande', statut_couleur: '#F59E0B',
    created_at: '2026-01-12', updated_at: '2026-01-12',
  },
]

const createMockSituations = (): SituationTravaux[] => [
  {
    id: 1, chantier_id: 100, budget_id: 1, numero: '1',
    periode_debut: '2026-01-01', periode_fin: '2026-01-31',
    montant_cumule_precedent_ht: 0, montant_periode_ht: 50000, montant_cumule_ht: 50000,
    retenue_garantie_pct: 5, taux_tva: 20,
    statut: 'validee' as const, notes: null,
    montant_retenue_garantie: 2500, montant_tva: 10000,
    montant_net_ht: 47500, montant_ttc: 57000,
    created_at: '2026-01-31', updated_at: '2026-01-31',
  },
]

const createMockDashboard = (overrides: Partial<DashboardFinancier> = {}): DashboardFinancier => ({
  kpi: createMockKPI(),
  derniers_achats: createMockAchats(),
  repartition_par_lot: createMockRepartitionLots(),
  ...overrides,
})

describe('BudgetTab', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('affiche le loader pendant le chargement du budget', () => {
    vi.mocked(financierService.getBudgetByChantier).mockReturnValue(new Promise(() => {}))
    vi.mocked(financierService.listSituations).mockReturnValue(new Promise(() => {}))

    render(<BudgetTab chantierId={100} />)

    expect(screen.getByLabelText('Chargement du budget')).toBeInTheDocument()
  })

  it('affiche le formulaire de creation quand pas de budget', async () => {
    vi.mocked(financierService.getBudgetByChantier).mockResolvedValue(null as unknown as Budget)
    vi.mocked(financierService.listSituations).mockResolvedValue([])

    render(<BudgetTab chantierId={100} />)

    await waitFor(() => {
      expect(screen.getByText('Aucun budget defini')).toBeInTheDocument()
    })
    expect(screen.getByText('Creer le budget')).toBeInTheDocument()
  })

  it('affiche le dashboard quand un budget existe', async () => {
    const budget = createMockBudget()
    const dashboard = createMockDashboard()
    vi.mocked(financierService.getBudgetByChantier).mockResolvedValue(budget)
    vi.mocked(financierService.getDashboardFinancier).mockResolvedValue(dashboard)
    vi.mocked(financierService.listAlertes).mockResolvedValue([])
    vi.mocked(financierService.listSituations).mockResolvedValue([])

    render(<BudgetTab chantierId={100} />)

    await waitFor(() => {
      expect(screen.getByTestId('budget-dashboard')).toBeInTheDocument()
    })
  })

  describe('Section A: Top 5 Lots les plus consommes', () => {
    it('affiche le tableau Top 5 Lots avec les lots tries par engage decroissant', async () => {
      const budget = createMockBudget()
      const dashboard = createMockDashboard()
      vi.mocked(financierService.getBudgetByChantier).mockResolvedValue(budget)
      vi.mocked(financierService.getDashboardFinancier).mockResolvedValue(dashboard)
      vi.mocked(financierService.listAlertes).mockResolvedValue([])
      vi.mocked(financierService.listSituations).mockResolvedValue([])

      render(<BudgetTab chantierId={100} />)

      await waitFor(() => {
        expect(screen.getByText('Top 5 Lots les plus consommes')).toBeInTheDocument()
      })

      // Verifie les en-tetes du tableau
      expect(screen.getByText('Code')).toBeInTheDocument()
      expect(screen.getByText('Libelle')).toBeInTheDocument()

      // Les 5 premiers lots par engage decroissant: GO-01 (150k), SEC-01 (80k),
      // ELEC-01 (70k), PLOMB-01 (20k), PEIN-01 (15k)
      // Le 6eme (TERR-01, 10k) ne doit pas apparaitre
      expect(screen.getByText('GO-01')).toBeInTheDocument()
      expect(screen.getByText('Gros oeuvre')).toBeInTheDocument()
      expect(screen.getByText('SEC-01')).toBeInTheDocument()
      expect(screen.getByText('ELEC-01')).toBeInTheDocument()
      expect(screen.getByText('PLOMB-01')).toBeInTheDocument()
      expect(screen.getByText('PEIN-01')).toBeInTheDocument()
    })

    it('limite a 5 lots maximum', async () => {
      const budget = createMockBudget()
      const dashboard = createMockDashboard()
      vi.mocked(financierService.getBudgetByChantier).mockResolvedValue(budget)
      vi.mocked(financierService.getDashboardFinancier).mockResolvedValue(dashboard)
      vi.mocked(financierService.listAlertes).mockResolvedValue([])
      vi.mocked(financierService.listSituations).mockResolvedValue([])

      render(<BudgetTab chantierId={100} />)

      await waitFor(() => {
        expect(screen.getByText('Top 5 Lots les plus consommes')).toBeInTheDocument()
      })

      // TERR-01 est le 6eme lot, ne doit pas apparaitre dans le Top 5
      expect(screen.queryByText('TERR-01')).not.toBeInTheDocument()
    })

    it('ne s affiche pas si pas de repartition par lot', async () => {
      const budget = createMockBudget()
      const dashboard = createMockDashboard({ repartition_par_lot: [] })
      vi.mocked(financierService.getBudgetByChantier).mockResolvedValue(budget)
      vi.mocked(financierService.getDashboardFinancier).mockResolvedValue(dashboard)
      vi.mocked(financierService.listAlertes).mockResolvedValue([])
      vi.mocked(financierService.listSituations).mockResolvedValue([])

      render(<BudgetTab chantierId={100} />)

      await waitFor(() => {
        expect(screen.getByTestId('budget-dashboard')).toBeInTheDocument()
      })

      expect(screen.queryByText('Top 5 Lots les plus consommes')).not.toBeInTheDocument()
    })
  })

  describe('Section B: Dernieres Operations', () => {
    it('affiche les derniers achats depuis dashboardData', async () => {
      const budget = createMockBudget()
      const dashboard = createMockDashboard()
      vi.mocked(financierService.getBudgetByChantier).mockResolvedValue(budget)
      vi.mocked(financierService.getDashboardFinancier).mockResolvedValue(dashboard)
      vi.mocked(financierService.listAlertes).mockResolvedValue([])
      vi.mocked(financierService.listSituations).mockResolvedValue([])

      render(<BudgetTab chantierId={100} />)

      await waitFor(() => {
        expect(screen.getByText('Derniers achats')).toBeInTheDocument()
      })

      // Attendre que les données du dashboard soient chargées et affichées
      await waitFor(() => {
        expect(screen.getByText('Ciment Portland')).toBeInTheDocument()
      })
      expect(screen.getByText('Sable fin')).toBeInTheDocument()
    })

    it('affiche message vide quand pas d achats', async () => {
      const budget = createMockBudget()
      const dashboard = createMockDashboard({ derniers_achats: [] })
      vi.mocked(financierService.getBudgetByChantier).mockResolvedValue(budget)
      vi.mocked(financierService.getDashboardFinancier).mockResolvedValue(dashboard)
      vi.mocked(financierService.listAlertes).mockResolvedValue([])
      vi.mocked(financierService.listSituations).mockResolvedValue([])

      render(<BudgetTab chantierId={100} />)

      await waitFor(() => {
        expect(screen.getByText('Aucun achat pour le moment')).toBeInTheDocument()
      })
    })

    it('affiche les dernieres situations', async () => {
      const budget = createMockBudget()
      const dashboard = createMockDashboard()
      const situations = createMockSituations()
      vi.mocked(financierService.getBudgetByChantier).mockResolvedValue(budget)
      vi.mocked(financierService.getDashboardFinancier).mockResolvedValue(dashboard)
      vi.mocked(financierService.listAlertes).mockResolvedValue([])
      vi.mocked(financierService.listSituations).mockResolvedValue(situations)

      render(<BudgetTab chantierId={100} />)

      await waitFor(() => {
        expect(screen.getByText('Dernieres situations')).toBeInTheDocument()
      })
    })

    it('affiche message vide quand pas de situations', async () => {
      const budget = createMockBudget()
      const dashboard = createMockDashboard()
      vi.mocked(financierService.getBudgetByChantier).mockResolvedValue(budget)
      vi.mocked(financierService.getDashboardFinancier).mockResolvedValue(dashboard)
      vi.mocked(financierService.listAlertes).mockResolvedValue([])
      vi.mocked(financierService.listSituations).mockResolvedValue([])

      render(<BudgetTab chantierId={100} />)

      await waitFor(() => {
        expect(screen.getByText('Aucune situation pour le moment')).toBeInTheDocument()
      })
    })
  })

  describe('Section C: Actions rapides', () => {
    it('affiche les 4 boutons d actions rapides pour admin', async () => {
      const budget = createMockBudget()
      const dashboard = createMockDashboard()
      vi.mocked(financierService.getBudgetByChantier).mockResolvedValue(budget)
      vi.mocked(financierService.getDashboardFinancier).mockResolvedValue(dashboard)
      vi.mocked(financierService.listAlertes).mockResolvedValue([])
      vi.mocked(financierService.listSituations).mockResolvedValue([])

      render(<BudgetTab chantierId={100} />)

      await waitFor(() => {
        expect(screen.getByText('Actions rapides')).toBeInTheDocument()
      })

      expect(screen.getByLabelText('Ouvrir la section Lots Budgetaires')).toBeInTheDocument()
      expect(screen.getByLabelText('Ouvrir la section Achats')).toBeInTheDocument()
      expect(screen.getByLabelText('Ouvrir la section Avenants')).toBeInTheDocument()
      expect(screen.getByLabelText('Ouvrir la section Situations de Travaux')).toBeInTheDocument()
    })

    it('cliquer sur Nouveau Lot deplie la section lots', async () => {
      const budget = createMockBudget()
      const dashboard = createMockDashboard()
      vi.mocked(financierService.getBudgetByChantier).mockResolvedValue(budget)
      vi.mocked(financierService.getDashboardFinancier).mockResolvedValue(dashboard)
      vi.mocked(financierService.listAlertes).mockResolvedValue([])
      vi.mocked(financierService.listSituations).mockResolvedValue([])

      render(<BudgetTab chantierId={100} />)

      await waitFor(() => {
        expect(screen.getByText('Actions rapides')).toBeInTheDocument()
      })

      // Collapse the lots section first
      const lotsButton = screen.getByText('Lots Budgetaires')
      fireEvent.click(lotsButton)

      // Now click the action rapide button
      fireEvent.click(screen.getByLabelText('Ouvrir la section Lots Budgetaires'))

      // Section should be expanded
      await waitFor(() => {
        expect(screen.getByTestId('lots-table')).toBeInTheDocument()
      })
    })

    it('cliquer sur Nouvel Achat deplie la section achats', async () => {
      const budget = createMockBudget()
      const dashboard = createMockDashboard()
      vi.mocked(financierService.getBudgetByChantier).mockResolvedValue(budget)
      vi.mocked(financierService.getDashboardFinancier).mockResolvedValue(dashboard)
      vi.mocked(financierService.listAlertes).mockResolvedValue([])
      vi.mocked(financierService.listSituations).mockResolvedValue([])

      render(<BudgetTab chantierId={100} />)

      await waitFor(() => {
        expect(screen.getByText('Actions rapides')).toBeInTheDocument()
      })

      // Collapse achats section first
      const achatsButton = screen.getByText('Achats')
      fireEvent.click(achatsButton)

      // Click action rapide
      fireEvent.click(screen.getByLabelText('Ouvrir la section Achats'))

      await waitFor(() => {
        expect(screen.getByTestId('achats-list')).toBeInTheDocument()
      })
    })
  })

  describe('Sections collapsables', () => {
    it('affiche les 7 sections collapsables', async () => {
      const budget = createMockBudget()
      const dashboard = createMockDashboard()
      vi.mocked(financierService.getBudgetByChantier).mockResolvedValue(budget)
      vi.mocked(financierService.getDashboardFinancier).mockResolvedValue(dashboard)
      vi.mocked(financierService.listAlertes).mockResolvedValue([])
      vi.mocked(financierService.listSituations).mockResolvedValue([])

      render(<BudgetTab chantierId={100} />)

      await waitFor(() => {
        expect(screen.getByText('Lots Budgetaires')).toBeInTheDocument()
      })

      expect(screen.getByText('Achats')).toBeInTheDocument()
      expect(screen.getByText('Avenants')).toBeInTheDocument()
      expect(screen.getByText('Situations de Travaux')).toBeInTheDocument()
      expect(screen.getByText('Factures')).toBeInTheDocument()
      expect(screen.getByText('Couts')).toBeInTheDocument()
      expect(screen.getByText('Alertes')).toBeInTheDocument()
    })

    it('toggle une section collapse/expand', async () => {
      const budget = createMockBudget()
      const dashboard = createMockDashboard()
      vi.mocked(financierService.getBudgetByChantier).mockResolvedValue(budget)
      vi.mocked(financierService.getDashboardFinancier).mockResolvedValue(dashboard)
      vi.mocked(financierService.listAlertes).mockResolvedValue([])
      vi.mocked(financierService.listSituations).mockResolvedValue([])

      render(<BudgetTab chantierId={100} />)

      await waitFor(() => {
        expect(screen.getByText('Lots Budgetaires')).toBeInTheDocument()
      })

      // By default, sections are expanded
      expect(screen.getByTestId('lots-table')).toBeInTheDocument()

      // Collapse
      fireEvent.click(screen.getByText('Lots Budgetaires'))
      expect(screen.queryByTestId('lots-table')).not.toBeInTheDocument()

      // Re-expand
      fireEvent.click(screen.getByText('Lots Budgetaires'))
      expect(screen.getByTestId('lots-table')).toBeInTheDocument()
    })
  })

  describe('Journal financier toggle', () => {
    it('toggle le journal financier', async () => {
      const budget = createMockBudget()
      const dashboard = createMockDashboard()
      vi.mocked(financierService.getBudgetByChantier).mockResolvedValue(budget)
      vi.mocked(financierService.getDashboardFinancier).mockResolvedValue(dashboard)
      vi.mocked(financierService.listAlertes).mockResolvedValue([])
      vi.mocked(financierService.listSituations).mockResolvedValue([])

      render(<BudgetTab chantierId={100} />)

      await waitFor(() => {
        expect(screen.getByText("Voir l'historique des modifications")).toBeInTheDocument()
      })

      // Journal hidden by default
      expect(screen.queryByTestId('journal-financier')).not.toBeInTheDocument()

      // Show journal
      fireEvent.click(screen.getByText("Voir l'historique des modifications"))
      expect(screen.getByTestId('journal-financier')).toBeInTheDocument()
    })
  })
})
