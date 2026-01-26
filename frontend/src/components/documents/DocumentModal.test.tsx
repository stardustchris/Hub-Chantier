/**
 * Tests pour DocumentModal (DossierModal et DocumentEditModal)
 *
 * Couvre:
 * - DossierModal: creation et edition de dossier
 * - DocumentEditModal: edition de document
 * - Formulaires et validation
 * - Fermeture
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { DossierModal, DocumentEditModal } from './DocumentModal'
import type { Dossier, Document } from '../../types/documents'

const createMockDossier = (overrides: Partial<Dossier> = {}): Dossier => ({
  id: 1,
  chantier_id: 1,
  nom: 'Plans',
  type_dossier: '01_plans',
  niveau_acces: 'compagnon',
  parent_id: null,
  chemin: '/Plans',
  nombre_documents: 5,
  created_at: '2024-01-15T10:00:00',
  updated_at: '2024-01-15T10:00:00',
  ...overrides,
})

const createMockDocument = (overrides: Partial<Document> = {}): Document => ({
  id: 1,
  dossier_id: 1,
  nom: 'plan.pdf',
  nom_original: 'plan.pdf',
  type_document: 'pdf',
  taille: 1024000,
  taille_formatee: '1 Mo',
  chemin_stockage: '/storage/plan.pdf',
  uploaded_by: 1,
  uploaded_at: '2024-01-15T10:00:00',
  description: 'Plan du RDC',
  niveau_acces: 'compagnon',
  ...overrides,
})

describe('DossierModal', () => {
  const mockOnClose = vi.fn()
  const mockOnSubmit = vi.fn()

  const defaultProps = {
    isOpen: true,
    onClose: mockOnClose,
    onSubmit: mockOnSubmit,
    chantierId: 1,
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Rendu conditionnel', () => {
    it('ne rend rien si isOpen est false', () => {
      render(<DossierModal {...defaultProps} isOpen={false} />)
      expect(screen.queryByText('Nouveau dossier')).not.toBeInTheDocument()
    })

    it('rend le modal si isOpen est true', () => {
      render(<DossierModal {...defaultProps} />)
      expect(screen.getByText('Nouveau dossier')).toBeInTheDocument()
    })
  })

  describe('Mode creation', () => {
    it('affiche le titre Nouveau dossier', () => {
      render(<DossierModal {...defaultProps} />)
      expect(screen.getByText('Nouveau dossier')).toBeInTheDocument()
    })

    it('affiche le champ nom vide', () => {
      render(<DossierModal {...defaultProps} />)
      const input = screen.getByRole('textbox')
      expect(input).toHaveValue('')
    })

    it('affiche le selecteur de type', () => {
      render(<DossierModal {...defaultProps} />)
      expect(screen.getByText('Type de dossier')).toBeInTheDocument()
    })

    it('affiche le selecteur de niveau d acces', () => {
      render(<DossierModal {...defaultProps} />)
      expect(screen.getByText(/Niveau d'accès/)).toBeInTheDocument()
    })

    it('affiche le bouton Creer', () => {
      render(<DossierModal {...defaultProps} />)
      expect(screen.getByText('Créer')).toBeInTheDocument()
    })
  })

  describe('Mode edition', () => {
    it('affiche le titre Modifier le dossier', () => {
      render(<DossierModal {...defaultProps} dossier={createMockDossier()} />)
      expect(screen.getByText('Modifier le dossier')).toBeInTheDocument()
    })

    it('preremplit le nom', () => {
      render(<DossierModal {...defaultProps} dossier={createMockDossier({ nom: 'Mon dossier' })} />)
      expect(screen.getByDisplayValue('Mon dossier')).toBeInTheDocument()
    })

    it('n affiche pas le selecteur de type en edition', () => {
      render(<DossierModal {...defaultProps} dossier={createMockDossier()} />)
      expect(screen.queryByText('Type de dossier')).not.toBeInTheDocument()
    })

    it('affiche le bouton Modifier', () => {
      render(<DossierModal {...defaultProps} dossier={createMockDossier()} />)
      expect(screen.getByText('Modifier')).toBeInTheDocument()
    })
  })

  describe('Soumission', () => {
    it('appelle onSubmit avec les donnees en creation', async () => {
      const user = userEvent.setup()
      render(<DossierModal {...defaultProps} />)

      await user.type(screen.getByRole('textbox'), 'Nouveau dossier')
      await user.click(screen.getByText('Créer'))

      expect(mockOnSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          chantier_id: 1,
          nom: 'Nouveau dossier',
        })
      )
    })

    it('appelle onSubmit avec les donnees modifiees en edition', async () => {
      const user = userEvent.setup()
      render(<DossierModal {...defaultProps} dossier={createMockDossier({ nom: 'Ancien nom' })} />)

      const input = screen.getByDisplayValue('Ancien nom')
      await user.clear(input)
      await user.type(input, 'Nouveau nom')
      await user.click(screen.getByText('Modifier'))

      expect(mockOnSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          nom: 'Nouveau nom',
        })
      )
    })

    it('desactive le bouton si nom vide', () => {
      render(<DossierModal {...defaultProps} />)
      expect(screen.getByText('Créer').closest('button')).toBeDisabled()
    })
  })

  describe('Fermeture', () => {
    it('appelle onClose au clic sur Annuler', async () => {
      const user = userEvent.setup()
      render(<DossierModal {...defaultProps} />)

      await user.click(screen.getByText('Annuler'))
      expect(mockOnClose).toHaveBeenCalled()
    })
  })

  describe('Etat de chargement', () => {
    it('affiche Enregistrement pendant le chargement', () => {
      render(<DossierModal {...defaultProps} loading />)
      expect(screen.getByText('Enregistrement...')).toBeInTheDocument()
    })

    it('desactive les boutons pendant le chargement', () => {
      render(<DossierModal {...defaultProps} loading />)
      expect(screen.getByText('Annuler').closest('button')).toBeDisabled()
    })
  })
})

describe('DocumentEditModal', () => {
  const mockOnClose = vi.fn()
  const mockOnSubmit = vi.fn()

  const defaultProps = {
    isOpen: true,
    onClose: mockOnClose,
    onSubmit: mockOnSubmit,
    document: createMockDocument(),
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Rendu conditionnel', () => {
    it('ne rend rien si isOpen est false', () => {
      render(<DocumentEditModal {...defaultProps} isOpen={false} />)
      expect(screen.queryByText('Modifier le document')).not.toBeInTheDocument()
    })

    it('ne rend rien si document est null', () => {
      render(<DocumentEditModal {...defaultProps} document={null} />)
      expect(screen.queryByText('Modifier le document')).not.toBeInTheDocument()
    })

    it('rend le modal si isOpen et document', () => {
      render(<DocumentEditModal {...defaultProps} />)
      expect(screen.getByText('Modifier le document')).toBeInTheDocument()
    })
  })

  describe('Affichage', () => {
    it('affiche le champ nom avec la valeur', () => {
      render(<DocumentEditModal {...defaultProps} />)
      expect(screen.getByDisplayValue('plan.pdf')).toBeInTheDocument()
    })

    it('affiche le champ description avec la valeur', () => {
      render(<DocumentEditModal {...defaultProps} />)
      expect(screen.getByDisplayValue('Plan du RDC')).toBeInTheDocument()
    })

    it('affiche le selecteur de niveau d acces', () => {
      render(<DocumentEditModal {...defaultProps} />)
      expect(screen.getByText(/Niveau d'accès spécifique/)).toBeInTheDocument()
    })
  })

  describe('Modification', () => {
    it('permet de modifier le nom', async () => {
      const user = userEvent.setup()
      render(<DocumentEditModal {...defaultProps} />)

      const input = screen.getByDisplayValue('plan.pdf')
      await user.clear(input)
      await user.type(input, 'nouveau_plan.pdf')

      expect(input).toHaveValue('nouveau_plan.pdf')
    })

    it('permet de modifier la description', async () => {
      const user = userEvent.setup()
      render(<DocumentEditModal {...defaultProps} />)

      const textarea = screen.getByDisplayValue('Plan du RDC')
      await user.clear(textarea)
      await user.type(textarea, 'Nouvelle description')

      expect(textarea).toHaveValue('Nouvelle description')
    })
  })

  describe('Soumission', () => {
    it('appelle onSubmit avec les donnees modifiees', async () => {
      const user = userEvent.setup()
      render(<DocumentEditModal {...defaultProps} />)

      const input = screen.getByDisplayValue('plan.pdf')
      await user.clear(input)
      await user.type(input, 'nouveau.pdf')
      await user.click(screen.getByText('Modifier'))

      expect(mockOnSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          nom: 'nouveau.pdf',
        })
      )
    })

    it('desactive le bouton si nom vide', async () => {
      const user = userEvent.setup()
      render(<DocumentEditModal {...defaultProps} />)

      const input = screen.getByDisplayValue('plan.pdf')
      await user.clear(input)

      expect(screen.getByText('Modifier').closest('button')).toBeDisabled()
    })
  })

  describe('Fermeture', () => {
    it('appelle onClose au clic sur Annuler', async () => {
      const user = userEvent.setup()
      render(<DocumentEditModal {...defaultProps} />)

      await user.click(screen.getByText('Annuler'))
      expect(mockOnClose).toHaveBeenCalled()
    })
  })
})
