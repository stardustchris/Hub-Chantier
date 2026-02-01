/**
 * AffectationsBudgetPanel - Affectation des budgets aux taches (FIN-03)
 *
 * Affiche pour chaque lot budgetaire les taches affectees avec leur pourcentage
 * d'allocation. Permet de creer et supprimer des affectations.
 */

import { useState, useEffect, useCallback } from 'react'
import { Loader2, Plus, X, AlertTriangle } from 'lucide-react'
import { financierService } from '../../services/financier'
import { tachesService } from '../../services/taches'
import { logger } from '../../services/logger'
import { formatEUR } from './ChartTooltip'
import type {
  AffectationBudgetTache,
  LotBudgetaire,
  Tache,
} from '../../types'

interface AffectationsBudgetPanelProps {
  chantierId: number
  budgetId: number
}

interface AffectationFormData {
  lotId: number
  tacheId: string
  pourcentage: string
}

export default function AffectationsBudgetPanel({
  chantierId,
  budgetId,
}: AffectationsBudgetPanelProps) {
  const [affectations, setAffectations] = useState<AffectationBudgetTache[]>([])
  const [lots, setLots] = useState<LotBudgetaire[]>([])
  const [taches, setTaches] = useState<Tache[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [formVisible, setFormVisible] = useState<number | null>(null) // lotId or null
  const [formData, setFormData] = useState<AffectationFormData>({
    lotId: 0,
    tacheId: '',
    pourcentage: '',
  })
  const [submitting, setSubmitting] = useState(false)
  const [deleteLoading, setDeleteLoading] = useState<number | null>(null)

  const loadData = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const [affectationsData, lotsData, tachesData] = await Promise.all([
        financierService.getAffectationsByChantier(chantierId),
        financierService.listLots(budgetId),
        tachesService.listByChantier(chantierId, { size: 200 }),
      ])
      setAffectations(affectationsData)
      setLots(lotsData)
      setTaches(tachesData.items)
    } catch (err) {
      setError('Erreur lors du chargement des affectations')
      logger.error('Erreur chargement affectations', err, { context: 'AffectationsBudgetPanel' })
    } finally {
      setLoading(false)
    }
  }, [chantierId, budgetId])

  useEffect(() => {
    loadData()
  }, [loadData])

  const getAffectationsForLot = useCallback(
    (lotId: number): AffectationBudgetTache[] => {
      return affectations.filter((a) => a.lot_budgetaire_id === lotId)
    },
    [affectations]
  )

  const getTotalPourcentage = useCallback(
    (lotId: number): number => {
      return getAffectationsForLot(lotId).reduce(
        (sum, a) => sum + Number(a.pourcentage_allocation),
        0
      )
    },
    [getAffectationsForLot]
  )

  const handleShowForm = useCallback((lotId: number) => {
    setFormVisible(lotId)
    setFormData({ lotId, tacheId: '', pourcentage: '' })
  }, [])

  const handleHideForm = useCallback(() => {
    setFormVisible(null)
    setFormData({ lotId: 0, tacheId: '', pourcentage: '' })
  }, [])

  const handleCreateAffectation = useCallback(async () => {
    const tacheId = parseInt(formData.tacheId, 10)
    const pourcentage = parseFloat(formData.pourcentage)

    if (isNaN(tacheId) || isNaN(pourcentage) || pourcentage <= 0 || pourcentage > 100) {
      return
    }

    try {
      setSubmitting(true)
      await financierService.createAffectation(formData.lotId, {
        tache_id: tacheId,
        pourcentage_allocation: pourcentage,
      })
      handleHideForm()
      await loadData()
    } catch (err) {
      logger.error('Erreur creation affectation', err, { context: 'AffectationsBudgetPanel' })
    } finally {
      setSubmitting(false)
    }
  }, [formData, handleHideForm, loadData])

  const handleDeleteAffectation = useCallback(
    async (affectationId: number) => {
      try {
        setDeleteLoading(affectationId)
        await financierService.deleteAffectation(affectationId)
        await loadData()
      } catch (err) {
        logger.error('Erreur suppression affectation', err, { context: 'AffectationsBudgetPanel' })
      } finally {
        setDeleteLoading(null)
      }
    },
    [loadData]
  )

  const getTacheLabel = useCallback(
    (tacheId: number): string => {
      const tache = taches.find((t) => t.id === tacheId)
      return tache ? tache.titre : `Tache #${tacheId}`
    },
    [taches]
  )

  if (loading) {
    return (
      <div className="flex items-center justify-center py-6">
        <Loader2
          className="w-6 h-6 animate-spin text-blue-600"
          aria-label="Chargement des affectations budget-taches"
        />
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-sm text-red-600 py-2" role="alert">
        {error}
      </div>
    )
  }

  if (lots.length === 0) {
    return (
      <p className="text-sm text-gray-400 py-2">
        Aucun lot budgetaire. Creez des lots pour affecter des taches.
      </p>
    )
  }

  return (
    <div
      className="space-y-4"
      role="region"
      aria-label="Affectations budget-taches"
    >
      {lots.map((lot) => {
        const lotAffectations = getAffectationsForLot(lot.id)
        const totalPct = getTotalPourcentage(lot.id)
        const isOverAllocated = totalPct > 100

        return (
          <div
            key={lot.id}
            className="border border-gray-200 rounded-lg p-3"
          >
            {/* Header du lot */}
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs bg-gray-100 px-1.5 py-0.5 rounded">
                  {lot.code_lot}
                </span>
                <span className="text-sm font-medium text-gray-800">
                  {lot.libelle}
                </span>
              </div>
              <span className="text-xs text-gray-500">
                {formatEUR(Number(lot.total_prevu_ht))}
              </span>
            </div>

            {/* Barre de progression */}
            <div className="mb-2">
              <div className="flex items-center gap-2 mb-1">
                <div className="flex-1 bg-gray-100 rounded-full h-2 overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all ${
                      isOverAllocated
                        ? 'bg-red-500'
                        : totalPct > 80
                          ? 'bg-orange-400'
                          : 'bg-blue-500'
                    }`}
                    style={{ width: `${Math.min(totalPct, 100)}%` }}
                  />
                </div>
                <span
                  className={`text-xs font-medium w-12 text-right ${
                    isOverAllocated ? 'text-red-600' : 'text-gray-600'
                  }`}
                >
                  {totalPct.toFixed(0)}%
                </span>
              </div>
              {isOverAllocated && (
                <div className="flex items-center gap-1 text-xs text-red-600">
                  <AlertTriangle size={12} />
                  <span>Allocation superieure a 100%</span>
                </div>
              )}
            </div>

            {/* Liste des affectations */}
            {lotAffectations.length > 0 && (
              <div className="space-y-1 mb-2">
                {lotAffectations.map((affectation) => (
                  <div
                    key={affectation.id}
                    className="flex items-center justify-between bg-gray-50 rounded px-2 py-1.5 text-sm"
                  >
                    <span className="text-gray-700 truncate flex-1">
                      {getTacheLabel(affectation.tache_id)}
                    </span>
                    <div className="flex items-center gap-2 flex-shrink-0 ml-2">
                      <span className="text-xs font-medium text-gray-600">
                        {Number(affectation.pourcentage_allocation).toFixed(0)}%
                      </span>
                      <button
                        onClick={() => handleDeleteAffectation(affectation.id)}
                        disabled={deleteLoading === affectation.id}
                        className="text-gray-400 hover:text-red-500 transition-colors disabled:opacity-50"
                        aria-label={`Supprimer l'affectation de ${getTacheLabel(affectation.tache_id)}`}
                      >
                        {deleteLoading === affectation.id ? (
                          <Loader2 size={14} className="animate-spin" />
                        ) : (
                          <X size={14} />
                        )}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Formulaire d'ajout */}
            {formVisible === lot.id ? (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 space-y-2">
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label
                      htmlFor={`tache-select-${lot.id}`}
                      className="block text-xs text-gray-600 mb-1"
                    >
                      Tache
                    </label>
                    <select
                      id={`tache-select-${lot.id}`}
                      value={formData.tacheId}
                      onChange={(e) =>
                        setFormData((prev) => ({ ...prev, tacheId: e.target.value }))
                      }
                      className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      aria-label="Selectionner une tache"
                    >
                      <option value="">-- Choisir --</option>
                      {taches.map((tache) => (
                        <option key={tache.id} value={tache.id}>
                          {tache.titre}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label
                      htmlFor={`pourcentage-input-${lot.id}`}
                      className="block text-xs text-gray-600 mb-1"
                    >
                      Pourcentage (%)
                    </label>
                    <input
                      id={`pourcentage-input-${lot.id}`}
                      type="number"
                      value={formData.pourcentage}
                      onChange={(e) =>
                        setFormData((prev) => ({ ...prev, pourcentage: e.target.value }))
                      }
                      min={0}
                      max={100}
                      step="0.1"
                      className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Ex: 25"
                      aria-label="Pourcentage d'allocation"
                    />
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={handleCreateAffectation}
                    disabled={submitting || !formData.tacheId || !formData.pourcentage}
                    className="px-3 py-1.5 text-xs bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
                    aria-label="Confirmer l'affectation"
                  >
                    {submitting ? 'Ajout...' : 'Ajouter'}
                  </button>
                  <button
                    onClick={handleHideForm}
                    className="px-3 py-1.5 text-xs text-gray-600 hover:text-gray-800 transition-colors"
                    aria-label="Annuler l'affectation"
                  >
                    Annuler
                  </button>
                </div>
              </div>
            ) : (
              <button
                onClick={() => handleShowForm(lot.id)}
                className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-700 transition-colors mt-1"
                aria-label={`Affecter une tache au lot ${lot.code_lot}`}
              >
                <Plus size={14} />
                Affecter une tache
              </button>
            )}
          </div>
        )
      })}
    </div>
  )
}
