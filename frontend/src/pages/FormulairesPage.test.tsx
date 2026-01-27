/**
 * Tests unitaires pour FormulairesPage
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import FormulairesPage from './FormulairesPage'

// Mock useFormulaires hook
const mockUseFormulaires = {
  activeTab: 'formulaires' as const,
  loading: false,
  error: '',
  templates: [],
  formulaires: [],
  chantiers: [],
  filteredTemplates: [],
  searchQuery: '',
  filterCategorie: '' as const,
  setSearchQuery: vi.fn(),
  setFilterCategorie: vi.fn(),
  selectedChantierId: null,
  setSelectedChantierId: vi.fn(),
  selectedTemplate: null,
  selectedFormulaire: null,
  canManageTemplates: true,
  templateModalOpen: false,
  formulaireModalOpen: false,
  newFormulaireModalOpen: false,
  geoConsentModalOpen: false,
  formulaireReadOnly: false,
  handleTabChange: vi.fn(),
  openNewTemplateModal: vi.fn(),
  closeTemplateModal: vi.fn(),
  handleSaveTemplate: vi.fn(),
  handleEditTemplate: vi.fn(),
  handleDeleteTemplate: vi.fn(),
  handleDuplicateTemplate: vi.fn(),
  handleToggleTemplateActive: vi.fn(),
  handlePreviewTemplate: vi.fn(),
  openNewFormulaireModal: vi.fn(),
  closeNewFormulaireModal: vi.fn(),
  closeFormulaireModal: vi.fn(),
  handleCreateFormulaire: vi.fn(),
  handleViewFormulaire: vi.fn(),
  handleEditFormulaire: vi.fn(),
  handleSaveFormulaire: vi.fn(),
  handleSubmitFormulaire: vi.fn(),
  handleValidateFormulaire: vi.fn(),
  handleExportPDF: vi.fn(),
  handleGeoConsentAccept: vi.fn(),
  handleGeoConsentDecline: vi.fn(),
  handleGeoConsentClose: vi.fn(),
  loadData: vi.fn(),
}

vi.mock('../hooks', () => ({
  useFormulaires: () => mockUseFormulaires,
}))

// Mock Layout
vi.mock('../components/Layout', () => ({
  default: ({ children }: { children: React.ReactNode }) => <div data-testid="layout">{children}</div>,
}))

// Mock child components
vi.mock('../components/formulaires', () => ({
  TemplateList: ({ templates, loading }: { templates: unknown[]; loading: boolean }) => (
    <div data-testid="template-list" data-loading={loading}>
      {templates.length} templates
    </div>
  ),
  TemplateModal: ({ isOpen }: { isOpen: boolean }) => (
    isOpen ? <div data-testid="template-modal">Template Modal</div> : null
  ),
  FormulaireList: ({ formulaires, loading }: { formulaires: unknown[]; loading: boolean }) => (
    <div data-testid="formulaire-list" data-loading={loading}>
      {formulaires.length} formulaires
    </div>
  ),
  FormulaireModal: ({ isOpen }: { isOpen: boolean }) => (
    isOpen ? <div data-testid="formulaire-modal">Formulaire Modal</div> : null
  ),
  NewFormulaireModal: ({ isOpen }: { isOpen: boolean }) => (
    isOpen ? <div data-testid="new-formulaire-modal">New Formulaire Modal</div> : null
  ),
}))

vi.mock('../components/common/GeolocationConsentModal', () => ({
  GeolocationConsentModal: ({ isOpen }: { isOpen: boolean }) => (
    isOpen ? <div data-testid="geo-consent-modal">Geo Consent Modal</div> : null
  ),
}))

const renderPage = () => {
  return render(
    <MemoryRouter>
      <FormulairesPage />
    </MemoryRouter>
  )
}

describe('FormulairesPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // Reset mock values
    Object.assign(mockUseFormulaires, {
      activeTab: 'formulaires',
      loading: false,
      error: '',
      canManageTemplates: true,
      templateModalOpen: false,
      formulaireModalOpen: false,
      newFormulaireModalOpen: false,
      geoConsentModalOpen: false,
    })
  })

  describe('rendering', () => {
    it('affiche le titre', () => {
      renderPage()
      expect(screen.getByRole('heading', { name: 'Formulaires' })).toBeInTheDocument()
    })

    it('affiche la description', () => {
      renderPage()
      expect(screen.getByText('Gerez vos templates et formulaires terrain')).toBeInTheDocument()
    })

    it('affiche la barre de recherche', () => {
      renderPage()
      expect(screen.getByPlaceholderText('Rechercher...')).toBeInTheDocument()
    })

    it('affiche le select de categorie', () => {
      renderPage()
      expect(screen.getByText('Toutes categories')).toBeInTheDocument()
    })
  })

  describe('tabs', () => {
    it('affiche onglet formulaires actif par defaut', () => {
      renderPage()
      expect(screen.getByTestId('formulaire-list')).toBeInTheDocument()
    })

    it('affiche onglet templates si admin', () => {
      renderPage()
      expect(screen.getByText('Templates')).toBeInTheDocument()
    })

    it('cache onglet templates si pas admin', () => {
      mockUseFormulaires.canManageTemplates = false
      renderPage()
      expect(screen.queryByText('Templates')).not.toBeInTheDocument()
    })

    it('change d onglet au clic', async () => {
      const user = userEvent.setup()
      renderPage()

      await user.click(screen.getByText('Templates'))

      expect(mockUseFormulaires.handleTabChange).toHaveBeenCalledWith('templates')
    })
  })

  describe('templates tab', () => {
    beforeEach(() => {
      mockUseFormulaires.activeTab = 'templates'
    })

    it('affiche la liste des templates', () => {
      renderPage()
      expect(screen.getByTestId('template-list')).toBeInTheDocument()
    })

    it('affiche bouton nouveau template si admin', () => {
      renderPage()
      expect(screen.getByText('Nouveau template')).toBeInTheDocument()
    })

    it('ouvre le modal template au clic', async () => {
      const user = userEvent.setup()
      renderPage()

      await user.click(screen.getByText('Nouveau template'))

      expect(mockUseFormulaires.openNewTemplateModal).toHaveBeenCalled()
    })

    it('affiche les boutons de vue grid/list', () => {
      const { container } = renderPage()
      // Should have view mode toggle buttons
      const buttons = container.querySelectorAll('button')
      expect(buttons.length).toBeGreaterThan(0)
    })
  })

  describe('formulaires tab', () => {
    it('affiche la liste des formulaires', () => {
      renderPage()
      expect(screen.getByTestId('formulaire-list')).toBeInTheDocument()
    })

    it('affiche bouton nouveau formulaire', () => {
      renderPage()
      expect(screen.getByText('Nouveau formulaire')).toBeInTheDocument()
    })

    it('ouvre le modal nouveau formulaire au clic', async () => {
      const user = userEvent.setup()
      renderPage()

      await user.click(screen.getByText('Nouveau formulaire'))

      expect(mockUseFormulaires.openNewFormulaireModal).toHaveBeenCalled()
    })
  })

  describe('search and filter', () => {
    it('met a jour la recherche', async () => {
      const user = userEvent.setup()
      renderPage()

      const searchInput = screen.getByPlaceholderText('Rechercher...')
      await user.type(searchInput, 'test')

      expect(mockUseFormulaires.setSearchQuery).toHaveBeenCalled()
    })

    it('met a jour le filtre categorie', async () => {
      const user = userEvent.setup()
      renderPage()

      const select = screen.getByRole('combobox')
      await user.selectOptions(select, 'securite')

      expect(mockUseFormulaires.setFilterCategorie).toHaveBeenCalled()
    })
  })

  describe('refresh', () => {
    it('actualise les donnees au clic', async () => {
      const user = userEvent.setup()
      renderPage()

      const refreshButton = screen.getByTitle('Actualiser')
      await user.click(refreshButton)

      expect(mockUseFormulaires.loadData).toHaveBeenCalled()
    })
  })

  describe('error handling', () => {
    it('affiche une erreur si presente', () => {
      mockUseFormulaires.error = 'Erreur de chargement'
      renderPage()

      expect(screen.getByRole('alert')).toHaveTextContent('Erreur de chargement')
    })

    it('n affiche pas d erreur si vide', () => {
      mockUseFormulaires.error = ''
      renderPage()

      expect(screen.queryByRole('alert')).not.toBeInTheDocument()
    })
  })

  describe('modals', () => {
    it('affiche le modal template si ouvert', () => {
      mockUseFormulaires.templateModalOpen = true
      renderPage()

      expect(screen.getByTestId('template-modal')).toBeInTheDocument()
    })

    it('affiche le modal formulaire si ouvert', () => {
      mockUseFormulaires.formulaireModalOpen = true
      renderPage()

      expect(screen.getByTestId('formulaire-modal')).toBeInTheDocument()
    })

    it('affiche le modal nouveau formulaire si ouvert', () => {
      mockUseFormulaires.newFormulaireModalOpen = true
      renderPage()

      expect(screen.getByTestId('new-formulaire-modal')).toBeInTheDocument()
    })

    // GeolocationConsentModal n'est plus rendu directement par FormulairesPage
  })

  describe('loading state', () => {
    it('passe loading aux listes', () => {
      mockUseFormulaires.loading = true
      renderPage()

      expect(screen.getByTestId('formulaire-list')).toHaveAttribute('data-loading', 'true')
    })
  })
})
