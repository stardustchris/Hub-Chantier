/**
 * LotsBudgetairesTable - Table des lots budgetaires (FIN-02)
 *
 * Affiche les lots d'un budget avec :
 * - Colonnes: Code, Libelle, Unite, Qte, PU HT, Total, Engagé, Déboursé, Ecart
 * - Barre de progression par lot
 * - Actions CRUD (creation, edition, suppression)
 */

import { useState, useEffect } from 'react'
import { Plus, Pencil, Trash2, Loader2, HardHat } from 'lucide-react'
import { financierService } from '../../services/financier'
import { useAuth } from '../../contexts/AuthContext'
import { useToast } from '../../contexts/ToastContext'
import { logger } from '../../services/logger'
import LotBudgetaireModal from './LotBudgetaireModal'
import type { LotBudgetaire } from '../../types'
import { UNITE_MESURE_FINANCIER_LABELS } from '../../types'

interface LotsBudgetairesTableProps {
  budgetId: number
  onRefresh: () => void
}

const formatEUR = (value: number): string =>
  new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(value)

export default function LotsBudgetairesTable({ budgetId, onRefresh }: LotsBudgetairesTableProps) {
  const { user } = useAuth()
  const { addToast, showUndoToast } = useToast()
  const [lots, setLots] = useState<LotBudgetaire[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showModal, setShowModal] = useState(false)
  const [editingLot, setEditingLot] = useState<LotBudgetaire | undefined>(undefined)
  const [applyingTemplate, setApplyingTemplate] = useState(false)

  const canEdit = user?.role === 'admin' || user?.role === 'conducteur'

  useEffect(() => {
    loadLots()
  }, [budgetId])

  const loadLots = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await financierService.listLots(budgetId)
      setLots(data)
    } catch (err) {
      setError('Erreur lors du chargement des lots')
      logger.error('Erreur chargement lots', err, { context: 'LotsBudgetairesTable' })
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = (lot: LotBudgetaire) => {
    const lotName = `${lot.code_lot} - ${lot.libelle}`
    const originalLots = [...lots]
    setLots(prev => prev.filter(l => l.id !== lot.id))

    showUndoToast(
      `Lot "${lotName}" supprime`,
      () => {
        setLots(originalLots)
        addToast({ message: 'Suppression annulee', type: 'success', duration: 3000 })
      },
      async () => {
        try {
          await financierService.deleteLot(lot.id)
          onRefresh()
        } catch (err) {
          setLots(originalLots)
          logger.error('Erreur suppression lot', err, { context: 'LotsBudgetairesTable' })
          addToast({ message: 'Erreur lors de la suppression', type: 'error' })
        }
      },
      5000
    )
  }

  const handleApplyTemplateGO = async () => {
    try {
      setApplyingTemplate(true)
      await financierService.appliquerTemplateGO(budgetId)
      addToast({ message: 'Template Gros Oeuvre applique avec succes', type: 'success', duration: 4000 })
      loadLots()
      onRefresh()
    } catch (err) {
      logger.error('Erreur application template GO', err, { context: 'LotsBudgetairesTable' })
      addToast({ message: 'Erreur lors de l\'application du template', type: 'error' })
    } finally {
      setApplyingTemplate(false)
    }
  }

  const handleModalSuccess = () => {
    setShowModal(false)
    setEditingLot(undefined)
    loadLots()
    onRefresh()
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="w-6 h-6 animate-spin text-primary-600" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
        {error}
      </div>
    )
  }

  // Totaux
  const totalPrevu = lots.reduce((sum, l) => sum + l.total_prevu_ht, 0)
  const totalEngage = lots.reduce((sum, l) => sum + l.engage, 0)
  const totalRealise = lots.reduce((sum, l) => sum + l.realise, 0)

  return (
    <div className="bg-white border rounded-xl">
      <div className="flex items-center justify-between p-4 border-b">
        <h3 className="font-semibold text-gray-900">Lots budgetaires</h3>
        {canEdit && (
          <div className="flex items-center gap-2">
            <button
              onClick={handleApplyTemplateGO}
              disabled={applyingTemplate}
              className="flex items-center gap-2 px-3 py-1.5 bg-amber-600 text-white rounded-lg hover:bg-amber-700 text-sm transition-colors disabled:opacity-50"
            >
              {applyingTemplate ? <Loader2 size={16} className="animate-spin" /> : <HardHat size={16} />}
              Template Gros Oeuvre
            </button>
            <button
              onClick={() => { setEditingLot(undefined); setShowModal(true) }}
              className="flex items-center gap-2 px-3 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm transition-colors"
            >
              <Plus size={16} />
              Ajouter un lot
            </button>
          </div>
        )}
      </div>

      {lots.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          Aucun lot budgetaire. Cliquez sur "Ajouter un lot" pour commencer.
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="text-left px-4 py-3 font-medium text-gray-500">Code</th>
                <th className="text-left px-4 py-3 font-medium text-gray-500">Libelle</th>
                <th className="text-center px-4 py-3 font-medium text-gray-500">Unite</th>
                <th className="text-right px-4 py-3 font-medium text-gray-500">Qte</th>
                <th className="text-right px-4 py-3 font-medium text-gray-500">PU HT</th>
                <th className="text-right px-4 py-3 font-medium text-gray-500">Total prévu</th>
                <th className="text-right px-4 py-3 font-medium text-gray-500">Engagé</th>
                <th className="text-right px-4 py-3 font-medium text-gray-500">Déboursé</th>
                <th className="text-right px-4 py-3 font-medium text-gray-500">Écart</th>
                {canEdit && (
                  <th className="text-center px-4 py-3 font-medium text-gray-500">Actions</th>
                )}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {lots.map((lot) => {
                const pctEngage = lot.total_prevu_ht > 0 ? (lot.engage / lot.total_prevu_ht) * 100 : 0
                return (
                  <tr
                    key={lot.id}
                    className={`hover:bg-gray-50 ${canEdit ? 'cursor-pointer' : ''}`}
                    onClick={() => {
                      if (canEdit) {
                        setEditingLot(lot)
                        setShowModal(true)
                      }
                    }}
                  >
                    <td className="px-4 py-3">
                      <span className="font-mono text-xs bg-gray-100 px-1.5 py-0.5 rounded">
                        {lot.code_lot}
                      </span>
                    </td>
                    <td className="px-4 py-3 font-medium text-gray-900">{lot.libelle}</td>
                    <td className="px-4 py-3 text-center text-gray-500">
                      {UNITE_MESURE_FINANCIER_LABELS[lot.unite] || lot.unite}
                    </td>
                    <td className="px-4 py-3 text-right">{lot.quantite_prevue}</td>
                    <td className="px-4 py-3 text-right">{formatEUR(lot.prix_unitaire_ht)}</td>
                    <td className="px-4 py-3 text-right font-medium">{formatEUR(lot.total_prevu_ht)}</td>
                    <td className="px-4 py-3 text-right">
                      <div>
                        <span>{formatEUR(lot.engage)}</span>
                        <div className="w-full bg-gray-200 rounded-full h-1.5 mt-1">
                          <div
                            className={`h-1.5 rounded-full ${pctEngage > 90 ? 'bg-orange-500' : 'bg-blue-500'}`}
                            style={{ width: `${Math.min(pctEngage, 100)}%` }}
                          />
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-right">{formatEUR(lot.realise)}</td>
                    <td className={`px-4 py-3 text-right font-medium ${lot.ecart < 0 ? 'text-red-600' : 'text-green-600'}`}>
                      {formatEUR(lot.ecart)}
                    </td>
                    {canEdit && (
                      <td className="px-4 py-3 text-center">
                        <div className="flex items-center justify-center gap-1" onClick={(e) => e.stopPropagation()}>
                          <button
                            onClick={() => { setEditingLot(lot); setShowModal(true) }}
                            className="p-1.5 text-gray-400 hover:text-blue-600 rounded"
                            title="Modifier"
                          >
                            <Pencil size={14} />
                          </button>
                          <button
                            onClick={() => handleDelete(lot)}
                            className="p-1.5 text-gray-400 hover:text-red-600 rounded"
                            title="Supprimer"
                          >
                            <Trash2 size={14} />
                          </button>
                        </div>
                      </td>
                    )}
                  </tr>
                )
              })}
            </tbody>
            <tfoot className="bg-gray-50 font-medium">
              <tr>
                <td className="px-4 py-3" colSpan={5}>Total</td>
                <td className="px-4 py-3 text-right">{formatEUR(totalPrevu)}</td>
                <td className="px-4 py-3 text-right">{formatEUR(totalEngage)}</td>
                <td className="px-4 py-3 text-right">{formatEUR(totalRealise)}</td>
                <td className={`px-4 py-3 text-right ${(totalPrevu - totalEngage) < 0 ? 'text-red-600' : 'text-green-600'}`}>
                  {formatEUR(totalPrevu - totalEngage)}
                </td>
                {canEdit && <td />}
              </tr>
            </tfoot>
          </table>
        </div>
      )}

      {showModal && (
        <LotBudgetaireModal
          budgetId={budgetId}
          lot={editingLot}
          onClose={() => { setShowModal(false); setEditingLot(undefined) }}
          onSuccess={handleModalSuccess}
        />
      )}
    </div>
  )
}
