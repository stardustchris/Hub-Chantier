/**
 * useDevisList - Hook pour charger la liste des devis avec parametres
 * DEV-03: Liste et creation de devis
 */

import { useState, useCallback } from 'react'
import { devisService } from '../services/devis'
import { logger } from '../services/logger'
import type { Devis, DevisCreate } from '../types'

export interface UseDevisListParams {
  limit: number
  offset: number
  sort_by?: string
  sort_direction?: string
  search?: string
  statut?: string
  date_debut?: string
  date_fin?: string
  montant_min?: number
  montant_max?: number
}

export interface UseDevisListReturn {
  devisList: Devis[]
  total: number
  loading: boolean
  error: string | null
  loadDevis: (params: UseDevisListParams) => Promise<void>
  createDevis: (data: DevisCreate) => Promise<Devis>
}

export function useDevisList(): UseDevisListReturn {
  const [devisList, setDevisList] = useState<Devis[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadDevis = useCallback(async (params: UseDevisListParams) => {
    try {
      setLoading(true)
      setError(null)
      const result = await devisService.listDevis(params as Parameters<typeof devisService.listDevis>[0])
      setDevisList(result.items)
      setTotal(result.total)
    } catch (err) {
      const message = 'Erreur lors du chargement des devis'
      setError(message)
      logger.error('useDevisList loadDevis error', err, { context: 'useDevisList' })
    } finally {
      setLoading(false)
    }
  }, [])

  const createDevis = useCallback(async (data: DevisCreate): Promise<Devis> => {
    const created = await devisService.createDevis(data)
    return created
  }, [])

  return {
    devisList,
    total,
    loading,
    error,
    loadDevis,
    createDevis,
  }
}

export default useDevisList
