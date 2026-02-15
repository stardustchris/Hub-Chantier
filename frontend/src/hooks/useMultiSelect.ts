import { useState, useCallback, useMemo } from 'react'

/**
 * Hook générique pour gérer la sélection multiple d'items
 * @template T - Type de l'ID (string ou number)
 */
export function useMultiSelect<T extends string | number>() {
  const [selectedIds, setSelectedIds] = useState<Set<T>>(new Set())

  /**
   * Bascule la sélection d'un item
   */
  const toggleItem = useCallback((id: T) => {
    setSelectedIds((prev) => {
      const next = new Set(prev)
      if (next.has(id)) {
        next.delete(id)
      } else {
        next.add(id)
      }
      return next
    })
  }, [])

  /**
   * Sélectionne tous les items fournis
   */
  const selectAll = useCallback((ids: T[]) => {
    setSelectedIds(new Set(ids))
  }, [])

  /**
   * Désélectionne tous les items
   */
  const deselectAll = useCallback(() => {
    setSelectedIds(new Set())
  }, [])

  /**
   * Vérifie si un item est sélectionné
   */
  const isSelected = useCallback(
    (id: T) => {
      return selectedIds.has(id)
    },
    [selectedIds]
  )

  /**
   * Nombre d'items sélectionnés
   */
  const count = useMemo(() => selectedIds.size, [selectedIds])

  /**
   * Array des IDs sélectionnés
   */
  const selectedArray = useMemo(() => Array.from(selectedIds), [selectedIds])

  return {
    selectedIds,
    selectedArray,
    count,
    toggleItem,
    selectAll,
    deselectAll,
    isSelected,
  }
}
