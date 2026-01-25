/**
 * Tests unitaires pour DocumentsPage
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import DocumentsPage from './DocumentsPage'

// Mock useDocuments hook
const mockUseDocuments = {
  chantiers: [
    { id: '1', code: 'CH001', nom: 'Chantier A' },
    { id: '2', code: 'CH002', nom: 'Chantier B' },
  ],
  selectedChantier: null as { id: string; code: string; nom: string } | null,
  selectChantier: vi.fn(),
  isLoadingChantiers: false,
  isLoadingArborescence: false,
  isLoadingDocuments: false,
  isUploading: false,
  arborescence: null as { dossiers: unknown[]; total_documents: number; total_taille: number } | null,
  refreshArborescence: vi.fn(),
  selectedDossier: null,
  handleSelectDossier: vi.fn(),
  handleCreateDossier: vi.fn(),
  handleEditDossier: vi.fn(),
  handleDeleteDossier: vi.fn(),
  handleInitArborescence: vi.fn(),
  canManage: true,
  user: { role: 'admin' },
  documents: [],
  searchQuery: '',
  setSearchQuery: vi.fn(),
  handleSearchDocuments: vi.fn(),
  handleUploadFiles: vi.fn(),
  handleDownloadDocument: vi.fn(),
  handleDeleteDocument: vi.fn(),
  setPreviewDocument: vi.fn(),
  previewDocument: null,
  closePreviewModal: vi.fn(),
  showDossierModal: false,
  parentDossierId: null,
  editingDossier: null,
  closeDossierModal: vi.fn(),
  handleDossierSaved: vi.fn(),
}

vi.mock('../hooks/useDocuments', () => ({
  useDocuments: () => mockUseDocuments,
  documentsApi: {
    formatFileSize: (size: number) => `${size} bytes`,
  },
}))

// Mock Layout
vi.mock('../components/Layout', () => ({
  default: ({ children }: { children: React.ReactNode }) => <div data-testid="layout">{children}</div>,
}))

// Mock document components
vi.mock('../components/documents', () => ({
  DossierTree: ({ dossiers }: { dossiers: unknown[] }) => (
    <div data-testid="dossier-tree">{dossiers.length} dossiers</div>
  ),
  DocumentList: ({ documents }: { documents: unknown[] }) => (
    <div data-testid="document-list">{documents.length} documents</div>
  ),
  FileUploadZone: ({ uploading }: { uploading: boolean }) => (
    <div data-testid="upload-zone" data-uploading={uploading}>Upload</div>
  ),
  DossierModal: ({ isOpen }: { isOpen: boolean }) => (
    isOpen ? <div data-testid="dossier-modal">Dossier Modal</div> : null
  ),
  DocumentPreviewModal: ({ isOpen }: { isOpen: boolean }) => (
    isOpen ? <div data-testid="preview-modal">Preview Modal</div> : null
  ),
}))

const renderPage = () => {
  return render(
    <MemoryRouter>
      <DocumentsPage />
    </MemoryRouter>
  )
}

describe('DocumentsPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    Object.assign(mockUseDocuments, {
      selectedChantier: null,
      isLoadingChantiers: false,
      isLoadingArborescence: false,
      isLoadingDocuments: false,
      arborescence: null,
      selectedDossier: null,
      documents: [],
      searchQuery: '',
      canManage: true,
      showDossierModal: false,
      previewDocument: null,
    })
  })

  describe('rendering', () => {
    it('affiche le titre', () => {
      renderPage()
      expect(screen.getByRole('heading', { name: 'Documents' })).toBeInTheDocument()
    })

    it('affiche la description', () => {
      renderPage()
      expect(screen.getByText('Gestion electronique des documents (GED)')).toBeInTheDocument()
    })

    it('affiche le selecteur de chantier', () => {
      renderPage()
      expect(screen.getByText('Selectionner un chantier...')).toBeInTheDocument()
    })

    it('affiche les chantiers dans le select', () => {
      renderPage()
      expect(screen.getByText('CH001 - Chantier A')).toBeInTheDocument()
      expect(screen.getByText('CH002 - Chantier B')).toBeInTheDocument()
    })
  })

  describe('loading states', () => {
    it('affiche le loader pendant le chargement des chantiers', () => {
      mockUseDocuments.isLoadingChantiers = true
      const { container } = renderPage()
      expect(container.querySelector('.animate-spin')).toBeTruthy()
    })

    it('affiche le loader pendant le chargement de l arborescence', () => {
      mockUseDocuments.selectedChantier = { id: '1', code: 'CH001', nom: 'Chantier A' }
      mockUseDocuments.isLoadingArborescence = true
      const { container } = renderPage()
      expect(container.querySelector('.animate-spin')).toBeTruthy()
    })
  })

  describe('no chantier selected', () => {
    it('affiche message de selection', () => {
      renderPage()
      expect(screen.getByText('Selectionnez un chantier')).toBeInTheDocument()
      expect(screen.getByText('Choisissez un chantier pour acceder a ses documents')).toBeInTheDocument()
    })
  })

  describe('empty arborescence', () => {
    beforeEach(() => {
      mockUseDocuments.selectedChantier = { id: '1', code: 'CH001', nom: 'Chantier A' }
      mockUseDocuments.arborescence = { dossiers: [], total_documents: 0, total_taille: 0 }
    })

    it('affiche message aucun dossier', () => {
      renderPage()
      expect(screen.getByText('Aucun dossier')).toBeInTheDocument()
    })

    it('affiche bouton initialiser si canManage', () => {
      mockUseDocuments.canManage = true
      renderPage()
      expect(screen.getByText("Initialiser l'arborescence standard")).toBeInTheDocument()
    })

    it('cache bouton initialiser si pas canManage', () => {
      mockUseDocuments.canManage = false
      renderPage()
      expect(screen.queryByText("Initialiser l'arborescence standard")).not.toBeInTheDocument()
    })

    it('appelle handleInitArborescence au clic', async () => {
      const user = userEvent.setup()
      renderPage()
      await user.click(screen.getByText("Initialiser l'arborescence standard"))
      expect(mockUseDocuments.handleInitArborescence).toHaveBeenCalled()
    })
  })

  describe('with arborescence', () => {
    beforeEach(() => {
      mockUseDocuments.selectedChantier = { id: '1', code: 'CH001', nom: 'Chantier A' }
      mockUseDocuments.arborescence = {
        dossiers: [{ id: 1, nom: 'Plans' }, { id: 2, nom: 'Photos' }],
        total_documents: 10,
        total_taille: 1024,
      }
    })

    it('affiche le tree de dossiers', () => {
      renderPage()
      expect(screen.getByTestId('dossier-tree')).toBeInTheDocument()
    })

    it('affiche les stats', () => {
      renderPage()
      expect(screen.getByText('Total documents:')).toBeInTheDocument()
      expect(screen.getByText('10')).toBeInTheDocument()
    })

    it('affiche la barre de recherche', () => {
      renderPage()
      expect(screen.getByPlaceholderText('Rechercher un document...')).toBeInTheDocument()
    })
  })

  describe('search', () => {
    beforeEach(() => {
      mockUseDocuments.selectedChantier = { id: '1', code: 'CH001', nom: 'Chantier A' }
      mockUseDocuments.arborescence = {
        dossiers: [{ id: 1, nom: 'Plans' }],
        total_documents: 5,
        total_taille: 512,
      }
    })

    it('met a jour la recherche', async () => {
      const user = userEvent.setup()
      renderPage()
      const input = screen.getByPlaceholderText('Rechercher un document...')
      await user.type(input, 'test')
      expect(mockUseDocuments.setSearchQuery).toHaveBeenCalled()
    })

    it('desactive le bouton rechercher si vide', () => {
      mockUseDocuments.searchQuery = ''
      renderPage()
      expect(screen.getByRole('button', { name: 'Rechercher' })).toBeDisabled()
    })

    it('active le bouton rechercher si texte', () => {
      mockUseDocuments.searchQuery = 'test'
      renderPage()
      expect(screen.getByRole('button', { name: 'Rechercher' })).not.toBeDisabled()
    })
  })

  describe('upload zone', () => {
    beforeEach(() => {
      mockUseDocuments.selectedChantier = { id: '1', code: 'CH001', nom: 'Chantier A' }
      mockUseDocuments.arborescence = {
        dossiers: [{ id: 1, nom: 'Plans' }],
        total_documents: 5,
        total_taille: 512,
      }
      mockUseDocuments.selectedDossier = { id: 1, nom: 'Plans' }
    })

    it('affiche la zone d upload si dossier selectionne et canManage', () => {
      mockUseDocuments.canManage = true
      renderPage()
      expect(screen.getByTestId('upload-zone')).toBeInTheDocument()
    })

    it('cache la zone d upload si pas canManage', () => {
      mockUseDocuments.canManage = false
      renderPage()
      expect(screen.queryByTestId('upload-zone')).not.toBeInTheDocument()
    })
  })

  describe('modals', () => {
    it('affiche le modal dossier si showDossierModal', () => {
      mockUseDocuments.selectedChantier = { id: '1', code: 'CH001', nom: 'Chantier A' }
      mockUseDocuments.showDossierModal = true
      renderPage()
      expect(screen.getByTestId('dossier-modal')).toBeInTheDocument()
    })

    it('affiche le modal preview si previewDocument', () => {
      mockUseDocuments.previewDocument = { id: 1, nom: 'doc.pdf' }
      renderPage()
      expect(screen.getByTestId('preview-modal')).toBeInTheDocument()
    })
  })

  describe('chantier selection', () => {
    it('appelle selectChantier au changement', async () => {
      const user = userEvent.setup()
      renderPage()
      const select = screen.getByRole('combobox')
      await user.selectOptions(select, '1')
      expect(mockUseDocuments.selectChantier).toHaveBeenCalled()
    })

    it('affiche bouton rafraichir si chantier selectionne', () => {
      mockUseDocuments.selectedChantier = { id: '1', code: 'CH001', nom: 'Chantier A' }
      renderPage()
      expect(screen.getByTitle('Rafraichir')).toBeInTheDocument()
    })

    it('appelle refreshArborescence au clic', async () => {
      const user = userEvent.setup()
      mockUseDocuments.selectedChantier = { id: '1', code: 'CH001', nom: 'Chantier A' }
      renderPage()
      await user.click(screen.getByTitle('Rafraichir'))
      expect(mockUseDocuments.refreshArborescence).toHaveBeenCalled()
    })
  })
})
