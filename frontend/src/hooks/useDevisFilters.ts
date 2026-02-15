/**
 * useDevisFilters - Hook pour gérer les filtres avancés et la recherche full-text
 * DEV-19: Recherche et filtres avancés
 * Persiste les filtres dans l'URL via query params
 */

import { useState, useCallback, useEffect, useMemo } from 'react'
import { useSearchParams } from 'react-router-dom'
import { devisService } from '../services/devis'
import type { Devis, StatutDevis } from '../types'
import { logger } from '../services/logger'

export interface DevisFilters {
  // Recherche full-text
  search?: string

  // Filtres combinables
  client_nom?: string
  statut?: StatutDevis
  date_min?: string
  date_max?: string
  montant_min?: number
  montant_max?: number
  commercial_id?: number
  lot?: string
  marge_min?: number
  marge_max?: number
}

export interface UseDevisFiltersReturn {
  // Data
  devis: Devis[]
  totalResults: number

  // State
  loading: boolean
  error: string | null

  // Filters
  filters: DevisFilters
  setFilter: <K extends keyof DevisFilters>(key: K, value: DevisFilters[K]) => void
  clearFilters: () => void
  hasActiveFilters: boolean
  activeFiltersCount: number

  // Pagination
  page: number
  pageSize: number
  totalPages: number
  setPage: (page: number) => void

  // Actions
  reload: () => Promise<void>
}

const DEFAULT_PAGE_SIZE = 20

export function useDevisFilters(): UseDevisFiltersReturn {
  const [searchParams, setSearchParams] = useSearchParams()
  const [devis, setDevis] = useState<Devis[]>([])
  const [totalResults, setTotalResults] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Lire les filtres depuis l'URL
  const filters = useMemo<DevisFilters>(() => ({
    search: searchParams.get('search') || undefined,
    client_nom: searchParams.get('client') || undefined,
    statut: (searchParams.get('statut') as StatutDevis) || undefined,
    date_min: searchParams.get('date_min') || undefined,
    date_max: searchParams.get('date_max') || undefined,
    montant_min: searchParams.get('montant_min') ? Number(searchParams.get('montant_min')) : undefined,
    montant_max: searchParams.get('montant_max') ? Number(searchParams.get('montant_max')) : undefined,
    commercial_id: searchParams.get('commercial_id') ? Number(searchParams.get('commercial_id')) : undefined,
    lot: searchParams.get('lot') || undefined,
    marge_min: searchParams.get('marge_min') ? Number(searchParams.get('marge_min')) : undefined,
    marge_max: searchParams.get('marge_max') ? Number(searchParams.get('marge_max')) : undefined,
  }), [searchParams])

  const page = Number(searchParams.get('page')) || 1
  const pageSize = Number(searchParams.get('pageSize')) || DEFAULT_PAGE_SIZE
  const totalPages = Math.ceil(totalResults / pageSize)

  // Compter les filtres actifs
  const activeFiltersCount = useMemo(() => {
    return Object.values(filters).filter(v => v !== undefined && v !== '').length
  }, [filters])

  const hasActiveFilters = activeFiltersCount > 0

  // Mettre à jour un filtre dans l'URL
  const setFilter = useCallback(<K extends keyof DevisFilters>(
    key: K,
    value: DevisFilters[K]
  ) => {
    setSearchParams(prev => {
      const newParams = new URLSearchParams(prev)

      if (value === undefined || value === '') {
        newParams.delete(key)
      } else {
        newParams.set(key, String(value))
      }

      // Reset page to 1 when filter changes
      newParams.set('page', '1')

      return newParams
    })
  }, [setSearchParams])

  // Effacer tous les filtres
  const clearFilters = useCallback(() => {
    setSearchParams({})
  }, [setSearchParams])

  // Changer de page
  const setPage = useCallback((newPage: number) => {
    setSearchParams(prev => {
      const newParams = new URLSearchParams(prev)
      newParams.set('page', String(newPage))
      return newParams
    })
  }, [setSearchParams])

  // Charger les devis avec les filtres actifs
  const reload = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      const result = await devisService.listDevis({
        limit: pageSize,
        offset: (page - 1) * pageSize,
        search: filters.search,
        client_nom: filters.client_nom,
        statut: filters.statut,
        date_min: filters.date_min,
        date_max: filters.date_max,
        montant_min: filters.montant_min,
        montant_max: filters.montant_max,
        commercial_id: filters.commercial_id,
      })

      setDevis(result.items)
      setTotalResults(result.total)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erreur lors du chargement des devis'
      setError(message)
      logger.error('useDevisFilters reload error', err, { context: 'useDevisFilters' })
    } finally {
      setLoading(false)
    }
  }, [filters, page, pageSize])

  // Charger au mount et quand les filtres/page changent
  useEffect(() => {
    reload()
  }, [reload])

  return {
    // Data
    devis,
    totalResults,

    // State
    loading,
    error,

    // Filters
    filters,
    setFilter,
    clearFilters,
    hasActiveFilters,
    activeFiltersCount,

    // Pagination
    page,
    pageSize,
    totalPages,
    setPage,

    // Actions
    reload,
  }
}

export default useDevisFilters
