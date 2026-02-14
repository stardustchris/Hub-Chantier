/**
 * Composant TaskModal - Modal de creation/edition de tache
 * Gere tous les champs selon CDC (TAC-06 à TAC-11)
 */

import { useState } from 'react'
import { X, Loader2 } from 'lucide-react'
import type { Tache, TacheCreate, TacheUpdate, UniteMesure } from '../../types'
import { UNITES_MESURE } from '../../types'
import { useFocusTrap } from '../../hooks/useFocusTrap'

interface TaskModalProps {
  tache?: Tache | null
  parentId?: number | null
  onClose: () => void
  onSave: (data: TacheCreate | TacheUpdate) => Promise<void>
}

export default function TaskModal({
  tache,
  parentId,
  onClose,
  onSave,
}: TaskModalProps) {
  const isEditing = !!tache
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [formData, setFormData] = useState({
    titre: tache?.titre || '',
    description: tache?.description || '',
    date_echeance: tache?.date_echeance || '',
    unite_mesure: tache?.unite_mesure || '',
    quantite_estimee: tache?.quantite_estimee?.toString() || '',
    heures_estimees: tache?.heures_estimees?.toString() || '',
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.titre.trim()) return

    setIsSubmitting(true)
    try {
      const data: TacheCreate | TacheUpdate = {
        titre: formData.titre.trim(),
        description: formData.description.trim() || undefined,
        date_echeance: formData.date_echeance || undefined,
        unite_mesure: (formData.unite_mesure as UniteMesure) || undefined,
        quantite_estimee: formData.quantite_estimee
          ? parseFloat(formData.quantite_estimee)
          : undefined,
        heures_estimees: formData.heures_estimees
          ? parseFloat(formData.heures_estimees)
          : undefined,
      }

      if (!isEditing && parentId) {
        ;(data as TacheCreate).parent_id = parentId
      }

      await onSave(data)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="fixed inset-0 bg-black/50" onClick={onClose} />
      <div className="relative bg-white rounded-xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b px-6 py-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold">
            {isEditing
              ? 'Modifier la tache'
              : parentId
              ? 'Ajouter une sous-tache'
              : 'Nouvelle tache'}
          </h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {/* Titre (obligatoire) */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Titre *
            </label>
            <input
              type="text"
              value={formData.titre}
              onChange={(e) => setFormData({ ...formData, titre: e.target.value })}
              className="input"
              placeholder="Ex: Coffrage voiles R+1"
              required
              autoFocus
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="input"
              rows={3}
              placeholder="Details supplementaires..."
            />
          </div>

          {/* Date echeance (TAC-08) */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Date d'echeance
            </label>
            <input
              type="date"
              value={formData.date_echeance}
              onChange={(e) => setFormData({ ...formData, date_echeance: e.target.value })}
              className="input"
            />
          </div>

          {/* Unite de mesure et quantite (TAC-09, TAC-10) */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Unite de mesure
              </label>
              <select
                value={formData.unite_mesure}
                onChange={(e) => setFormData({ ...formData, unite_mesure: e.target.value })}
                className="input"
              >
                <option value="">-- Aucune --</option>
                {Object.entries(UNITES_MESURE).map(([key, { label, symbol }]) => (
                  <option key={key} value={key}>
                    {label} ({symbol})
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Quantite estimee
              </label>
              <input
                type="number"
                value={formData.quantite_estimee}
                onChange={(e) =>
                  setFormData({ ...formData, quantite_estimee: e.target.value })
                }
                className="input"
                min="0"
                step="0.1"
                placeholder="0"
                disabled={!formData.unite_mesure}
              />
            </div>
          </div>

          {/* Heures estimees (TAC-11) */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Heures estimees
            </label>
            <div className="relative">
              <input
                type="number"
                value={formData.heures_estimees}
                onChange={(e) =>
                  setFormData({ ...formData, heures_estimees: e.target.value })
                }
                className="input pr-8"
                min="0"
                step="0.5"
                placeholder="0"
              />
              <span className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-600 text-sm">
                h
              </span>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Temps prevu pour realiser cette tache
            </p>
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-4 border-t">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 btn btn-outline"
              disabled={isSubmitting}
            >
              Annuler
            </button>
            <button
              type="submit"
              disabled={isSubmitting || !formData.titre.trim()}
              className="flex-1 btn btn-primary flex items-center justify-center gap-2"
            >
              {isSubmitting && <Loader2 className="w-4 h-4 animate-spin" />}
              {isEditing ? 'Enregistrer' : 'Creer'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
