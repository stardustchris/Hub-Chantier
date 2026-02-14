// @vitest-environment jsdom
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, waitFor, act } from '@testing-library/react'

vi.mock('../contexts/AuthContext', () => ({
  useAuth: vi.fn(),
}))

vi.mock('../contexts/ToastContext', () => ({
  useToast: vi.fn(),
}))

vi.mock('../services/planning', () => ({
  planningService: {
    getByUtilisateur: vi.fn(),
    getAffectations: vi.fn(),
  },
}))

vi.mock('../services/documents', () => ({
  searchDocuments: vi.fn(),
  downloadDocument: vi.fn(),
}))

vi.mock('../services/logger', () => ({
  logger: {
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
    debug: vi.fn(),
  },
}))

import { useRecentDocuments } from './useRecentDocuments'
import { useAuth } from '../contexts/AuthContext'
import { useToast } from '../contexts/ToastContext'
import { planningService } from '../services/planning'
import * as documentsService from '../services/documents'

const mockUseAuth = vi.mocked(useAuth)
const mockUseToast = vi.mocked(useToast)
const mockGetByUtilisateur = vi.mocked(planningService.getByUtilisateur)
const mockGetAffectations = vi.mocked(planningService.getAffectations)
const mockSearchDocuments = vi.mocked(documentsService.searchDocuments)
const mockDownloadDocument = vi.mocked(documentsService.downloadDocument)

const mockAddToast = vi.fn()

describe('useRecentDocuments', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockUseToast.mockReturnValue({
      toasts: [],
      addToast: mockAddToast,
      removeToast: vi.fn(),
      showUndoToast: vi.fn(),
    })
  })

  it('should stop loading when user is null', async () => {
    mockUseAuth.mockReturnValue({
      user: null,
      isLoading: false,
      isAuthenticated: false,
      login: vi.fn(),
      logout: vi.fn(),
    })

    const { result } = renderHook(() => useRecentDocuments())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(result.current.documents).toEqual([])
  })

  it('should load documents from API for chantiers on today planning', async () => {
    mockUseAuth.mockReturnValue({
      user: { id: '1', nom: 'Test', prenom: 'User', email: 't@t.com', role: 'ouvrier' } as any,
      isLoading: false,
      isAuthenticated: true,
      login: vi.fn(),
      logout: vi.fn(),
    })

    mockGetByUtilisateur.mockResolvedValue([
      { chantier_id: '10', chantier_nom: 'Chantier Alpha', utilisateur_id: '1' } as any,
    ])

    mockSearchDocuments.mockResolvedValue({
      documents: [
        { id: 1, nom: 'Plan.pdf', type_document: 'pdf' } as any,
        { id: 2, nom: 'Photo.jpg', type_document: 'image' } as any,
      ],
      total: 2,
    } as any)

    const { result } = renderHook(() => useRecentDocuments())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(result.current.documents.length).toBe(2)
    expect(result.current.documents[0].name).toBe('Plan.pdf')
    expect(result.current.documents[0].type).toBe('pdf')
    expect(result.current.documents[0].siteName).toBe('Chantier Alpha')
    expect(result.current.documents[1].type).toBe('image')
  })

  it('should return empty list when API returns no documents', async () => {
    mockUseAuth.mockReturnValue({
      user: { id: '1', nom: 'Test', prenom: 'User', email: 't@t.com', role: 'ouvrier' } as any,
      isLoading: false,
      isAuthenticated: true,
      login: vi.fn(),
      logout: vi.fn(),
    })

    mockGetByUtilisateur.mockResolvedValue([
      { chantier_id: '10', chantier_nom: 'Chantier Alpha', utilisateur_id: '1' } as any,
    ])

    mockSearchDocuments.mockResolvedValue({ documents: [], total: 0 } as any)

    const { result } = renderHook(() => useRecentDocuments())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(result.current.documents.length).toBe(0)
    expect(result.current.hasMore).toBe(false)
  })

  it('should return empty list on API error', async () => {
    mockUseAuth.mockReturnValue({
      user: { id: '1', nom: 'Test', prenom: 'User', email: 't@t.com', role: 'ouvrier' } as any,
      isLoading: false,
      isAuthenticated: true,
      login: vi.fn(),
      logout: vi.fn(),
    })

    mockGetByUtilisateur.mockRejectedValue(new Error('API Error'))

    const { result } = renderHook(() => useRecentDocuments())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(result.current.documents.length).toBe(0)
  })

  it('should support loadMore to display more documents', async () => {
    mockUseAuth.mockReturnValue({
      user: { id: '1', nom: 'Test', prenom: 'User', email: 't@t.com', role: 'ouvrier' } as any,
      isLoading: false,
      isAuthenticated: true,
      login: vi.fn(),
      logout: vi.fn(),
    })

    // Provide 6 documents from API to test loadMore
    const mockDocs = Array.from({ length: 6 }, (_, i) => ({
      id: i + 1, nom: `Doc${i + 1}.pdf`, type_document: 'pdf',
    }))
    mockGetByUtilisateur.mockResolvedValue([
      { chantier_id: '10', chantier_nom: 'Chantier', utilisateur_id: '1' } as any,
    ])
    mockSearchDocuments.mockResolvedValue({ documents: mockDocs, total: 6 } as any)

    const { result } = renderHook(() => useRecentDocuments())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(result.current.documents.length).toBe(4) // INITIAL_DISPLAY_COUNT
    expect(result.current.hasMore).toBe(true)

    act(() => {
      result.current.loadMore()
    })

    expect(result.current.documents.length).toBe(6)
    expect(result.current.hasMore).toBe(false)
  })

  it('should open a demo document using window.open', async () => {
    mockUseAuth.mockReturnValue({
      user: { id: '1', nom: 'Test', prenom: 'User', email: 't@t.com', role: 'ouvrier' } as any,
      isLoading: false,
      isAuthenticated: true,
      login: vi.fn(),
      logout: vi.fn(),
    })

    mockGetByUtilisateur.mockResolvedValue([
      { chantier_id: '10', chantier_nom: 'Chantier', utilisateur_id: '1' } as any,
    ])
    mockSearchDocuments.mockResolvedValue({ documents: [], total: 0 } as any)

    const mockOpen = vi.fn()
    vi.stubGlobal('open', mockOpen)

    const { result } = renderHook(() => useRecentDocuments())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    await act(async () => {
      await result.current.openDocument({
        id: 'demo-1',
        name: 'Consignes.pdf',
        siteName: 'General',
        type: 'pdf',
        chantierId: 1,
        documentId: 1,
        demoUrl: '/demo-documents/consignes.pdf',
      })
    })

    expect(mockOpen).toHaveBeenCalledWith('/demo-documents/consignes.pdf', '_blank', 'noopener,noreferrer')
    expect(mockAddToast).toHaveBeenCalledWith(
      expect.objectContaining({ type: 'success' })
    )

    vi.unstubAllGlobals()
  })

  it('should open API document via downloadDocument', async () => {
    mockUseAuth.mockReturnValue({
      user: { id: '1', nom: 'Test', prenom: 'User', email: 't@t.com', role: 'ouvrier' } as any,
      isLoading: false,
      isAuthenticated: true,
      login: vi.fn(),
      logout: vi.fn(),
    })

    mockGetByUtilisateur.mockResolvedValue([])
    mockSearchDocuments.mockResolvedValue({ documents: [], total: 0 } as any)

    const mockBlob = new Blob(['test pdf content'], { type: 'application/pdf' })
    mockDownloadDocument.mockResolvedValue(mockBlob)

    const mockOpen = vi.fn()
    vi.stubGlobal('open', mockOpen)

    // Mock URL.createObjectURL (not available in jsdom)
    const mockCreateObjectURL = vi.fn().mockReturnValue('blob:http://localhost/fake-blob-url')
    globalThis.URL.createObjectURL = mockCreateObjectURL

    const { result } = renderHook(() => useRecentDocuments())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    await act(async () => {
      await result.current.openDocument({
        id: '10-42',
        name: 'plan.pdf',
        siteName: 'Chantier Alpha',
        type: 'pdf',
        chantierId: 10,
        documentId: 42,
        // no demoUrl
      })
    })

    expect(mockDownloadDocument).toHaveBeenCalledWith(42)
    // The hook creates a blob URL via URL.createObjectURL, then opens it
    expect(mockOpen).toHaveBeenCalledWith(expect.any(String), '_blank', 'noopener,noreferrer')

    vi.unstubAllGlobals()
  })

  it('should show error toast when openDocument fails', async () => {
    mockUseAuth.mockReturnValue({
      user: { id: '1', nom: 'Test', prenom: 'User', email: 't@t.com', role: 'ouvrier' } as any,
      isLoading: false,
      isAuthenticated: true,
      login: vi.fn(),
      logout: vi.fn(),
    })

    mockGetByUtilisateur.mockResolvedValue([])
    mockSearchDocuments.mockResolvedValue({ documents: [], total: 0 } as any)
    mockDownloadDocument.mockRejectedValue(new Error('Download failed'))

    const { result } = renderHook(() => useRecentDocuments())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    await act(async () => {
      await result.current.openDocument({
        id: '10-42',
        name: 'plan.pdf',
        siteName: 'Chantier Alpha',
        type: 'pdf',
        chantierId: 10,
        documentId: 42,
      })
    })

    expect(mockAddToast).toHaveBeenCalledWith(
      expect.objectContaining({ type: 'error' })
    )
  })

  it('should load all affectations for admin with no personal ones', async () => {
    mockUseAuth.mockReturnValue({
      user: { id: '1', nom: 'Admin', prenom: 'Greg', email: 'a@t.com', role: 'admin' } as any,
      isLoading: false,
      isAuthenticated: true,
      login: vi.fn(),
      logout: vi.fn(),
    })

    mockGetByUtilisateur.mockResolvedValue([])
    mockGetAffectations.mockResolvedValue([
      { chantier_id: '10', chantier_nom: 'Chantier Alpha', utilisateur_id: '2' } as any,
    ])
    mockSearchDocuments.mockResolvedValue({ documents: [], total: 0 } as any)

    const { result } = renderHook(() => useRecentDocuments())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(mockGetAffectations).toHaveBeenCalled()
  })

  it('should expose refreshDocuments function', async () => {
    mockUseAuth.mockReturnValue({
      user: { id: '1', nom: 'Test', prenom: 'User', email: 't@t.com', role: 'ouvrier' } as any,
      isLoading: false,
      isAuthenticated: true,
      login: vi.fn(),
      logout: vi.fn(),
    })

    mockGetByUtilisateur.mockResolvedValue([])

    const { result } = renderHook(() => useRecentDocuments())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(typeof result.current.refreshDocuments).toBe('function')
  })
})
