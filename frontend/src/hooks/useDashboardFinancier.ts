/**
 * useDashboardFinancier - Hook de données pour le dashboard financier consolidé
 * Extrait de DashboardFinancierPage pour respecter l'architecture Clean (pages -> hooks -> services)
 */

import { useState, useEffect, useCallback } from 'react'
import { financierService } from '../services/financier'
import { chantiersService } from '../services/chantiers'
import { logger } from '../services/logger'
import type { VueConsolidee } from '../types'

// Type local pour adapter l'interface de l'API à l'affichage
export interface AnalyseIADisplay {
  synthese: string
  alertes_prioritaires: string[]
  recommandations: string[]
  source: 'gemini-3-flash' | 'regles'
  ai_available: boolean
  tendance?: 'hausse' | 'stable' | 'baisse'
  score_sante?: number
}

export interface UseDashboardFinancierReturn {
  data: VueConsolidee | null
  loading: boolean
  error: string | null
  analyseIA: AnalyseIADisplay | null
  loadingIA: boolean
  loadData: () => Promise<void>
}

export function useDashboardFinancier(): UseDashboardFinancierReturn {
  const [data, setData] = useState<VueConsolidee | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [analyseIA, setAnalyseIA] = useState<AnalyseIADisplay | null>(null)
  const [loadingIA, setLoadingIA] = useState(false)

  // Charge l'analyse IA depuis Gemini 3 Flash (ou fallback règles)
  const loadAnalyseIA = useCallback(async (chantierIds: number[]) => {
    try {
      setLoadingIA(true)
      const analyse = await financierService.getAnalyseIAConsolidee(chantierIds)
      // Adapter la réponse API à l'interface d'affichage
      setAnalyseIA({
        synthese: analyse.synthese,
        alertes_prioritaires: analyse.alertes,
        recommandations: analyse.recommandations,
        source: analyse.source,
        ai_available: analyse.ai_available,
        tendance: analyse.tendance,
        score_sante: analyse.score_sante,
      })
    } catch (err) {
      logger.error('Erreur chargement analyse IA Gemini 3 Flash', err, { context: 'useDashboardFinancier' })
      // En cas d'erreur, pas d'analyse IA
      setAnalyseIA(null)
    } finally {
      setLoadingIA(false)
    }
  }, [])

  const loadData = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      // Charger la liste des chantiers pour obtenir les IDs
      const chantiersResponse = await chantiersService.list({ size: 100 })
      const chantierIds = chantiersResponse.items.map((c) => Number(c.id))

      if (chantierIds.length === 0) {
        setData({
          kpi_globaux: {
            total_budget_revise: 0,
            total_engage: 0,
            total_realise: 0,
            total_reste_a_depenser: 0,
            marge_moyenne_pct: 0,
            nb_chantiers: 0,
            nb_chantiers_ok: 0,
            nb_chantiers_attention: 0,
            nb_chantiers_depassement: 0,
          },
          chantiers: [],
          top_rentables: [],
          top_derives: [],
        })
        setAnalyseIA(null)
        return
      }

      const consolidation = await financierService.getConsolidation(chantierIds)
      setData(consolidation)

      // Charger l'analyse IA depuis Gemini 3 Flash en parallèle
      loadAnalyseIA(chantierIds)
    } catch (err) {
      setError('Erreur lors du chargement des donnees financieres')
      logger.error('Erreur chargement consolidation', err, { context: 'useDashboardFinancier' })
    } finally {
      setLoading(false)
    }
  }, [loadAnalyseIA])

  useEffect(() => {
    loadData()
  }, [loadData])

  return {
    data,
    loading,
    error,
    analyseIA,
    loadingIA,
    loadData,
  }
}
