/**
 * Tests pour FormulaireModal
 *
 * Couvre:
 * - Rendu conditionnel (isOpen, template)
 * - Affichage header avec statut
 * - Affichage metadata formulaire
 * - Rendu des champs via FieldRenderer
 * - Validation des champs obligatoires
 * - Sauvegarde et soumission
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import FormulaireModal from './FormulaireModal'
import type { TemplateFormulaire, FormulaireRempli, ChampRempli } from '../../types'

// Mock useFocusTrap to prevent auto-focus stealing during userEvent.type()
vi.mock('../../hooks/useFocusTrap', () => ({
  useFocusTrap: () => ({ current: null }),
  default: () => ({ current: null }),
}))

// Mock FieldRenderer
vi.mock('./FieldRenderer', () => ({
  default: ({ champ, value, onChange, error }: {
    champ: { nom: string; label: string; obligatoire?: boolean }
    value: unknown
    onChange: (v: unknown) => void
    error?: string
  }) => (
    <div data-testid={`field-${champ.nom}`}>
      <label>{champ.label}{champ.obligatoire && ' *'}</label>
      <input
        data-testid={`input-${champ.nom}`}
        value={String(value || '')}
        onChange={(e) => onChange(e.target.value)}
      />
      {error && <span data-testid={`error-${champ.nom}`}>{error}</span>}
    </div>
  ),
}))

const createMockTemplate = (overrides: Partial<TemplateFormulaire> = {}): TemplateFormulaire => ({
  id: 1,
  nom: 'Rapport de chantier',
  description: 'Description du formulaire',
  categorie: 'securite',
  champs: [
    {
      nom: 'titre',
      label: 'Titre',
      type_champ: 'texte',
      obligatoire: true,
      ordre: 1,
    },
    {
      nom: 'commentaire',
      label: 'Commentaire',
      type_champ: 'texte_long',
      obligatoire: false,
      ordre: 2,
    },
  ],
  is_active: true,
  version: 1,
  nombre_champs: 2,
  a_signature: false,
  a_photo: false,
  created_by: 1,
  created_at: '2024-01-15T10:00:00',
  updated_at: '2024-01-15T10:00:00',
  ...overrides,
})

const createMockFormulaire = (overrides: Partial<FormulaireRempli> = {}): FormulaireRempli => ({
  id: 1,
  template_id: 1,
  chantier_id: 1,
  user_id: 1,
  statut: 'brouillon',
  champs: [
    { nom: 'titre', valeur: 'Mon titre', type_champ: 'texte' },
    { nom: 'commentaire', valeur: 'Mon commentaire', type_champ: 'texte_long' },
  ] as ChampRempli[],
  photos: [],
  est_signe: false,
  est_geolocalise: false,
  version: 1,
  created_at: '2024-01-15T10:00:00',
  updated_at: '2024-01-15T10:00:00',
  chantier_nom: 'Chantier Test',
  user_nom: 'Jean Dupont',
  ...overrides,
})

describe('FormulaireModal', () => {
  const mockOnClose = vi.fn()
  const mockOnSave = vi.fn().mockResolvedValue(undefined)
  const mockOnSubmit = vi.fn().mockResolvedValue(undefined)

  const defaultProps = {
    isOpen: true,
    onClose: mockOnClose,
    onSave: mockOnSave,
    onSubmit: mockOnSubmit,
    formulaire: null,
    template: createMockTemplate(),
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Rendu conditionnel', () => {
    it('ne rend rien si isOpen est false', () => {
      render(<FormulaireModal {...defaultProps} isOpen={false} />)
      expect(screen.queryByText('Rapport de chantier')).not.toBeInTheDocument()
    })

    it('ne rend rien si template est null', () => {
      render(<FormulaireModal {...defaultProps} template={null} />)
      expect(screen.queryByText('Rapport de chantier')).not.toBeInTheDocument()
    })

    it('rend le modal si isOpen et template sont fournis', () => {
      render(<FormulaireModal {...defaultProps} />)
      expect(screen.getByText('Rapport de chantier')).toBeInTheDocument()
    })
  })

  describe('Header', () => {
    it('affiche le nom du template', () => {
      render(<FormulaireModal {...defaultProps} />)
      expect(screen.getByText('Rapport de chantier')).toBeInTheDocument()
    })

    it('affiche le statut si formulaire fourni', () => {
      render(
        <FormulaireModal
          {...defaultProps}
          formulaire={createMockFormulaire({ statut: 'brouillon' })}
        />
      )
      expect(screen.getByText('Brouillon')).toBeInTheDocument()
    })

    it('affiche le statut soumis', () => {
      render(
        <FormulaireModal
          {...defaultProps}
          formulaire={createMockFormulaire({ statut: 'soumis' })}
        />
      )
      expect(screen.getByText('Soumis')).toBeInTheDocument()
    })
  })

  describe('Metadata', () => {
    it('affiche le nom du chantier', () => {
      render(
        <FormulaireModal
          {...defaultProps}
          formulaire={createMockFormulaire({ chantier_nom: 'Chantier Alpha' })}
        />
      )
      expect(screen.getByText('Chantier Alpha')).toBeInTheDocument()
    })

    it('affiche le nom de l\'utilisateur', () => {
      render(
        <FormulaireModal
          {...defaultProps}
          formulaire={createMockFormulaire({ user_nom: 'Pierre Martin' })}
        />
      )
      expect(screen.getByText('Pierre Martin')).toBeInTheDocument()
    })

  })

  describe('Description', () => {
    it('affiche la description du template', () => {
      render(<FormulaireModal {...defaultProps} />)
      expect(screen.getByText('Description du formulaire')).toBeInTheDocument()
    })
  })

  describe('Champs du formulaire', () => {
    it('affiche tous les champs du template', () => {
      render(<FormulaireModal {...defaultProps} />)
      expect(screen.getByTestId('field-titre')).toBeInTheDocument()
      expect(screen.getByTestId('field-commentaire')).toBeInTheDocument()
    })

    it('initialise les valeurs depuis le formulaire existant', () => {
      render(
        <FormulaireModal
          {...defaultProps}
          formulaire={createMockFormulaire()}
        />
      )
      expect(screen.getByTestId('input-titre')).toHaveValue('Mon titre')
      expect(screen.getByTestId('input-commentaire')).toHaveValue('Mon commentaire')
    })

    it('permet de modifier les valeurs', async () => {
      const user = userEvent.setup()
      render(<FormulaireModal {...defaultProps} />)

      const titreInput = screen.getByTestId('input-titre')
      await user.type(titreInput, 'Nouveau titre')
      expect(titreInput).toHaveValue('Nouveau titre')
    })
  })

  describe('Photos', () => {
    it('affiche la section photos si formulaire contient des photos', () => {
      render(
        <FormulaireModal
          {...defaultProps}
          formulaire={createMockFormulaire({
            photos: [
              { url: 'http://example.com/photo1.jpg', nom_fichier: 'photo1.jpg', champ_nom: 'photo_chantier' },
              { url: 'http://example.com/photo2.jpg', nom_fichier: 'photo2.jpg', champ_nom: 'photo_chantier' },
            ],
          })}
        />
      )
      expect(screen.getByText('Photos (2)')).toBeInTheDocument()
    })

    it('n\'affiche pas la section photos si pas de photos', () => {
      render(
        <FormulaireModal
          {...defaultProps}
          formulaire={createMockFormulaire({ photos: [] })}
        />
      )
      expect(screen.queryByText(/Photos \(/)).not.toBeInTheDocument()
    })
  })

  describe('Signature', () => {
    it('affiche la section signature si formulaire signé', () => {
      render(
        <FormulaireModal
          {...defaultProps}
          formulaire={createMockFormulaire({
            est_signe: true,
            signature_nom: 'Jean Dupont',
            signature_timestamp: '2024-01-15T14:30:00',
          })}
        />
      )
      expect(screen.getByText('Signature')).toBeInTheDocument()
      expect(screen.getByText(/Signe par Jean Dupont/)).toBeInTheDocument()
    })
  })

  describe('Actions', () => {
    it('affiche le bouton Annuler si éditable', () => {
      render(<FormulaireModal {...defaultProps} />)
      expect(screen.getByText('Annuler')).toBeInTheDocument()
    })

    it('affiche le bouton Fermer si lecture seule', () => {
      render(<FormulaireModal {...defaultProps} readOnly />)
      expect(screen.getByText('Fermer')).toBeInTheDocument()
    })

    it('affiche les boutons Sauvegarder et Soumettre si éditable', () => {
      render(<FormulaireModal {...defaultProps} />)
      expect(screen.getByText('Sauvegarder')).toBeInTheDocument()
      expect(screen.getByText('Soumettre')).toBeInTheDocument()
    })

    it('n\'affiche pas les boutons d\'action si lecture seule', () => {
      render(<FormulaireModal {...defaultProps} readOnly />)
      expect(screen.queryByText('Sauvegarder')).not.toBeInTheDocument()
      expect(screen.queryByText('Soumettre')).not.toBeInTheDocument()
    })

    it('n\'affiche pas les boutons d\'action si formulaire soumis', () => {
      render(
        <FormulaireModal
          {...defaultProps}
          formulaire={createMockFormulaire({ statut: 'soumis' })}
        />
      )
      expect(screen.queryByText('Sauvegarder')).not.toBeInTheDocument()
      expect(screen.queryByText('Soumettre')).not.toBeInTheDocument()
    })
  })

  describe('Sauvegarde', () => {
    it('appelle onSave avec les données du formulaire', async () => {
      const user = userEvent.setup()
      render(<FormulaireModal {...defaultProps} />)

      await user.type(screen.getByTestId('input-titre'), 'Test')
      await user.click(screen.getByText('Sauvegarder'))

      await waitFor(() => {
        expect(mockOnSave).toHaveBeenCalled()
      })
    })
  })

  describe('Soumission', () => {
    it('valide les champs obligatoires avant soumission', async () => {
      const user = userEvent.setup()
      render(<FormulaireModal {...defaultProps} />)

      // Ne pas remplir le champ obligatoire
      await user.click(screen.getByText('Soumettre'))

      await waitFor(() => {
        expect(screen.getByText('Veuillez remplir tous les champs obligatoires')).toBeInTheDocument()
      })
    })

    it('appelle onSubmit après validation réussie', async () => {
      const user = userEvent.setup()
      render(<FormulaireModal {...defaultProps} />)

      // Remplir le champ obligatoire
      await user.type(screen.getByTestId('input-titre'), 'Titre valide')
      await user.click(screen.getByText('Soumettre'))

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalled()
      })
    })

    it('affiche l\'erreur en cas d\'échec de soumission', async () => {
      mockOnSave.mockRejectedValueOnce(new Error('Erreur serveur'))

      const user = userEvent.setup()
      render(<FormulaireModal {...defaultProps} />)

      await user.type(screen.getByTestId('input-titre'), 'Titre valide')
      await user.click(screen.getByText('Soumettre'))

      await waitFor(() => {
        expect(screen.getByText('Erreur serveur')).toBeInTheDocument()
      })
    })
  })

  describe('Fermeture', () => {
    it('appelle onClose au clic sur le bouton Annuler', async () => {
      const user = userEvent.setup()
      render(<FormulaireModal {...defaultProps} />)

      await user.click(screen.getByText('Annuler'))
      expect(mockOnClose).toHaveBeenCalled()
    })

    it('appelle onClose au clic sur le bouton X', async () => {
      const user = userEvent.setup()
      render(<FormulaireModal {...defaultProps} />)

      const closeButton = screen.getAllByRole('button').find(
        btn => btn.querySelector('svg.lucide-x')
      )
      if (closeButton) {
        await user.click(closeButton)
        expect(mockOnClose).toHaveBeenCalled()
      }
    })

    it('appelle onClose au clic sur l\'overlay', async () => {
      const user = userEvent.setup()
      render(<FormulaireModal {...defaultProps} />)

      const overlay = document.querySelector('.bg-black\\/50')
      if (overlay) {
        await user.click(overlay)
        expect(mockOnClose).toHaveBeenCalled()
      }
    })
  })
})
