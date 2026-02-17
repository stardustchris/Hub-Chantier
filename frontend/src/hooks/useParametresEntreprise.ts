/**
 * useParametresEntreprise - Hook pour la gestion des parametres financiers de l'entreprise.
 *
 * Extrait de ParametresEntreprisePage la logique metier:
 * - Chargement de la configuration financiere de l'annee en cours
 * - Sauvegarde de la configuration via PUT /api/financier/configuration/:annee
 */

import { useState, useEffect, useCallback } from 'react'
import api from '../services/api'
import type { ApiError } from '../types/api'

export interface ConfigurationEntreprise {
  id: number
  couts_fixes_annuels: string
  annee: number
  coeff_frais_generaux: string
  coeff_charges_patronales: string
  coeff_heures_sup: string
  coeff_heures_sup_2: string
  coeff_productivite: string
  coeff_charges_ouvrier: string | null
  coeff_charges_etam: string | null
  coeff_charges_cadre: string | null
  seuil_alerte_budget_pct: string
  seuil_alerte_budget_critique_pct: string
  notes: string | null
  updated_at: string | null
  updated_by: number | null
  is_default?: boolean
  stale_warning?: string | null
}

export interface ConfigurationUpdateResponse extends ConfigurationEntreprise {
  created?: boolean
  warnings?: string[]
}

const CURRENT_YEAR = new Date().getFullYear()

export interface SaveConfigPayload {
  coutsFixesAnnuels: string
  coeffFraisGeneraux: string
  coeffChargesPatronales: string
  coeffHeuresSup: string
  coeffHeuresSup2: string
  coeffProductivite: string
  coeffChargesOuvrier: string
  coeffChargesEtam: string
  coeffChargesCadre: string
  seuilAlerteBudget: string
  seuilAlerteBudgetCritique: string
  notes: string
}

interface SaveConfigResult {
  success: boolean
  data?: ConfigurationUpdateResponse
  errorStatus?: number
  errorDetail?: string
}

interface UseParametresEntrepriseReturn {
  config: ConfigurationEntreprise | null
  isLoading: boolean
  isSaving: boolean
  currentYear: number
  loadConfig: () => Promise<{ isDefault?: boolean }>
  saveConfig: (payload: SaveConfigPayload) => Promise<SaveConfigResult>
}

export function useParametresEntreprise(): UseParametresEntrepriseReturn {
  const [config, setConfig] = useState<ConfigurationEntreprise | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)

  const loadConfig = useCallback(async (): Promise<{ isDefault?: boolean }> => {
    setIsLoading(true)
    try {
      const response = await api.get<ConfigurationEntreprise>(
        `/api/financier/configuration/${CURRENT_YEAR}`
      )
      setConfig(response.data)
      return { isDefault: response.data.is_default }
    } catch {
      return {}
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    loadConfig()
  }, [loadConfig])

  const saveConfig = useCallback(async (payload: SaveConfigPayload): Promise<SaveConfigResult> => {
    setIsSaving(true)
    try {
      const response = await api.put<ConfigurationUpdateResponse>(
        `/api/financier/configuration/${CURRENT_YEAR}`,
        {
          couts_fixes_annuels: parseFloat(payload.coutsFixesAnnuels),
          coeff_frais_generaux: parseFloat(payload.coeffFraisGeneraux),
          coeff_charges_patronales: parseFloat(payload.coeffChargesPatronales),
          coeff_heures_sup: parseFloat(payload.coeffHeuresSup),
          coeff_heures_sup_2: parseFloat(payload.coeffHeuresSup2),
          coeff_productivite: parseFloat(payload.coeffProductivite),
          coeff_charges_ouvrier: payload.coeffChargesOuvrier ? parseFloat(payload.coeffChargesOuvrier) : null,
          coeff_charges_etam: payload.coeffChargesEtam ? parseFloat(payload.coeffChargesEtam) : null,
          coeff_charges_cadre: payload.coeffChargesCadre ? parseFloat(payload.coeffChargesCadre) : null,
          seuil_alerte_budget_pct: parseFloat(payload.seuilAlerteBudget),
          seuil_alerte_budget_critique_pct: parseFloat(payload.seuilAlerteBudgetCritique),
          notes: payload.notes || null,
        }
      )
      setConfig(response.data)
      return { success: true, data: response.data }
    } catch (err) {
      const error = err as ApiError
      return {
        success: false,
        errorStatus: error.response?.status,
        errorDetail: error.response?.data?.detail,
      }
    } finally {
      setIsSaving(false)
    }
  }, [])

  return {
    config,
    isLoading,
    isSaving,
    currentYear: CURRENT_YEAR,
    loadConfig,
    saveConfig,
  }
}

export default useParametresEntreprise
