import { useState, useRef } from 'react'
import { X, Loader2 } from 'lucide-react'
import type { UserRole, UserCreate } from '../../types'
import { ROLES, METIERS, USER_COLORS } from '../../types'
import type { Metier } from '../../types'
import { useFocusTrap } from '../../hooks/useFocusTrap'

interface CreateUserModalProps {
  onClose: () => void
  onSubmit: (data: UserCreate) => Promise<void>
}

export function CreateUserModal({ onClose, onSubmit }: CreateUserModalProps) {
  const focusTrapRef = useFocusTrap({ enabled: true, onClose })
  const [formData, setFormData] = useState<UserCreate>({
    email: '',
    password: '',
    nom: '',
    prenom: '',
    role: 'compagnon',
    type_utilisateur: 'employe',
    couleur: USER_COLORS[0].code,
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')
  const modalRef = useRef<HTMLDivElement>(null)
  const firstInputRef = useRef<HTMLInputElement>(null)

  // Focus le premier input a l'ouverture du modal
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsSubmitting(true)
    try {
      await onSubmit(formData)
    } catch (err: unknown) {
      const apiError = err as { response?: { data?: { detail?: string } } }
      setError(apiError.response?.data?.detail || 'Erreur lors de la creation')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div ref={focusTrapRef} className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="fixed inset-0 bg-black/50" onClick={onClose} aria-hidden="true" />
      <div
        ref={modalRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="create-user-title"
        className="relative bg-white rounded-xl shadow-xl w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto"
      >
        <div className="sticky top-0 bg-white border-b px-6 py-4 flex items-center justify-between">
          <h2 id="create-user-title" className="text-lg font-semibold">Nouvel utilisateur</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg"
            aria-label="Fermer le formulaire"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="bg-red-50 text-red-600 p-3 rounded-lg text-sm">{error}</div>
          )}

          <p className="text-sm text-gray-500"><span className="text-red-500">*</span> Champs obligatoires</p>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Prenom *
              </label>
              <input
                ref={firstInputRef}
                type="text"
                required
                aria-required="true"
                value={formData.prenom}
                onChange={(e) => setFormData({ ...formData, prenom: e.target.value })}
                className="input"
                placeholder="Jean"
                autoComplete="given-name"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nom *
              </label>
              <input
                type="text"
                required
                aria-required="true"
                value={formData.nom}
                onChange={(e) => setFormData({ ...formData, nom: e.target.value })}
                className="input"
                placeholder="Dupont"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email *
            </label>
            <input
              type="email"
              required
              aria-required="true"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              className="input"
              placeholder="jean.dupont@email.com"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Mot de passe *
            </label>
            <input
              type="password"
              required
              aria-required="true"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              className="input"
              placeholder="********"
              minLength={6}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Role
              </label>
              <select
                value={formData.role}
                onChange={(e) => setFormData({ ...formData, role: e.target.value as UserRole })}
                className="input"
              >
                {(Object.entries(ROLES) as [UserRole, typeof ROLES[UserRole]][]).map(
                  ([role, info]) => (
                    <option key={role} value={role}>
                      {info.label}
                    </option>
                  )
                )}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Type
              </label>
              <select
                value={formData.type_utilisateur}
                onChange={(e) =>
                  setFormData({ ...formData, type_utilisateur: e.target.value as 'employe' | 'sous_traitant' })
                }
                className="input"
              >
                <option value="employe">Employe</option>
                <option value="sous_traitant">Sous-traitant</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Metier
            </label>
            <select
              value={formData.metier || ''}
              onChange={(e) =>
                setFormData({ ...formData, metier: (e.target.value as Metier) || undefined })
              }
              className="input"
            >
              <option value="">Non specifie</option>
              {(Object.entries(METIERS) as [Metier, typeof METIERS[Metier]][]).map(
                ([metier, info]) => (
                  <option key={metier} value={metier}>
                    {info.label}
                  </option>
                )
              )}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Telephone
            </label>
            <input
              type="tel"
              value={formData.telephone || ''}
              onChange={(e) => setFormData({ ...formData, telephone: e.target.value })}
              className="input"
              placeholder="06 12 34 56 78"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Couleur
            </label>
            <div className="flex flex-wrap gap-2">
              {USER_COLORS.map((color) => (
                <button
                  key={color.code}
                  type="button"
                  onClick={() => setFormData({ ...formData, couleur: color.code })}
                  className={`w-11 h-11 rounded-full border-2 transition-all ${
                    formData.couleur === color.code
                      ? 'border-gray-900 scale-110'
                      : 'border-transparent'
                  }`}
                  style={{ backgroundColor: color.code }}
                  aria-label={`Couleur ${color.name}${formData.couleur === color.code ? ' (selectionnee)' : ''}`}
                  aria-pressed={formData.couleur === color.code}
                />
              ))}
            </div>
          </div>

          <div className="flex gap-3 pt-4">
            <button type="button" onClick={onClose} className="flex-1 btn btn-outline">
              Annuler
            </button>
            <button
              type="submit"
              disabled={isSubmitting || !formData.email || !formData.password || !formData.nom || !formData.prenom}
              className="flex-1 btn btn-primary flex items-center justify-center gap-2"
            >
              {isSubmitting && <Loader2 className="w-4 h-4 animate-spin" />}
              Creer
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default CreateUserModal
