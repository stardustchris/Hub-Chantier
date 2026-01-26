/**
 * Tests pour DocumentsCard
 * Utilise le hook useRecentDocuments pour charger les documents
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import DocumentsCard from './DocumentsCard'
import type { RecentDocument } from '../../hooks/useRecentDocuments'

// Mock du hook useRecentDocuments
const mockOpenDocument = vi.fn()
const mockRefreshDocuments = vi.fn()
const mockLoadMore = vi.fn()

vi.mock('../../hooks', () => ({
  useRecentDocuments: vi.fn(() => ({
    documents: [],
    isLoading: false,
    hasMore: false,
    openDocument: mockOpenDocument,
    loadMore: mockLoadMore,
    refreshDocuments: mockRefreshDocuments,
  })),
}))

// Mock de useNavigate
const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

// Import apres les mocks
import { useRecentDocuments } from '../../hooks'

const mockUseRecentDocuments = useRecentDocuments as ReturnType<typeof vi.fn>

function renderWithRouter(component: React.ReactElement) {
  return render(<BrowserRouter>{component}</BrowserRouter>)
}

describe('DocumentsCard', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockUseRecentDocuments.mockReturnValue({
      documents: [],
      isLoading: false,
      hasMore: false,
      openDocument: mockOpenDocument,
      loadMore: mockLoadMore,
      refreshDocuments: mockRefreshDocuments,
    })
  })

  it('affiche le titre Mes documents', () => {
    renderWithRouter(<DocumentsCard />)
    expect(screen.getByText('Mes documents')).toBeInTheDocument()
  })

  it('affiche le bouton Voir tout', () => {
    renderWithRouter(<DocumentsCard />)
    expect(screen.getByText('Voir tout')).toBeInTheDocument()
  })

  it('affiche le loading state', () => {
    mockUseRecentDocuments.mockReturnValue({
      documents: [],
      isLoading: true,
      hasMore: false,
      openDocument: mockOpenDocument,
      loadMore: mockLoadMore,
      refreshDocuments: mockRefreshDocuments,
    })

    const { container } = renderWithRouter(<DocumentsCard />)

    // Verifier que le spinner est present
    const spinner = container.querySelector('.animate-spin')
    expect(spinner).toBeInTheDocument()
  })

  it('affiche le state vide quand pas de documents', () => {
    mockUseRecentDocuments.mockReturnValue({
      documents: [],
      isLoading: false,
      hasMore: false,
      openDocument: mockOpenDocument,
      loadMore: mockLoadMore,
      refreshDocuments: mockRefreshDocuments,
    })

    renderWithRouter(<DocumentsCard />)

    expect(screen.getByText('Aucun document recent')).toBeInTheDocument()
    expect(screen.getByText('Acceder a la GED')).toBeInTheDocument()
  })

  it('affiche les documents charges', () => {
    const docs: RecentDocument[] = [
      { id: '1', name: 'Document A.pdf', siteName: 'Chantier 1', type: 'pdf', chantierId: 1, documentId: 1 },
      { id: '2', name: 'Image B.jpg', siteName: 'Chantier 2', type: 'image', chantierId: 2, documentId: 2 },
    ]

    mockUseRecentDocuments.mockReturnValue({
      documents: docs,
      isLoading: false,
      hasMore: false,
      openDocument: mockOpenDocument,
      loadMore: mockLoadMore,
      refreshDocuments: mockRefreshDocuments,
    })

    renderWithRouter(<DocumentsCard />)

    expect(screen.getByText('Document A.pdf')).toBeInTheDocument()
    expect(screen.getByText('Image B.jpg')).toBeInTheDocument()
    expect(screen.getByText('Chantier 1')).toBeInTheDocument()
    expect(screen.getByText('Chantier 2')).toBeInTheDocument()
  })

  it('navigue vers /documents au clic sur Voir tout', () => {
    renderWithRouter(<DocumentsCard />)

    fireEvent.click(screen.getByText('Voir tout'))

    expect(mockNavigate).toHaveBeenCalledWith('/documents')
  })

  it('navigue vers /documents au clic sur Acceder a la GED', () => {
    mockUseRecentDocuments.mockReturnValue({
      documents: [],
      isLoading: false,
      hasMore: false,
      openDocument: mockOpenDocument,
      loadMore: mockLoadMore,
      refreshDocuments: mockRefreshDocuments,
    })

    renderWithRouter(<DocumentsCard />)

    fireEvent.click(screen.getByText('Acceder a la GED'))

    expect(mockNavigate).toHaveBeenCalledWith('/documents')
  })

  it('appelle openDocument au clic sur un document', () => {
    const doc: RecentDocument = {
      id: 'doc-123',
      name: 'Mon Document.pdf',
      siteName: 'Chantier Test',
      type: 'pdf',
      chantierId: 1,
      documentId: 123,
    }

    mockUseRecentDocuments.mockReturnValue({
      documents: [doc],
      isLoading: false,
      hasMore: false,
      openDocument: mockOpenDocument,
      loadMore: mockLoadMore,
      refreshDocuments: mockRefreshDocuments,
    })

    renderWithRouter(<DocumentsCard />)

    fireEvent.click(screen.getByText('Mon Document.pdf'))

    expect(mockOpenDocument).toHaveBeenCalledWith(doc)
  })

  it('gere les differents types de documents', () => {
    const docs: RecentDocument[] = [
      { id: '1', name: 'PDF Doc', siteName: '', type: 'pdf', chantierId: 1, documentId: 1 },
      { id: '2', name: 'Word Doc', siteName: '', type: 'doc', chantierId: 1, documentId: 2 },
      { id: '3', name: 'Image Doc', siteName: '', type: 'image', chantierId: 1, documentId: 3 },
      { id: '4', name: 'Other Doc', siteName: '', type: 'other', chantierId: 1, documentId: 4 },
    ]

    mockUseRecentDocuments.mockReturnValue({
      documents: docs,
      isLoading: false,
      hasMore: false,
      openDocument: mockOpenDocument,
      loadMore: mockLoadMore,
      refreshDocuments: mockRefreshDocuments,
    })

    renderWithRouter(<DocumentsCard />)

    expect(screen.getByText('PDF Doc')).toBeInTheDocument()
    expect(screen.getByText('Word Doc')).toBeInTheDocument()
    expect(screen.getByText('Image Doc')).toBeInTheDocument()
    expect(screen.getByText('Other Doc')).toBeInTheDocument()
  })

  it('applique les couleurs correctes pour les types de fichiers', () => {
    const docs: RecentDocument[] = [
      { id: '1', name: 'PDF', siteName: '', type: 'pdf', chantierId: 1, documentId: 1 },
    ]

    mockUseRecentDocuments.mockReturnValue({
      documents: docs,
      isLoading: false,
      hasMore: false,
      openDocument: mockOpenDocument,
      loadMore: mockLoadMore,
      refreshDocuments: mockRefreshDocuments,
    })

    const { container } = renderWithRouter(<DocumentsCard />)

    // PDF devrait avoir la couleur rouge
    const pdfIcon = container.querySelector('.bg-red-100')
    expect(pdfIcon).toBeInTheDocument()
  })

  it('affiche le bouton Voir plus quand hasMore est true', () => {
    const docs: RecentDocument[] = [
      { id: '1', name: 'Doc1.pdf', siteName: '', type: 'pdf', chantierId: 1, documentId: 1 },
    ]

    mockUseRecentDocuments.mockReturnValue({
      documents: docs,
      isLoading: false,
      hasMore: true,
      openDocument: mockOpenDocument,
      loadMore: mockLoadMore,
      refreshDocuments: mockRefreshDocuments,
    })

    renderWithRouter(<DocumentsCard />)

    expect(screen.getByText('Voir plus')).toBeInTheDocument()
  })

  it('appelle loadMore au clic sur Voir plus', () => {
    const docs: RecentDocument[] = [
      { id: '1', name: 'Doc1.pdf', siteName: '', type: 'pdf', chantierId: 1, documentId: 1 },
    ]

    mockUseRecentDocuments.mockReturnValue({
      documents: docs,
      isLoading: false,
      hasMore: true,
      openDocument: mockOpenDocument,
      loadMore: mockLoadMore,
      refreshDocuments: mockRefreshDocuments,
    })

    renderWithRouter(<DocumentsCard />)

    fireEvent.click(screen.getByText('Voir plus'))

    expect(mockLoadMore).toHaveBeenCalled()
  })

  it('ne affiche pas le bouton Voir plus quand hasMore est false', () => {
    const docs: RecentDocument[] = [
      { id: '1', name: 'Doc1.pdf', siteName: '', type: 'pdf', chantierId: 1, documentId: 1 },
    ]

    mockUseRecentDocuments.mockReturnValue({
      documents: docs,
      isLoading: false,
      hasMore: false,
      openDocument: mockOpenDocument,
      loadMore: mockLoadMore,
      refreshDocuments: mockRefreshDocuments,
    })

    renderWithRouter(<DocumentsCard />)

    expect(screen.queryByText('Voir plus')).not.toBeInTheDocument()
  })
})
