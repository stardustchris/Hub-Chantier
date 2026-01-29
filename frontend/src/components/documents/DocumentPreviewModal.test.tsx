/**
 * Tests unitaires pour DocumentPreviewModal
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import DocumentPreviewModal from './DocumentPreviewModal'
import type { Document } from '../../types/documents'

const mockGetDocumentPreview = vi.fn()

vi.mock('../../services/documents', () => ({
  getDocumentPreviewUrl: vi.fn().mockReturnValue('/api/documents/documents/1/preview/content'),
  getDocumentPreview: (...args: any[]) => mockGetDocumentPreview(...args),
}))

const createMockDocument = (overrides: Partial<Document> = {}): Document => ({
  id: 1,
  chantier_id: 1,
  dossier_id: 1,
  nom: 'rapport.pdf',
  nom_original: 'rapport.pdf',
  type_document: 'pdf',
  taille: 1024,
  taille_formatee: '1 Ko',
  mime_type: 'application/pdf',
  uploaded_by: 1,
  uploaded_by_nom: 'Jean Dupont',
  uploaded_at: '2024-01-15T10:00:00Z',
  description: null,
  version: 1,
  icone: 'pdf',
  extension: '.pdf',
  niveau_acces: null,
  ...overrides,
})

describe('DocumentPreviewModal', () => {
  const defaultProps = {
    document: createMockDocument(),
    isOpen: true,
    onClose: vi.fn(),
  }

  beforeEach(() => {
    vi.clearAllMocks()
    mockGetDocumentPreview.mockResolvedValue({
      id: 1,
      nom: 'rapport.pdf',
      type_document: 'pdf',
      mime_type: 'application/pdf',
      taille: 1024,
      can_preview: true,
      preview_url: '/preview',
    })
  })

  it('ne rend rien quand isOpen est false', () => {
    // Arrange & Act
    const { container } = render(
      <DocumentPreviewModal {...defaultProps} isOpen={false} />
    )

    // Assert
    expect(container.innerHTML).toBe('')
  })

  it('ne rend rien quand document est null', () => {
    // Arrange & Act
    const { container } = render(
      <DocumentPreviewModal {...defaultProps} document={null} />
    )

    // Assert
    expect(container.innerHTML).toBe('')
  })

  it('affiche le nom du document dans le header', async () => {
    // Arrange & Act
    render(<DocumentPreviewModal {...defaultProps} />)

    // Assert
    await waitFor(() => {
      expect(screen.getByText('rapport.pdf')).toBeInTheDocument()
    })
  })

  it('affiche la taille formatee et le type', async () => {
    // Arrange & Act
    render(<DocumentPreviewModal {...defaultProps} />)

    // Assert
    await waitFor(() => {
      expect(screen.getByText(/1 Ko/)).toBeInTheDocument()
      expect(screen.getByText(/PDF/)).toBeInTheDocument()
    })
  })

  it('affiche un iframe pour les documents PDF', async () => {
    // Arrange & Act
    const { container } = render(<DocumentPreviewModal {...defaultProps} />)

    // Assert
    await waitFor(() => {
      const iframe = container.querySelector('iframe')
      expect(iframe).toBeInTheDocument()
      expect(iframe).toHaveAttribute('title', 'rapport.pdf')
    })
  })

  it('affiche une image pour les documents image', async () => {
    // Arrange
    const doc = createMockDocument({
      type_document: 'image',
      nom: 'photo.jpg',
      mime_type: 'image/jpeg',
    })

    // Act
    render(<DocumentPreviewModal {...defaultProps} document={doc} />)

    // Assert
    await waitFor(() => {
      const img = screen.getByAltText('photo.jpg')
      expect(img).toBeInTheDocument()
    })
  })

  it('affiche une video pour les documents video', async () => {
    // Arrange
    const doc = createMockDocument({
      type_document: 'video',
      nom: 'video.mp4',
      mime_type: 'video/mp4',
    })

    // Act
    const { container } = render(<DocumentPreviewModal {...defaultProps} document={doc} />)

    // Assert
    await waitFor(() => {
      const video = container.querySelector('video')
      expect(video).toBeInTheDocument()
    })
  })

  it('affiche le bouton Telecharger quand onDownload est fourni', async () => {
    // Arrange
    const onDownload = vi.fn()

    // Act
    render(<DocumentPreviewModal {...defaultProps} onDownload={onDownload} />)

    // Assert
    await waitFor(() => {
      expect(screen.getByText(/Télécharger/)).toBeInTheDocument()
    })
  })

  it('appelle onClose au clic sur le bouton fermer', async () => {
    // Arrange
    const onClose = vi.fn()
    render(<DocumentPreviewModal {...defaultProps} onClose={onClose} />)

    // Act
    await waitFor(() => {
      const closeButton = screen.getByText('✕')
      fireEvent.click(closeButton)
    })

    // Assert
    expect(onClose).toHaveBeenCalled()
  })

  it('affiche le loader pendant le chargement', () => {
    // Arrange - mock getDocumentPreview as pending (never resolves)
    mockGetDocumentPreview.mockReturnValue(new Promise(() => {}))

    // Act
    const { container } = render(<DocumentPreviewModal {...defaultProps} />)

    // Assert
    const spinner = container.querySelector('.animate-spin')
    expect(spinner).toBeInTheDocument()
  })

  it('affiche le message d\'erreur quand le preview echoue', async () => {
    // Arrange
    mockGetDocumentPreview.mockRejectedValue(new Error('Erreur serveur'))

    // Act
    render(<DocumentPreviewModal {...defaultProps} />)

    // Assert
    await waitFor(() => {
      expect(screen.getByText('Impossible de charger la prévisualisation')).toBeInTheDocument()
    })
  })
})
