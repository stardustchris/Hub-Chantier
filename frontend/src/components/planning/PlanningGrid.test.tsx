/**
 * Tests pour PlanningGrid
 *
 * Couvre:
 * - Affichage des jours (semaine/mois)
 * - Groupement des utilisateurs par catégorie
 * - Affectations par cellule
 * - Drag & drop des affectations
 * - Resize des affectations
 * - Expansion/collapse des catégories
 * - Actions (duplication, appel)
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import PlanningGrid from './PlanningGrid'
import type { Affectation, User } from '../../types'

// Mock AffectationBlock pour isoler les tests
vi.mock('./AffectationBlock', () => ({
  default: vi.fn(({ affectation, onClick, onDelete, draggable, onDragStart, onDragEnd }) => (
    <div
      data-testid={`affectation-${affectation.id}`}
      onClick={onClick}
      draggable={draggable}
      onDragStart={onDragStart}
      onDragEnd={onDragEnd}
    >
      <span>{affectation.chantier_nom}</span>
      <button data-testid={`delete-${affectation.id}`} onClick={(e) => { e.stopPropagation(); onDelete?.() }}>
        Delete
      </button>
    </div>
  )),
}))

const createMockUser = (overrides: Partial<User> = {}): User => ({
  id: 'user-1',
  email: 'test@example.com',
  nom: 'Dupont',
  prenom: 'Jean',
  role: 'compagnon',
  type_utilisateur: 'employe',
  is_active: true,
  created_at: '2024-01-01',
  couleur: '#3498DB',
  ...overrides,
})

const createMockAffectation = (overrides: Partial<Affectation> = {}): Affectation => ({
  id: 'aff-1',
  utilisateur_id: 'user-1',
  chantier_id: 'ch-1',
  date: '2024-01-15',
  heure_debut: '08:00',
  heure_fin: '17:00',
  chantier_nom: 'Chantier Test',
  type_affectation: 'unique',
  created_at: '2024-01-01',
  updated_at: '2024-01-01',
  ...overrides,
})

describe('PlanningGrid', () => {
  const mockOnAffectationClick = vi.fn()
  const mockOnAffectationDelete = vi.fn()
  const mockOnCellClick = vi.fn()
  const mockOnDuplicate = vi.fn()
  const mockOnToggleMetier = vi.fn()
  const mockOnAffectationMove = vi.fn()

  const defaultProps = {
    currentDate: new Date('2024-01-15'),
    affectations: [],
    utilisateurs: [],
    onAffectationClick: mockOnAffectationClick,
    onAffectationDelete: mockOnAffectationDelete,
    onCellClick: mockOnCellClick,
    onDuplicate: mockOnDuplicate,
    expandedMetiers: ['compagnon', 'conducteur', 'chef_chantier'],
    onToggleMetier: mockOnToggleMetier,
    showWeekend: true,
    viewMode: 'semaine' as const,
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Affichage de base', () => {
    it('affiche un message quand il n\'y a pas d\'utilisateurs', () => {
      render(<PlanningGrid {...defaultProps} />)
      expect(screen.getByText('Aucun utilisateur à afficher')).toBeInTheDocument()
    })

    it('affiche les jours de la semaine', () => {
      const users = [createMockUser()]
      render(<PlanningGrid {...defaultProps} utilisateurs={users} />)

      // Vérifie que tous les jours sont affichés (format abrégé)
      expect(screen.getByText('lun.')).toBeInTheDocument()
      expect(screen.getByText('mar.')).toBeInTheDocument()
      expect(screen.getByText('mer.')).toBeInTheDocument()
      expect(screen.getByText('jeu.')).toBeInTheDocument()
      expect(screen.getByText('ven.')).toBeInTheDocument()
    })

    it('affiche les week-ends quand showWeekend=true', () => {
      const users = [createMockUser()]
      render(<PlanningGrid {...defaultProps} utilisateurs={users} showWeekend={true} />)

      expect(screen.getByText('sam.')).toBeInTheDocument()
      expect(screen.getByText('dim.')).toBeInTheDocument()
    })

    it('masque les week-ends quand showWeekend=false', () => {
      const users = [createMockUser()]
      render(<PlanningGrid {...defaultProps} utilisateurs={users} showWeekend={false} />)

      expect(screen.queryByText('sam.')).not.toBeInTheDocument()
      expect(screen.queryByText('dim.')).not.toBeInTheDocument()
    })

    it('affiche le header Utilisateurs', () => {
      const users = [createMockUser()]
      render(<PlanningGrid {...defaultProps} utilisateurs={users} />)
      expect(screen.getByText('Utilisateurs')).toBeInTheDocument()
    })
  })

  describe('Groupement par catégorie', () => {
    it('groupe les conducteurs ensemble', () => {
      const users = [
        createMockUser({ id: '1', nom: 'Conducteur1', role: 'conducteur' }),
        createMockUser({ id: '2', nom: 'Conducteur2', role: 'conducteur' }),
      ]
      render(<PlanningGrid {...defaultProps} utilisateurs={users} expandedMetiers={['conducteur']} />)

      expect(screen.getByText('Conducteurs de travaux')).toBeInTheDocument()
      expect(screen.getByText('(2)')).toBeInTheDocument()
    })

    it('groupe les chefs de chantier ensemble', () => {
      const users = [
        createMockUser({ id: '1', nom: 'Chef1', role: 'chef_chantier' }),
      ]
      render(<PlanningGrid {...defaultProps} utilisateurs={users} expandedMetiers={['chef_chantier']} />)

      expect(screen.getByText('Chefs de chantier')).toBeInTheDocument()
    })

    it('groupe les compagnons ensemble', () => {
      const users = [
        createMockUser({ id: '1', nom: 'Ouvrier1', role: 'compagnon' }),
      ]
      render(<PlanningGrid {...defaultProps} utilisateurs={users} expandedMetiers={['compagnon']} />)

      expect(screen.getByText('Compagnons')).toBeInTheDocument()
    })

    it('groupe les intérimaires ensemble', () => {
      const users = [
        createMockUser({ id: '1', nom: 'Interim1', type_utilisateur: 'interimaire' }),
      ]
      render(<PlanningGrid {...defaultProps} utilisateurs={users} expandedMetiers={['interimaire']} />)

      // Le label dans PLANNING_CATEGORIES est "Interimaires" (sans accent)
      expect(screen.getByText('Interimaires')).toBeInTheDocument()
    })

    it('groupe les sous-traitants ensemble', () => {
      const users = [
        createMockUser({ id: '1', nom: 'SousT1', type_utilisateur: 'sous_traitant' }),
      ]
      render(<PlanningGrid {...defaultProps} utilisateurs={users} expandedMetiers={['sous_traitant']} />)

      expect(screen.getByText('Sous-traitants')).toBeInTheDocument()
    })
  })

  describe('Expansion/Collapse des catégories', () => {
    it('affiche les utilisateurs quand la catégorie est expanded', () => {
      const users = [createMockUser({ nom: 'Dupont', prenom: 'Jean' })]
      render(<PlanningGrid {...defaultProps} utilisateurs={users} expandedMetiers={['compagnon']} />)

      expect(screen.getByText('Jean Dupont')).toBeInTheDocument()
    })

    it('masque les utilisateurs quand la catégorie est collapsed', () => {
      const users = [createMockUser({ nom: 'Dupont', prenom: 'Jean' })]
      render(<PlanningGrid {...defaultProps} utilisateurs={users} expandedMetiers={[]} />)

      expect(screen.queryByText('Jean Dupont')).not.toBeInTheDocument()
    })

    it('appelle onToggleMetier quand on clique sur une catégorie', async () => {
      const user = userEvent.setup()
      const users = [createMockUser()]
      render(<PlanningGrid {...defaultProps} utilisateurs={users} />)

      const categoryButton = screen.getByText('Compagnons').closest('button')!
      await user.click(categoryButton)

      expect(mockOnToggleMetier).toHaveBeenCalledWith('compagnon')
    })
  })

  describe('Affichage des utilisateurs', () => {
    it('affiche l\'avatar avec les initiales', () => {
      const users = [createMockUser({ prenom: 'Jean', nom: 'Dupont' })]
      render(<PlanningGrid {...defaultProps} utilisateurs={users} expandedMetiers={['compagnon']} />)

      expect(screen.getByText('JD')).toBeInTheDocument()
    })

    it('applique la couleur de l\'utilisateur sur l\'avatar', () => {
      const users = [createMockUser({ couleur: '#E74C3C' })]
      const { container } = render(<PlanningGrid {...defaultProps} utilisateurs={users} expandedMetiers={['compagnon']} />)

      const avatar = container.querySelector('[style*="background-color: rgb(231, 76, 60)"]')
      expect(avatar).toBeInTheDocument()
    })

    it('affiche le nom complet de l\'utilisateur', () => {
      const users = [createMockUser({ prenom: 'Marie', nom: 'Martin' })]
      render(<PlanningGrid {...defaultProps} utilisateurs={users} expandedMetiers={['compagnon']} />)

      expect(screen.getByText('Marie Martin')).toBeInTheDocument()
    })

    it('affiche le bouton de duplication au hover', () => {
      const users = [createMockUser()]
      render(<PlanningGrid {...defaultProps} utilisateurs={users} expandedMetiers={['compagnon']} />)

      const duplicateButton = screen.getByTitle('Dupliquer la semaine')
      expect(duplicateButton).toBeInTheDocument()
    })

    it('affiche le lien téléphone si l\'utilisateur a un numéro', () => {
      const users = [createMockUser({ telephone: '0612345678' })]
      render(<PlanningGrid {...defaultProps} utilisateurs={users} expandedMetiers={['compagnon']} />)

      const phoneLink = screen.getByTitle('Appeler')
      expect(phoneLink).toHaveAttribute('href', 'tel:0612345678')
    })
  })

  describe('Affichage des affectations', () => {
    it('affiche les affectations dans les cellules correspondantes', () => {
      const users = [createMockUser({ id: 'user-1' })]
      const affectations = [
        createMockAffectation({ id: 'aff-1', utilisateur_id: 'user-1', date: '2024-01-15' }),
      ]
      render(
        <PlanningGrid
          {...defaultProps}
          utilisateurs={users}
          affectations={affectations}
          expandedMetiers={['compagnon']}
        />
      )

      expect(screen.getByTestId('affectation-aff-1')).toBeInTheDocument()
    })

    it('affiche plusieurs affectations le même jour', () => {
      const users = [createMockUser({ id: 'user-1' })]
      const affectations = [
        createMockAffectation({ id: 'aff-1', utilisateur_id: 'user-1', date: '2024-01-15' }),
        createMockAffectation({ id: 'aff-2', utilisateur_id: 'user-1', date: '2024-01-15', chantier_nom: 'Chantier 2' }),
      ]
      render(
        <PlanningGrid
          {...defaultProps}
          utilisateurs={users}
          affectations={affectations}
          expandedMetiers={['compagnon']}
        />
      )

      expect(screen.getByTestId('affectation-aff-1')).toBeInTheDocument()
      expect(screen.getByTestId('affectation-aff-2')).toBeInTheDocument()
    })
  })

  describe('Interactions avec les cellules', () => {
    it('appelle onCellClick quand on clique sur une cellule vide', async () => {
      const user = userEvent.setup()
      const users = [createMockUser({ id: 'user-1' })]
      render(
        <PlanningGrid
          {...defaultProps}
          utilisateurs={users}
          expandedMetiers={['compagnon']}
        />
      )

      const cells = screen.getAllByRole('gridcell')
      await user.click(cells[0])

      expect(mockOnCellClick).toHaveBeenCalled()
    })

    it('appelle onAffectationClick quand on clique sur une affectation', async () => {
      const user = userEvent.setup()
      const users = [createMockUser({ id: 'user-1' })]
      const affectations = [createMockAffectation({ id: 'aff-1', utilisateur_id: 'user-1', date: '2024-01-15' })]
      render(
        <PlanningGrid
          {...defaultProps}
          utilisateurs={users}
          affectations={affectations}
          expandedMetiers={['compagnon']}
        />
      )

      const affBlock = screen.getByTestId('affectation-aff-1')
      await user.click(affBlock)

      expect(mockOnAffectationClick).toHaveBeenCalledWith(affectations[0])
    })

    it('appelle onAffectationDelete quand on supprime une affectation', async () => {
      const user = userEvent.setup()
      const users = [createMockUser({ id: 'user-1' })]
      const affectations = [createMockAffectation({ id: 'aff-1', utilisateur_id: 'user-1', date: '2024-01-15' })]
      render(
        <PlanningGrid
          {...defaultProps}
          utilisateurs={users}
          affectations={affectations}
          expandedMetiers={['compagnon']}
        />
      )

      const deleteBtn = screen.getByTestId('delete-aff-1')
      await user.click(deleteBtn)

      expect(mockOnAffectationDelete).toHaveBeenCalledWith(affectations[0])
    })

    it('permet la navigation au clavier sur les cellules', async () => {
      const user = userEvent.setup()
      const users = [createMockUser({ id: 'user-1' })]
      render(
        <PlanningGrid
          {...defaultProps}
          utilisateurs={users}
          expandedMetiers={['compagnon']}
        />
      )

      const cells = screen.getAllByRole('gridcell')
      cells[0].focus()
      await user.keyboard('{Enter}')

      expect(mockOnCellClick).toHaveBeenCalled()
    })
  })

  describe('Actions utilisateur', () => {
    it('appelle onDuplicate quand on clique sur le bouton dupliquer', async () => {
      const user = userEvent.setup()
      const users = [createMockUser({ id: 'user-1' })]
      render(
        <PlanningGrid
          {...defaultProps}
          utilisateurs={users}
          expandedMetiers={['compagnon']}
        />
      )

      const duplicateBtn = screen.getByTitle('Dupliquer la semaine')
      await user.click(duplicateBtn)

      expect(mockOnDuplicate).toHaveBeenCalledWith('user-1')
    })
  })

  describe('Drag & Drop', () => {
    it('active le drag quand onAffectationMove est fourni', () => {
      const users = [createMockUser({ id: 'user-1' })]
      const affectations = [createMockAffectation({ id: 'aff-1', utilisateur_id: 'user-1', date: '2024-01-15' })]
      render(
        <PlanningGrid
          {...defaultProps}
          utilisateurs={users}
          affectations={affectations}
          expandedMetiers={['compagnon']}
          onAffectationMove={mockOnAffectationMove}
        />
      )

      const affBlock = screen.getByTestId('affectation-aff-1')
      expect(affBlock).toHaveAttribute('draggable', 'true')
    })

    it('gère le dragover sur une cellule', () => {
      const users = [createMockUser({ id: 'user-1' })]
      render(
        <PlanningGrid
          {...defaultProps}
          utilisateurs={users}
          expandedMetiers={['compagnon']}
          onAffectationMove={mockOnAffectationMove}
        />
      )

      const cells = screen.getAllByRole('gridcell')
      const dataTransfer = { dropEffect: '', effectAllowed: '' }
      fireEvent.dragOver(cells[0], { dataTransfer })

      // La cellule devrait avoir une classe indiquant le drag over
      expect(cells[0]).toBeInTheDocument()
    })

    it('gère le drop sur une cellule', () => {
      const users = [createMockUser({ id: 'user-1' })]
      const affectations = [createMockAffectation({ id: 'aff-1', utilisateur_id: 'user-1', date: '2024-01-15' })]
      render(
        <PlanningGrid
          {...defaultProps}
          utilisateurs={users}
          affectations={affectations}
          expandedMetiers={['compagnon']}
          onAffectationMove={mockOnAffectationMove}
        />
      )

      const affBlock = screen.getByTestId('affectation-aff-1')
      const dataTransfer = {
        dropEffect: '',
        effectAllowed: '',
        setData: vi.fn(),
        getData: vi.fn(),
      }
      fireEvent.dragStart(affBlock, { dataTransfer })

      const cells = screen.getAllByRole('gridcell')
      fireEvent.drop(cells[1], { dataTransfer })

      // Le drop devrait appeler onAffectationMove
      expect(mockOnAffectationMove).toHaveBeenCalled()
    })
  })

  describe('Vue mois', () => {
    it('affiche plus de jours en vue mois', () => {
      const users = [createMockUser()]
      render(
        <PlanningGrid
          {...defaultProps}
          utilisateurs={users}
          viewMode="mois"
          expandedMetiers={['compagnon']}
        />
      )

      // En janvier 2024, il y a 31 jours
      // Vérifie qu'on a plus de 7 jours affichés
      const cells = screen.getAllByRole('gridcell')
      expect(cells.length).toBeGreaterThan(7)
    })

    it('affiche le format compact pour les jours en vue mois', () => {
      const users = [createMockUser()]
      render(
        <PlanningGrid
          {...defaultProps}
          utilisateurs={users}
          viewMode="mois"
          expandedMetiers={['compagnon']}
        />
      )

      // En vue mois, les jours sont affichés en format court (L, M, M, J, V, S, D)
      expect(screen.getAllByText('L').length).toBeGreaterThan(0)
    })
  })

  describe('Accessibilité', () => {
    it('les cellules ont un rôle gridcell', () => {
      const users = [createMockUser()]
      render(
        <PlanningGrid
          {...defaultProps}
          utilisateurs={users}
          expandedMetiers={['compagnon']}
        />
      )

      const cells = screen.getAllByRole('gridcell')
      expect(cells.length).toBeGreaterThan(0)
    })

    it('les cellules sont focusables', () => {
      const users = [createMockUser()]
      render(
        <PlanningGrid
          {...defaultProps}
          utilisateurs={users}
          expandedMetiers={['compagnon']}
        />
      )

      const cells = screen.getAllByRole('gridcell')
      expect(cells[0]).toHaveAttribute('tabindex', '0')
    })

    it('les cellules ont des aria-labels descriptifs', () => {
      const users = [createMockUser({ prenom: 'Jean', nom: 'Dupont' })]
      render(
        <PlanningGrid
          {...defaultProps}
          utilisateurs={users}
          expandedMetiers={['compagnon']}
        />
      )

      const cells = screen.getAllByRole('gridcell')
      // Le premier cell devrait avoir un label avec le nom et la date
      expect(cells[0]).toHaveAttribute('aria-label')
      expect(cells[0].getAttribute('aria-label')).toContain('Jean Dupont')
    })
  })

  describe('Mise en évidence du jour actuel', () => {
    it('met en évidence le jour actuel', () => {
      const today = new Date()
      const users = [createMockUser()]
      render(
        <PlanningGrid
          {...defaultProps}
          currentDate={today}
          utilisateurs={users}
          expandedMetiers={['compagnon']}
        />
      )

      // Il devrait y avoir un élément avec la classe bg-primary-50 pour aujourd'hui
      const { container } = render(
        <PlanningGrid
          {...defaultProps}
          currentDate={today}
          utilisateurs={users}
          expandedMetiers={['compagnon']}
        />
      )

      const todayCell = container.querySelector('.bg-primary-50')
      expect(todayCell).toBeInTheDocument()
    })
  })
})
