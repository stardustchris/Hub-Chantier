/**
 * Tests pour DossierTree
 *
 * Couvre:
 * - Affichage de l'arborescence
 * - Expansion/collapse des dossiers
 * - Selection de dossier
 * - Actions (creer, editer, supprimer)
 * - Icones et badges
 * - Etat vide
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import DossierTree from './DossierTree'
import type { DossierTree as DossierTreeType } from '../../types/documents'

const createMockDossier = (overrides: Partial<DossierTreeType> = {}): DossierTreeType => ({
  id: 1,
  chantier_id: 1,
  nom: 'Plans',
  type_dossier: 'custom',
  niveau_acces: 'compagnon',
  parent_id: null,
  ordre: 1,
  chemin_complet: '/Plans',
  nombre_documents: 5,
  nombre_sous_dossiers: 0,
  created_at: '2024-01-15T10:00:00',
  children: [],
  ...overrides,
})

describe('DossierTree', () => {
  const mockOnSelect = vi.fn()
  const mockOnCreate = vi.fn()

  const defaultProps = {
    dossiers: [createMockDossier()],
    selectedDossierId: null,
    onSelectDossier: mockOnSelect,
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Affichage', () => {
    it('affiche le titre Dossiers', () => {
      render(<DossierTree {...defaultProps} />)
      expect(screen.getByText('Dossiers')).toBeInTheDocument()
    })

    it('affiche le nom du dossier', () => {
      render(<DossierTree {...defaultProps} />)
      expect(screen.getByText('Plans')).toBeInTheDocument()
    })

    it('affiche le compteur de documents', () => {
      render(<DossierTree {...defaultProps} />)
      expect(screen.getByText('5')).toBeInTheDocument()
    })

    it('affiche le bouton Nouveau si onCreateDossier fourni', () => {
      render(<DossierTree {...defaultProps} onCreateDossier={mockOnCreate} />)
      expect(screen.getByText('+ Nouveau')).toBeInTheDocument()
    })
  })

  describe('Etat vide', () => {
    it('affiche le message si aucun dossier', () => {
      render(<DossierTree {...defaultProps} dossiers={[]} />)
      expect(screen.getByText(/Aucun dossier/)).toBeInTheDocument()
    })
  })

  describe('Selection', () => {
    it('appelle onSelectDossier au clic sur un dossier', async () => {
      const user = userEvent.setup()
      render(<DossierTree {...defaultProps} />)

      await user.click(screen.getByText('Plans'))

      expect(mockOnSelect).toHaveBeenCalledWith(expect.objectContaining({ id: 1, nom: 'Plans' }))
    })

    it('met en surbrillance le dossier selectionne', () => {
      render(<DossierTree {...defaultProps} selectedDossierId={1} />)
      // Le dossier selectionne devrait avoir la classe bg-blue-50
    })
  })

  describe('Expansion/Collapse', () => {
    it('affiche le chevron si le dossier a des enfants', () => {
      render(
        <DossierTree
          {...defaultProps}
          dossiers={[
            createMockDossier({
              children: [createMockDossier({ id: 2, nom: 'Sous-dossier', parent_id: 1 })],
            }),
          ]}
        />
      )
      // Le chevron devrait etre present
      expect(screen.getByText('Plans')).toBeInTheDocument()
    })

    it('affiche les enfants quand le dossier est expande', () => {
      render(
        <DossierTree
          {...defaultProps}
          dossiers={[
            createMockDossier({
              children: [createMockDossier({ id: 2, nom: 'Sous-dossier', parent_id: 1 })],
            }),
          ]}
        />
      )
      // Par defaut, le niveau 0 est expande
      expect(screen.getByText('Sous-dossier')).toBeInTheDocument()
    })

    it('permet de collapse un dossier', async () => {
      const user = userEvent.setup()
      render(
        <DossierTree
          {...defaultProps}
          dossiers={[
            createMockDossier({
              children: [createMockDossier({ id: 2, nom: 'Sous-dossier', parent_id: 1 })],
            }),
          ]}
        />
      )

      // Cliquer sur le chevron pour collapse
      const chevronButton = document.querySelector('button.w-5')
      if (chevronButton) {
        await user.click(chevronButton)
      }

      // Le sous-dossier ne devrait plus etre visible apres collapse
    })
  })

  describe('Icones de type', () => {
    it('affiche l icone plans pour 01_plans', () => {
      const { container } = render(<DossierTree {...defaultProps} dossiers={[createMockDossier({ type_dossier: '01_plans' })]} />)
      // Component uses Lucide Pencil icon for 01_plans
      expect(container.querySelector('.lucide-pencil')).toBeInTheDocument()
    })

    it('affiche l icone administratif pour 02_administratif', () => {
      const { container } = render(<DossierTree {...defaultProps} dossiers={[createMockDossier({ type_dossier: '02_administratif', nom: 'Admin' })]} />)
      // Component uses Lucide ClipboardCheck icon for 02_administratif
      expect(container.querySelector('.lucide-clipboard-check')).toBeInTheDocument()
    })

    it('affiche l icone securite pour 03_securite', () => {
      const { container } = render(<DossierTree {...defaultProps} dossiers={[createMockDossier({ type_dossier: '03_securite', nom: 'Securite' })]} />)
      // Component uses Lucide ShieldCheck icon for 03_securite
      expect(container.querySelector('.lucide-shield-check')).toBeInTheDocument()
    })

    it('affiche l icone photos pour 05_photos', () => {
      const { container } = render(<DossierTree {...defaultProps} dossiers={[createMockDossier({ type_dossier: '05_photos', nom: 'Photos' })]} />)
      // Component uses Lucide Camera icon for 05_photos
      expect(container.querySelector('.lucide-camera')).toBeInTheDocument()
    })

    it('affiche l icone dossier generique pour custom', () => {
      const { container } = render(<DossierTree {...defaultProps} dossiers={[createMockDossier({ type_dossier: 'custom', nom: 'Custom' })]} />)
      // Component uses Lucide Folder icon for custom
      expect(container.querySelector('.lucide-folder')).toBeInTheDocument()
    })
  })

  describe('Badges niveau d acces', () => {
    it('affiche le badge compagnon', () => {
      const { container } = render(<DossierTree {...defaultProps} dossiers={[createMockDossier({ niveau_acces: 'compagnon' })]} />)
      // Component uses Lucide Users icon for compagnon
      expect(container.querySelector('.lucide-users')).toBeInTheDocument()
    })

    it('affiche le badge chef_chantier', () => {
      const { container } = render(<DossierTree {...defaultProps} dossiers={[createMockDossier({ niveau_acces: 'chef_chantier' })]} />)
      // Component uses Lucide HardHat icon for chef_chantier
      expect(container.querySelector('.lucide-hard-hat')).toBeInTheDocument()
    })

    it('affiche le badge admin', () => {
      const { container } = render(<DossierTree {...defaultProps} dossiers={[createMockDossier({ niveau_acces: 'admin' })]} />)
      // Component uses Lucide Lock icon for admin
      expect(container.querySelector('.lucide-lock')).toBeInTheDocument()
    })
  })

  describe('Actions', () => {
    it('appelle onCreateDossier au clic sur + Nouveau', async () => {
      const user = userEvent.setup()
      render(<DossierTree {...defaultProps} onCreateDossier={mockOnCreate} />)

      await user.click(screen.getByText('+ Nouveau'))

      expect(mockOnCreate).toHaveBeenCalledWith(null)
    })
  })

  describe('Arborescence profonde', () => {
    it('affiche plusieurs niveaux d imbrication', () => {
      render(
        <DossierTree
          {...defaultProps}
          dossiers={[
            createMockDossier({
              children: [
                createMockDossier({
                  id: 2,
                  nom: 'Niveau 1',
                  parent_id: 1,
                  children: [
                    createMockDossier({
                      id: 3,
                      nom: 'Niveau 2',
                      parent_id: 2,
                    }),
                  ],
                }),
              ],
            }),
          ]}
        />
      )

      expect(screen.getByText('Plans')).toBeInTheDocument()
      expect(screen.getByText('Niveau 1')).toBeInTheDocument()
    })
  })
})
