/**
 * EditUserModal - Modal d'édition d'un utilisateur
 * Extrait de UserDetailPage pour réduction de taille
 */

import { useState } from 'react'
import { X, Loader2 } from 'lucide-react'
import type { User, UserUpdate, UserRole, Metier } from '../../types'
import { ROLES, METIERS, USER_COLORS } from '../../types'

interface EditUserModalProps {
  user: User
  onClose: () => void
  onSubmit: (data: UserUpdate) => void
}

export function EditUserModal({ user, onClose, onSubmit }: EditUserModalProps) {
  const [formData, setFormData] = useState<UserUpdate>({
    nom: user.nom,
    prenom: user.prenom,
    role: user.role,
    type_utilisateur: user.type_utilisateur,
    telephone: user.telephone,
    metier: user.metier,
    code_utilisateur: user.code_utilisateur,
    couleur: user.couleur,
    contact_urgence_nom: user.contact_urgence_nom,
    contact_urgence_telephone: user.contact_urgence_telephone,
  })
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    try {
      await onSubmit(formData)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="fixed inset-0 bg-black/50" onClick={onClose} />
      <div className="relative bg-white rounded-xl shadow-xl w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b px-6 py-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold">Modifier l'utilisateur</h2>
          <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-lg">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Prenom
              </label>
              <input
                type="text"
                value={formData.prenom || ''}
                onChange={(e) => setFormData({ ...formData, prenom: e.target.value })}
                className="input"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nom
              </label>
              <input
                type="text"
                value={formData.nom || ''}
                onChange={(e) => setFormData({ ...formData, nom: e.target.value })}
                className="input"
              />
            </div>
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
                  setFormData({
                    ...formData,
                    type_utilisateur: e.target.value as 'employe' | 'sous_traitant',
                  })
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

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Telephone
              </label>
              <input
                type="tel"
                value={formData.telephone || ''}
                onChange={(e) => setFormData({ ...formData, telephone: e.target.value })}
                className="input"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Code utilisateur
              </label>
              <input
                type="text"
                value={formData.code_utilisateur || ''}
                onChange={(e) => setFormData({ ...formData, code_utilisateur: e.target.value })}
                className="input"
                placeholder="Ex: EMP001"
              />
            </div>
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
                  className={`w-8 h-8 rounded-full border-2 transition-all ${
                    formData.couleur === color.code
                      ? 'border-gray-900 scale-110'
                      : 'border-transparent'
                  }`}
                  style={{ backgroundColor: color.code }}
                  title={color.name}
                />
              ))}
            </div>
          </div>

          <div className="border-t pt-4">
            <h3 className="font-medium text-gray-900 mb-3">Contact d'urgence</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nom
                </label>
                <input
                  type="text"
                  value={formData.contact_urgence_nom || ''}
                  onChange={(e) =>
                    setFormData({ ...formData, contact_urgence_nom: e.target.value })
                  }
                  className="input"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Telephone
                </label>
                <input
                  type="tel"
                  value={formData.contact_urgence_telephone || ''}
                  onChange={(e) =>
                    setFormData({ ...formData, contact_urgence_telephone: e.target.value })
                  }
                  className="input"
                />
              </div>
            </div>
          </div>

          <div className="flex gap-3 pt-4">
            <button type="button" onClick={onClose} className="flex-1 btn btn-outline">
              Annuler
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="flex-1 btn btn-primary flex items-center justify-center gap-2"
            >
              {isSubmitting && <Loader2 className="w-4 h-4 animate-spin" />}
              Enregistrer
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
