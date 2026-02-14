/**
 * FournisseurModal - Modal de creation/edition d'un fournisseur (FIN-14)
 */

import { useState } from 'react'
import { X, Save, AlertCircle } from 'lucide-react'
import { financierService } from '../../services/financier'
import { useToast } from '../../contexts/ToastContext'
import { logger } from '../../services/logger'
import type { Fournisseur, FournisseurCreate, TypeFournisseur } from '../../types'
import { TYPE_FOURNISSEUR_LABELS } from '../../types'
import { useFocusTrap } from '../../hooks/useFocusTrap'

interface FournisseurModalProps {
  fournisseur?: Fournisseur
  onClose: () => void
  onSuccess: () => void
}

export default function FournisseurModal({ fournisseur, onClose, onSuccess }: FournisseurModalProps) {
  const { addToast } = useToast()
  const isEdit = !!fournisseur
  const focusTrapRef = useFocusTrap({ enabled: true, onClose })

  const [formData, setFormData] = useState({
    raison_sociale: fournisseur?.raison_sociale || '',
    type: (fournisseur?.type || 'negoce_materiaux') as TypeFournisseur,
    siret: fournisseur?.siret || '',
    adresse: fournisseur?.adresse || '',
    contact_principal: fournisseur?.contact_principal || '',
    telephone: fournisseur?.telephone || '',
    email: fournisseur?.email || '',
    conditions_paiement: fournisseur?.conditions_paiement || '',
    notes: fournisseur?.notes || '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    setError(null)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      if (!formData.raison_sociale.trim()) throw new Error('La raison sociale est obligatoire')

      const data: FournisseurCreate = {
        raison_sociale: formData.raison_sociale,
        type: formData.type,
        siret: formData.siret || undefined,
        adresse: formData.adresse || undefined,
        contact_principal: formData.contact_principal || undefined,
        telephone: formData.telephone || undefined,
        email: formData.email || undefined,
        conditions_paiement: formData.conditions_paiement || undefined,
        notes: formData.notes || undefined,
      }

      if (isEdit && fournisseur) {
        await financierService.updateFournisseur(fournisseur.id, data)
        addToast({ message: 'Fournisseur mis a jour', type: 'success' })
      } else {
        await financierService.createFournisseur(data)
        addToast({ message: 'Fournisseur cree', type: 'success' })
      }
      onSuccess()
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } }; message?: string }
      const message = error.response?.data?.detail || error.message || 'Une erreur est survenue'
      setError(message)
      logger.error('Erreur sauvegarde fournisseur', err, { context: 'FournisseurModal' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div ref={focusTrapRef} role="dialog" aria-modal="true" aria-labelledby="modal-title" className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 id="modal-title" className="text-xl font-semibold text-gray-900">
            {isEdit ? 'Modifier le fournisseur' : 'Nouveau fournisseur'}
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

          {/* Raison sociale + Type */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Raison sociale <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={formData.raison_sociale}
                onChange={(e) => handleChange('raison_sociale', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Ex: Point P"
                required
                disabled={loading}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Type <span className="text-red-500">*</span>
              </label>
              <select
                value={formData.type}
                onChange={(e) => handleChange('type', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                disabled={loading}
              >
                {Object.entries(TYPE_FOURNISSEUR_LABELS).map(([key, label]) => (
                  <option key={key} value={key}>{label}</option>
                ))}
              </select>
            </div>
          </div>

          {/* SIRET */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">SIRET</label>
            <input
              type="text"
              value={formData.siret}
              onChange={(e) => handleChange('siret', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-mono"
              placeholder="123 456 789 00012"
              maxLength={17}
              disabled={loading}
            />
          </div>

          {/* Adresse */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Adresse</label>
            <input
              type="text"
              value={formData.adresse}
              onChange={(e) => handleChange('adresse', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Adresse complete"
              disabled={loading}
            />
          </div>

          {/* Contact + Telephone */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Contact principal</label>
              <input
                type="text"
                value={formData.contact_principal}
                onChange={(e) => handleChange('contact_principal', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Nom du contact"
                disabled={loading}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Telephone</label>
              <input
                type="tel"
                value={formData.telephone}
                onChange={(e) => handleChange('telephone', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="01 23 45 67 89"
                disabled={loading}
              />
            </div>
          </div>

          {/* Email */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input
              type="email"
              value={formData.email}
              onChange={(e) => handleChange('email', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="contact@fournisseur.fr"
              disabled={loading}
            />
          </div>

          {/* Conditions paiement */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Conditions de paiement</label>
            <input
              type="text"
              value={formData.conditions_paiement}
              onChange={(e) => handleChange('conditions_paiement', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Ex: 30 jours fin de mois"
              disabled={loading}
            />
          </div>

          {/* Notes */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
            <textarea
              value={formData.notes}
              onChange={(e) => handleChange('notes', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Notes libres..."
              rows={3}
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
