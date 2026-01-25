/**
 * Tests unitaires pour DocumentList
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import DocumentList from './DocumentList'
import type { Document } from '../../types/documents'
import * as documentsService from '../../services/documents'

// Mock services
vi.mock('../../services/documents', () => ({
  getDocumentIcon: vi.fn((type) => {
    const icons: Record<string, string> = {
      pdf: '📄',
      image: '🖼️',
      excel: '📊',
      word: '📝',
      video: '🎬',
      autre: '📎',
    }
    return icons[type] || '📎'
  }),
  downloadAndSaveZip: vi.fn(),
}))

vi.mock('../../services/logger', () => ({
  logger: {
    error: vi.fn(),
    info: vi.fn(),
    warn: vi.fn(),
  },
}))

vi.mock('../../utils/dates', () => ({
  formatDateDayMonthYearTime: vi.fn((date) => '25/01/2026 14:30'),
}))

const mockDocuments: Document[] = [
  {
    id: 1,
    nom: 'Rapport.pdf',
    description: 'Rapport mensuel',
    type_document: 'pdf',
    taille: 1024000,
    taille_formatee: '1 Mo',
    uploaded_by: 1,
    uploaded_by_nom: 'Jean Dupont',
    uploaded_at: '2026-01-25T14:30:00',
    dossier_id: 1,
    url: '/files/rapport.pdf',
  },
  {
    id: 2,
    nom: 'Photo.jpg',
    description: 'Photo du chantier',
    type_document: 'image',
    taille: 2048000,
    taille_formatee: '2 Mo',
    uploaded_by: 2,
    uploaded_by_nom: 'Marie Martin',
    uploaded_at: '2026-01-24T10:00:00',
    dossier_id: 1,
    url: '/files/photo.jpg',
  },
  {
    id: 3,
    nom: 'Video.mp4',
    type_document: 'video',
    taille: 15000000, // 15 Mo - too big to preview
    taille_formatee: '15 Mo',
    uploaded_by: 1,
    uploaded_at: '2026-01-23T09:00:00',
    dossier_id: 1,
    url: '/files/video.mp4',
  },
]

const mockOnDocumentClick = vi.fn()
const mockOnDocumentDownload = vi.fn()
const mockOnDocumentEdit = vi.fn()
const mockOnDocumentDelete = vi.fn()
const mockOnDocumentPreview = vi.fn()

const defaultProps = {
  documents: mockDocuments,
  onDocumentClick: mockOnDocumentClick,
  onDocumentDownload: mockOnDocumentDownload,
  onDocumentEdit: mockOnDocumentEdit,
  onDocumentDelete: mockOnDocumentDelete,
  onDocumentPreview: mockOnDocumentPreview,
}

describe('DocumentList', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('rendering', () => {
    it('affiche la liste des documents', () => {
      render(<DocumentList {...defaultProps} />)

      expect(screen.getByText('Rapport.pdf')).toBeInTheDocument()
      expect(screen.getByText('Photo.jpg')).toBeInTheDocument()
      expect(screen.getByText('Video.mp4')).toBeInTheDocument()
    })

    it('affiche les descriptions', () => {
      render(<DocumentList {...defaultProps} />)

      expect(screen.getByText('Rapport mensuel')).toBeInTheDocument()
      expect(screen.getByText('Photo du chantier')).toBeInTheDocument()
    })

    it('affiche les tailles formatees', () => {
      render(<DocumentList {...defaultProps} />)

      expect(screen.getByText('1 Mo')).toBeInTheDocument()
      expect(screen.getByText('2 Mo')).toBeInTheDocument()
    })

    it('affiche les noms d uploaders', () => {
      render(<DocumentList {...defaultProps} />)

      expect(screen.getByText('Jean Dupont')).toBeInTheDocument()
      expect(screen.getByText('Marie Martin')).toBeInTheDocument()
    })

    it('affiche message si aucun document', () => {
      render(<DocumentList {...defaultProps} documents={[]} />)

      expect(screen.getByText('Aucun document dans ce dossier')).toBeInTheDocument()
    })

    it('affiche le loader si loading', () => {
      render(<DocumentList {...defaultProps} loading={true} />)

      expect(screen.queryByText('Rapport.pdf')).not.toBeInTheDocument()
      // Le spinner devrait être présent
      expect(document.querySelector('.animate-spin')).toBeInTheDocument()
    })

    it('affiche les en-tetes de colonnes', () => {
      render(<DocumentList {...defaultProps} />)

      expect(screen.getByText('Nom')).toBeInTheDocument()
      expect(screen.getByText('Type')).toBeInTheDocument()
      expect(screen.getByText('Taille')).toBeInTheDocument()
      expect(screen.getByText('Ajouté par')).toBeInTheDocument()
      expect(screen.getByText('Date')).toBeInTheDocument()
      expect(screen.getByText('Actions')).toBeInTheDocument()
    })
  })

  describe('document actions', () => {
    it('appelle onDocumentClick quand on clique sur une ligne', async () => {
      const user = userEvent.setup()
      render(<DocumentList {...defaultProps} />)

      await user.click(screen.getByText('Rapport.pdf'))

      expect(mockOnDocumentClick).toHaveBeenCalledWith(mockDocuments[0])
    })

    it('appelle onDocumentDownload quand on clique sur telecharger', async () => {
      const user = userEvent.setup()
      render(<DocumentList {...defaultProps} />)

      const downloadButtons = screen.getAllByTitle('Télécharger')
      await user.click(downloadButtons[0])

      expect(mockOnDocumentDownload).toHaveBeenCalledWith(mockDocuments[0])
    })

    it('appelle onDocumentEdit quand on clique sur modifier', async () => {
      const user = userEvent.setup()
      render(<DocumentList {...defaultProps} />)

      const editButtons = screen.getAllByTitle('Modifier')
      await user.click(editButtons[0])

      expect(mockOnDocumentEdit).toHaveBeenCalledWith(mockDocuments[0])
    })

    it('appelle onDocumentDelete quand on clique sur supprimer', async () => {
      const user = userEvent.setup()
      render(<DocumentList {...defaultProps} />)

      const deleteButtons = screen.getAllByTitle('Supprimer')
      await user.click(deleteButtons[0])

      expect(mockOnDocumentDelete).toHaveBeenCalledWith(mockDocuments[0])
    })

    it('appelle onDocumentPreview pour fichiers previewable', async () => {
      const user = userEvent.setup()
      render(<DocumentList {...defaultProps} />)

      // PDF is previewable (< 10Mo)
      const previewButtons = screen.getAllByTitle('Prévisualiser')
      await user.click(previewButtons[0])

      expect(mockOnDocumentPreview).toHaveBeenCalledWith(mockDocuments[0])
    })
  })

  describe('selection', () => {
    it('affiche les checkboxes quand selectionEnabled', () => {
      render(<DocumentList {...defaultProps} selectionEnabled={true} />)

      const checkboxes = screen.getAllByRole('checkbox')
      // 1 pour select all + 3 pour les documents
      expect(checkboxes.length).toBe(4)
    })

    it('masque les checkboxes quand selectionEnabled=false', () => {
      render(<DocumentList {...defaultProps} selectionEnabled={false} />)

      expect(screen.queryByRole('checkbox')).not.toBeInTheDocument()
    })

    it('selectionne un document individuellement', async () => {
      const user = userEvent.setup()
      render(<DocumentList {...defaultProps} />)

      const checkboxes = screen.getAllByRole('checkbox')
      await user.click(checkboxes[1]) // Premier document

      expect(screen.getByText('1 document sélectionné')).toBeInTheDocument()
    })

    it('selectionne tous les documents', async () => {
      const user = userEvent.setup()
      render(<DocumentList {...defaultProps} />)

      const selectAllCheckbox = screen.getAllByRole('checkbox')[0]
      await user.click(selectAllCheckbox)

      expect(screen.getByText('3 documents sélectionnés')).toBeInTheDocument()
    })

    it('deselectionne tous les documents', async () => {
      const user = userEvent.setup()
      render(<DocumentList {...defaultProps} />)

      // Select all
      const selectAllCheckbox = screen.getAllByRole('checkbox')[0]
      await user.click(selectAllCheckbox)

      // Deselect all
      await user.click(selectAllCheckbox)

      expect(screen.queryByText(/sélectionné/)).not.toBeInTheDocument()
    })

    it('affiche bouton telecharger ZIP quand selection', async () => {
      const user = userEvent.setup()
      render(<DocumentList {...defaultProps} />)

      const checkboxes = screen.getAllByRole('checkbox')
      await user.click(checkboxes[1])

      expect(screen.getByText(/Télécharger en ZIP/)).toBeInTheDocument()
    })

    it('telecharge ZIP des documents selectionnes', async () => {
      const user = userEvent.setup()
      vi.mocked(documentsService.downloadAndSaveZip).mockResolvedValue(undefined)
      render(<DocumentList {...defaultProps} />)

      const checkboxes = screen.getAllByRole('checkbox')
      await user.click(checkboxes[1]) // doc id 1
      await user.click(checkboxes[2]) // doc id 2

      await user.click(screen.getByText(/Télécharger en ZIP/))

      expect(documentsService.downloadAndSaveZip).toHaveBeenCalledWith([1, 2])
    })

    it('annule la selection', async () => {
      const user = userEvent.setup()
      render(<DocumentList {...defaultProps} />)

      const checkboxes = screen.getAllByRole('checkbox')
      await user.click(checkboxes[1])

      await user.click(screen.getByText('Annuler'))

      expect(screen.queryByText(/sélectionné/)).not.toBeInTheDocument()
    })
  })

  describe('document highlighting', () => {
    it('highlight le document selectionne', () => {
      render(<DocumentList {...defaultProps} selectedDocumentId={1} />)

      // La première ligne devrait avoir la classe bg-blue-50
      const row = screen.getByText('Rapport.pdf').closest('tr')
      expect(row).toHaveClass('bg-blue-50')
    })
  })

  describe('preview availability', () => {
    it('affiche preview pour PDF < 10Mo', () => {
      render(<DocumentList {...defaultProps} />)
      // PDF (1Mo) should have preview button
      expect(screen.getAllByTitle('Prévisualiser').length).toBeGreaterThan(0)
    })

    it('n affiche pas preview pour fichier > 10Mo', () => {
      const largeDoc: Document[] = [
        {
          id: 1,
          nom: 'Large.pdf',
          type_document: 'pdf',
          taille: 15000000, // 15 Mo
          taille_formatee: '15 Mo',
          uploaded_by: 1,
          uploaded_at: '2026-01-25',
          dossier_id: 1,
          url: '/files/large.pdf',
        },
      ]

      render(<DocumentList {...defaultProps} documents={largeDoc} />)

      expect(screen.queryByTitle('Prévisualiser')).not.toBeInTheDocument()
    })
  })
})
