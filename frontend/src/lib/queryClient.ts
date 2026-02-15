/**
 * Configuration TanStack Query Client
 * Optimisation performance Phase 2 - Caching et invalidation intelligente
 * Performance 2.1.5 - Persistence localStorage
 */

import { QueryClient } from '@tanstack/react-query'

const CACHE_KEY = 'hub-chantier-query-cache'
const CACHE_MAX_AGE = 30 * 60 * 1000 // 30 minutes

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes - données considérées fraîches
      gcTime: 30 * 60 * 1000, // 30 minutes - conservation en cache (anciennement cacheTime)
      retry: 1, // 1 seul retry en cas d'échec
      refetchOnWindowFocus: false, // Pas de refetch au focus (PWA mobile)
    },
  },
})

/**
 * Restore cache from localStorage on startup (Performance 2.1.5)
 * Manual implementation without @tanstack/react-query-persist-client
 */
export function restoreQueryCache() {
  try {
    const cached = localStorage.getItem(CACHE_KEY)
    if (!cached) return

    const { timestamp, queries } = JSON.parse(cached)

    // Vérifie que le cache n'est pas trop vieux
    if (Date.now() - timestamp > CACHE_MAX_AGE) {
      localStorage.removeItem(CACHE_KEY)
      return
    }

    // Restaure les queries une par une
    if (queries && typeof queries === 'object') {
      Object.entries(queries).forEach(([queryKey, queryData]: [string, any]) => {
        if (queryData?.state?.data) {
          queryClient.setQueryData(JSON.parse(queryKey), queryData.state.data)
        }
      })
    }
  } catch (error) {
    // Erreur silencieuse - on continue sans cache
    console.warn('Failed to restore query cache from localStorage:', error)
    localStorage.removeItem(CACHE_KEY)
  }
}

/**
 * Persist cache to localStorage (Performance 2.1.5)
 * Appelé périodiquement et avant unload
 */
export function persistQueryCache() {
  try {
    const cache = queryClient.getQueryCache()
    const queries: Record<string, any> = {}

    // Sérialise uniquement les queries avec succès
    cache.getAll().forEach((query) => {
      if (query.state.status === 'success' && query.state.data) {
        const queryKey = JSON.stringify(query.queryKey)
        queries[queryKey] = {
          state: {
            data: query.state.data,
            dataUpdatedAt: query.state.dataUpdatedAt,
          },
        }
      }
    })

    localStorage.setItem(
      CACHE_KEY,
      JSON.stringify({
        timestamp: Date.now(),
        queries,
      })
    )
  } catch (error) {
    // Quota dépassé ou autre erreur - on ignore
    console.warn('Failed to persist query cache to localStorage:', error)
  }
}

// Restaure le cache au chargement
if (typeof window !== 'undefined') {
  restoreQueryCache()

  // Persiste le cache périodiquement (toutes les 30s)
  setInterval(persistQueryCache, 30 * 1000)

  // Persiste le cache avant déchargement de la page
  window.addEventListener('beforeunload', persistQueryCache)
}
