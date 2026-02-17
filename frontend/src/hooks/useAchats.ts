/**
 * useAchats - Hook de données pour la gestion des achats
 * Extrait de AchatsPage pour respecter l'architecture Clean (pages -> hooks -> services)
 */

import { useState, useEffect, useCallback } from 'react'
import { financierService } from '../services/financier'
import { chantiersService } from '../services/chantiers'
import { logger } from '../services/logger'
import type { Achat, Chantier, Fournisseur, LotBudgetaire } from '../types'

export interface UseAchatsReturn {
  achats: Achat[]
  loading: boolean
  error: string
  chantiers: Chantier[]
  fournisseurs: Fournisseur[]
  lots: LotBudgetaire[]
  loadAchats: () => Promise<void>
  loadChantiers: () => Promise<void>
  loadModalData: (chantierId: number) => Promise<{ fournisseurs: Fournisseur[]; lots: LotBudgetaire[] }>
}

export function useAchats(statutFilter: string): UseAchatsReturn {
  const [achats, setAchats] = useState<Achat[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [chantiers, setChantiers] = useState<Chantier[]>([])
  const [fournisseurs, setFournisseurs] = useState<Fournisseur[]>([])
  const [lots, setLots] = useState<LotBudgetaire[]>([])

  const loadAchats = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const params: { statut?: string } = {}
      if (statutFilter !== 'tous') params.statut = statutFilter
      const data = await financierService.listAchats(params)
      setAchats(data.items)
    } catch (err) {
      logger.error('Erreur chargement achats', err, { context: 'useAchats' })
      setError('Erreur lors du chargement des achats')
    } finally {
      setLoading(false)
    }
  }, [statutFilter])

  const loadChantiers = useCallback(async () => {
    try {
      const data = await chantiersService.list({ size: 100 })
      setChantiers(data.items.filter((c) => c.statut !== 'ferme'))
    } catch (err) {
      logger.error('Erreur chargement chantiers', err, { context: 'useAchats' })
    }
  }, [])

  useEffect(() => {
    loadAchats()
    loadChantiers()
  }, [loadAchats, loadChantiers])

  const loadModalData = useCallback(
    async (chantierId: number): Promise<{ fournisseurs: Fournisseur[]; lots: LotBudgetaire[] }> => {
      try {
        const [fournData, budgetData] = await Promise.all([
          financierService.listFournisseurs(),
          financierService.getBudgetByChantier(chantierId).catch(() => null),
        ])
        const resolvedFournisseurs: Fournisseur[] = fournData.items || fournData
        let resolvedLots: LotBudgetaire[] = []
        if (budgetData) {
          resolvedLots = (await financierService.listLots(budgetData.id)) || []
        }
        setFournisseurs(resolvedFournisseurs)
        setLots(resolvedLots)
        return { fournisseurs: resolvedFournisseurs, lots: resolvedLots }
      } catch (err) {
        logger.error('Erreur chargement données modal', err, { context: 'useAchats' })
        return { fournisseurs: [], lots: [] }
      }
    },
    []
  )

  return {
    achats,
    loading,
    error,
    chantiers,
    fournisseurs,
    lots,
    loadAchats,
    loadChantiers,
    loadModalData,
  }
}
