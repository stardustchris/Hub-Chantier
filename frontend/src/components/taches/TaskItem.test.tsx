/**
 * Tests unitaires pour TaskItem
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import TaskItem from './TaskItem'
import type { Tache } from '../../types'

// Mock du context TasksContext
const mockTasksContext = {
  onToggleComplete: vi.fn(),
  onEdit: vi.fn(),
  onDelete: vi.fn(),
  onAddSubtask: vi.fn(),
}

vi.mock('../../contexts/TasksContext', () => ({
  useTasks: () => mockTasksContext,
}))

const createMockTache = (overrides: Partial<Tache> = {}): Tache => ({
  id: 1,
  titre: 'Tache Test',
  description: 'Description de test',
  chantier_id: 1,
  est_terminee: false,
  est_en_retard: false,
  ordre: 1,
  couleur_progression: 'vert',
  heures_estimees: 10,
  heures_realisees: 5,
  quantite_estimee: 100,
  quantite_realisee: 50,
  unite_mesure: 'm2',
  nombre_sous_taches: 0,
  nombre_sous_taches_terminees: 0,
  ...overrides,
})

describe('TaskItem', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('rendering', () => {
    it('affiche le titre de la tache', () => {
      render(<TaskItem tache={createMockTache({ titre: 'Coulage dalle' })} />)
      expect(screen.getByText('Coulage dalle')).toBeInTheDocument()
    })

    it('affiche les heures estimees et realisees', () => {
      render(<TaskItem tache={createMockTache({ heures_estimees: 10, heures_realisees: 5 })} />)
      expect(screen.getByText(/5\.0\/10h/)).toBeInTheDocument()
    })

    it('affiche les quantites', () => {
      render(<TaskItem tache={createMockTache({ quantite_estimee: 100, quantite_realisee: 50, unite_mesure: 'm2' })} />)
      expect(screen.getByText(/50\.0\/100/)).toBeInTheDocument()
    })

    it('affiche une date d echeance si fournie', () => {
      const { container } = render(<TaskItem tache={createMockTache({ date_echeance: '2026-02-01' })} />)
      // Check for Calendar icon presence which indicates date is rendered
      expect(container.querySelector('.lucide-calendar')).toBeInTheDocument()
    })

    it('affiche le badge de sous-taches', () => {
      render(<TaskItem tache={createMockTache({
        nombre_sous_taches: 5,
        nombre_sous_taches_terminees: 2,
        sous_taches: [createMockTache({ id: 'sub-1' })],
      })} />)
      expect(screen.getByText('2/5')).toBeInTheDocument()
    })
  })

  describe('etat termine', () => {
    it('applique le style barre si termine', () => {
      render(<TaskItem tache={createMockTache({ est_terminee: true })} />)
      const titre = screen.getByText('Tache Test')
      expect(titre).toHaveClass('line-through')
    })

    it('applique l opacite si termine', () => {
      const { container } = render(<TaskItem tache={createMockTache({ est_terminee: true })} />)
      expect(container.querySelector('.opacity-60')).toBeInTheDocument()
    })
  })

  describe('retard', () => {
    it('applique le style rouge si en retard', () => {
      const { container } = render(<TaskItem tache={createMockTache({ est_en_retard: true, date_echeance: '2026-01-01' })} />)
      // Check that red styling is applied somewhere
      expect(container.querySelector('.text-red-500')).toBeInTheDocument()
    })
  })

  describe('interactions', () => {
    it('appelle onToggleComplete au clic sur checkbox', () => {
      render(<TaskItem tache={createMockTache()} />)

      fireEvent.click(screen.getByTitle(/Marquer termine/i))

      expect(mockTasksContext.onToggleComplete).toHaveBeenCalledWith('1', true)
    })

    it('appelle onToggleComplete pour decocher', () => {
      render(<TaskItem tache={createMockTache({ est_terminee: true })} />)

      fireEvent.click(screen.getByTitle(/Marquer a faire/i))

      expect(mockTasksContext.onToggleComplete).toHaveBeenCalledWith('1', false)
    })
  })

  describe('menu actions', () => {
    const openMenu = () => {
      // Find the menu button by looking for buttons and selecting the last one (menu button)
      const buttons = screen.getAllByRole('button')
      const menuButton = buttons[buttons.length - 1]
      fireEvent.click(menuButton)
    }

    it('affiche le menu au clic', () => {
      render(<TaskItem tache={createMockTache()} />)

      openMenu()

      expect(screen.getByText('Modifier')).toBeInTheDocument()
      expect(screen.getByText('Supprimer')).toBeInTheDocument()
      expect(screen.getByText('Ajouter sous-tache')).toBeInTheDocument()
    })

    it('appelle onEdit au clic sur Modifier', () => {
      render(<TaskItem tache={createMockTache()} />)

      openMenu()
      fireEvent.click(screen.getByText('Modifier'))

      expect(mockTasksContext.onEdit).toHaveBeenCalledWith(expect.objectContaining({ id: '1' }))
    })

    it('appelle onDelete au clic sur Supprimer', () => {
      render(<TaskItem tache={createMockTache()} />)

      openMenu()
      fireEvent.click(screen.getByText('Supprimer'))

      expect(mockTasksContext.onDelete).toHaveBeenCalledWith('1')
    })

    it('appelle onAddSubtask au clic sur Ajouter sous-tache', () => {
      render(<TaskItem tache={createMockTache()} />)

      openMenu()
      fireEvent.click(screen.getByText('Ajouter sous-tache'))

      expect(mockTasksContext.onAddSubtask).toHaveBeenCalledWith('1')
    })
  })

  describe('sous-taches', () => {
    it('affiche le chevron si a des sous-taches', () => {
      render(<TaskItem tache={createMockTache({
        sous_taches: [createMockTache({ id: 'sub-1', titre: 'Sous-tache 1' })],
      })} />)

      expect(screen.getByTitle(/Replier/i)).toBeInTheDocument()
    })

    it('affiche les sous-taches par defaut', () => {
      render(<TaskItem tache={createMockTache({
        sous_taches: [createMockTache({ id: 'sub-1', titre: 'Sous-tache visible' })],
      })} />)

      expect(screen.getByText('Sous-tache visible')).toBeInTheDocument()
    })

    it('masque les sous-taches au clic sur chevron', () => {
      render(<TaskItem tache={createMockTache({
        sous_taches: [createMockTache({ id: 'sub-1', titre: 'Sous-tache cachee' })],
      })} />)

      fireEvent.click(screen.getByTitle(/Replier/i))

      expect(screen.queryByText('Sous-tache cachee')).not.toBeInTheDocument()
    })

    it('affiche a nouveau au clic sur chevron', () => {
      render(<TaskItem tache={createMockTache({
        sous_taches: [createMockTache({ id: 'sub-1', titre: 'Sous-tache re-visible' })],
      })} />)

      fireEvent.click(screen.getByTitle(/Replier/i))
      fireEvent.click(screen.getByTitle(/Derouler/i))

      expect(screen.getByText('Sous-tache re-visible')).toBeInTheDocument()
    })
  })

  describe('drag and drop', () => {
    it('applique l opacite lors du dragging', () => {
      const { container } = render(<TaskItem tache={createMockTache()} isDragging />)
      expect(container.firstChild).toHaveClass('opacity-50')
    })

    it('affiche le grip handle si dragHandleProps fourni', () => {
      const { container } = render(<TaskItem tache={createMockTache()} dragHandleProps={{}} />)
      expect(container.querySelector('.lucide-grip-vertical')).toBeInTheDocument()
    })
  })

  describe('niveau d indentation', () => {
    it('applique le padding selon le niveau', () => {
      const { container } = render(<TaskItem tache={createMockTache()} level={2} />)
      const row = container.querySelector('[style*="padding-left"]')
      expect(row).toHaveStyle({ paddingLeft: '60px' }) // (2 * 24) + 12
    })
  })
})
