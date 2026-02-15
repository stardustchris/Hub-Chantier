/**
 * AchatModal - Modal de creation/edition d'un achat (FIN-05)
 *
 * Formulaire complet avec calcul temps reel du TTC.
 */

import { useState, useMemo } from 'react'
import { X, Save, AlertCircle } from 'lucide-react'
import { financierService } from '../../services/financier'
import type { AchatSuggestion } from '../../services/financier'
import { useToast } from '../../contexts/ToastContext'
import { logger } from '../../services/logger'
import AchatSuggestions from './AchatSuggestions'
import { useFocusTrap } from '../../hooks/useFocusTrap'
import type {
  Achat,
  AchatCreate,
  Fournisseur,
  LotBudgetaire,
  TypeAchat,
  UniteMesureFinancier,
} from '../../types'
import {
  TYPE_ACHAT_LABELS,
  UNITE_MESURE_FINANCIER_LABELS,
  TAUX_TVA_OPTIONS,
} from '../../types'
import { formatEUR } from '../../utils/format'

interface AchatModalProps {
  chantierId: number
  achat?: Achat
  fournisseurs: Fournisseur[]
  lots: LotBudgetaire[]
  onClose: () => void
  onSuccess: () => void
}

export default function AchatModal({
  chantierId,
  achat,
  fournisseurs,
  lots,
  onClose,
  onSuccess,
}: AchatModalProps) {
  const focusTrapRef = useFocusTrap({ enabled: true, onClose })
  const { addToast } = useToast()
  const isEdit = !!achat

  const [formData, setFormData] = useState({
    type_achat: (achat?.type_achat || 'materiau') as TypeAchat,
    fournisseur_id: achat?.fournisseur_id ?? (fournisseurs[0]?.id || 0),
    lot_budgetaire_id: achat?.lot_budgetaire_id ?? undefined as number | undefined,
    libelle: achat?.libelle || '',
    quantite: achat?.quantite ?? 1,
    unite: (achat?.unite || 'u') as UniteMesureFinancier,
    prix_unitaire_ht: achat?.prix_unitaire_ht ?? 0,
    taux_tva: achat?.taux_tva ?? 20,
    date_commande: achat?.date_commande || new Date().toISOString().split('T')[0],
    date_livraison_prevue: achat?.date_livraison_prevue || '',
    commentaire: achat?.commentaire || '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Calculs temps reel
  const totalHT = useMemo(() => formData.quantite * formData.prix_unitaire_ht, [formData.quantite, formData.prix_unitaire_ht])
  const montantTVA = useMemo(() => totalHT * (formData.taux_tva / 100), [totalHT, formData.taux_tva])
  const totalTTC = useMemo(() => totalHT + montantTVA, [totalHT, montantTVA])

  const handleChange = (field: string, value: string | number | undefined) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    setError(null)
  }

  const handleSuggestionSelect = (suggestion: AchatSuggestion) => {
    setFormData(prev => ({
      ...prev,
      libelle: suggestion.libelle,
      prix_unitaire_ht: parseFloat(suggestion.prix_unitaire_ht) || 0,
      unite: (suggestion.unite || prev.unite) as UniteMesureFinancier,
      type_achat: (suggestion.type_achat || prev.type_achat) as TypeAchat,
      fournisseur_id: suggestion.fournisseur_id ?? prev.fournisseur_id,
    }))
    setError(null)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      if (!formData.libelle.trim()) throw new Error('Le libelle est obligatoire')
      if (!formData.fournisseur_id) throw new Error('Le fournisseur est obligatoire')
      if (formData.quantite <= 0) throw new Error('La quantite doit etre positive')
      if (formData.prix_unitaire_ht < 0) throw new Error('Le prix unitaire ne peut pas etre negatif')

      if (isEdit && achat) {
        await financierService.updateAchat(achat.id, {
          type_achat: formData.type_achat,
          fournisseur_id: formData.fournisseur_id,
          lot_budgetaire_id: formData.lot_budgetaire_id,
          libelle: formData.libelle,
          quantite: formData.quantite,
          unite: formData.unite,
          prix_unitaire_ht: formData.prix_unitaire_ht,
          taux_tva: formData.taux_tva,
          date_commande: formData.date_commande,
          date_livraison_prevue: formData.date_livraison_prevue || undefined,
          commentaire: formData.commentaire || undefined,
        })
        addToast({ message: 'Achat mis a jour', type: 'success' })
      } else {
        const createData: AchatCreate = {
          chantier_id: chantierId,
          type_achat: formData.type_achat,
          fournisseur_id: formData.fournisseur_id,
          lot_budgetaire_id: formData.lot_budgetaire_id,
          libelle: formData.libelle,
          quantite: formData.quantite,
          unite: formData.unite,
          prix_unitaire_ht: formData.prix_unitaire_ht,
          taux_tva: formData.taux_tva,
          date_commande: formData.date_commande,
          date_livraison_prevue: formData.date_livraison_prevue || undefined,
          commentaire: formData.commentaire || undefined,
        }
        await financierService.createAchat(createData)
        addToast({ message: 'Achat cree', type: 'success' })
      }
      onSuccess()
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } }; message?: string }
      const message = error.response?.data?.detail || error.message || 'Une erreur est survenue'
      setError(message)
      logger.error('Erreur sauvegarde achat', err, { context: 'AchatModal' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div ref={focusTrapRef} className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">
            {isEdit ? 'Modifier l\'achat' : 'Nouvel achat'}
          </h2>
          <button onClick={onClose} className="text-gray-600 hover:text-gray-800" disabled={loading}>
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

          {/* Type + Fournisseur */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Type d'achat <span className="text-red-500">*</span>
              </label>
              <select
                value={formData.type_achat}
                onChange={(e) => handleChange('type_achat', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                disabled={loading}
              >
                {Object.entries(TYPE_ACHAT_LABELS).map(([key, label]) => (
                  <option key={key} value={key}>{label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Fournisseur <span className="text-red-500">*</span>
              </label>
              <select
                value={formData.fournisseur_id}
                onChange={(e) => handleChange('fournisseur_id', parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                disabled={loading}
                required
              >
                <option value={0} disabled>Choisir un fournisseur</option>
                {fournisseurs.map((f) => (
                  <option key={f.id} value={f.id}>{f.raison_sociale}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Lot budgetaire (optionnel) */}
          {lots.length > 0 && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Lot budgetaire (optionnel)
              </label>
              <select
                value={formData.lot_budgetaire_id ?? ''}
                onChange={(e) => handleChange('lot_budgetaire_id', e.target.value ? parseInt(e.target.value) : undefined)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                disabled={loading}
              >
                <option value="">Aucun lot</option>
                {lots.map((l) => (
                  <option key={l.id} value={l.id}>{l.code_lot} - {l.libelle}</option>
                ))}
              </select>
            </div>
          )}

          {/* Libelle avec autocomplete */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Libelle <span className="text-red-500">*</span>
            </label>
            <AchatSuggestions
              value={formData.libelle}
              onChange={(val) => handleChange('libelle', val)}
              onSelect={handleSuggestionSelect}
              disabled={loading}
              placeholder="Ex: Beton pret a l'emploi C25/30"
            />
          </div>

          {/* Quantite / Unite / PU HT */}
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Quantite <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                value={formData.quantite}
                onChange={(e) => handleChange('quantite', parseFloat(e.target.value) || 0)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                min={0}
                step="0.01"
                required
                disabled={loading}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Unite</label>
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

          {/* TVA */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Taux TVA</label>
            <select
              value={formData.taux_tva}
              onChange={(e) => handleChange('taux_tva', parseFloat(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              disabled={loading}
            >
              {TAUX_TVA_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </div>

          {/* Totaux */}
          <div className="bg-gray-50 rounded-lg p-4 space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">Total HT</span>
              <span className="font-medium">{formatEUR(totalHT)}</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">TVA ({formData.taux_tva}%)</span>
              <span className="font-medium">{formatEUR(montantTVA)}</span>
            </div>
            <div className="flex items-center justify-between text-base border-t pt-2">
              <span className="font-semibold text-gray-900">Total TTC</span>
              <span className="font-bold text-gray-900">{formatEUR(totalTTC)}</span>
            </div>
          </div>

          {/* Dates */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Date commande <span className="text-red-500">*</span>
              </label>
              <input
                type="date"
                value={formData.date_commande}
                onChange={(e) => handleChange('date_commande', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
                disabled={loading}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Date livraison prevue
              </label>
              <input
                type="date"
                value={formData.date_livraison_prevue}
                onChange={(e) => handleChange('date_livraison_prevue', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                disabled={loading}
              />
            </div>
          </div>

          {/* Commentaire */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Commentaire</label>
            <textarea
              value={formData.commentaire}
              onChange={(e) => handleChange('commentaire', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Notes sur cet achat..."
              rows={2}
              disabled={loading}
            />
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
