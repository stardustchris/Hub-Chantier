/**
 * Tests pour PlanningChantierGrid
 *
 * Couvre:
 * - Affichage des jours (semaine/mois)
 * - Affichage des chantiers triés
 * - Affectations par cellule
 * - Drag & drop des affectations
 * - Actions (duplication)
 * - Vue mois compacte
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import PlanningChantierGrid from './PlanningChantierGrid'
import type { Affectation, Chantier } from '../../types'

const createMockChantier = (overrides: Partial<Chantier> = {}): Chantier => ({
  id: 'ch-1',
  code: 'CH001',
  nom: 'Chantier Test',
  adresse: '123 Rue Test, Paris',
  statut: 'en_cours',
  couleur: '#E74C3C',
  conducteurs: [],
  chefs: [],
  created_at: '2024-01-01',
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
  chantier_couleur: '#E74C3C',
  utilisateur_nom: 'Jean Dupont',
  utilisateur_couleur: '#3498DB',
  type_affectation: 'unique',
  created_at: '2024-01-01',
  updated_at: '2024-01-01',
  created_by: 'user-1',
  ...overrides,
})

describe('PlanningChantierGrid', () => {
  const mockOnAffectationClick = vi.fn()
  const mockOnCellClick = vi.fn()
  const mockOnDuplicateChantier = vi.fn()
  const mockOnAffectationMove = vi.fn()

  const defaultProps = {
    currentDate: new Date('2024-01-15'),
    affectations: [],
    chantiers: [],
    onAffectationClick: mockOnAffectationClick,
    onCellClick: mockOnCellClick,
    onDuplicateChantier: mockOnDuplicateChantier,
    showWeekend: true,
    viewMode: 'semaine' as const,
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Affichage de base', () => {
    it('affiche un message quand il n\'y a pas de chantiers', () => {
      render(<PlanningChantierGrid {...defaultProps} />)
      expect(screen.getByText('Aucun chantier a afficher')).toBeInTheDocument()
    })

    it('affiche les jours de la semaine', () => {
      const chantiers = [createMockChantier()]
      render(<PlanningChantierGrid {...defaultProps} chantiers={chantiers} />)

      expect(screen.getByText('lun.')).toBeInTheDocument()
      expect(screen.getByText('mar.')).toBeInTheDocument()
      expect(screen.getByText('mer.')).toBeInTheDocument()
      expect(screen.getByText('jeu.')).toBeInTheDocument()
      expect(screen.getByText('ven.')).toBeInTheDocument()
    })

    it('affiche les week-ends quand showWeekend=true', () => {
      const chantiers = [createMockChantier()]
      render(<PlanningChantierGrid {...defaultProps} chantiers={chantiers} showWeekend={true} />)

      expect(screen.getByText('sam.')).toBeInTheDocument()
      expect(screen.getByText('dim.')).toBeInTheDocument()
    })

    it('masque les week-ends quand showWeekend=false', () => {
      const chantiers = [createMockChantier()]
      render(<PlanningChantierGrid {...defaultProps} chantiers={chantiers} showWeekend={false} />)

      expect(screen.queryByText('sam.')).not.toBeInTheDocument()
      expect(screen.queryByText('dim.')).not.toBeInTheDocument()
    })

    it('affiche le header Chantiers', () => {
      const chantiers = [createMockChantier()]
      render(<PlanningChantierGrid {...defaultProps} chantiers={chantiers} />)
      expect(screen.getByText('Chantiers')).toBeInTheDocument()
    })
  })

  describe('Affichage des chantiers', () => {
    it('affiche le code et le nom du chantier', () => {
      const chantiers = [createMockChantier({ code: 'CH123', nom: 'Mon Chantier' })]
      render(<PlanningChantierGrid {...defaultProps} chantiers={chantiers} />)

      expect(screen.getByText('CH123 - Mon Chantier')).toBeInTheDocument()
    })

    it('affiche le statut du chantier', () => {
      const chantiers = [createMockChantier({ statut: 'en_cours' })]
      render(<PlanningChantierGrid {...defaultProps} chantiers={chantiers} />)

      expect(screen.getByText('En cours')).toBeInTheDocument()
    })

    it('affiche l\'adresse du chantier', () => {
      const chantiers = [createMockChantier({ adresse: '456 Avenue Test' })]
      render(<PlanningChantierGrid {...defaultProps} chantiers={chantiers} />)

      expect(screen.getByText('456 Avenue Test')).toBeInTheDocument()
    })

    it('affiche les dates du chantier', () => {
      const chantiers = [
        createMockChantier({
          date_debut_prevue: '2024-03-01',
          date_fin_prevue: '2024-06-30',
        }),
      ]
      render(<PlanningChantierGrid {...defaultProps} chantiers={chantiers} />)

      expect(screen.getByText(/01\/03.*30\/06/)).toBeInTheDocument()
    })

    it('affiche le nombre d\'utilisateurs affectés', () => {
      const chantiers = [createMockChantier({ id: 'ch-1' })]
      const affectations = [
        createMockAffectation({ id: 'aff-1', chantier_id: 'ch-1', utilisateur_id: 'u1' }),
        createMockAffectation({ id: 'aff-2', chantier_id: 'ch-1', utilisateur_id: 'u2' }),
      ]
      render(<PlanningChantierGrid {...defaultProps} chantiers={chantiers} affectations={affectations} />)

      expect(screen.getByText('2')).toBeInTheDocument()
    })

    it('applique la couleur du chantier', () => {
      const chantiers = [createMockChantier({ couleur: '#FF5500' })]
      const { container } = render(<PlanningChantierGrid {...defaultProps} chantiers={chantiers} />)

      const colorIndicator = container.querySelector('[style*="background-color: rgb(255, 85, 0)"]')
      expect(colorIndicator).toBeInTheDocument()
    })
  })

  describe('Tri des chantiers', () => {
    it('trie les chantiers par statut puis par nom', () => {
      const chantiers = [
        createMockChantier({ id: 'ch-1', nom: 'Chantier B', statut: 'ferme' }),
        createMockChantier({ id: 'ch-2', nom: 'Chantier A', statut: 'en_cours' }),
        createMockChantier({ id: 'ch-3', nom: 'Chantier C', statut: 'en_cours' }),
      ]
      render(<PlanningChantierGrid {...defaultProps} chantiers={chantiers} />)

      const chantierNames = screen.getAllByText(/CH\d{3} - Chantier/)
      // en_cours avant ferme, puis alphabétique
      expect(chantierNames[0]).toHaveTextContent('Chantier A')
      expect(chantierNames[1]).toHaveTextContent('Chantier C')
      expect(chantierNames[2]).toHaveTextContent('Chantier B')
    })
  })

  describe('Affichage des affectations', () => {
    it('affiche les affectations dans les cellules correspondantes', () => {
      const chantiers = [createMockChantier({ id: 'ch-1' })]
      const affectations = [
        createMockAffectation({
          id: 'aff-1',
          chantier_id: 'ch-1',
          date: '2024-01-15',
          utilisateur_nom: 'Jean Dupont',
        }),
      ]
      render(
        <PlanningChantierGrid
          {...defaultProps}
          chantiers={chantiers}
          affectations={affectations}
        />
      )

      expect(screen.getByText('Jean Dupont')).toBeInTheDocument()
    })

    it('affiche les initiales de l\'utilisateur', () => {
      const chantiers = [createMockChantier({ id: 'ch-1' })]
      const affectations = [
        createMockAffectation({
          id: 'aff-1',
          chantier_id: 'ch-1',
          utilisateur_nom: 'Jean Dupont',
        }),
      ]
      render(
        <PlanningChantierGrid
          {...defaultProps}
          chantiers={chantiers}
          affectations={affectations}
        />
      )

      expect(screen.getByText('JD')).toBeInTheDocument()
    })

    it('affiche les horaires de l\'affectation', () => {
      const chantiers = [createMockChantier({ id: 'ch-1' })]
      const affectations = [
        createMockAffectation({
          id: 'aff-1',
          chantier_id: 'ch-1',
          date: '2024-01-15',
          heure_debut: '09:00',
          heure_fin: '18:00',
        }),
      ]
      render(
        <PlanningChantierGrid
          {...defaultProps}
          chantiers={chantiers}
          affectations={affectations}
        />
      )

      expect(screen.getByText('09:00 - 18:00')).toBeInTheDocument()
    })

    it('affiche plusieurs affectations le même jour', () => {
      const chantiers = [createMockChantier({ id: 'ch-1' })]
      const affectations = [
        createMockAffectation({
          id: 'aff-1',
          chantier_id: 'ch-1',
          date: '2024-01-15',
          utilisateur_nom: 'Jean Dupont',
        }),
        createMockAffectation({
          id: 'aff-2',
          chantier_id: 'ch-1',
          date: '2024-01-15',
          utilisateur_nom: 'Marie Martin',
        }),
      ]
      render(
        <PlanningChantierGrid
          {...defaultProps}
          chantiers={chantiers}
          affectations={affectations}
        />
      )

      expect(screen.getByText('Jean Dupont')).toBeInTheDocument()
      expect(screen.getByText('Marie Martin')).toBeInTheDocument()
    })
  })

  describe('Interactions avec les cellules', () => {
    it('appelle onCellClick quand on clique sur une cellule vide', async () => {
      const user = userEvent.setup()
      const chantiers = [createMockChantier({ id: 'ch-1' })]
      render(<PlanningChantierGrid {...defaultProps} chantiers={chantiers} />)

      const cells = screen.getAllByRole('gridcell')
      await user.click(cells[0])

      expect(mockOnCellClick).toHaveBeenCalled()
    })

    it('appelle onAffectationClick quand on clique sur une affectation', async () => {
      const user = userEvent.setup()
      const chantiers = [createMockChantier({ id: 'ch-1' })]
      const affectations = [
        createMockAffectation({
          id: 'aff-1',
          chantier_id: 'ch-1',
          date: '2024-01-15',
          utilisateur_nom: 'Jean Dupont',
        }),
      ]
      render(
        <PlanningChantierGrid
          {...defaultProps}
          chantiers={chantiers}
          affectations={affectations}
        />
      )

      await user.click(screen.getByText('Jean Dupont'))

      expect(mockOnAffectationClick).toHaveBeenCalledWith(affectations[0])
    })

    it('permet la navigation au clavier sur les cellules', async () => {
      const user = userEvent.setup()
      const chantiers = [createMockChantier({ id: 'ch-1' })]
      render(<PlanningChantierGrid {...defaultProps} chantiers={chantiers} />)

      const cells = screen.getAllByRole('gridcell')
      cells[0].focus()
      await user.keyboard('{Enter}')

      expect(mockOnCellClick).toHaveBeenCalled()
    })
  })

  describe('Actions chantier', () => {
    it('appelle onDuplicateChantier au clic sur le bouton dupliquer', async () => {
      const user = userEvent.setup()
      const chantiers = [createMockChantier({ id: 'ch-1' })]
      render(<PlanningChantierGrid {...defaultProps} chantiers={chantiers} />)

      const duplicateBtn = screen.getByTitle('Dupliquer les affectations vers la semaine suivante')
      await user.click(duplicateBtn)

      expect(mockOnDuplicateChantier).toHaveBeenCalledWith('ch-1')
    })
  })

  describe('Drag & Drop', () => {
    it('active le drag quand onAffectationMove est fourni', () => {
      const chantiers = [createMockChantier({ id: 'ch-1' })]
      const affectations = [
        createMockAffectation({
          id: 'aff-1',
          chantier_id: 'ch-1',
          date: '2024-01-15',
        }),
      ]
      render(
        <PlanningChantierGrid
          {...defaultProps}
          chantiers={chantiers}
          affectations={affectations}
          onAffectationMove={mockOnAffectationMove}
        />
      )

      const affBlock = screen.getByText('Jean Dupont').closest('[draggable]')
      expect(affBlock).toHaveAttribute('draggable', 'true')
    })

    it('gère le dragover sur une cellule', () => {
      const chantiers = [createMockChantier({ id: 'ch-1' })]
      render(
        <PlanningChantierGrid
          {...defaultProps}
          chantiers={chantiers}
          onAffectationMove={mockOnAffectationMove}
        />
      )

      const cells = screen.getAllByRole('gridcell')
      const dataTransfer = { dropEffect: '', effectAllowed: '' }
      fireEvent.dragOver(cells[0], { dataTransfer })

      expect(cells[0]).toBeInTheDocument()
    })

    it('gère le drop sur une cellule', () => {
      const chantiers = [createMockChantier({ id: 'ch-1' })]
      const affectations = [
        createMockAffectation({
          id: 'aff-1',
          chantier_id: 'ch-1',
          date: '2024-01-15',
        }),
      ]
      render(
        <PlanningChantierGrid
          {...defaultProps}
          chantiers={chantiers}
          affectations={affectations}
          onAffectationMove={mockOnAffectationMove}
        />
      )

      const affBlock = screen.getByText('Jean Dupont').closest('[draggable]')!
      const dataTransfer = {
        dropEffect: '',
        effectAllowed: '',
        setData: vi.fn(),
        getData: vi.fn(),
      }
      fireEvent.dragStart(affBlock, { dataTransfer })

      const cells = screen.getAllByRole('gridcell')
      fireEvent.drop(cells[1], { dataTransfer })

      expect(mockOnAffectationMove).toHaveBeenCalled()
    })
  })

  describe('Vue mois', () => {
    it('affiche plus de jours en vue mois', () => {
      const chantiers = [createMockChantier()]
      render(
        <PlanningChantierGrid
          {...defaultProps}
          chantiers={chantiers}
          viewMode="mois"
        />
      )

      // En janvier 2024, il y a 31 jours
      const cells = screen.getAllByRole('gridcell')
      expect(cells.length).toBeGreaterThan(7)
    })

    it('affiche le format compact pour les jours en vue mois', () => {
      const chantiers = [createMockChantier()]
      render(
        <PlanningChantierGrid
          {...defaultProps}
          chantiers={chantiers}
          viewMode="mois"
        />
      )

      // En vue mois, les jours sont affichés en format court (L, M, M, J, V, S, D)
      expect(screen.getAllByText('L').length).toBeGreaterThan(0)
    })
  })

  describe('Accessibilité', () => {
    it('les cellules ont un rôle gridcell', () => {
      const chantiers = [createMockChantier()]
      render(<PlanningChantierGrid {...defaultProps} chantiers={chantiers} />)

      const cells = screen.getAllByRole('gridcell')
      expect(cells.length).toBeGreaterThan(0)
    })

    it('les cellules sont focusables', () => {
      const chantiers = [createMockChantier()]
      render(<PlanningChantierGrid {...defaultProps} chantiers={chantiers} />)

      const cells = screen.getAllByRole('gridcell')
      expect(cells[0]).toHaveAttribute('tabindex', '0')
    })

    it('les cellules ont des aria-labels descriptifs', () => {
      const chantiers = [createMockChantier({ nom: 'Mon Chantier' })]
      render(<PlanningChantierGrid {...defaultProps} chantiers={chantiers} />)

      const cells = screen.getAllByRole('gridcell')
      expect(cells[0]).toHaveAttribute('aria-label')
      expect(cells[0].getAttribute('aria-label')).toContain('Mon Chantier')
    })
  })

  describe('Mise en évidence du jour actuel', () => {
    it('met en évidence le jour actuel', () => {
      const today = new Date()
      const chantiers = [createMockChantier()]
      const { container } = render(
        <PlanningChantierGrid
          {...defaultProps}
          currentDate={today}
          chantiers={chantiers}
        />
      )

      const todayCell = container.querySelector('.bg-primary-50')
      expect(todayCell).toBeInTheDocument()
    })
  })
})
