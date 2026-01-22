import { useState, useEffect } from 'react'
import { X } from 'lucide-react'
import { format } from 'date-fns'
import { fr } from 'date-fns/locale'
import type { Affectation, AffectationCreate, AffectationUpdate, User, Chantier, TypeRecurrence } from '../../types'
import { JOURS_SEMAINE, RECURRENCE_TYPES } from '../../types'

interface AffectationFormProps {
  isOpen: boolean
  onClose: () => void
  onSubmit: (data: AffectationCreate | AffectationUpdate) => Promise<void>
  onDelete?: () => Promise<void>
  affectation?: Affectation | null
  preselectedUser?: User | null
  preselectedDate?: Date | null
  users: User[]
  chantiers: Chantier[]
}

/**
 * Modal de création/édition d'affectation (PLN-03, PLN-28).
 */
export function AffectationForm({
  isOpen,
  onClose,
  onSubmit,
  onDelete,
  affectation,
  preselectedUser,
  preselectedDate,
  users,
  chantiers,
}: AffectationFormProps) {
  const isEdit = !!affectation

  const [utilisateurId, setUtilisateurId] = useState<number | ''>('')
  const [chantierId, setChantierId] = useState<number | ''>('')
  const [dateAffectation, setDateAffectation] = useState('')
  const [heureDebut, setHeureDebut] = useState('')
  const [heureFin, setHeureFin] = useState('')
  const [note, setNote] = useState('')
  const [recurrence, setRecurrence] = useState<TypeRecurrence>('unique')
  const [joursRecurrence, setJoursRecurrence] = useState<number[]>([])
  const [dateFinRecurrence, setDateFinRecurrence] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  // Initialiser le formulaire
  useEffect(() => {
    if (affectation) {
      setUtilisateurId(affectation.utilisateur_id)
      setChantierId(affectation.chantier_id)
      setDateAffectation(affectation.date_affectation)
      setHeureDebut(affectation.heure_debut || '')
      setHeureFin(affectation.heure_fin || '')
      setNote(affectation.note || '')
      setRecurrence(affectation.recurrence)
      setJoursRecurrence(affectation.jours_recurrence || [])
      setDateFinRecurrence(affectation.date_fin_recurrence || '')
    } else {
      // Réinitialiser pour création
      setUtilisateurId(preselectedUser ? parseInt(preselectedUser.id) : '')
      setChantierId('')
      setDateAffectation(preselectedDate ? format(preselectedDate, 'yyyy-MM-dd') : '')
      setHeureDebut('07:00')
      setHeureFin('17:00')
      setNote('')
      setRecurrence('unique')
      setJoursRecurrence([])
      setDateFinRecurrence('')
    }
    setError('')
  }, [affectation, preselectedUser, preselectedDate, isOpen])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      if (isEdit) {
        const updateData: AffectationUpdate = {
          chantier_id: chantierId as number,
          date_affectation: dateAffectation,
          heure_debut: heureDebut || undefined,
          heure_fin: heureFin || undefined,
          note: note || undefined,
        }
        await onSubmit(updateData)
      } else {
        if (!utilisateurId || !chantierId || !dateAffectation) {
          setError('Veuillez remplir tous les champs obligatoires')
          setIsLoading(false)
          return
        }
        const createData: AffectationCreate = {
          utilisateur_id: utilisateurId as number,
          chantier_id: chantierId as number,
          date_affectation: dateAffectation,
          heure_debut: heureDebut || undefined,
          heure_fin: heureFin || undefined,
          note: note || undefined,
          recurrence,
          jours_recurrence: recurrence === 'hebdomadaire' ? joursRecurrence : undefined,
          date_fin_recurrence: dateFinRecurrence || undefined,
        }
        await onSubmit(createData)
      }
      onClose()
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur lors de l'enregistrement")
    } finally {
      setIsLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!onDelete || !window.confirm('Supprimer cette affectation ?')) return
    setIsLoading(true)
    try {
      await onDelete()
      onClose()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors de la suppression')
    } finally {
      setIsLoading(false)
    }
  }

  const toggleJour = (jour: number) => {
    setJoursRecurrence((prev) => (prev.includes(jour) ? prev.filter((j) => j !== jour) : [...prev, jour]))
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="text-lg font-semibold">{isEdit ? "Modifier l'affectation" : 'Nouvelle affectation'}</h2>
          <button onClick={onClose} className="p-1 hover:bg-gray-100 rounded">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-4 space-y-4">
          {error && <div className="p-3 bg-red-50 text-red-600 rounded-md text-sm">{error}</div>}

          {/* Utilisateur (non modifiable en édition) */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Utilisateur <span className="text-red-500">*</span>
            </label>
            <select
              value={utilisateurId}
              onChange={(e) => setUtilisateurId(parseInt(e.target.value) || '')}
              className="input w-full"
              disabled={isEdit}
              required
            >
              <option value="">Sélectionner un utilisateur</option>
              {users
                .filter((u) => u.is_active)
                .map((user) => (
                  <option key={user.id} value={user.id}>
                    {user.prenom} {user.nom}
                  </option>
                ))}
            </select>
          </div>

          {/* Chantier */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Chantier <span className="text-red-500">*</span>
            </label>
            <select
              value={chantierId}
              onChange={(e) => setChantierId(parseInt(e.target.value) || '')}
              className="input w-full"
              required
            >
              <option value="">Sélectionner un chantier</option>
              {chantiers
                .filter((c) => c.statut !== 'ferme')
                .map((chantier) => (
                  <option key={chantier.id} value={chantier.id}>
                    {chantier.nom}
                  </option>
                ))}
            </select>
          </div>

          {/* Date */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Date <span className="text-red-500">*</span>
            </label>
            <input
              type="date"
              value={dateAffectation}
              onChange={(e) => setDateAffectation(e.target.value)}
              className="input w-full"
              required
            />
          </div>

          {/* Horaires */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Heure début</label>
              <input
                type="time"
                value={heureDebut}
                onChange={(e) => setHeureDebut(e.target.value)}
                className="input w-full"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Heure fin</label>
              <input
                type="time"
                value={heureFin}
                onChange={(e) => setHeureFin(e.target.value)}
                className="input w-full"
              />
            </div>
          </div>

          {/* Note (PLN-25) */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Note privée</label>
            <textarea
              value={note}
              onChange={(e) => setNote(e.target.value)}
              className="input w-full h-20 resize-none"
              placeholder="Commentaire visible uniquement par l'affecté..."
            />
          </div>

          {/* Récurrence (uniquement en création) */}
          {!isEdit && (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Récurrence</label>
                <select
                  value={recurrence}
                  onChange={(e) => setRecurrence(e.target.value as TypeRecurrence)}
                  className="input w-full"
                >
                  {Object.entries(RECURRENCE_TYPES).map(([key, { label }]) => (
                    <option key={key} value={key}>
                      {label}
                    </option>
                  ))}
                </select>
              </div>

              {recurrence === 'hebdomadaire' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Jours de répétition</label>
                  <div className="flex flex-wrap gap-2">
                    {JOURS_SEMAINE.map(({ value, short }) => (
                      <button
                        key={value}
                        type="button"
                        onClick={() => toggleJour(value)}
                        className={`
                          w-8 h-8 rounded-full text-sm font-medium transition-colors
                          ${joursRecurrence.includes(value) ? 'bg-primary text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}
                        `}
                      >
                        {short}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {recurrence !== 'unique' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Date de fin (optionnel)</label>
                  <input
                    type="date"
                    value={dateFinRecurrence}
                    onChange={(e) => setDateFinRecurrence(e.target.value)}
                    className="input w-full"
                    min={dateAffectation}
                  />
                </div>
              )}
            </>
          )}

          {/* Actions */}
          <div className="flex justify-between pt-4 border-t">
            {isEdit && onDelete ? (
              <button
                type="button"
                onClick={handleDelete}
                className="btn text-red-600 hover:bg-red-50"
                disabled={isLoading}
              >
                Supprimer
              </button>
            ) : (
              <div />
            )}
            <div className="flex gap-2">
              <button type="button" onClick={onClose} className="btn btn-outline" disabled={isLoading}>
                Annuler
              </button>
              <button type="submit" className="btn btn-primary" disabled={isLoading}>
                {isLoading ? 'Enregistrement...' : isEdit ? 'Modifier' : 'Créer'}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  )
}
