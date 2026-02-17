/**
 * useBudgets - Hook de données pour la gestion des budgets par chantier
 * Extrait de BudgetsPage pour respecter l'architecture Clean (pages -> hooks -> services)
 */

import { useState, useEffect, useCallback } from 'react'
import { financierService } from '../services/financier'
import { chantiersService } from '../services/chantiers'
import { logger } from '../services/logger'
import type { Chantier, Budget } from '../types'

export interface BudgetKPI {
  montant_prevu: number
  montant_engage: number
  montant_realise: number
  pct_engage: number
  pct_realise: number
}

export interface BudgetChantier {
  chantier: Chantier
  kpi: BudgetKPI | null
}

export interface UseBudgetsReturn {
  budgetChantiers: BudgetChantier[]
  loading: boolean
  error: string | null
  loadData: () => Promise<void>
}

export function useBudgets(): UseBudgetsReturn {
  const [budgetChantiers, setBudgetChantiers] = useState<BudgetChantier[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadData = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      // Charger les chantiers
      const chantiersData = await chantiersService.list()
      const chantiersList: Chantier[] = Array.isArray(chantiersData)
        ? chantiersData
        : (chantiersData as { items?: Chantier[] }).items || []

      // Pour chaque chantier, tenter de charger le budget + achats
      const results: BudgetChantier[] = await Promise.all(
        chantiersList.map(async (chantier) => {
          try {
            const budget: Budget | null = await financierService.getBudgetByChantier(Number(chantier.id))
            if (!budget) return { chantier, kpi: null }

            const montant_prevu = Number(budget.montant_revise_ht || budget.montant_initial_ht || 0)

            // Charger les achats pour calculer engagé/réalisé
            let montant_engage = 0
            let montant_realise = 0
            try {
              const achatsData = await financierService.listAchats({ chantier_id: Number(chantier.id) })
              const achats = achatsData.items || []
              for (const a of achats) {
                const total = Number(a.quantite) * Number(a.prix_unitaire_ht)
                // Engagé = tout sauf "demande" et "refuse"
                if (!['demande', 'refuse'].includes(a.statut)) {
                  montant_engage += total
                }
                // Réalisé = livré
                if (a.statut === 'livre') {
                  montant_realise += total
                }
              }
            } catch {
              // Pas d'achats = 0
            }

            return {
              chantier,
              kpi: {
                montant_prevu,
                montant_engage,
                montant_realise,
                pct_engage: montant_prevu > 0 ? (montant_engage / montant_prevu) * 100 : 0,
                pct_realise: montant_prevu > 0 ? (montant_realise / montant_prevu) * 100 : 0,
              },
            }
          } catch {
            return { chantier, kpi: null }
          }
        })
      )

      setBudgetChantiers(results.filter((r) => r.kpi !== null))
    } catch (err) {
      logger.error('Erreur chargement budgets', err, { context: 'useBudgets' })
      setError('Impossible de charger les budgets')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadData()
  }, [loadData])

  return {
    budgetChantiers,
    loading,
    error,
    loadData,
  }
}
