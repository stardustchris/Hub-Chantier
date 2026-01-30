import { useState, useRef, useEffect } from 'react'
import { X, Loader2, Mail } from 'lucide-react'
import type { UserRole } from '../../types'
import { ROLES } from '../../types'

interface InviteUserData {
  email: string
  nom: string
  prenom: string
  role: UserRole
}

interface InviteUserModalProps {
  onClose: () => void
  onSubmit: (data: InviteUserData) => Promise<void>
}

export function InviteUserModal({ onClose, onSubmit }: InviteUserModalProps) {
  const [formData, setFormData] = useState<InviteUserData>({
    email: '',
    nom: '',
    prenom: '',
    role: 'compagnon',
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')
  const modalRef = useRef<HTMLDivElement>(null)
  const firstInputRef = useRef<HTMLInputElement>(null)

  // Focus le premier input a l'ouverture du modal
  useEffect(() => {
    firstInputRef.current?.focus()
  }, [])

  // Fermer avec Echap
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', handleEscape)
    return () => document.removeEventListener('keydown', handleEscape)
  }, [onClose])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsSubmitting(true)
    try {
      await onSubmit(formData)
    } catch (err: unknown) {
      const apiError = err as { response?: { data?: { detail?: string } } }
      setError(apiError.response?.data?.detail || 'Erreur lors de l\'envoi de l\'invitation')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="fixed inset-0 bg-black/50" onClick={onClose} aria-hidden="true" />
      <div
        ref={modalRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="invite-user-title"
        className="relative bg-white rounded-xl shadow-xl w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto"
      >
        <div className="sticky top-0 bg-white border-b px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Mail className="w-5 h-5 text-primary-600" />
            <h2 id="invite-user-title" className="text-lg font-semibold">Inviter un utilisateur</h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg"
            aria-label="Fermer le formulaire"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <div className="flex">
              <div className="flex-shrink-0">
                <Mail className="h-5 w-5 text-blue-400" aria-hidden="true" />
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-blue-800">
                  Invitation par email
                </h3>
                <div className="mt-2 text-sm text-blue-700">
                  <p>
                    Un email d'invitation sera envoyé à l'utilisateur avec un lien sécurisé pour créer son compte et définir son mot de passe.
                  </p>
                </div>
              </div>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="bg-red-50 text-red-600 p-3 rounded-lg text-sm">{error}</div>
            )}

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Prénom *
                </label>
                <input
                  ref={firstInputRef}
                  type="text"
                  required
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
                  value={formData.nom}
                  onChange={(e) => setFormData({ ...formData, nom: e.target.value })}
                  className="input"
                  placeholder="Dupont"
                  autoComplete="family-name"
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
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="input"
                placeholder="jean.dupont@email.com"
                autoComplete="email"
              />
              <p className="mt-1 text-xs text-gray-500">
                L'invitation sera envoyée à cette adresse
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Rôle *
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
              <p className="mt-1 text-xs text-gray-500">
                Le rôle détermine les permissions de l'utilisateur
              </p>
            </div>

            <div className="flex gap-3 pt-4">
              <button type="button" onClick={onClose} className="flex-1 btn btn-outline">
                Annuler
              </button>
              <button
                type="submit"
                disabled={isSubmitting || !formData.email || !formData.nom || !formData.prenom}
                className="flex-1 btn btn-primary flex items-center justify-center gap-2"
              >
                {isSubmitting && <Loader2 className="w-4 h-4 animate-spin" />}
                <Mail className="w-4 h-4" />
                Envoyer l'invitation
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}

export default InviteUserModal
