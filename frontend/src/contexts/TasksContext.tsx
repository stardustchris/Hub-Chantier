/**
 * TasksContext - Contexte pour gérer l'état et les actions des tâches
 * Élimine le props drilling dans TaskList/TaskItem (P1-6, P1-10)
 */

import { createContext, useContext, useCallback, useMemo, type ReactNode } from 'react'
import type { Tache } from '../types'

interface TasksContextValue {
  // Actions (memoized pour éviter re-renders - P1-7)
  onToggleComplete: (tacheId: number, terminer: boolean) => void
  onEdit: (tache: Tache) => void
  onDelete: (tacheId: number) => void
  onAddSubtask: (parentId: number) => void
}

const TasksContext = createContext<TasksContextValue | null>(null)

interface TasksProviderProps {
  children: ReactNode
  onToggleComplete: (tacheId: number, terminer: boolean) => void
  onEdit: (tache: Tache) => void
  onDelete: (tacheId: number) => void
  onAddSubtask: (parentId: number) => void
}

export function TasksProvider({
  children,
  onToggleComplete,
  onEdit,
  onDelete,
  onAddSubtask,
}: TasksProviderProps) {
  // Memoize les callbacks pour éviter les re-renders inutiles (P1-7)
  const memoizedToggle = useCallback(onToggleComplete, [onToggleComplete])
  const memoizedEdit = useCallback(onEdit, [onEdit])
  const memoizedDelete = useCallback(onDelete, [onDelete])
  const memoizedAddSubtask = useCallback(onAddSubtask, [onAddSubtask])

  const value = useMemo<TasksContextValue>(
    () => ({
      onToggleComplete: memoizedToggle,
      onEdit: memoizedEdit,
      onDelete: memoizedDelete,
      onAddSubtask: memoizedAddSubtask,
    }),
    [memoizedToggle, memoizedEdit, memoizedDelete, memoizedAddSubtask]
  )

  return <TasksContext.Provider value={value}>{children}</TasksContext.Provider>
}

export function useTasks(): TasksContextValue {
  const context = useContext(TasksContext)
  if (!context) {
    throw new Error('useTasks must be used within a TasksProvider')
  }
  return context
}

export { TasksContext }
