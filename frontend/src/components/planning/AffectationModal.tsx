import { useState, useEffect } from 'react'
import { X } from 'lucide-react'
import { format } from 'date-fns'
import type { Affectation, AffectationCreate, AffectationUpdate, User, Chantier, JourSemaine } from '../../types'
import { JOURS_SEMAINE } from '../../types'

interface AffectationModalProps {
  isOpen: boolean
  onClose: () => void
  onSave: (data: AffectationCreate | AffectationUpdate) => Promise<void>
  affectation?: Affectation | null
  utilisateurs: User[]
  chantiers: Chantier[]
  selectedDate?: Date
  selectedUserId?: string
  selectedChantierId?: string
}

export default function AffectationModal({
  isOpen,
  onClose,
  onSave,
  affectation,
  utilisateurs,
  chantiers,
  selectedDate,
  selectedUserId,
  selectedChantierId,
}: AffectationModalProps) {
  const isEdit = !!affectation

  const [formData, setFormData] = useState({
    utilisateur_id: '',
    chantier_id: '',
    date: '',
    heure_debut: '08:00',
    heure_fin: '17:00',
    note: '',
    type_affectation: 'unique' as 'unique' | 'recurrente',
    jours_recurrence: [] as JourSemaine[],
    date_fin_recurrence: '',
  })

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (affectation) {
      setFormData({
        utilisateur_id: affectation.utilisateur_id,
        chantier_id: affectation.chantier_id,
        date: affectation.date,
        heure_debut: affectation.heure_debut || '08:00',
        heure_fin: affectation.heure_fin || '17:00',
        note: affectation.note || '',
        type_affectation: affectation.type_affectation,
        jours_recurrence: affectation.jours_recurrence || [],
        date_fin_recurrence: '',
      })
    } else {
      setFormData({
        utilisateur_id: selectedUserId || '',
        chantier_id: selectedChantierId || '',
        date: selectedDate ? format(selectedDate, 'yyyy-MM-dd') : '',
        heure_debut: '08:00',
        heure_fin: '17:00',
        note: '',
        type_affectation: 'unique',
        jours_recurrence: [],
        date_fin_recurrence: '',
      })
    }
    setError('')
  }, [affectation, selectedDate, selectedUserId, selectedChantierId, isOpen])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      if (isEdit) {
        await onSave({
          heure_debut: formData.heure_debut || undefined,
          heure_fin: formData.heure_fin || undefined,
          note: formData.note || undefined,
          chantier_id: formData.chantier_id || undefined,
        })
      } else {
        await onSave({
          utilisateur_id: formData.utilisateur_id,
          chantier_id: formData.chantier_id,
          date: formData.date,
          heure_debut: formData.heure_debut || undefined,
          heure_fin: formData.heure_fin || undefined,
          note: formData.note || undefined,
          type_affectation: formData.type_affectation,
          jours_recurrence: formData.type_affectation === 'recurrente' ? formData.jours_recurrence : undefined,
          date_fin_recurrence: formData.type_affectation === 'recurrente' ? formData.date_fin_recurrence : undefined,
        })
      }
      onClose()
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Une erreur est survenue'
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const toggleJour = (jour: JourSemaine) => {
    setFormData(prev => ({
      ...prev,
      jours_recurrence: prev.jours_recurrence.includes(jour)
        ? prev.jours_recurrence.filter(j => j !== jour)
        : [...prev.jours_recurrence, jour],
    }))
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-screen items-center justify-center p-4">
        {/* Overlay */}
        <div className="fixed inset-0 bg-black/50" onClick={onClose} />

        {/* Modal */}
        <div className="relative bg-white rounded-xl shadow-xl w-full max-w-md">
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-4 border-b">
            <h2 className="text-lg font-semibold">
              {isEdit ? 'Modifier l\'affectation' : 'Nouvelle affectation'}
            </h2>
            <button
              onClick={onClose}
              className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="p-6 space-y-4">
            {error && (
              <div className="p-3 bg-red-50 text-red-700 rounded-lg text-sm">
                {error}
              </div>
            )}

            {/* Utilisateur (seulement en création) */}
            {!isEdit && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Utilisateur *
                </label>
                <select
                  value={formData.utilisateur_id}
                  onChange={e => setFormData({ ...formData, utilisateur_id: e.target.value })}
                  className="input w-full"
                  required
                >
                  <option value="">Sélectionner un utilisateur</option>
                  {utilisateurs.map(user => (
                    <option key={user.id} value={user.id}>
                      {user.prenom} {user.nom}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {/* Chantier */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Chantier *
              </label>
              <select
                value={formData.chantier_id}
                onChange={e => setFormData({ ...formData, chantier_id: e.target.value })}
                className="input w-full"
                required
              >
                <option value="">Sélectionner un chantier</option>
                {chantiers.map(chantier => (
                  <option key={chantier.id} value={chantier.id}>
                    {chantier.code} - {chantier.nom}
                  </option>
                ))}
              </select>
            </div>

            {/* Date (seulement en création) */}
            {!isEdit && (
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Date début *
                  </label>
                  <input
                    type="date"
                    value={formData.date}
                    onChange={e => setFormData({ ...formData, date: e.target.value })}
                    className="input w-full"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Date fin {formData.type_affectation === 'recurrente' ? '*' : ''}
                  </label>
                  <input
                    type="date"
                    value={formData.date_fin_recurrence}
                    onChange={e => setFormData({ ...formData, date_fin_recurrence: e.target.value })}
                    className="input w-full"
                    min={formData.date}
                    required={formData.type_affectation === 'recurrente'}
                  />
                </div>
              </div>
            )}

            {/* Horaires */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Heure début
                </label>
                <input
                  type="time"
                  value={formData.heure_debut}
                  onChange={e => setFormData({ ...formData, heure_debut: e.target.value })}
                  className="input w-full"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Heure fin
                </label>
                <input
                  type="time"
                  value={formData.heure_fin}
                  onChange={e => setFormData({ ...formData, heure_fin: e.target.value })}
                  className="input w-full"
                />
              </div>
            </div>

            {/* Type d'affectation (seulement en création) */}
            {!isEdit && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Type d'affectation
                </label>
                <div className="flex gap-4">
                  <label className="flex items-center gap-2">
                    <input
                      type="radio"
                      value="unique"
                      checked={formData.type_affectation === 'unique'}
                      onChange={() => setFormData({ ...formData, type_affectation: 'unique' })}
                      className="text-primary-600"
                    />
                    <span className="text-sm">Unique</span>
                  </label>
                  <label className="flex items-center gap-2">
                    <input
                      type="radio"
                      value="recurrente"
                      checked={formData.type_affectation === 'recurrente'}
                      onChange={() => setFormData({ ...formData, type_affectation: 'recurrente' })}
                      className="text-primary-600"
                    />
                    <span className="text-sm">Récurrente</span>
                  </label>
                </div>
              </div>
            )}

            {/* Jours de récurrence */}
            {!isEdit && formData.type_affectation === 'recurrente' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Jours de récurrence
                </label>
                <div className="flex flex-wrap gap-2">
                  {([0, 1, 2, 3, 4, 5, 6] as JourSemaine[]).map(jour => (
                    <button
                      key={jour}
                      type="button"
                      onClick={() => toggleJour(jour)}
                      className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                        formData.jours_recurrence.includes(jour)
                          ? 'bg-primary-100 text-primary-700'
                          : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                      }`}
                    >
                      {JOURS_SEMAINE[jour].short}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Note */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Note privée
              </label>
              <textarea
                value={formData.note}
                onChange={e => setFormData({ ...formData, note: e.target.value })}
                className="input w-full"
                rows={3}
                placeholder="Commentaire visible uniquement par l'affecté"
                maxLength={500}
              />
            </div>

            {/* Boutons */}
            <div className="flex gap-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="btn btn-outline flex-1"
                disabled={loading}
              >
                Annuler
              </button>
              <button
                type="submit"
                className="btn btn-primary flex-1"
                disabled={loading}
              >
                {loading ? 'Enregistrement...' : isEdit ? 'Modifier' : 'Créer'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
