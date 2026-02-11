/**
 * LotBudgetaireModal - Modal de creation/edition d'un lot budgetaire (FIN-02)
 */

import { useState } from 'react'
import { X, Save, AlertCircle } from 'lucide-react'
import { financierService } from '../../services/financier'
import { useToast } from '../../contexts/ToastContext'
import { logger } from '../../services/logger'
import type { LotBudgetaire, LotBudgetaireCreate, UniteMesureFinancier } from '../../types'
import { UNITE_MESURE_FINANCIER_LABELS } from '../../types'
import { formatEUR } from '../../utils/format'

interface LotBudgetaireModalProps {
  budgetId: number
  lot?: LotBudgetaire
  onClose: () => void
  onSuccess: () => void
}

export default function LotBudgetaireModal({ budgetId, lot, onClose, onSuccess }: LotBudgetaireModalProps) {
  const { addToast } = useToast()
  const isEdit = !!lot

  const [formData, setFormData] = useState({
    code_lot: lot?.code_lot || '',
    libelle: lot?.libelle || '',
    unite: (lot?.unite || 'forfait') as UniteMesureFinancier,
    quantite_prevue: lot?.quantite_prevue ?? 1,
    prix_unitaire_ht: lot?.prix_unitaire_ht ?? 0,
    ordre: lot?.ordre ?? 0,
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const totalPrevu = formData.quantite_prevue * formData.prix_unitaire_ht

  const handleChange = (field: string, value: string | number) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    setError(null)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      if (!formData.code_lot.trim()) throw new Error('Le code lot est obligatoire')
      if (!formData.libelle.trim()) throw new Error('Le libelle est obligatoire')
      if (formData.quantite_prevue <= 0) throw new Error('La quantite doit etre positive')
      if (formData.prix_unitaire_ht < 0) throw new Error('Le prix unitaire ne peut pas etre negatif')

      if (isEdit && lot) {
        await financierService.updateLot(lot.id, {
          code_lot: formData.code_lot,
          libelle: formData.libelle,
          unite: formData.unite,
          quantite_prevue: formData.quantite_prevue,
          prix_unitaire_ht: formData.prix_unitaire_ht,
          ordre: formData.ordre,
        })
        addToast({ message: 'Lot mis a jour', type: 'success' })
      } else {
        const createData: LotBudgetaireCreate = {
          budget_id: budgetId,
          code_lot: formData.code_lot,
          libelle: formData.libelle,
          unite: formData.unite,
          quantite_prevue: formData.quantite_prevue,
          prix_unitaire_ht: formData.prix_unitaire_ht,
          ordre: formData.ordre,
        }
        await financierService.createLot(createData)
        addToast({ message: 'Lot cree', type: 'success' })
      }
      onSuccess()
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } }; message?: string }
      const message = error.response?.data?.detail || error.message || 'Une erreur est survenue'
      setError(message)
      logger.error('Erreur sauvegarde lot budgetaire', err, { context: 'LotBudgetaireModal' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">
            {isEdit ? 'Modifier le lot' : 'Nouveau lot budgetaire'}
          </h2>
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

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Code lot <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={formData.code_lot}
                onChange={(e) => handleChange('code_lot', e.target.value.toUpperCase())}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-mono"
                placeholder="LOT01"
                required
                disabled={loading}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Ordre
              </label>
              <input
                type="number"
                value={formData.ordre}
                onChange={(e) => handleChange('ordre', parseInt(e.target.value) || 0)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                min={0}
                disabled={loading}
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Libelle <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.libelle}
              onChange={(e) => handleChange('libelle', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Ex: Gros oeuvre"
              required
              disabled={loading}
            />
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Unite
              </label>
              <select
                value={formData.unite}
                onChange={(e) => handleChange('unite', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                disabled={loading}
              >
                {Object.entries(UNITE_MESURE_FINANCIER_LABELS).map(([key, label]) => (
                  <option key={key} value={key}>{label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Quantite <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                value={formData.quantite_prevue}
                onChange={(e) => handleChange('quantite_prevue', parseFloat(e.target.value) || 0)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                min={0}
                step="0.01"
                required
                disabled={loading}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                PU HT <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                value={formData.prix_unitaire_ht}
                onChange={(e) => handleChange('prix_unitaire_ht', parseFloat(e.target.value) || 0)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                min={0}
                step="0.01"
                required
                disabled={loading}
              />
            </div>
          </div>

          {/* Total prevu */}
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Total prevu HT</span>
              <span className="text-lg font-bold text-gray-900">{formatEUR(totalPrevu)}</span>
            </div>
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
              disabled={loading}
            >
              <Save size={18} />
              <span>{loading ? 'Enregistrement...' : isEdit ? 'Mettre a jour' : 'Creer'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
