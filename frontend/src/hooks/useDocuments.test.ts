/**
 * Tests pour le hook useDocuments
 * Gestion de la GED (Gestion Electronique des Documents)
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { useDocuments } from './useDocuments'

// Mock des modules
vi.mock('react-router-dom', () => ({
  useSearchParams: () => {
    const params = new URLSearchParams()
    return [params, vi.fn()]
  },
}))

const mockAddToast = vi.fn()
vi.mock('../contexts/ToastContext', () => ({
  useToast: () => ({
    addToast: mockAddToast,
  }),
}))

let mockUserRole = 'admin'
vi.mock('../contexts/AuthContext', () => ({
  useAuth: () => ({
    user: { id: '1', role: mockUserRole },
  }),
}))

vi.mock('../services/logger', () => ({
  logger: {
    error: vi.fn(),
    warn: vi.fn(),
    info: vi.fn(),
  },
}))

vi.mock('../services/chantiers', () => ({
  chantiersService: {
    list: vi.fn(),
  },
}))

vi.mock('../services/documents', () => ({
  getArborescence: vi.fn(),
  initArborescence: vi.fn(),
  listDocuments: vi.fn(),
  createDossier: vi.fn(),
  updateDossier: vi.fn(),
  deleteDossier: vi.fn(),
  uploadMultipleDocuments: vi.fn(),
  downloadDocument: vi.fn(),
  deleteDocument: vi.fn(),
  searchDocuments: vi.fn(),
}))

import { chantiersService } from '../services/chantiers'
import * as documentsApi from '../services/documents'

const mockChantiers: any[] = [
  { id: '1', nom: 'Chantier A', statut: 'en_cours' },
  { id: '2', nom: 'Chantier B', statut: 'en_cours' },
]

const mockDossierTree: any = {
  id: 1,
  chantier_id: 1,
  nom: 'Plans',
  type_dossier: '01_plans',
  niveau_acces: 'compagnon',
  parent_id: null,
  ordre: 1,
  chemin_complet: '/Plans',
  nombre_documents: 5,
  nombre_sous_dossiers: 2,
  created_at: '2024-01-15',
  children: [],
}

const mockArborescence: any = {
  chantier_id: 1,
  dossiers: [mockDossierTree],
  total_documents: 5,
  total_taille: 1024000,
}

const mockDocuments: any[] = [
  {
    id: 1,
    chantier_id: 1,
    dossier_id: 1,
    nom: 'plan-rdc.pdf',
    nom_original: 'Plan RDC.pdf',
    type_document: 'pdf',
    taille: 102400,
    taille_formatee: '100 Ko',
    mime_type: 'application/pdf',
    uploaded_by: 1,
    uploaded_by_nom: 'Jean Dupont',
    uploaded_at: '2024-01-15',
    description: null,
    version: 1,
    icone: 'file-pdf',
    extension: 'pdf',
    niveau_acces: null,
  },
]

describe('useDocuments', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockUserRole = 'admin'

    vi.mocked(chantiersService.list).mockResolvedValue({
      items: mockChantiers,
      total: 2,
      page: 1,
      size: 100,
      pages: 1,
    })
    vi.mocked(documentsApi.getArborescence).mockResolvedValue(mockArborescence)
    vi.mocked(documentsApi.listDocuments).mockResolvedValue({
      items: mockDocuments,
      total: 1,
      skip: 0,
      limit: 50,
    })

    vi.spyOn(window, 'confirm').mockReturnValue(true)
  })

  describe('etat initial', () => {
    it('initialise avec les valeurs par defaut', () => {
      const { result } = renderHook(() => useDocuments())

      expect(result.current.chantiers).toEqual([])
      expect(result.current.selectedChantier).toBeNull()
      expect(result.current.arborescence).toBeNull()
      expect(result.current.selectedDossier).toBeNull()
      expect(result.current.documents).toEqual([])
      expect(result.current.searchQuery).toBe('')
      expect(result.current.isLoadingChantiers).toBe(true)
      expect(result.current.showDossierModal).toBe(false)
    })

    it('canManage est true pour admin', () => {
      mockUserRole = 'admin'
      const { result } = renderHook(() => useDocuments())
      expect(result.current.canManage).toBe(true)
    })

    it('canManage est true pour conducteur', () => {
      mockUserRole = 'conducteur'
      const { result } = renderHook(() => useDocuments())
      expect(result.current.canManage).toBe(true)
    })

    it('canManage est false pour compagnon', () => {
      mockUserRole = 'compagnon'
      const { result } = renderHook(() => useDocuments())
      expect(result.current.canManage).toBe(false)
    })
  })

  describe('chargement des chantiers', () => {
    it('charge les chantiers au montage', async () => {
      const { result } = renderHook(() => useDocuments())

      await waitFor(() => {
        expect(result.current.isLoadingChantiers).toBe(false)
      })

      expect(chantiersService.list).toHaveBeenCalledWith({ size: 100 })
      expect(result.current.chantiers).toEqual(mockChantiers)
    })

    it('gere les erreurs de chargement', async () => {
      vi.mocked(chantiersService.list).mockRejectedValue(new Error('Network error'))

      const { result } = renderHook(() => useDocuments())

      await waitFor(() => {
        expect(result.current.isLoadingChantiers).toBe(false)
      })

      expect(mockAddToast).toHaveBeenCalledWith({
        message: 'Erreur lors du chargement des chantiers',
        type: 'error',
      })
    })
  })

  describe('selection de chantier', () => {
    it('selectChantier charge l\'arborescence', async () => {
      const { result } = renderHook(() => useDocuments())

      await waitFor(() => {
        expect(result.current.isLoadingChantiers).toBe(false)
      })

      act(() => {
        result.current.selectChantier(mockChantiers[0])
      })

      await waitFor(() => {
        expect(result.current.isLoadingArborescence).toBe(false)
      })

      expect(documentsApi.getArborescence).toHaveBeenCalledWith(1)
      expect(result.current.arborescence).toEqual(mockArborescence)
    })

    it('gere 404 en creant arborescence vide', async () => {
      vi.mocked(documentsApi.getArborescence).mockRejectedValue({
        response: { status: 404 },
      })

      const { result } = renderHook(() => useDocuments())

      await waitFor(() => {
        expect(result.current.isLoadingChantiers).toBe(false)
      })

      act(() => {
        result.current.selectChantier(mockChantiers[0])
      })

      await waitFor(() => {
        expect(result.current.isLoadingArborescence).toBe(false)
      })

      expect(result.current.arborescence).toEqual({
        chantier_id: 1,
        dossiers: [],
        total_documents: 0,
        total_taille: 0,
      })
    })
  })

  describe('selection de dossier', () => {
    it('handleSelectDossier charge les documents', async () => {
      const { result } = renderHook(() => useDocuments())

      await waitFor(() => {
        expect(result.current.isLoadingChantiers).toBe(false)
      })

      act(() => {
        result.current.handleSelectDossier(mockDossierTree)
      })

      await waitFor(() => {
        expect(result.current.isLoadingDocuments).toBe(false)
      })

      expect(documentsApi.listDocuments).toHaveBeenCalledWith(mockDossierTree.id)
      expect(result.current.documents).toEqual(mockDocuments)
    })
  })

  describe('gestion des dossiers', () => {
    it('handleCreateDossier ouvre la modal', async () => {
      const { result } = renderHook(() => useDocuments())

      act(() => {
        result.current.handleCreateDossier(null)
      })

      expect(result.current.showDossierModal).toBe(true)
      expect(result.current.editingDossier).toBeNull()
      expect(result.current.parentDossierId).toBeNull()
    })

    it('handleCreateDossier avec parent', async () => {
      const { result } = renderHook(() => useDocuments())

      act(() => {
        result.current.handleCreateDossier(5)
      })

      expect(result.current.showDossierModal).toBe(true)
      expect(result.current.parentDossierId).toBe(5)
    })

    it('handleEditDossier ouvre la modal en mode edition', async () => {
      const { result } = renderHook(() => useDocuments())

      act(() => {
        result.current.handleEditDossier(mockDossierTree)
      })

      expect(result.current.showDossierModal).toBe(true)
      expect(result.current.editingDossier).toEqual(mockDossierTree)
    })

    it('handleDeleteDossier supprime le dossier', async () => {
      vi.mocked(documentsApi.deleteDossier).mockResolvedValue(undefined)

      const { result } = renderHook(() => useDocuments())

      await act(async () => {
        await result.current.handleDeleteDossier(mockDossierTree)
      })

      expect(documentsApi.deleteDossier).toHaveBeenCalledWith(mockDossierTree.id)
      expect(mockAddToast).toHaveBeenCalledWith({
        message: 'Dossier supprime',
        type: 'success',
      })
    })

    it('handleDeleteDossier annulable', async () => {
      vi.spyOn(window, 'confirm').mockReturnValue(false)

      const { result } = renderHook(() => useDocuments())

      await act(async () => {
        await result.current.handleDeleteDossier(mockDossierTree)
      })

      expect(documentsApi.deleteDossier).not.toHaveBeenCalled()
    })

    it('handleDossierSaved cree un nouveau dossier', async () => {
      vi.mocked(documentsApi.createDossier).mockResolvedValue({ id: 2 } as any)

      const { result } = renderHook(() => useDocuments())

      act(() => {
        result.current.handleCreateDossier(null)
      })

      const newDossier = {
        chantier_id: 1,
        nom: 'Nouveau dossier',
        type_dossier: '01_plans',
      }

      await act(async () => {
        await result.current.handleDossierSaved(newDossier)
      })

      expect(documentsApi.createDossier).toHaveBeenCalledWith(newDossier)
      expect(mockAddToast).toHaveBeenCalledWith({
        message: 'Dossier cree',
        type: 'success',
      })
      expect(result.current.showDossierModal).toBe(false)
    })

    it('handleDossierSaved met a jour un dossier existant', async () => {
      vi.mocked(documentsApi.updateDossier).mockResolvedValue({ id: 1 } as any)

      const { result } = renderHook(() => useDocuments())

      act(() => {
        result.current.handleEditDossier(mockDossierTree)
      })

      const updateData = { nom: 'Plans modifies' }

      await act(async () => {
        await result.current.handleDossierSaved(updateData)
      })

      expect(documentsApi.updateDossier).toHaveBeenCalledWith(mockDossierTree.id, updateData)
      expect(mockAddToast).toHaveBeenCalledWith({
        message: 'Dossier modifie',
        type: 'success',
      })
    })

    it('closeDossierModal ferme la modal', async () => {
      const { result } = renderHook(() => useDocuments())

      act(() => {
        result.current.handleCreateDossier(null)
      })

      expect(result.current.showDossierModal).toBe(true)

      act(() => {
        result.current.closeDossierModal()
      })

      expect(result.current.showDossierModal).toBe(false)
    })
  })

  describe('initialisation arborescence', () => {
    it('handleInitArborescence ne fait rien sans chantier selectionne', async () => {
      const { result } = renderHook(() => useDocuments())

      await act(async () => {
        await result.current.handleInitArborescence()
      })

      expect(documentsApi.initArborescence).not.toHaveBeenCalled()
    })
  })

  describe('gestion des documents', () => {
    it('handleUploadFiles sans dossier selectionne', async () => {
      const { result } = renderHook(() => useDocuments())

      await waitFor(() => {
        expect(result.current.isLoadingChantiers).toBe(false)
      })

      const files = [new File(['content'], 'test.pdf')]

      await act(async () => {
        await result.current.handleUploadFiles(files)
      })

      expect(documentsApi.uploadMultipleDocuments).not.toHaveBeenCalled()
      expect(mockAddToast).toHaveBeenCalledWith({
        message: 'Selectionnez un dossier',
        type: 'warning',
      })
    })

    it('handleDownloadDocument ouvre le document', async () => {
      vi.mocked(documentsApi.downloadDocument).mockResolvedValue({ url: 'https://example.com/doc.pdf', filename: 'doc.pdf', mime_type: 'application/pdf' })
      const mockOpen = vi.spyOn(window, 'open').mockImplementation(() => null)

      const { result } = renderHook(() => useDocuments())

      await act(async () => {
        await result.current.handleDownloadDocument(mockDocuments[0])
      })

      expect(documentsApi.downloadDocument).toHaveBeenCalledWith(mockDocuments[0].id)
      expect(mockOpen).toHaveBeenCalledWith('https://example.com/doc.pdf', '_blank')
    })

    it('handleDeleteDocument supprime le document', async () => {
      vi.mocked(documentsApi.deleteDocument).mockResolvedValue(undefined)

      const { result } = renderHook(() => useDocuments())

      await waitFor(() => {
        expect(result.current.isLoadingChantiers).toBe(false)
      })

      act(() => {
        result.current.handleSelectDossier(mockDossierTree)
      })

      await waitFor(() => {
        expect(result.current.isLoadingDocuments).toBe(false)
      })

      await act(async () => {
        await result.current.handleDeleteDocument(mockDocuments[0])
      })

      expect(documentsApi.deleteDocument).toHaveBeenCalledWith(mockDocuments[0].id)
      expect(mockAddToast).toHaveBeenCalledWith({
        message: 'Document supprime',
        type: 'success',
      })
    })

    it('handleDeleteDocument annulable', async () => {
      vi.spyOn(window, 'confirm').mockReturnValue(false)

      const { result } = renderHook(() => useDocuments())

      await act(async () => {
        await result.current.handleDeleteDocument(mockDocuments[0])
      })

      expect(documentsApi.deleteDocument).not.toHaveBeenCalled()
    })
  })

  describe('recherche', () => {
    it('handleSearchDocuments ne fait rien sans chantier', async () => {
      const { result } = renderHook(() => useDocuments())

      act(() => {
        result.current.setSearchQuery('plan')
      })

      await act(async () => {
        await result.current.handleSearchDocuments()
      })

      expect(documentsApi.searchDocuments).not.toHaveBeenCalled()
    })

    it('handleSearchDocuments ne fait rien sans query vide', async () => {
      const { result } = renderHook(() => useDocuments())

      // Pas de query definie
      await act(async () => {
        await result.current.handleSearchDocuments()
      })

      expect(documentsApi.searchDocuments).not.toHaveBeenCalled()
    })

    it('setSearchQuery met a jour la query', () => {
      const { result } = renderHook(() => useDocuments())

      expect(result.current.searchQuery).toBe('')

      act(() => {
        result.current.setSearchQuery('test search')
      })

      expect(result.current.searchQuery).toBe('test search')
    })
  })

  describe('preview', () => {
    it('setPreviewDocument ouvre le preview', async () => {
      const { result } = renderHook(() => useDocuments())

      act(() => {
        result.current.setPreviewDocument(mockDocuments[0])
      })

      expect(result.current.previewDocument).toEqual(mockDocuments[0])
    })

    it('closePreviewModal ferme le preview', async () => {
      const { result } = renderHook(() => useDocuments())

      act(() => {
        result.current.setPreviewDocument(mockDocuments[0])
      })

      expect(result.current.previewDocument).not.toBeNull()

      act(() => {
        result.current.closePreviewModal()
      })

      expect(result.current.previewDocument).toBeNull()
    })
  })

  describe('refresh', () => {
    it('refreshArborescence recharge l\'arborescence', async () => {
      const { result } = renderHook(() => useDocuments())

      await waitFor(() => {
        expect(result.current.isLoadingChantiers).toBe(false)
      })

      act(() => {
        result.current.selectChantier(mockChantiers[0])
      })

      await waitFor(() => {
        expect(result.current.isLoadingArborescence).toBe(false)
      })

      vi.mocked(documentsApi.getArborescence).mockClear()

      act(() => {
        result.current.refreshArborescence()
      })

      await waitFor(() => {
        expect(documentsApi.getArborescence).toHaveBeenCalled()
      })
    })

    it('refreshArborescence ne fait rien sans chantier', async () => {
      const { result } = renderHook(() => useDocuments())

      vi.mocked(documentsApi.getArborescence).mockClear()

      act(() => {
        result.current.refreshArborescence()
      })

      expect(documentsApi.getArborescence).not.toHaveBeenCalled()
    })
  })
})
