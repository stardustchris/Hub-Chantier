/**
 * Hook reutilisable pour les pages de liste
 * Gere: loading, pagination, search, filtres, CRUD
 */

import { useState, useCallback, useEffect, useRef } from 'react'
import { logger } from '../services/logger'

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

export interface ListParams {
  page?: number
  size?: number
  search?: string
  [key: string]: string | number | boolean | undefined
}

export interface UseListPageOptions<T, TCreate = Partial<T>> {
  /** Fonction pour charger les items */
  fetchItems: (params: ListParams) => Promise<PaginatedResponse<T>>
  /** Fonction pour creer un item (optionnel) */
  createItem?: (data: TCreate) => Promise<T>
  /** Fonction pour supprimer un item (optionnel) */
  deleteItem?: (id: string) => Promise<void>
  /** Taille de page par defaut */
  pageSize?: number
  /** Charger automatiquement au mount */
  autoLoad?: boolean
}

export interface UseListPageReturn<T, TCreate = Partial<T>> {
  // Data
  items: T[]
  totalItems: number
  totalPages: number

  // State
  isLoading: boolean
  error: string | null

  // Pagination
  page: number
  setPage: (page: number) => void

  // Search
  search: string
  setSearch: (search: string) => void

  // Filters (generic)
  filters: Record<string, string | number | boolean | undefined>
  setFilter: (key: string, value: string | number | boolean | undefined) => void
  clearFilters: () => void

  // Actions
  reload: () => Promise<void>
  create: TCreate extends never ? never : (data: TCreate) => Promise<T | null>
  remove: (id: string) => Promise<boolean>
}

export function useListPage<T, TCreate = Partial<T>>(
  options: UseListPageOptions<T, TCreate>
): UseListPageReturn<T, TCreate> {
  const {
    fetchItems,
    createItem,
    deleteItem,
    pageSize = 12,
    autoLoad = true,
  } = options

  // State
  const [items, setItems] = useState<T[]>([])
  const [totalItems, setTotalItems] = useState(0)
  const [totalPages, setTotalPages] = useState(1)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Pagination
  const [page, setPage] = useState(1)

  // Search
  const [search, setSearch] = useState('')

  // Filters
  const [filters, setFilters] = useState<Record<string, string | number | boolean | undefined>>({})

  // Refs pour eviter les double calls et appels concurrents
  const isMounted = useRef(true)
  const isLoadingRef = useRef(false)

  // Ref pour stocker fetchItems (evite les re-renders infinies)
  const fetchItemsRef = useRef(fetchItems)
  fetchItemsRef.current = fetchItems

  // Load items
  const reload = useCallback(async () => {
    // Eviter les appels concurrents
    if (!isMounted.current || isLoadingRef.current) return
    isLoadingRef.current = true

    setIsLoading(true)
    setError(null)

    try {
      const params: ListParams = {
        page,
        size: pageSize,
        search: search || undefined,
        ...filters,
      }

      const response = await fetchItemsRef.current(params)

      if (isMounted.current) {
        setItems(response.items)
        setTotalItems(response.total)
        setTotalPages(response.pages)
      }
    } catch (err) {
      if (isMounted.current) {
        const message = err instanceof Error ? err.message : 'Erreur de chargement'
        setError(message)
        logger.error('useListPage error', err, { context: 'useListPage' })
      }
    } finally {
      isLoadingRef.current = false
      if (isMounted.current) {
        setIsLoading(false)
      }
    }
  }, [page, pageSize, search, filters])

  // Create item
  const create = useCallback(async (data: TCreate): Promise<T | null> => {
    if (!createItem) {
      logger.warn('createItem not provided to useListPage')
      return null
    }

    try {
      const newItem = await createItem(data)
      await reload()
      return newItem
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erreur de creation'
      setError(message)
      logger.error('useListPage create error', err, { context: 'useListPage' })
      return null
    }
  }, [createItem, reload])

  // Delete item
  const remove = useCallback(async (id: string): Promise<boolean> => {
    if (!deleteItem) {
      logger.warn('deleteItem not provided to useListPage')
      return false
    }

    try {
      await deleteItem(id)
      await reload()
      return true
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erreur de suppression'
      setError(message)
      logger.error('useListPage delete error', err, { context: 'useListPage' })
      return false
    }
  }, [deleteItem, reload])

  // Set filter
  const setFilter = useCallback((key: string, value: string | number | boolean | undefined) => {
    setFilters(prev => ({
      ...prev,
      [key]: value,
    }))
    setPage(1) // Reset page when filter changes
  }, [])

  // Clear all filters
  const clearFilters = useCallback(() => {
    setFilters({})
    setSearch('')
    setPage(1)
  }, [])

  // Reset page when search changes
  const handleSetSearch = useCallback((newSearch: string) => {
    setSearch(newSearch)
    setPage(1)
  }, [])

  // Cleanup - doit être avant le chargement initial
  useEffect(() => {
    isMounted.current = true
    return () => {
      isMounted.current = false
    }
  }, [])

  // Charger quand les params changent
  useEffect(() => {
    if (autoLoad) {
      reload()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, pageSize, search, filters, autoLoad])

  return {
    // Data
    items,
    totalItems,
    totalPages,

    // State
    isLoading,
    error,

    // Pagination
    page,
    setPage,

    // Search
    search,
    setSearch: handleSetSearch,

    // Filters
    filters,
    setFilter,
    clearFilters,

    // Actions
    reload,
    create: create as UseListPageReturn<T, TCreate>['create'],
    remove,
  }
}

export default useListPage
