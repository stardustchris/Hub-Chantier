/**
 * Tests unitaires pour FeuillesHeuresPage
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import FeuillesHeuresPage from './FeuillesHeuresPage'

// Mock useFeuillesHeures hook
const mockUseFeuillesHeures = {
  viewTab: 'compagnons' as const,
  setViewTab: vi.fn(),
  showFilters: false,
  setShowFilters: vi.fn(),
  filterUtilisateurs: [] as number[],
  filterChantiers: [] as number[],
  handleFilterUtilisateur: vi.fn(),
  handleFilterChantier: vi.fn(),
  clearFilterUtilisateurs: vi.fn(),
  clearFilterChantiers: vi.fn(),
  showWeekend: false,
  setShowWeekend: vi.fn(),
  utilisateurs: [
    { id: '1', nom: 'Dupont', prenom: 'Jean' },
    { id: '2', nom: 'Martin', prenom: 'Pierre' },
  ],
  chantiers: [
    { id: '1', nom: 'Chantier A', couleur: '#3498DB' },
    { id: '2', nom: 'Chantier B', couleur: '#E74C3C' },
  ],
  currentDate: new Date('2026-01-25'),
  setCurrentDate: vi.fn(),
  handleExport: vi.fn(),
  isExporting: false,
  error: '',
  loading: false,
  vueCompagnons: [],
  vueChantiers: [],
  handleCellClick: vi.fn(),
  handleChantierCellClick: vi.fn(),
  handlePointageClick: vi.fn(),
  canEdit: true,
  modalOpen: false,
  closeModal: vi.fn(),
  handleSavePointage: vi.fn(),
  handleDeletePointage: vi.fn(),
  handleSignPointage: vi.fn(),
  handleSubmitPointage: vi.fn(),
  handleValidatePointage: vi.fn(),
  handleRejectPointage: vi.fn(),
  editingPointage: null,
  selectedDate: null,
  selectedUserId: null,
  selectedChantierId: null,
  isValidateur: false,
}

vi.mock('../hooks/useFeuillesHeures', () => ({
  useFeuillesHeures: () => mockUseFeuillesHeures,
}))

// Mock useAuth
vi.mock('../contexts/AuthContext', () => ({
  useAuth: () => ({
    user: { role: 'admin' },
  }),
}))

// Mock Layout
vi.mock('../components/Layout', () => ({
  default: ({ children }: { children: React.ReactNode }) => <div data-testid="layout">{children}</div>,
}))

// Mock pointages components
vi.mock('../components/pointages', () => ({
  TimesheetWeekNavigation: ({ currentDate }: { currentDate: Date }) => (
    <div data-testid="week-navigation">{currentDate.toISOString().split('T')[0]}</div>
  ),
  TimesheetGrid: ({ vueCompagnons }: { vueCompagnons: unknown[] }) => (
    <div data-testid="timesheet-grid">{vueCompagnons.length} compagnons</div>
  ),
  TimesheetChantierGrid: ({ vueChantiers }: { vueChantiers: unknown[] }) => (
    <div data-testid="timesheet-chantier-grid">{vueChantiers.length} chantiers</div>
  ),
  PointageModal: ({ isOpen }: { isOpen: boolean }) => (
    isOpen ? <div data-testid="pointage-modal">Pointage Modal</div> : null
  ),
  PayrollMacrosConfig: ({ isOpen }: { isOpen: boolean }) => (
    isOpen ? <div data-testid="macros-modal">Macros Modal</div> : null
  ),
}))

const renderPage = () => {
  return render(
    <MemoryRouter>
      <FeuillesHeuresPage />
    </MemoryRouter>
  )
}

describe('FeuillesHeuresPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    Object.assign(mockUseFeuillesHeures, {
      viewTab: 'compagnons',
      showFilters: false,
      filterUtilisateurs: [],
      filterChantiers: [],
      loading: false,
      error: '',
      modalOpen: false,
    })
  })

  describe('rendering', () => {
    it('affiche le titre', () => {
      renderPage()
      expect(screen.getByRole('heading', { name: "Feuilles d'heures" })).toBeInTheDocument()
    })

    it('affiche la description', () => {
      renderPage()
      expect(screen.getByText('Saisie et validation des heures travaillees')).toBeInTheDocument()
    })

    it('affiche les onglets compagnons et chantiers', () => {
      renderPage()
      expect(screen.getByText('Compagnons')).toBeInTheDocument()
      expect(screen.getByText('Chantiers')).toBeInTheDocument()
    })

    it('affiche le bouton filtres', () => {
      renderPage()
      expect(screen.getByText('Filtres')).toBeInTheDocument()
    })

    it('affiche la checkbox weekend', () => {
      renderPage()
      expect(screen.getByText('Weekend')).toBeInTheDocument()
    })
  })

  describe('admin features', () => {
    it('affiche bouton macros de paie pour admin', () => {
      renderPage()
      expect(screen.getByLabelText('Configurer les macros de paie')).toBeInTheDocument()
    })

    it('ouvre le modal macros au clic', async () => {
      const user = userEvent.setup()
      renderPage()
      await user.click(screen.getByLabelText('Configurer les macros de paie'))
      expect(screen.getByTestId('macros-modal')).toBeInTheDocument()
    })
  })

  describe('view tabs', () => {
    it('affiche la grille compagnons par defaut', () => {
      renderPage()
      expect(screen.getByTestId('timesheet-grid')).toBeInTheDocument()
    })

    it('change d onglet au clic sur chantiers', async () => {
      const user = userEvent.setup()
      renderPage()
      await user.click(screen.getByText('Chantiers'))
      expect(mockUseFeuillesHeures.setViewTab).toHaveBeenCalledWith('chantiers')
    })

    it('affiche la grille chantiers si onglet chantiers', () => {
      mockUseFeuillesHeures.viewTab = 'chantiers'
      renderPage()
      expect(screen.getByTestId('timesheet-chantier-grid')).toBeInTheDocument()
    })
  })

  describe('filters', () => {
    it('ouvre les filtres au clic', async () => {
      const user = userEvent.setup()
      renderPage()
      await user.click(screen.getByText('Filtres'))
      expect(mockUseFeuillesHeures.setShowFilters).toHaveBeenCalledWith(true)
    })

    it('affiche les filtres utilisateurs si showFilters', () => {
      mockUseFeuillesHeures.showFilters = true
      renderPage()
      expect(screen.getByText('Utilisateurs :')).toBeInTheDocument()
      expect(screen.getByText('Jean Dupont')).toBeInTheDocument()
    })

    it('affiche les filtres chantiers si showFilters', () => {
      mockUseFeuillesHeures.showFilters = true
      renderPage()
      expect(screen.getByText('Chantiers :')).toBeInTheDocument()
      expect(screen.getByText('Chantier A')).toBeInTheDocument()
    })

    it('affiche le badge de filtres actifs', () => {
      mockUseFeuillesHeures.filterUtilisateurs = [1, 2]
      renderPage()
      expect(screen.getByText('2')).toBeInTheDocument()
    })

    it('appelle handleFilterUtilisateur au clic sur utilisateur', async () => {
      const user = userEvent.setup()
      mockUseFeuillesHeures.showFilters = true
      renderPage()
      await user.click(screen.getByText('Jean Dupont'))
      expect(mockUseFeuillesHeures.handleFilterUtilisateur).toHaveBeenCalledWith(1)
    })
  })

  describe('weekend toggle', () => {
    it('toggle weekend au changement', async () => {
      const user = userEvent.setup()
      renderPage()
      const checkbox = screen.getByRole('checkbox')
      await user.click(checkbox)
      expect(mockUseFeuillesHeures.setShowWeekend).toHaveBeenCalled()
    })
  })

  describe('loading state', () => {
    it('affiche le loader pendant le chargement', () => {
      mockUseFeuillesHeures.loading = true
      const { container } = renderPage()
      expect(container.querySelector('.animate-spin')).toBeTruthy()
      expect(screen.getByText("Chargement des feuilles d'heures...")).toBeInTheDocument()
    })
  })

  describe('error state', () => {
    it('affiche l erreur si presente', () => {
      mockUseFeuillesHeures.error = 'Erreur de chargement'
      renderPage()
      expect(screen.getByText('Erreur de chargement')).toBeInTheDocument()
    })
  })

  describe('modal', () => {
    it('affiche le modal pointage si modalOpen', () => {
      mockUseFeuillesHeures.modalOpen = true
      renderPage()
      expect(screen.getByTestId('pointage-modal')).toBeInTheDocument()
    })
  })
})
