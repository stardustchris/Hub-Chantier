import { X } from 'lucide-react'
import type { User } from '../../types'
import { useFocusTrap } from '../../hooks/useFocusTrap'

interface AddUserModalProps {
  type: 'conducteur' | 'chef' | 'ouvrier'
  users: User[]
  onClose: () => void
  onSelect: (userId: string) => void
}

export default function AddUserModal({ type, users, onClose, onSelect }: AddUserModalProps) {
  const focusTrapRef = useFocusTrap({ enabled: true, onClose })

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center" role="dialog" aria-modal="true" aria-labelledby="add-user-title">
      <div className="fixed inset-0 bg-black/50" onClick={onClose} aria-hidden="true" />
      <div
        ref={focusTrapRef}
        className="relative bg-white rounded-xl shadow-xl w-full max-w-md mx-4 max-h-[80vh] overflow-y-auto"
      >
        <div className="sticky top-0 bg-white border-b px-6 py-4 flex items-center justify-between">
          <h2 id="add-user-title" className="text-lg font-semibold">
            Ajouter un {type === 'conducteur' ? 'conducteur' : type === 'chef' ? 'chef de chantier' : 'ouvrier'}
          </h2>
          <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-lg" aria-label="Fermer">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-4">
          {users.length === 0 ? (
            <p className="text-center text-gray-500 py-8">
              Aucun utilisateur disponible
            </p>
          ) : (
            <div className="space-y-2" role="listbox" aria-label="Liste des utilisateurs">
              {users.map((user) => (
                <button
                  key={user.id}
                  onClick={() => onSelect(user.id)}
                  className="w-full flex items-center gap-3 p-3 rounded-lg hover:bg-gray-50 text-left focus:ring-2 focus:ring-primary-500 focus:outline-none"
                  role="option"
                  aria-selected="false"
                >
                  <div
                    className="w-10 h-10 rounded-full flex items-center justify-center text-white font-semibold"
                    style={{ backgroundColor: user.couleur || '#3498DB' }}
                    aria-hidden="true"
                  >
                    {user.prenom?.[0]}
                    {user.nom?.[0]}
                  </div>
                  <div>
                    <p className="font-medium">
                      {user.prenom} {user.nom}
                    </p>
                    <p className="text-sm text-gray-500">{user.email}</p>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
