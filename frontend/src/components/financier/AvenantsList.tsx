/**
 * AvenantsList - Liste des avenants budgetaires (FIN-04)
 *
 * Affiche les avenants d'un budget avec :
 * - Colonnes: numero, motif, montant_ht (vert/rouge), statut badge, actions
 * - Modal de creation (motif, montant, impact)
 * - Actions: Valider, Supprimer (brouillon uniquement)
 */

import { useState, useEffect, useCallback } from 'react'
import { Plus, Loader2, Check, Trash2, X } from 'lucide-react'
import { financierService } from '../../services/financier'
import { useAuth } from '../../contexts/AuthContext'
import { logger } from '../../services/logger'
import type { AvenantBudgetaire, AvenantCreate } from '../../types'
import { STATUT_AVENANT_CONFIG } from '../../types'

interface AvenantsListProps {
  budgetId: number
}

const formatEUR = (value: number): string =>
  new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(value)

const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

export default function AvenantsList({ budgetId }: AvenantsListProps) {
  const { user } = useAuth()
  const [avenants, setAvenants] = useState<AvenantBudgetaire[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showModal, setShowModal] = useState(false)
  const [saving, setSaving] = useState(false)

  // Form state
  const [motif, setMotif] = useState('')
  const [montantHt, setMontantHt] = useState('')
  const [impactDescription, setImpactDescription] = useState('')

  const canManage = user?.role === 'admin' || user?.role === 'conducteur'

  const loadAvenants = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await financierService.listAvenants(budgetId)
      setAvenants(data)
    } catch (err) {
      setError('Erreur lors du chargement des avenants')
      logger.error('Erreur chargement avenants', err, { context: 'AvenantsList' })
    } finally {
      setLoading(false)
    }
  }, [budgetId])

  useEffect(() => {
    loadAvenants()
  }, [loadAvenants])

  const handleCreate = async () => {
    const montant = parseFloat(montantHt)
    if (!motif.trim() || isNaN(montant)) return

    try {
      setSaving(true)
      const data: AvenantCreate = {
        budget_id: budgetId,
        motif: motif.trim(),
        montant_ht: montant,
        impact_description: impactDescription.trim() || undefined,
      }
      await financierService.createAvenant(data)
      setShowModal(false)
      setMotif('')
      setMontantHt('')
      setImpactDescription('')
      await loadAvenants()
    } catch (err) {
      console.error('Erreur creation avenant:', err)
    } finally {
      setSaving(false)
    }
  }

  const handleValider = async (id: number) => {
    try {
      const updated = await financierService.validerAvenant(id)
      setAvenants(prev => prev.map(a => a.id === updated.id ? updated : a))
    } catch (err) {
      console.error('Erreur validation avenant:', err)
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Supprimer cet avenant ?')) return
    try {
      await financierService.deleteAvenant(id)
      setAvenants(prev => prev.filter(a => a.id !== id))
    } catch (err) {
      console.error('Erreur suppression avenant:', err)
    }
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

  return (
    <div className="bg-white border rounded-xl">
      <div className="flex items-center justify-between p-4 border-b">
        <h3 className="font-semibold text-gray-900">Avenants budgetaires</h3>
        {canManage && (
          <button
            onClick={() => setShowModal(true)}
            className="flex items-center gap-1 px-3 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm transition-colors"
          >
            <Plus size={14} />
            Nouvel avenant
          </button>
        )}
      </div>

      {avenants.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          Aucun avenant pour ce budget
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="text-left px-4 py-3 font-medium text-gray-500">Numero</th>
                <th className="text-left px-4 py-3 font-medium text-gray-500">Date</th>
                <th className="text-left px-4 py-3 font-medium text-gray-500">Motif</th>
                <th className="text-right px-4 py-3 font-medium text-gray-500">Montant HT</th>
                <th className="text-center px-4 py-3 font-medium text-gray-500">Statut</th>
                {canManage && (
                  <th className="text-center px-4 py-3 font-medium text-gray-500">Actions</th>
                )}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {avenants.map((avenant) => {
                const statutConfig = STATUT_AVENANT_CONFIG[avenant.statut]
                const isPositive = avenant.montant_ht >= 0
                return (
                  <tr key={avenant.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-mono text-gray-700">{avenant.numero}</td>
                    <td className="px-4 py-3 text-gray-500 whitespace-nowrap">
                      {formatDate(avenant.created_at)}
                    </td>
                    <td className="px-4 py-3 text-gray-700 max-w-[250px] truncate">
                      {avenant.motif}
                    </td>
                    <td className={`px-4 py-3 text-right font-medium whitespace-nowrap ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
                      {isPositive ? '+' : ''}{formatEUR(avenant.montant_ht)}
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span
                        className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium"
                        style={{
                          backgroundColor: statutConfig.couleur + '20',
                          color: statutConfig.couleur,
                        }}
                      >
                        {statutConfig.label}
                      </span>
                    </td>
                    {canManage && (
                      <td className="px-4 py-3 text-center">
                        {avenant.statut === 'brouillon' && (
                          <div className="flex items-center justify-center gap-1">
                            <button
                              onClick={() => handleValider(avenant.id)}
                              className="p-1 text-green-600 hover:bg-green-50 rounded"
                              title="Valider"
                            >
                              <Check size={16} />
                            </button>
                            <button
                              onClick={() => handleDelete(avenant.id)}
                              className="p-1 text-red-600 hover:bg-red-50 rounded"
                              title="Supprimer"
                            >
                              <Trash2 size={16} />
                            </button>
                          </div>
                        )}
                      </td>
                    )}
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Modal creation */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-lg">
            <div className="flex items-center justify-between p-4 border-b">
              <h3 className="font-semibold text-gray-900">Nouvel avenant</h3>
              <button onClick={() => setShowModal(false)} className="text-gray-400 hover:text-gray-600">
                <X size={20} />
              </button>
            </div>
            <div className="p-4 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Motif *</label>
                <textarea
                  value={motif}
                  onChange={(e) => setMotif(e.target.value)}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Motif de l'avenant..."
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Montant HT (EUR) *</label>
                <input
                  type="number"
                  value={montantHt}
                  onChange={(e) => setMontantHt(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Positif ou negatif"
                  step="0.01"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description de l'impact</label>
                <textarea
                  value={impactDescription}
                  onChange={(e) => setImpactDescription(e.target.value)}
                  rows={2}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Impact sur le budget..."
                />
              </div>
            </div>
            <div className="flex justify-end gap-2 p-4 border-t">
              <button
                onClick={() => setShowModal(false)}
                className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Annuler
              </button>
              <button
                onClick={handleCreate}
                disabled={saving || !motif.trim() || !montantHt}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
              >
                {saving ? 'Creation...' : 'Creer'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
