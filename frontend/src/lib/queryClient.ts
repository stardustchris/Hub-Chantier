/**
 * Configuration TanStack Query Client
 * Optimisation performance Phase 2 - Caching et invalidation intelligente
 */

import { QueryClient } from '@tanstack/react-query'

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
