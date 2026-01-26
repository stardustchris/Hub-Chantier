/**
 * Tests pour DocumentModal (DossierModal et DocumentEditModal)
 *
 * Couvre:
 * - DossierModal: création et édition de dossiers
 * - DocumentEditModal: édition de documents
 * - Initialisation et soumission des formulaires
 * - Gestion des niveaux d'accès
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { DossierModal, DocumentEditModal } from './DocumentModal'
import type { Dossier, Document } from '../../types/documents'

// Helper to get form field by label text (since labels don't have htmlFor)
const getFieldByLabel = (labelText: RegExp): HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement => {
  const label = screen.getByText(labelText)
  const container = label.parentElement
  if (!container) throw new Error(`Cannot find container for label: ${labelText}`)
  const input = container.querySelector('input, select, textarea')
  if (!input) throw new Error(`Cannot find input for label: ${labelText}`)
  return input as HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
}

const createMockDossier = (overrides: Partial<Dossier> = {}): Dossier => ({
  id: 1,
  chantier_id: 1,
  nom: 'Mon Dossier',
  type_dossier: 'custom',
  niveau_acces: 'compagnon',
  parent_id: null,
  created_at: '2024-01-15T10:00:00',
  updated_at: '2024-01-15T10:00:00',
  documents: [],
  sous_dossiers: [],
  ...overrides,
})

const createMockDocument = (overrides: Partial<Document> = {}): Document => ({
  id: 1,
  dossier_id: 1,
  nom: 'document.pdf',
  nom_original: 'document.pdf',
  type_mime: 'application/pdf',
  taille: 1024,
  chemin_stockage: '/storage/document.pdf',
  created_at: '2024-01-15T10:00:00',
  updated_at: '2024-01-15T10:00:00',
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
    it('ne rend rien quand isOpen est false', () => {
      render(<DossierModal {...defaultProps} isOpen={false} />)
      expect(screen.queryByText('Nouveau dossier')).not.toBeInTheDocument()
    })

    it('rend le modal quand isOpen est true', () => {
      render(<DossierModal {...defaultProps} />)
      expect(screen.getByText('Nouveau dossier')).toBeInTheDocument()
    })
  })

  describe('Mode création', () => {
    it('affiche le titre "Nouveau dossier"', () => {
      render(<DossierModal {...defaultProps} />)
      expect(screen.getByText('Nouveau dossier')).toBeInTheDocument()
    })

    it('affiche le bouton Créer', () => {
      render(<DossierModal {...defaultProps} />)
      expect(screen.getByRole('button', { name: 'Créer' })).toBeInTheDocument()
    })

    it('affiche le sélecteur de type de dossier', () => {
      render(<DossierModal {...defaultProps} />)
      expect(screen.getByText(/type de dossier/i)).toBeInTheDocument()
      expect(getFieldByLabel(/type de dossier/i)).toBeInTheDocument()
    })

    it('initialise le formulaire vide', () => {
      render(<DossierModal {...defaultProps} />)

      const nomInput = getFieldByLabel(/nom du dossier/i)
      expect(nomInput).toHaveValue('')
    })

    it('initialise avec les valeurs par défaut', () => {
      render(<DossierModal {...defaultProps} />)

      expect(getFieldByLabel(/type de dossier/i)).toHaveValue('custom')
      expect(getFieldByLabel(/niveau d'accès/i)).toHaveValue('compagnon')
    })

    it('soumet les données de création', async () => {
      const user = userEvent.setup()
      render(<DossierModal {...defaultProps} />)

      await user.type(getFieldByLabel(/nom du dossier/i), 'Nouveau Dossier')
      await user.selectOptions(getFieldByLabel(/type de dossier/i), '01_plans')
      await user.selectOptions(getFieldByLabel(/niveau d'accès/i), 'chef_chantier')

      await user.click(screen.getByRole('button', { name: 'Créer' }))

      expect(mockOnSubmit).toHaveBeenCalledWith({
        chantier_id: 1,
        nom: 'Nouveau Dossier',
        type_dossier: '01_plans',
        niveau_acces: 'chef_chantier',
        parent_id: null,
      })
    })

    it('inclut le parent_id si fourni', async () => {
      const user = userEvent.setup()
      render(<DossierModal {...defaultProps} parentId={5} />)

      await user.type(getFieldByLabel(/nom du dossier/i), 'Sous-dossier')
      await user.click(screen.getByRole('button', { name: 'Créer' }))

      expect(mockOnSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          parent_id: 5,
        })
      )
    })
  })

  describe('Mode édition', () => {
    const editDossier = createMockDossier({
      nom: 'Dossier Existant',
      type_dossier: 'plans',
      niveau_acces: 'chef_chantier',
    })

    it('affiche le titre "Modifier le dossier"', () => {
      render(<DossierModal {...defaultProps} dossier={editDossier} />)
      expect(screen.getByText('Modifier le dossier')).toBeInTheDocument()
    })

    it('affiche le bouton Modifier', () => {
      render(<DossierModal {...defaultProps} dossier={editDossier} />)
      expect(screen.getByRole('button', { name: 'Modifier' })).toBeInTheDocument()
    })

    it('n\'affiche pas le sélecteur de type', () => {
      render(<DossierModal {...defaultProps} dossier={editDossier} />)
      expect(screen.queryByText(/type de dossier/i)).not.toBeInTheDocument()
    })

    it('initialise le formulaire avec les données du dossier', () => {
      render(<DossierModal {...defaultProps} dossier={editDossier} />)

      expect(getFieldByLabel(/nom du dossier/i)).toHaveValue('Dossier Existant')
      expect(getFieldByLabel(/niveau d'accès/i)).toHaveValue('chef_chantier')
    })

    it('soumet uniquement les champs modifiés', async () => {
      const user = userEvent.setup()
      render(<DossierModal {...defaultProps} dossier={editDossier} />)

      // Modifier seulement le nom
      const nomInput = getFieldByLabel(/nom du dossier/i)
      await user.clear(nomInput)
      await user.type(nomInput, 'Nouveau Nom')

      await user.click(screen.getByRole('button', { name: 'Modifier' }))

      expect(mockOnSubmit).toHaveBeenCalledWith({
        nom: 'Nouveau Nom',
        niveau_acces: undefined,
      })
    })

    it('inclut niveau_acces si modifié', async () => {
      const user = userEvent.setup()
      render(<DossierModal {...defaultProps} dossier={editDossier} />)

      await user.selectOptions(getFieldByLabel(/niveau d'accès/i), 'conducteur')
      await user.click(screen.getByRole('button', { name: 'Modifier' }))

      expect(mockOnSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          niveau_acces: 'conducteur',
        })
      )
    })
  })

  describe('États', () => {
    it('désactive les boutons pendant le chargement', () => {
      render(<DossierModal {...defaultProps} loading={true} />)

      expect(screen.getByRole('button', { name: 'Annuler' })).toBeDisabled()
      expect(screen.getByRole('button', { name: 'Enregistrement...' })).toBeDisabled()
    })

    it('désactive le bouton Créer si le nom est vide', () => {
      render(<DossierModal {...defaultProps} />)

      expect(screen.getByRole('button', { name: 'Créer' })).toBeDisabled()
    })

    it('active le bouton Créer quand le nom est rempli', async () => {
      const user = userEvent.setup()
      render(<DossierModal {...defaultProps} />)

      await user.type(getFieldByLabel(/nom du dossier/i), 'Test')

      expect(screen.getByRole('button', { name: 'Créer' })).not.toBeDisabled()
    })
  })

  describe('Fermeture', () => {
    it('appelle onClose au clic sur Annuler', async () => {
      const user = userEvent.setup()
      render(<DossierModal {...defaultProps} />)

      await user.click(screen.getByRole('button', { name: 'Annuler' }))

      expect(mockOnClose).toHaveBeenCalled()
    })
  })

  describe('Réinitialisation', () => {
    it('réinitialise le formulaire quand on passe d\'édition à création', () => {
      const { rerender } = render(
        <DossierModal {...defaultProps} dossier={createMockDossier({ nom: 'Test' })} />
      )

      expect(getFieldByLabel(/nom du dossier/i)).toHaveValue('Test')

      rerender(<DossierModal {...defaultProps} dossier={null} />)

      expect(getFieldByLabel(/nom du dossier/i)).toHaveValue('')
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
    it('ne rend rien quand isOpen est false', () => {
      render(<DocumentEditModal {...defaultProps} isOpen={false} />)
      expect(screen.queryByText('Modifier le document')).not.toBeInTheDocument()
    })

    it('ne rend rien quand document est null', () => {
      render(<DocumentEditModal {...defaultProps} document={null} />)
      expect(screen.queryByText('Modifier le document')).not.toBeInTheDocument()
    })

    it('rend le modal quand isOpen et document sont fournis', () => {
      render(<DocumentEditModal {...defaultProps} />)
      expect(screen.getByText('Modifier le document')).toBeInTheDocument()
    })
  })

  describe('Affichage du formulaire', () => {
    it('affiche le titre "Modifier le document"', () => {
      render(<DocumentEditModal {...defaultProps} />)
      expect(screen.getByText('Modifier le document')).toBeInTheDocument()
    })

    it('affiche les champs du formulaire', () => {
      render(<DocumentEditModal {...defaultProps} />)

      expect(getFieldByLabel(/nom du fichier/i)).toBeInTheDocument()
      expect(getFieldByLabel(/description/i)).toBeInTheDocument()
      expect(getFieldByLabel(/niveau d'accès spécifique/i)).toBeInTheDocument()
    })

    it('affiche l\'option "Hériter du dossier"', () => {
      render(<DocumentEditModal {...defaultProps} />)
      expect(screen.getByText('Hériter du dossier')).toBeInTheDocument()
    })
  })

  describe('Initialisation', () => {
    it('initialise le formulaire avec les données du document', () => {
      const doc = createMockDocument({
        nom: 'rapport.pdf',
        description: 'Mon rapport',
        niveau_acces: 'conducteur',
      })
      render(<DocumentEditModal {...defaultProps} document={doc} />)

      expect(getFieldByLabel(/nom du fichier/i)).toHaveValue('rapport.pdf')
      expect(getFieldByLabel(/description/i)).toHaveValue('Mon rapport')
      expect(getFieldByLabel(/niveau d'accès spécifique/i)).toHaveValue('conducteur')
    })

    it('gère les valeurs nulles', () => {
      const doc = createMockDocument({
        description: undefined,
        niveau_acces: undefined,
      })
      render(<DocumentEditModal {...defaultProps} document={doc} />)

      expect(getFieldByLabel(/description/i)).toHaveValue('')
      expect(getFieldByLabel(/niveau d'accès spécifique/i)).toHaveValue('')
    })
  })

  describe('Soumission', () => {
    it('soumet uniquement les champs modifiés', async () => {
      const user = userEvent.setup()
      const doc = createMockDocument({ nom: 'original.pdf' })
      render(<DocumentEditModal {...defaultProps} document={doc} />)

      const nomInput = getFieldByLabel(/nom du fichier/i)
      await user.clear(nomInput)
      await user.type(nomInput, 'nouveau.pdf')

      await user.click(screen.getByRole('button', { name: 'Modifier' }))

      expect(mockOnSubmit).toHaveBeenCalledWith({
        nom: 'nouveau.pdf',
      })
    })

    it('inclut la description si modifiée', async () => {
      const user = userEvent.setup()
      const doc = createMockDocument({ description: '' })
      render(<DocumentEditModal {...defaultProps} document={doc} />)

      await user.type(getFieldByLabel(/description/i), 'Nouvelle description')
      await user.click(screen.getByRole('button', { name: 'Modifier' }))

      expect(mockOnSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          description: 'Nouvelle description',
        })
      )
    })

    it('envoie null pour niveau_acces si vidé', async () => {
      const user = userEvent.setup()
      const doc = createMockDocument({ niveau_acces: 'conducteur' })
      render(<DocumentEditModal {...defaultProps} document={doc} />)

      await user.selectOptions(getFieldByLabel(/niveau d'accès spécifique/i), '')
      await user.click(screen.getByRole('button', { name: 'Modifier' }))

      expect(mockOnSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          niveau_acces: null,
        })
      )
    })

    it('envoie un objet vide si rien n\'a changé', async () => {
      const user = userEvent.setup()
      const doc = createMockDocument()
      render(<DocumentEditModal {...defaultProps} document={doc} />)

      await user.click(screen.getByRole('button', { name: 'Modifier' }))

      expect(mockOnSubmit).toHaveBeenCalledWith({})
    })
  })

  describe('États', () => {
    it('désactive les boutons pendant le chargement', () => {
      render(<DocumentEditModal {...defaultProps} loading={true} />)

      expect(screen.getByRole('button', { name: 'Annuler' })).toBeDisabled()
      expect(screen.getByRole('button', { name: 'Enregistrement...' })).toBeDisabled()
    })

    it('désactive le bouton si le nom est vide', async () => {
      const user = userEvent.setup()
      render(<DocumentEditModal {...defaultProps} />)

      const nomInput = getFieldByLabel(/nom du fichier/i)
      await user.clear(nomInput)

      expect(screen.getByRole('button', { name: 'Modifier' })).toBeDisabled()
    })
  })

  describe('Fermeture', () => {
    it('appelle onClose au clic sur Annuler', async () => {
      const user = userEvent.setup()
      render(<DocumentEditModal {...defaultProps} />)

      await user.click(screen.getByRole('button', { name: 'Annuler' }))

      expect(mockOnClose).toHaveBeenCalled()
    })
  })
})
