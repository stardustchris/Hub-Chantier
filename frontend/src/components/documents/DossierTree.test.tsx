/**
 * Tests pour DossierTree
 *
 * Couvre:
 * - Affichage de l'arborescence des dossiers
 * - Expansion/collapse des nœuds
 * - Sélection de dossiers
 * - Actions (créer, éditer, supprimer)
 * - Affichage des badges de niveau d'accès
 * - Icônes par type de dossier
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import DossierTree from './DossierTree'
import type { DossierTree as DossierTreeType } from '../../types/documents'

const createMockDossier = (overrides: Partial<DossierTreeType> = {}): DossierTreeType => ({
  id: 1,
  chantier_id: 1,
  nom: 'Mon Dossier',
  type_dossier: 'custom',
  niveau_acces: 'compagnon',
  parent_id: null,
  created_at: '2024-01-15T10:00:00',
  updated_at: '2024-01-15T10:00:00',
  nombre_documents: 0,
  children: [],
  ...overrides,
})

describe('DossierTree', () => {
  const mockOnSelectDossier = vi.fn()
  const mockOnCreateDossier = vi.fn()
  const mockOnEditDossier = vi.fn()
  const mockOnDeleteDossier = vi.fn()

  const defaultProps = {
    dossiers: [],
    selectedDossierId: null,
    onSelectDossier: mockOnSelectDossier,
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Affichage de base', () => {
    it('affiche le titre "Dossiers"', () => {
      render(<DossierTree {...defaultProps} />)
      expect(screen.getByText('Dossiers')).toBeInTheDocument()
    })

    it('affiche un message quand il n\'y a pas de dossiers', () => {
      render(<DossierTree {...defaultProps} />)
      expect(screen.getByText(/aucun dossier/i)).toBeInTheDocument()
    })

    it('affiche le bouton "Nouveau" si onCreateDossier est fourni', () => {
      render(<DossierTree {...defaultProps} onCreateDossier={mockOnCreateDossier} />)
      expect(screen.getByRole('button', { name: '+ Nouveau' })).toBeInTheDocument()
    })

    it('n\'affiche pas le bouton "Nouveau" si onCreateDossier n\'est pas fourni', () => {
      render(<DossierTree {...defaultProps} />)
      expect(screen.queryByRole('button', { name: '+ Nouveau' })).not.toBeInTheDocument()
    })
  })

  describe('Affichage des dossiers', () => {
    it('affiche le nom des dossiers', () => {
      const dossiers = [createMockDossier({ nom: 'Plans' })]
      render(<DossierTree {...defaultProps} dossiers={dossiers} />)

      expect(screen.getByText('Plans')).toBeInTheDocument()
    })

    it('affiche le compteur de documents', () => {
      const dossiers = [createMockDossier({ nombre_documents: 5 })]
      render(<DossierTree {...defaultProps} dossiers={dossiers} />)

      expect(screen.getByText('5')).toBeInTheDocument()
    })

    it('n\'affiche pas le compteur si 0 documents', () => {
      const dossiers = [createMockDossier({ nombre_documents: 0 })]
      render(<DossierTree {...defaultProps} dossiers={dossiers} />)

      // Le compteur ne devrait pas être visible
      expect(screen.queryByText('0')).not.toBeInTheDocument()
    })

    it('affiche plusieurs dossiers au niveau racine', () => {
      const dossiers = [
        createMockDossier({ id: 1, nom: 'Dossier 1' }),
        createMockDossier({ id: 2, nom: 'Dossier 2' }),
        createMockDossier({ id: 3, nom: 'Dossier 3' }),
      ]
      render(<DossierTree {...defaultProps} dossiers={dossiers} />)

      expect(screen.getByText('Dossier 1')).toBeInTheDocument()
      expect(screen.getByText('Dossier 2')).toBeInTheDocument()
      expect(screen.getByText('Dossier 3')).toBeInTheDocument()
    })
  })

  describe('Icônes par type de dossier', () => {
    it('affiche l\'icône plans pour type 01_plans', () => {
      const dossiers = [createMockDossier({ type_dossier: '01_plans' })]
      render(<DossierTree {...defaultProps} dossiers={dossiers} />)

      expect(screen.getByText('📐')).toBeInTheDocument()
    })

    it('affiche l\'icône administratif pour type 02_administratif', () => {
      const dossiers = [createMockDossier({ type_dossier: '02_administratif' })]
      render(<DossierTree {...defaultProps} dossiers={dossiers} />)

      expect(screen.getByText('📋')).toBeInTheDocument()
    })

    it('affiche l\'icône sécurité pour type 03_securite', () => {
      const dossiers = [createMockDossier({ type_dossier: '03_securite' })]
      render(<DossierTree {...defaultProps} dossiers={dossiers} />)

      expect(screen.getByText('🦺')).toBeInTheDocument()
    })

    it('affiche l\'icône photos pour type 05_photos', () => {
      const dossiers = [createMockDossier({ type_dossier: '05_photos' })]
      render(<DossierTree {...defaultProps} dossiers={dossiers} />)

      expect(screen.getByText('📷')).toBeInTheDocument()
    })

    it('affiche l\'icône dossier générique pour custom', () => {
      const dossiers = [createMockDossier({ type_dossier: 'custom' })]
      render(<DossierTree {...defaultProps} dossiers={dossiers} />)

      expect(screen.getByText('📁')).toBeInTheDocument()
    })
  })

  describe('Badges de niveau d\'accès', () => {
    it('affiche le badge pour niveau compagnon', () => {
      const dossiers = [createMockDossier({ niveau_acces: 'compagnon' })]
      render(<DossierTree {...defaultProps} dossiers={dossiers} />)

      expect(screen.getByText('👥')).toBeInTheDocument()
    })

    it('affiche le badge pour niveau chef_chantier', () => {
      const dossiers = [createMockDossier({ niveau_acces: 'chef_chantier' })]
      render(<DossierTree {...defaultProps} dossiers={dossiers} />)

      expect(screen.getByText('👷')).toBeInTheDocument()
    })

    it('affiche le badge pour niveau conducteur', () => {
      const dossiers = [createMockDossier({ niveau_acces: 'conducteur' })]
      render(<DossierTree {...defaultProps} dossiers={dossiers} />)

      expect(screen.getByText('🔐')).toBeInTheDocument()
    })

    it('affiche le badge pour niveau admin', () => {
      const dossiers = [createMockDossier({ niveau_acces: 'admin' })]
      render(<DossierTree {...defaultProps} dossiers={dossiers} />)

      expect(screen.getByText('🔒')).toBeInTheDocument()
    })
  })

  describe('Sélection de dossiers', () => {
    it('appelle onSelectDossier au clic sur un dossier', async () => {
      const user = userEvent.setup()
      const dossiers = [createMockDossier({ id: 1, nom: 'Mon Dossier' })]
      render(<DossierTree {...defaultProps} dossiers={dossiers} />)

      await user.click(screen.getByText('Mon Dossier'))

      expect(mockOnSelectDossier).toHaveBeenCalledWith(dossiers[0])
    })

    it('applique un style au dossier sélectionné', () => {
      const dossiers = [createMockDossier({ id: 1 })]
      const { container } = render(
        <DossierTree {...defaultProps} dossiers={dossiers} selectedDossierId={1} />
      )

      const selectedElement = container.querySelector('.bg-blue-50')
      expect(selectedElement).toBeInTheDocument()
    })
  })

  describe('Expansion/Collapse', () => {
    it('affiche le chevron pour les dossiers avec enfants', () => {
      const dossiers = [
        createMockDossier({
          id: 1,
          nom: 'Parent',
          children: [createMockDossier({ id: 2, nom: 'Enfant' })],
        }),
      ]
      render(<DossierTree {...defaultProps} dossiers={dossiers} />)

      expect(screen.getByText('▼')).toBeInTheDocument()
    })

    it('n\'affiche pas le chevron pour les dossiers sans enfants', () => {
      const dossiers = [createMockDossier({ children: [] })]
      render(<DossierTree {...defaultProps} dossiers={dossiers} />)

      expect(screen.queryByText('▼')).not.toBeInTheDocument()
      expect(screen.queryByText('▶')).not.toBeInTheDocument()
    })

    it('expand au niveau racine par défaut', () => {
      const dossiers = [
        createMockDossier({
          id: 1,
          nom: 'Parent',
          children: [createMockDossier({ id: 2, nom: 'Enfant' })],
        }),
      ]
      render(<DossierTree {...defaultProps} dossiers={dossiers} />)

      expect(screen.getByText('Enfant')).toBeInTheDocument()
    })

    it('permet de collapse un dossier', async () => {
      const user = userEvent.setup()
      const dossiers = [
        createMockDossier({
          id: 1,
          nom: 'Parent',
          children: [createMockDossier({ id: 2, nom: 'Enfant' })],
        }),
      ]
      render(<DossierTree {...defaultProps} dossiers={dossiers} />)

      // Cliquer sur le chevron pour collapse
      await user.click(screen.getByText('▼'))

      expect(screen.queryByText('Enfant')).not.toBeInTheDocument()
      expect(screen.getByText('▶')).toBeInTheDocument()
    })

    it('permet d\'expand un dossier collapsé', async () => {
      const user = userEvent.setup()
      const dossiers = [
        createMockDossier({
          id: 1,
          nom: 'Parent',
          children: [createMockDossier({ id: 2, nom: 'Enfant' })],
        }),
      ]
      render(<DossierTree {...defaultProps} dossiers={dossiers} />)

      // Collapse puis expand
      await user.click(screen.getByText('▼'))
      await user.click(screen.getByText('▶'))

      expect(screen.getByText('Enfant')).toBeInTheDocument()
    })
  })

  describe('Actions', () => {
    it('appelle onCreateDossier(null) au clic sur "Nouveau"', async () => {
      const user = userEvent.setup()
      render(<DossierTree {...defaultProps} onCreateDossier={mockOnCreateDossier} />)

      await user.click(screen.getByRole('button', { name: '+ Nouveau' }))

      expect(mockOnCreateDossier).toHaveBeenCalledWith(null)
    })

    it('appelle onCreateDossier avec parentId au clic sur "+" d\'un dossier', async () => {
      const user = userEvent.setup()
      const dossiers = [createMockDossier({ id: 5 })]
      render(
        <DossierTree
          {...defaultProps}
          dossiers={dossiers}
          onCreateDossier={mockOnCreateDossier}
        />
      )

      const addButton = screen.getByTitle('Créer un sous-dossier')
      await user.click(addButton)

      expect(mockOnCreateDossier).toHaveBeenCalledWith(5)
    })

    it('appelle onEditDossier au clic sur éditer', async () => {
      const user = userEvent.setup()
      const dossiers = [createMockDossier({ id: 1 })]
      render(
        <DossierTree {...defaultProps} dossiers={dossiers} onEditDossier={mockOnEditDossier} />
      )

      const editButton = screen.getByTitle('Modifier')
      await user.click(editButton)

      expect(mockOnEditDossier).toHaveBeenCalledWith(dossiers[0])
    })

    it('appelle onDeleteDossier au clic sur supprimer pour dossier custom', async () => {
      const user = userEvent.setup()
      const dossiers = [createMockDossier({ id: 1, type_dossier: 'custom' })]
      render(
        <DossierTree {...defaultProps} dossiers={dossiers} onDeleteDossier={mockOnDeleteDossier} />
      )

      const deleteButton = screen.getByTitle('Supprimer')
      await user.click(deleteButton)

      expect(mockOnDeleteDossier).toHaveBeenCalledWith(dossiers[0])
    })

    it('n\'affiche pas le bouton supprimer pour les dossiers système', () => {
      const dossiers = [createMockDossier({ type_dossier: '01_plans' })]
      render(
        <DossierTree {...defaultProps} dossiers={dossiers} onDeleteDossier={mockOnDeleteDossier} />
      )

      expect(screen.queryByTitle('Supprimer')).not.toBeInTheDocument()
    })
  })

  describe('Arborescence profonde', () => {
    it('affiche les sous-dossiers récursivement', () => {
      const dossiers = [
        createMockDossier({
          id: 1,
          nom: 'Niveau 1',
          children: [
            createMockDossier({
              id: 2,
              nom: 'Niveau 2',
              children: [
                createMockDossier({
                  id: 3,
                  nom: 'Niveau 3',
                }),
              ],
            }),
          ],
        }),
      ]
      render(<DossierTree {...defaultProps} dossiers={dossiers} />)

      expect(screen.getByText('Niveau 1')).toBeInTheDocument()
      expect(screen.getByText('Niveau 2')).toBeInTheDocument()
      // Niveau 2 n'est pas expanded par défaut (level > 0)
    })
  })

  describe('Isolation des clics', () => {
    it('ne sélectionne pas le dossier quand on clique sur le chevron', async () => {
      const user = userEvent.setup()
      const dossiers = [
        createMockDossier({
          id: 1,
          children: [createMockDossier({ id: 2 })],
        }),
      ]
      render(<DossierTree {...defaultProps} dossiers={dossiers} />)

      await user.click(screen.getByText('▼'))

      expect(mockOnSelectDossier).not.toHaveBeenCalled()
    })

    it('ne sélectionne pas le dossier quand on clique sur une action', async () => {
      const user = userEvent.setup()
      const dossiers = [createMockDossier({ id: 1 })]
      render(
        <DossierTree {...defaultProps} dossiers={dossiers} onEditDossier={mockOnEditDossier} />
      )

      await user.click(screen.getByTitle('Modifier'))

      expect(mockOnSelectDossier).not.toHaveBeenCalled()
    })
  })
})
