/**
 * useDevisDetail - Hook pour charger et manipuler un devis en detail
 * DEV-03 / DEV-05 / DEV-06 / DEV-15 / DEV-16
 * Utilise par DevisDetailPage, DevisDetailPageEnhanced, DevisGeneratorPage et DevisPreviewPage
 */

import { useState, useCallback } from 'react'
import { devisService } from '../services/devis'
import { logger } from '../services/logger'
import type {
  DevisDetail,
  DevisCreate,
  DevisUpdate,
  LotDevisCreate,
  LotDevisUpdate,
  LigneDevisCreate,
  LigneDevisUpdate,
  ConvertirDevisResult,
} from '../types'

export interface UseDevisDetailReturn {
  devis: DevisDetail | null
  loading: boolean
  error: string | null

  // Chargement
  loadDevis: () => Promise<void>
  recalculerEtRecharger: () => Promise<void>

  // Edition
  updateDevis: (data: DevisCreate | DevisUpdate) => Promise<void>

  // Workflow
  soumettre: () => Promise<void>
  valider: () => Promise<void>
  retournerBrouillon: () => Promise<void>
  accepter: () => Promise<void>
  refuser: (motif: string) => Promise<void>
  marquerPerdu: (motif: string) => Promise<void>

  // Lots
  createLot: (data: LotDevisCreate) => Promise<void>
  updateLot: (lotId: number, data: LotDevisUpdate) => Promise<void>
  deleteLot: (lotId: number) => Promise<void>

  // Lignes
  createLigne: (data: LigneDevisCreate) => Promise<void>
  updateLigne: (ligneId: number, data: LigneDevisUpdate) => Promise<void>
  deleteLigne: (ligneId: number) => Promise<void>

  // Revision
  creerRevision: (commentaire?: string) => Promise<DevisDetail | null>

  // Conversion
  convertirEnChantier: (options?: { notify_client?: boolean; notify_team?: boolean }) => Promise<ConvertirDevisResult>

  // Calcul totaux
  calculerTotaux: () => Promise<void>
}

export function useDevisDetail(devisId: number): UseDevisDetailReturn {
  const [devis, setDevis] = useState<DevisDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadDevis = useCallback(async () => {
    if (!devisId || isNaN(devisId)) return
    try {
      setLoading(true)
      setError(null)
      const data = await devisService.getDevis(devisId)
      setDevis(data)
    } catch (err) {
      setError('Erreur lors du chargement du devis')
      logger.error('useDevisDetail loadDevis error', err, { context: 'useDevisDetail', devisId })
    } finally {
      setLoading(false)
    }
  }, [devisId])

  const calculerTotaux = useCallback(async () => {
    try {
      await devisService.calculerTotaux(devisId)
    } catch (err) {
      // Le recalcul peut echouer si le devis n'a pas de lignes, on continue
      logger.error('useDevisDetail calculerTotaux error', err, { context: 'useDevisDetail', devisId })
    }
  }, [devisId])

  const recalculerEtRecharger = useCallback(async () => {
    await calculerTotaux()
    await loadDevis()
  }, [calculerTotaux, loadDevis])

  const updateDevis = useCallback(async (data: DevisCreate | DevisUpdate) => {
    await devisService.updateDevis(devisId, data as DevisUpdate)
  }, [devisId])

  const soumettre = useCallback(async () => {
    await devisService.soumettreDevis(devisId)
    await loadDevis()
  }, [devisId, loadDevis])

  const valider = useCallback(async () => {
    await devisService.validerDevis(devisId)
    await loadDevis()
  }, [devisId, loadDevis])

  const retournerBrouillon = useCallback(async () => {
    await devisService.retournerBrouillon(devisId)
    await loadDevis()
  }, [devisId, loadDevis])

  const accepter = useCallback(async () => {
    await devisService.accepterDevis(devisId)
    await loadDevis()
  }, [devisId, loadDevis])

  const refuser = useCallback(async (motif: string) => {
    await devisService.refuserDevis(devisId, motif)
    await loadDevis()
  }, [devisId, loadDevis])

  const marquerPerdu = useCallback(async (motif: string) => {
    await devisService.marquerPerdu(devisId, motif)
    await loadDevis()
  }, [devisId, loadDevis])

  const createLot = useCallback(async (data: LotDevisCreate) => {
    await devisService.createLot(data)
  }, [])

  const updateLot = useCallback(async (lotId: number, data: LotDevisUpdate) => {
    await devisService.updateLot(lotId, data)
  }, [])

  const deleteLot = useCallback(async (lotId: number) => {
    await devisService.deleteLot(lotId)
  }, [])

  const createLigne = useCallback(async (data: LigneDevisCreate) => {
    await devisService.createLigne(data)
  }, [])

  const updateLigne = useCallback(async (ligneId: number, data: LigneDevisUpdate) => {
    await devisService.updateLigne(ligneId, data)
  }, [])

  const deleteLigne = useCallback(async (ligneId: number) => {
    await devisService.deleteLigne(ligneId)
  }, [])

  const creerRevision = useCallback(async (commentaire?: string): Promise<DevisDetail | null> => {
    try {
      const nouveau = await devisService.creerRevision(devisId, commentaire)
      return nouveau as unknown as DevisDetail
    } catch (err) {
      logger.error('useDevisDetail creerRevision error', err, { context: 'useDevisDetail', devisId })
      return null
    }
  }, [devisId])

  const convertirEnChantier = useCallback(async (
    options?: { notify_client?: boolean; notify_team?: boolean }
  ): Promise<ConvertirDevisResult> => {
    const result = await devisService.convertirEnChantier(devisId, options)
    await loadDevis()
    return result
  }, [devisId, loadDevis])

  return {
    devis,
    loading,
    error,
    loadDevis,
    recalculerEtRecharger,
    updateDevis,
    soumettre,
    valider,
    retournerBrouillon,
    accepter,
    refuser,
    marquerPerdu,
    createLot,
    updateLot,
    deleteLot,
    createLigne,
    updateLigne,
    deleteLigne,
    creerRevision,
    convertirEnChantier,
    calculerTotaux,
  }
}

export default useDevisDetail
