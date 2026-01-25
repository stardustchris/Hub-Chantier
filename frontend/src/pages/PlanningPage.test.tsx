/**
 * Tests unitaires pour PlanningPage
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import PlanningPage from './PlanningPage'

// Mock usePlanning hook
const mockUsePlanning = {
  canEdit: true,
  viewTab: 'utilisateurs' as const,
  setViewTab: vi.fn(),
  nonPlanifiesCount: 3,
  showNonPlanifiesOnly: false,
  setShowNonPlanifiesOnly: vi.fn(),
  filterChantier: null,
  setFilterChantier: vi.fn(),
  chantiers: [{ id: 1, nom: 'Chantier A' }],
  showFilters: false,
  setShowFilters: vi.fn(),
  filterMetiers: [],
  toggleFilterMetier: vi.fn(),
  clearFilterMetiers: vi.fn(),
  showWeekend: false,
  setShowWeekend: vi.fn(),
  openCreateModal: vi.fn(),
  currentDate: new Date('2026-01-25'),
  setCurrentDate: vi.fn(),
  viewMode: 'week' as const,
  setViewMode: vi.fn(),
  error: '',
  loading: false,
  filteredAffectations: [],
  filteredUtilisateurs: [{ id: 1, nom: 'Dupont', prenom: 'Jean', metier: 'Maçon' }],
  utilisateurs: [{ id: 1, nom: 'Dupont', prenom: 'Jean', metier: 'Maçon' }],
  handleAffectationClick: vi.fn(),
  handleAffectationDelete: vi.fn(),
  handleCellClick: vi.fn(),
  handleChantierCellClick: vi.fn(),
  handleDuplicate: vi.fn(),
  handleDuplicateChantier: vi.fn(),
  expandedMetiers: new Set<string>(),
  handleToggleMetier: vi.fn(),
  handleAffectationMove: vi.fn(),
  modalOpen: false,
  closeModal: vi.fn(),
  handleSaveAffectation: vi.fn(),
  editingAffectation: null,
  selectedDate: null,
  selectedUserId: null,
  selectedChantierId: null,
}

vi.mock('../hooks/usePlanning', () => ({
  usePlanning: () => mockUsePlanning,
}))

// Mock Layout
vi.mock('../components/Layout', () => ({
  default: ({ children }: { children: React.ReactNode }) => <div data-testid="layout">{children}</div>,
}))

// Mock planning components
vi.mock('../components/planning', () => ({
  PlanningGrid: ({ utilisateurs }: { utilisateurs: unknown[] }) => (
    <div data-testid="planning-grid">{utilisateurs.length} utilisateurs</div>
  ),
  PlanningChantierGrid: ({ chantiers }: { chantiers: unknown[] }) => (
    <div data-testid="planning-chantier-grid">{chantiers.length} chantiers</div>
  ),
  WeekNavigation: ({ currentDate }: { currentDate: Date }) => (
    <div data-testid="week-navigation">{currentDate.toISOString().split('T')[0]}</div>
  ),
  AffectationModal: ({ isOpen }: { isOpen: boolean }) => (
    isOpen ? <div data-testid="affectation-modal">Modal</div> : null
  ),
}))

vi.mock('../components/planning/PlanningToolbar', () => ({
  PlanningToolbar: ({ viewTab, canEdit }: { viewTab: string; canEdit: boolean }) => (
    <div data-testid="planning-toolbar" data-view={viewTab} data-can-edit={canEdit}>
      Toolbar
    </div>
  ),
  PlanningFiltersPanel: ({ show }: { show: boolean }) => (
    show ? <div data-testid="filters-panel">Filters</div> : null
  ),
}))

const renderPage = () => {
  return render(
    <MemoryRouter>
      <PlanningPage />
    </MemoryRouter>
  )
}

describe('PlanningPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    Object.assign(mockUsePlanning, {
      loading: false,
      error: '',
      viewTab: 'utilisateurs',
      showFilters: false,
      modalOpen: false,
    })
  })

  describe('rendering', () => {
    it('affiche dans le layout', () => {
      renderPage()
      expect(screen.getByTestId('layout')).toBeInTheDocument()
    })

    it('affiche la toolbar', () => {
      renderPage()
      expect(screen.getByTestId('planning-toolbar')).toBeInTheDocument()
    })

    it('affiche la navigation semaine', () => {
      renderPage()
      expect(screen.getByTestId('week-navigation')).toBeInTheDocument()
    })

    it('passe canEdit a la toolbar', () => {
      mockUsePlanning.canEdit = true
      renderPage()
      expect(screen.getByTestId('planning-toolbar')).toHaveAttribute('data-can-edit', 'true')
    })
  })

  describe('loading state', () => {
    it('affiche le loader pendant le chargement', () => {
      mockUsePlanning.loading = true
      const { container } = renderPage()
      expect(container.querySelector('.animate-spin')).toBeTruthy()
      expect(screen.getByText('Chargement du planning...')).toBeInTheDocument()
    })

    it('n affiche pas le loader apres chargement', () => {
      mockUsePlanning.loading = false
      renderPage()
      expect(screen.queryByText('Chargement du planning...')).not.toBeInTheDocument()
    })
  })

  describe('error state', () => {
    it('affiche l erreur si presente', () => {
      mockUsePlanning.error = 'Erreur de chargement'
      renderPage()
      expect(screen.getByText('Erreur de chargement')).toBeInTheDocument()
    })

    it('n affiche pas d erreur si vide', () => {
      mockUsePlanning.error = ''
      renderPage()
      expect(screen.queryByText('Erreur de chargement')).not.toBeInTheDocument()
    })
  })

  describe('view tabs', () => {
    it('affiche la grille utilisateurs par defaut', () => {
      mockUsePlanning.viewTab = 'utilisateurs'
      renderPage()
      expect(screen.getByTestId('planning-grid')).toBeInTheDocument()
    })

    it('affiche la grille chantiers si onglet chantiers', () => {
      mockUsePlanning.viewTab = 'chantiers'
      renderPage()
      expect(screen.getByTestId('planning-chantier-grid')).toBeInTheDocument()
    })
  })

  describe('filters panel', () => {
    it('affiche le panneau de filtres si showFilters', () => {
      mockUsePlanning.showFilters = true
      renderPage()
      expect(screen.getByTestId('filters-panel')).toBeInTheDocument()
    })

    it('cache le panneau de filtres si pas showFilters', () => {
      mockUsePlanning.showFilters = false
      renderPage()
      expect(screen.queryByTestId('filters-panel')).not.toBeInTheDocument()
    })
  })

  describe('modal', () => {
    it('affiche le modal si modalOpen', () => {
      mockUsePlanning.modalOpen = true
      renderPage()
      expect(screen.getByTestId('affectation-modal')).toBeInTheDocument()
    })

    it('cache le modal si pas modalOpen', () => {
      mockUsePlanning.modalOpen = false
      renderPage()
      expect(screen.queryByTestId('affectation-modal')).not.toBeInTheDocument()
    })
  })

  describe('date display', () => {
    it('affiche la date courante dans la navigation', () => {
      mockUsePlanning.currentDate = new Date('2026-01-25')
      renderPage()
      expect(screen.getByTestId('week-navigation')).toHaveTextContent('2026-01-25')
    })
  })
})
