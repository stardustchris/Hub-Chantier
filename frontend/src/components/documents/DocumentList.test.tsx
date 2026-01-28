/**
 * Tests pour DocumentList
 *
 * Couvre:
 * - Affichage de la liste des documents
 * - Etat de chargement et vide
 * - Selection multiple
 * - Telechargement ZIP
 * - Actions sur les documents
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import DocumentList from './DocumentList'
import type { Document } from '../../types/documents'

// Mock services
const mockDownloadAndSaveZip = vi.fn()

vi.mock('../../services/documents', () => ({
  getDocumentIcon: (type: string) => type === 'pdf' ? '📄' : '📁',
  downloadAndSaveZip: (...args: unknown[]) => mockDownloadAndSaveZip(...args),
}))

vi.mock('../../services/logger', () => ({
  logger: {
    error: vi.fn(),
    warn: vi.fn(),
    info: vi.fn(),
  },
}))

vi.mock('../../utils/dates', () => ({
  formatDateDayMonthYearTime: () => '15/01/2024 10:00',
}))

const createMockDocument = (overrides: Partial<Document> = {}): Document => ({
  id: 1,
  dossier_id: 1,
  nom: 'document.pdf',
  nom_original: 'document.pdf',
  type_document: 'plan',
  taille: 1024000,
  taille_formatee: '1 Mo',
  mime_type: 'application/pdf',
  uploaded_by: 1,
  uploaded_by_nom: 'Jean Dupont',
  uploaded_at: '2024-01-15T10:00:00',
  description: null,
  version: 1,
  icone: 'file-text',
  extension: 'pdf',
  niveau_acces: null,
  ...overrides,
})

describe('DocumentList', () => {
  const mockOnClick = vi.fn()
  const mockOnDownload = vi.fn()
  const mockOnEdit = vi.fn()
  const mockOnDelete = vi.fn()
  const mockOnPreview = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    mockDownloadAndSaveZip.mockResolvedValue(undefined)
  })

  describe('Etat de chargement', () => {
    it('affiche le spinner pendant le chargement', () => {
      render(<DocumentList documents={[]} loading />)
      expect(document.querySelector('.animate-spin')).toBeInTheDocument()
    })
  })

  describe('Etat vide', () => {
    it('affiche le message si aucun document', () => {
      render(<DocumentList documents={[]} />)
      expect(screen.getByText('Aucun document dans ce dossier')).toBeInTheDocument()
    })

    it('affiche l indication de glisser-deposer', () => {
      render(<DocumentList documents={[]} />)
      expect(screen.getByText(/Glissez-déposez/)).toBeInTheDocument()
    })
  })

  describe('Affichage des documents', () => {
    it('affiche le nom du document', () => {
      render(<DocumentList documents={[createMockDocument()]} />)
      expect(screen.getByText('document.pdf')).toBeInTheDocument()
    })

    it('affiche le type du document', () => {
      render(<DocumentList documents={[createMockDocument()]} />)
      expect(screen.getByText('PDF')).toBeInTheDocument()
    })

    it('affiche la taille formatee', () => {
      render(<DocumentList documents={[createMockDocument()]} />)
      expect(screen.getByText('1 Mo')).toBeInTheDocument()
    })

    it('affiche le nom de l uploadeur', () => {
      render(<DocumentList documents={[createMockDocument()]} />)
      expect(screen.getByText('Jean Dupont')).toBeInTheDocument()
    })

    it('affiche la date', () => {
      render(<DocumentList documents={[createMockDocument()]} />)
      expect(screen.getByText('15/01/2024 10:00')).toBeInTheDocument()
    })

    it('affiche la description si presente', () => {
      render(<DocumentList documents={[createMockDocument({ description: 'Ma description' })]} />)
      expect(screen.getByText('Ma description')).toBeInTheDocument()
    })
  })

  describe('Actions sur les documents', () => {
    it('appelle onDocumentClick au clic sur la ligne', async () => {
      const user = userEvent.setup()
      render(<DocumentList documents={[createMockDocument()]} onDocumentClick={mockOnClick} />)

      await user.click(screen.getByText('document.pdf'))

      expect(mockOnClick).toHaveBeenCalled()
    })

    it('affiche le bouton telecharger si onDocumentDownload fourni', () => {
      render(<DocumentList documents={[createMockDocument()]} onDocumentDownload={mockOnDownload} />)
      expect(screen.getByTitle('Télécharger')).toBeInTheDocument()
    })

    it('appelle onDocumentDownload au clic', async () => {
      const user = userEvent.setup()
      render(<DocumentList documents={[createMockDocument()]} onDocumentDownload={mockOnDownload} />)

      await user.click(screen.getByTitle('Télécharger'))

      expect(mockOnDownload).toHaveBeenCalled()
    })

    it('affiche le bouton modifier si onDocumentEdit fourni', () => {
      render(<DocumentList documents={[createMockDocument()]} onDocumentEdit={mockOnEdit} />)
      expect(screen.getByTitle('Modifier')).toBeInTheDocument()
    })

    it('affiche le bouton supprimer si onDocumentDelete fourni', () => {
      render(<DocumentList documents={[createMockDocument()]} onDocumentDelete={mockOnDelete} />)
      expect(screen.getByTitle('Supprimer')).toBeInTheDocument()
    })

    it('affiche le bouton previsualiser pour les fichiers compatibles', () => {
      render(
        <DocumentList
          documents={[createMockDocument({ type_document: 'pdf', taille: 1000 })]}
          onDocumentPreview={mockOnPreview}
        />
      )
      expect(screen.getByTitle('Prévisualiser')).toBeInTheDocument()
    })

    it('n affiche pas previsualiser pour fichiers trop gros', () => {
      render(
        <DocumentList
          documents={[createMockDocument({ type_document: 'pdf', taille: 15 * 1024 * 1024 })]}
          onDocumentPreview={mockOnPreview}
        />
      )
      expect(screen.queryByTitle('Prévisualiser')).not.toBeInTheDocument()
    })
  })

  describe('Selection multiple', () => {
    it('affiche les checkboxes si selectionEnabled', () => {
      render(<DocumentList documents={[createMockDocument()]} selectionEnabled />)
      expect(screen.getAllByRole('checkbox')).toHaveLength(2) // header + row
    })

    it('n affiche pas les checkboxes si selectionEnabled false', () => {
      render(<DocumentList documents={[createMockDocument()]} selectionEnabled={false} />)
      expect(screen.queryAllByRole('checkbox')).toHaveLength(0)
    })

    it('selectionne un document au clic sur la checkbox', async () => {
      const user = userEvent.setup()
      render(<DocumentList documents={[createMockDocument()]} selectionEnabled />)

      const checkboxes = screen.getAllByRole('checkbox')
      await user.click(checkboxes[1]) // row checkbox

      expect(screen.getByText('1 document sélectionné')).toBeInTheDocument()
    })

    it('affiche le nombre de documents selectionnes', async () => {
      const user = userEvent.setup()
      render(
        <DocumentList
          documents={[createMockDocument({ id: 1 }), createMockDocument({ id: 2, nom: 'autre.pdf' })]}
          selectionEnabled
        />
      )

      const checkboxes = screen.getAllByRole('checkbox')
      await user.click(checkboxes[1])
      await user.click(checkboxes[2])

      expect(screen.getByText('2 documents sélectionnés')).toBeInTheDocument()
    })

    it('selectionne tout au clic sur checkbox header', async () => {
      const user = userEvent.setup()
      render(
        <DocumentList
          documents={[createMockDocument({ id: 1 }), createMockDocument({ id: 2, nom: 'autre.pdf' })]}
          selectionEnabled
        />
      )

      const checkboxes = screen.getAllByRole('checkbox')
      await user.click(checkboxes[0]) // header checkbox

      expect(screen.getByText('2 documents sélectionnés')).toBeInTheDocument()
    })
  })

  describe('Telechargement ZIP', () => {
    it('affiche le bouton telecharger en ZIP si selection', async () => {
      const user = userEvent.setup()
      render(<DocumentList documents={[createMockDocument()]} selectionEnabled />)

      const checkboxes = screen.getAllByRole('checkbox')
      await user.click(checkboxes[1])

      expect(screen.getByText(/Télécharger en ZIP/)).toBeInTheDocument()
    })

    it('appelle downloadAndSaveZip au clic', async () => {
      const user = userEvent.setup()
      render(<DocumentList documents={[createMockDocument()]} selectionEnabled />)

      const checkboxes = screen.getAllByRole('checkbox')
      await user.click(checkboxes[1])

      await user.click(screen.getByText(/Télécharger en ZIP/))

      await waitFor(() => {
        expect(mockDownloadAndSaveZip).toHaveBeenCalledWith([1])
      })
    })

    it('affiche le bouton Annuler pour deselectionner', async () => {
      const user = userEvent.setup()
      render(<DocumentList documents={[createMockDocument()]} selectionEnabled />)

      const checkboxes = screen.getAllByRole('checkbox')
      await user.click(checkboxes[1])

      expect(screen.getByText('Annuler')).toBeInTheDocument()
    })

    it('deselectionne tout au clic sur Annuler', async () => {
      const user = userEvent.setup()
      render(<DocumentList documents={[createMockDocument()]} selectionEnabled />)

      const checkboxes = screen.getAllByRole('checkbox')
      await user.click(checkboxes[1])

      await user.click(screen.getByText('Annuler'))

      expect(screen.queryByText('1 document sélectionné')).not.toBeInTheDocument()
    })
  })

  describe('Document selectionne', () => {
    it('met en surbrillance le document selectionne', () => {
      render(<DocumentList documents={[createMockDocument()]} selectedDocumentId={1} />)
      // La ligne devrait avoir la classe bg-blue-50
    })
  })
})
