/**
 * useDevisDashboard - Hook pour charger les donnees du dashboard pipeline commercial
 * DEV-17: Tableau de bord devis
 */

import { useState, useCallback } from 'react'
import { devisService } from '../services/devis'
import { logger } from '../services/logger'
import type { DashboardDevis } from '../types'

export interface UseDevisDashboardReturn {
  data: DashboardDevis | null
  loading: boolean
  error: string | null
  loadDashboard: () => Promise<void>
}

export function useDevisDashboard(): UseDevisDashboardReturn {
  const [data, setData] = useState<DashboardDevis | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadDashboard = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const dashboard = await devisService.getDashboard()
      setData(dashboard)
    } catch (err) {
      const message = 'Erreur lors du chargement du dashboard devis'
      setError(message)
      logger.error('useDevisDashboard loadDashboard error', err, { context: 'useDevisDashboard' })
    } finally {
      setLoading(false)
    }
  }, [])

  return {
    data,
    loading,
    error,
    loadDashboard,
  }
}

export default useDevisDashboard
