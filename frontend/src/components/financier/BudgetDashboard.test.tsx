/**
 * Tests pour BudgetDashboard - KPI cards et callback onDashboardLoaded
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import BudgetDashboard from './BudgetDashboard'
import { financierService } from '../../services/financier'
import type { Budget, DashboardFinancier, KPIFinancier, RepartitionLot } from '../../types'

// Mock services
vi.mock('../../services/financier', () => ({
  financierService: {
    getDashboardFinancier: vi.fn(),
    listAlertes: vi.fn(),
  },
}))

vi.mock('../../services/logger', () => ({
  logger: {
    error: vi.fn(),
    warn: vi.fn(),
    info: vi.fn(),
  },
}))

// Mock sub-components that make their own API calls
vi.mock('./CircularGauge', () => ({
  default: ({ value }: { value: number }) => (
    <div data-testid="circular-gauge">{value}%</div>
  ),
}))

vi.mock('./EvolutionChart', () => ({
  default: () => <div data-testid="evolution-chart">EvolutionChart</div>,
}))

vi.mock('./CamembertLots', () => ({
  default: () => <div data-testid="camembert-lots">CamembertLots</div>,
}))

vi.mock('./BarresComparativesLots', () => ({
  default: () => <div data-testid="barres-comparatives">BarresComparativesLots</div>,
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

const createMockDashboard = (
  overrides: Partial<DashboardFinancier> = {},
): DashboardFinancier => ({
  kpi: createMockKPI(),
  derniers_achats: [],
  repartition_par_lot: [],
  ...overrides,
})

describe('BudgetDashboard', () => {
  const mockBudget = createMockBudget()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('affiche le loader pendant le chargement', () => {
    // Never resolve the promise to keep loading state
    vi.mocked(financierService.getDashboardFinancier).mockReturnValue(
      new Promise(() => {}),
    )
    vi.mocked(financierService.listAlertes).mockReturnValue(
      new Promise(() => {}),
    )

    render(
      <BudgetDashboard chantierId={100} budget={mockBudget} />,
    )

    expect(screen.getByText((_, el) => el?.classList.contains('animate-spin') ?? false)).toBeInTheDocument()
  })

  it('affiche les KPI apres chargement', async () => {
    const dashboard = createMockDashboard()
    vi.mocked(financierService.getDashboardFinancier).mockResolvedValue(dashboard)
    vi.mocked(financierService.listAlertes).mockResolvedValue([])

    render(
      <BudgetDashboard chantierId={100} budget={mockBudget} />,
    )

    await waitFor(() => {
      expect(screen.getByText('Budget revise HT')).toBeInTheDocument()
    })
    expect(screen.getByText('Engagé')).toBeInTheDocument()
    expect(screen.getByText('Réalisé')).toBeInTheDocument()
    expect(screen.getByText('Reste a depenser')).toBeInTheDocument()
    expect(screen.getByText('Marge estimee')).toBeInTheDocument()
  })

  it('appelle onDashboardLoaded avec les donnees du dashboard', async () => {
    const dashboard = createMockDashboard()
    const onDashboardLoaded = vi.fn()
    vi.mocked(financierService.getDashboardFinancier).mockResolvedValue(dashboard)
    vi.mocked(financierService.listAlertes).mockResolvedValue([])

    render(
      <BudgetDashboard
        chantierId={100}
        budget={mockBudget}
        onDashboardLoaded={onDashboardLoaded}
      />,
    )

    await waitFor(() => {
      expect(onDashboardLoaded).toHaveBeenCalledWith(dashboard)
    })
    expect(onDashboardLoaded).toHaveBeenCalledTimes(1)
  })

  it('ne plante pas sans onDashboardLoaded', async () => {
    const dashboard = createMockDashboard()
    vi.mocked(financierService.getDashboardFinancier).mockResolvedValue(dashboard)
    vi.mocked(financierService.listAlertes).mockResolvedValue([])

    render(
      <BudgetDashboard chantierId={100} budget={mockBudget} />,
    )

    await waitFor(() => {
      expect(screen.getByText('Budget revise HT')).toBeInTheDocument()
    })
  })

  it('affiche un message d erreur en cas d echec API', async () => {
    vi.mocked(financierService.getDashboardFinancier).mockRejectedValue(
      new Error('Network error'),
    )
    vi.mocked(financierService.listAlertes).mockResolvedValue([])

    render(
      <BudgetDashboard chantierId={100} budget={mockBudget} />,
    )

    await waitFor(() => {
      expect(
        screen.getByText('Erreur lors du chargement du dashboard financier'),
      ).toBeInTheDocument()
    })
  })

  it('affiche la banniere d alertes quand il y en a', async () => {
    const dashboard = createMockDashboard()
    const alertes = [
      {
        id: 1,
        chantier_id: 100,
        budget_id: 1,
        type_alerte: 'depassement_seuil' as const,
        message: 'Budget depasse le seuil de 80%',
        pourcentage_atteint: 85,
        seuil_configure: 80,
        montant_budget_ht: 550000,
        montant_atteint_ht: 467500,
        est_acquittee: false,
        acquittee_par: null,
        acquittee_at: null,
        created_at: '2026-01-15',
      },
    ]

    vi.mocked(financierService.getDashboardFinancier).mockResolvedValue(dashboard)
    vi.mocked(financierService.listAlertes).mockResolvedValue(alertes)

    render(
      <BudgetDashboard chantierId={100} budget={mockBudget} />,
    )

    await waitFor(() => {
      expect(screen.getByText('1 alerte budgetaire')).toBeInTheDocument()
    })
    expect(screen.getByText('- Budget depasse le seuil de 80%')).toBeInTheDocument()
  })

  it('affiche la marge estimee en pourcentage', async () => {
    const dashboard = createMockDashboard({
      kpi: createMockKPI({ marge_estimee: 25.5 }),
    })
    vi.mocked(financierService.getDashboardFinancier).mockResolvedValue(dashboard)
    vi.mocked(financierService.listAlertes).mockResolvedValue([])

    render(
      <BudgetDashboard chantierId={100} budget={mockBudget} />,
    )

    await waitFor(() => {
      expect(screen.getByText('Marge estimee')).toBeInTheDocument()
    })
    // marge_estimee = 25.5 -> formatPct(25.5) => "25,5 %"
    expect(screen.getByText('Marge correcte')).toBeInTheDocument()
  })

  it('alerte quand la marge est inferieure a 5%', async () => {
    const dashboard = createMockDashboard({
      kpi: createMockKPI({ marge_estimee: 3 }),
    })
    vi.mocked(financierService.getDashboardFinancier).mockResolvedValue(dashboard)
    vi.mocked(financierService.listAlertes).mockResolvedValue([])

    render(
      <BudgetDashboard chantierId={100} budget={mockBudget} />,
    )

    await waitFor(() => {
      expect(screen.getByText('Marge inferieure a 5%')).toBeInTheDocument()
    })
  })

  it('affiche la repartition par lot avec barres de progression', async () => {
    const lots: RepartitionLot[] = [
      { lot_id: 1, code_lot: 'GO-01', libelle: 'Gros oeuvre', total_prevu_ht: 200000, engage: 100000, realise: 50000 },
      { lot_id: 2, code_lot: 'SEC-01', libelle: 'Second oeuvre', total_prevu_ht: 100000, engage: 80000, realise: 60000 },
    ]
    const dashboard = createMockDashboard({ repartition_par_lot: lots })
    vi.mocked(financierService.getDashboardFinancier).mockResolvedValue(dashboard)
    vi.mocked(financierService.listAlertes).mockResolvedValue([])

    render(
      <BudgetDashboard chantierId={100} budget={mockBudget} />,
    )

    await waitFor(() => {
      expect(screen.getByText('GO-01')).toBeInTheDocument()
    })
    expect(screen.getByText('SEC-01')).toBeInTheDocument()
    expect(screen.getByText('Gros oeuvre')).toBeInTheDocument()
    expect(screen.getByText('Second oeuvre')).toBeInTheDocument()
  })

  it('affiche les graphiques Phase 2', async () => {
    const dashboard = createMockDashboard()
    vi.mocked(financierService.getDashboardFinancier).mockResolvedValue(dashboard)
    vi.mocked(financierService.listAlertes).mockResolvedValue([])

    render(
      <BudgetDashboard chantierId={100} budget={mockBudget} />,
    )

    await waitFor(() => {
      expect(screen.getByText('Evolution financiere')).toBeInTheDocument()
    })
    expect(screen.getByTestId('evolution-chart')).toBeInTheDocument()
    expect(screen.getByTestId('camembert-lots')).toBeInTheDocument()
  })
})
