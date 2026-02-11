/**
 * SituationCreateModal - Modal de creation d'une situation de travaux (FIN-07)
 *
 * Formulaire pour creer une nouvelle situation avec :
 * - Periode debut/fin
 * - Retenue de garantie et TVA
 * - Tableau des lots avec saisie de l'avancement %
 */

import { useState, useEffect } from 'react'
import { X, Save, AlertCircle, Loader2 } from 'lucide-react'
import { financierService } from '../../services/financier'
import { useToast } from '../../contexts/ToastContext'
import { logger } from '../../services/logger'
import type { SituationCreate, LotBudgetaire } from '../../types'
import { formatEUR } from '../../utils/format'

interface SituationCreateModalProps {
  chantierId: number
  budgetId: number
  onClose: () => void
  onSuccess: () => void
}

export default function SituationCreateModal({
  chantierId,
  budgetId,
  onClose,
  onSuccess,
}: SituationCreateModalProps) {
  const { addToast } = useToast()

  // Dates par defaut : 1er et dernier jour du mois en cours
  const today = new Date()
  const firstDay = new Date(today.getFullYear(), today.getMonth(), 1)
  const lastDay = new Date(today.getFullYear(), today.getMonth() + 1, 0)

  const [formData, setFormData] = useState({
    periode_debut: firstDay.toISOString().split('T')[0],
    periode_fin: lastDay.toISOString().split('T')[0],
    retenue_garantie_pct: 5.0,
    taux_tva: 20.0,
    notes: '',
  })

  const [lots, setLots] = useState<LotBudgetaire[]>([])
  const [avancements, setAvancements] = useState<Record<number, number>>({})
  const [loading, setLoading] = useState(false)
  const [loadingLots, setLoadingLots] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Charger les lots au montage
  useEffect(() => {
    const loadLots = async () => {
      try {
        setLoadingLots(true)
        const data = await financierService.listLots(budgetId)
        setLots(data)
        // Initialiser les avancements a 0
        const initialAvancements: Record<number, number> = {}
        data.forEach((lot) => {
          initialAvancements[lot.id] = 0
        })
        setAvancements(initialAvancements)
      } catch (err) {
        logger.error('Erreur chargement lots', err, { context: 'SituationCreateModal' })
        setError('Impossible de charger les lots budgetaires')
      } finally {
        setLoadingLots(false)
      }
    }

    loadLots()
  }, [budgetId])

  const handleChange = (field: string, value: string | number) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
    setError(null)
  }

  const handleAvancementChange = (lotId: number, value: number) => {
    setAvancements((prev) => ({ ...prev, [lotId]: value }))
    setError(null)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      // Validation
      if (!formData.periode_debut) throw new Error('La periode de debut est obligatoire')
      if (!formData.periode_fin) throw new Error('La periode de fin est obligatoire')
      if (new Date(formData.periode_debut) > new Date(formData.periode_fin)) {
        throw new Error('La periode de debut doit etre anterieure a la periode de fin')
      }

      // Construire les lignes (uniquement les lots avec avancement > 0)
      const lignes = Object.entries(avancements)
        .filter(([, avancement]) => avancement > 0)
        .map(([lotId, avancement]) => ({
          lot_budgetaire_id: parseInt(lotId),
          pourcentage_avancement: avancement,
        }))

      if (lignes.length === 0) {
        throw new Error('Vous devez saisir au moins un lot avec un avancement superieur a 0')
      }

      const createData: SituationCreate = {
        chantier_id: chantierId,
        budget_id: budgetId,
        periode_debut: formData.periode_debut,
        periode_fin: formData.periode_fin,
        lignes,
        retenue_garantie_pct: formData.retenue_garantie_pct,
        taux_tva: formData.taux_tva,
        notes: formData.notes || undefined,
      }

      await financierService.createSituation(createData)
      addToast({ message: 'Situation creee', type: 'success' })
      onSuccess()
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } }; message?: string }
      const message = error.response?.data?.detail || error.message || 'Une erreur est survenue'
      setError(message)
      logger.error('Erreur creation situation', err, { context: 'SituationCreateModal' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">Nouvelle situation de travaux</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600" disabled={loading}>
            <X size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3 flex items-start gap-2">
              <AlertCircle className="text-red-500 flex-shrink-0 mt-0.5" size={18} />
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          {/* Periode */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Periode debut <span className="text-red-500">*</span>
              </label>
              <input
                type="date"
                value={formData.periode_debut}
                onChange={(e) => handleChange('periode_debut', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
                disabled={loading}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Periode fin <span className="text-red-500">*</span>
              </label>
              <input
                type="date"
                value={formData.periode_fin}
                onChange={(e) => handleChange('periode_fin', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
                disabled={loading}
              />
            </div>
          </div>

          {/* Retenue de garantie / TVA */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Retenue de garantie %
              </label>
              <input
                type="number"
                value={formData.retenue_garantie_pct}
                onChange={(e) => handleChange('retenue_garantie_pct', parseFloat(e.target.value) || 0)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                min={0}
                max={5}
                step="0.01"
                disabled={loading}
              />
              <p className="text-xs text-gray-500 mt-1">Max 5% (Loi 71-584)</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Taux TVA %</label>
              <input
                type="number"
                value={formData.taux_tva}
                onChange={(e) => handleChange('taux_tva', parseFloat(e.target.value) || 0)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                min={0}
                max={100}
                step="0.01"
                disabled={loading}
              />
            </div>
          </div>

          {/* Notes */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
            <textarea
              value={formData.notes}
              onChange={(e) => handleChange('notes', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Notes sur cette situation..."
              rows={2}
              disabled={loading}
            />
          </div>

          {/* Tableau des lots */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Avancement par lot <span className="text-red-500">*</span>
            </label>

            {loadingLots ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="w-6 h-6 animate-spin text-blue-600" />
              </div>
            ) : lots.length === 0 ? (
              <div className="text-center py-8 text-gray-500 bg-gray-50 rounded-lg">
                Aucun lot budgetaire disponible
              </div>
            ) : (
              <div className="border border-gray-200 rounded-lg overflow-hidden">
                <div className="max-h-80 overflow-y-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-gray-50 sticky top-0">
                      <tr>
                        <th className="text-left px-3 py-2 font-medium text-gray-500">Code</th>
                        <th className="text-left px-3 py-2 font-medium text-gray-500">Libelle</th>
                        <th className="text-right px-3 py-2 font-medium text-gray-500">
                          Montant marche HT
                        </th>
                        <th className="text-right px-3 py-2 font-medium text-gray-500">
                          Avancement %
                        </th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {lots.map((lot) => (
                        <tr key={lot.id} className="hover:bg-gray-50">
                          <td className="px-3 py-2 font-mono text-gray-700">{lot.code_lot}</td>
                          <td className="px-3 py-2 text-gray-700">{lot.libelle}</td>
                          <td className="px-3 py-2 text-right text-gray-700">
                            {formatEUR(lot.total_prevu_ht)}
                          </td>
                          <td className="px-3 py-2 text-right">
                            <input
                              type="number"
                              value={avancements[lot.id] ?? 0}
                              onChange={(e) =>
                                handleAvancementChange(lot.id, parseFloat(e.target.value) || 0)
                              }
                              className="w-20 px-2 py-1 border border-gray-300 rounded text-right focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                              min={0}
                              max={100}
                              step="0.1"
                              disabled={loading}
                            />
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              disabled={loading}
            >
              Annuler
            </button>
            <button
              type="submit"
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
              disabled={loading || loadingLots}
            >
              <Save size={18} />
              <span>{loading ? 'Creation...' : 'Creer'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
