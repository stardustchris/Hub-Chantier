/**
 * Tests pour TasksContext
 */

import { describe, it, expect, vi } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { TasksProvider, useTasks } from './TasksContext'
import type { Tache } from '../types'
import type { ReactNode } from 'react'

const mockTache: Tache = {
  id: 1,
  titre: 'Test tache',
  description: 'Description test',
  statut: 'a_faire',
  statut_display: 'A faire',
  statut_icon: '☐',
  ordre: 0,
  chantier_id: 1,
  quantite_realisee: 0,
  heures_realisees: 0,
  progression_heures: 0,
  progression_quantite: 0,
  couleur_progression: 'gris',
  couleur_hex: '#9E9E9E',
  est_terminee: false,
  est_en_retard: false,
  a_sous_taches: false,
  nombre_sous_taches: 0,
  nombre_sous_taches_terminees: 0,
  sous_taches: [],
  created_at: '2024-01-01',
  updated_at: '2024-01-01',
}

describe('TasksContext', () => {
  describe('useTasks without provider', () => {
    it('throws error when used outside TasksProvider', () => {
      // Capture console.error to suppress React error logging
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

      expect(() => {
        renderHook(() => useTasks())
      }).toThrow('useTasks must be used within a TasksProvider')

      consoleSpy.mockRestore()
    })
  })

  describe('TasksProvider', () => {
    const createWrapper = (props: {
      onToggleComplete: (tacheId: number, terminer: boolean) => void
      onEdit: (tache: Tache) => void
      onDelete: (tacheId: number) => void
      onAddSubtask: (parentId: number) => void
    }) => {
      return function Wrapper({ children }: { children: ReactNode }) {
        return <TasksProvider {...props}>{children}</TasksProvider>
      }
    }

    it('provides onToggleComplete callback', () => {
      const onToggleComplete = vi.fn()
      const onEdit = vi.fn()
      const onDelete = vi.fn()
      const onAddSubtask = vi.fn()

      const wrapper = createWrapper({ onToggleComplete, onEdit, onDelete, onAddSubtask })
      const { result } = renderHook(() => useTasks(), { wrapper })

      act(() => {
        result.current.onToggleComplete(1, true)
      })

      expect(onToggleComplete).toHaveBeenCalledWith(1, true)
    })

    it('provides onEdit callback', () => {
      const onToggleComplete = vi.fn()
      const onEdit = vi.fn()
      const onDelete = vi.fn()
      const onAddSubtask = vi.fn()

      const wrapper = createWrapper({ onToggleComplete, onEdit, onDelete, onAddSubtask })
      const { result } = renderHook(() => useTasks(), { wrapper })

      act(() => {
        result.current.onEdit(mockTache)
      })

      expect(onEdit).toHaveBeenCalledWith(mockTache)
    })

    it('provides onDelete callback', () => {
      const onToggleComplete = vi.fn()
      const onEdit = vi.fn()
      const onDelete = vi.fn()
      const onAddSubtask = vi.fn()

      const wrapper = createWrapper({ onToggleComplete, onEdit, onDelete, onAddSubtask })
      const { result } = renderHook(() => useTasks(), { wrapper })

      act(() => {
        result.current.onDelete(1)
      })

      expect(onDelete).toHaveBeenCalledWith(1)
    })

    it('provides onAddSubtask callback', () => {
      const onToggleComplete = vi.fn()
      const onEdit = vi.fn()
      const onDelete = vi.fn()
      const onAddSubtask = vi.fn()

      const wrapper = createWrapper({ onToggleComplete, onEdit, onDelete, onAddSubtask })
      const { result } = renderHook(() => useTasks(), { wrapper })

      act(() => {
        result.current.onAddSubtask(1)
      })

      expect(onAddSubtask).toHaveBeenCalledWith(1)
    })

    it('memoizes callbacks to prevent unnecessary re-renders', () => {
      const onToggleComplete = vi.fn()
      const onEdit = vi.fn()
      const onDelete = vi.fn()
      const onAddSubtask = vi.fn()

      const wrapper = createWrapper({ onToggleComplete, onEdit, onDelete, onAddSubtask })
      const { result, rerender } = renderHook(() => useTasks(), { wrapper })

      const firstToggle = result.current.onToggleComplete
      const firstEdit = result.current.onEdit
      const firstDelete = result.current.onDelete
      const firstAddSubtask = result.current.onAddSubtask

      // Rerender with same callbacks
      rerender()

      // Callbacks should be the same reference
      expect(result.current.onToggleComplete).toBe(firstToggle)
      expect(result.current.onEdit).toBe(firstEdit)
      expect(result.current.onDelete).toBe(firstDelete)
      expect(result.current.onAddSubtask).toBe(firstAddSubtask)
    })

    it('calls onToggleComplete with false to reopen task', () => {
      const onToggleComplete = vi.fn()
      const onEdit = vi.fn()
      const onDelete = vi.fn()
      const onAddSubtask = vi.fn()

      const wrapper = createWrapper({ onToggleComplete, onEdit, onDelete, onAddSubtask })
      const { result } = renderHook(() => useTasks(), { wrapper })

      act(() => {
        result.current.onToggleComplete(5, false)
      })

      expect(onToggleComplete).toHaveBeenCalledWith(5, false)
    })

    it('handles multiple callback invocations', () => {
      const onToggleComplete = vi.fn()
      const onEdit = vi.fn()
      const onDelete = vi.fn()
      const onAddSubtask = vi.fn()

      const wrapper = createWrapper({ onToggleComplete, onEdit, onDelete, onAddSubtask })
      const { result } = renderHook(() => useTasks(), { wrapper })

      act(() => {
        result.current.onToggleComplete(1, true)
        result.current.onToggleComplete(2, true)
        result.current.onDelete(3)
        result.current.onAddSubtask(4)
      })

      expect(onToggleComplete).toHaveBeenCalledTimes(2)
      expect(onDelete).toHaveBeenCalledTimes(1)
      expect(onAddSubtask).toHaveBeenCalledTimes(1)
    })

    it('works with complex tache objects', () => {
      const onToggleComplete = vi.fn()
      const onEdit = vi.fn()
      const onDelete = vi.fn()
      const onAddSubtask = vi.fn()

      const complexTache: Tache = {
        ...mockTache,
        sous_taches: [
          { ...mockTache, id: 2, parent_id: 1 },
          { ...mockTache, id: 3, parent_id: 1 },
        ],
      }

      const wrapper = createWrapper({ onToggleComplete, onEdit, onDelete, onAddSubtask })
      const { result } = renderHook(() => useTasks(), { wrapper })

      act(() => {
        result.current.onEdit(complexTache)
      })

      expect(onEdit).toHaveBeenCalledWith(complexTache)
      expect(onEdit.mock.calls[0][0].sous_taches).toHaveLength(2)
    })
  })
})
