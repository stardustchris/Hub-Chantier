/**
 * useDevisKanban - Hook pour gérer le kanban des devis avec drag & drop
 * DEV-17: Tableau de bord devis (vue kanban)
 */

import { useState, useCallback, useEffect } from 'react'
import { devisService } from '../services/devis'
import type { DevisRecent, StatutDevis, DashboardDevis } from '../types'
import { logger } from '../services/logger'

export interface UseDevisKanbanReturn {
  // Data
  devis: DevisRecent[]
  kpi: DashboardDevis['kpi'] | null
  devisParStatut: Record<StatutDevis, number>

  // State
  loading: boolean
  error: string | null

  // Actions
  reload: () => Promise<void>
  moveDevis: (devisId: number, newStatut: StatutDevis) => Promise<boolean>

  // Filters
  filters: KanbanFilters
  setFilter: <K extends keyof KanbanFilters>(key: K, value: KanbanFilters[K]) => void
  clearFilters: () => void
  hasActiveFilters: boolean
}

export interface KanbanFilters {
  commercial_id?: number
  date_debut?: string
  date_fin?: string
  client_nom?: string
}

export function useDevisKanban(): UseDevisKanbanReturn {
  const [devis, setDevis] = useState<DevisRecent[]>([])
  const [kpi, setKpi] = useState<DashboardDevis['kpi'] | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filters, setFilters] = useState<KanbanFilters>({})

  // Calculer le nombre de devis par statut
  const devisParStatut: Record<StatutDevis, number> = {
    brouillon: kpi?.nb_brouillon || 0,
    en_validation: kpi?.nb_en_validation || 0,
    envoye: kpi?.nb_envoye || 0,
    vu: kpi?.nb_vu || 0,
    en_negociation: kpi?.nb_en_negociation || 0,
    accepte: kpi?.nb_accepte || 0,
    refuse: kpi?.nb_refuse || 0,
    perdu: kpi?.nb_perdu || 0,
    expire: kpi?.nb_expire || 0,
    converti: 0, // Non utilisé dans le kanban
  }

  const hasActiveFilters = Object.values(filters).some(v => v !== undefined && v !== '')

  // Charger le dashboard
  const reload = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      const dashboard = await devisService.getDashboard()
      setKpi(dashboard.kpi)

      // Si filtres actifs, charger avec filtres, sinon utiliser les derniers devis du dashboard
      if (hasActiveFilters) {
        const filtered = await devisService.listDevis({
          limit: 100,
          offset: 0,
          client_nom: filters.client_nom,
          date_min: filters.date_debut,
          date_max: filters.date_fin,
          commercial_id: filters.commercial_id,
        })
        setDevis(filtered.items as DevisRecent[])
      } else {
        setDevis(dashboard.derniers_devis)
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erreur lors du chargement du kanban'
      setError(message)
      logger.error('useDevisKanban reload error', err, { context: 'useDevisKanban' })
    } finally {
      setLoading(false)
    }
  }, [filters, hasActiveFilters])

  // Déplacer un devis vers un nouveau statut (drag & drop)
  const moveDevis = useCallback(async (devisId: number, newStatut: StatutDevis): Promise<boolean> => {
    try {
      // Transitions de statut autorisées via les endpoints appropriés
      const statusTransitions: Record<StatutDevis, () => Promise<unknown>> = {
        brouillon: () => devisService.retournerBrouillon(devisId),
        en_validation: () => devisService.soumettreDevis(devisId),
        envoye: () => devisService.validerDevis(devisId), // valider puis envoyer
        vu: () => Promise.resolve(), // Transition automatique côté backend
        en_negociation: () => Promise.resolve(), // Statut intermédiaire
        accepte: () => devisService.accepterDevis(devisId),
        refuse: () => devisService.refuserDevis(devisId, 'Refusé via kanban'),
        perdu: () => devisService.marquerPerdu(devisId, 'Perdu via kanban'),
        expire: () => Promise.resolve(), // Transition automatique
        converti: () => Promise.resolve(), // Non utilisé dans le kanban
      }

      const transition = statusTransitions[newStatut]
      if (!transition) {
        throw new Error(`Transition vers ${newStatut} non supportée`)
      }

      await transition()
      await reload()
      return true
    } catch (err) {
      logger.error('useDevisKanban moveDevis error', err, {
        context: 'useDevisKanban',
        devisId,
        newStatut,
      })
      return false
    }
  }, [reload])

  // Mettre à jour un filtre
  const setFilter = useCallback(<K extends keyof KanbanFilters>(
    key: K,
    value: KanbanFilters[K]
  ) => {
    setFilters(prev => ({
      ...prev,
      [key]: value,
    }))
  }, [])

  // Effacer tous les filtres
  const clearFilters = useCallback(() => {
    setFilters({})
  }, [])

  // Charger au mount et quand les filtres changent
  useEffect(() => {
    reload()
  }, [reload])

  return {
    // Data
    devis,
    kpi,
    devisParStatut,

    // State
    loading,
    error,

    // Actions
    reload,
    moveDevis,

    // Filters
    filters,
    setFilter,
    clearFilters,
    hasActiveFilters,
  }
}

export default useDevisKanban
