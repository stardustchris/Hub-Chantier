/**
 * Composant ChantierEquipeTab - Onglet Equipe de la page chantier
 * Extrait de ChantierDetailPage pour réduire la complexité
 */

import { Plus } from 'lucide-react'
import UserRow from './UserRow'
import type { User } from '../../types'

interface ChantierEquipeTabProps {
  conducteurs: User[]
  chefs: User[]
  canEdit: boolean
  onAddUser: (type: 'conducteur' | 'chef') => void
  onRemoveUser: (userId: string, type: 'conducteur' | 'chef') => void
}

export default function ChantierEquipeTab({
  conducteurs,
  chefs,
  canEdit,
  onAddUser,
  onRemoveUser,
}: ChantierEquipeTabProps) {
  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h2 className="font-semibold text-gray-900">Equipe</h2>
      </div>

      {/* Conducteurs */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-medium text-gray-700">Conducteurs de travaux</h3>
          {canEdit && (
            <button
              onClick={() => onAddUser('conducteur')}
              className="text-sm text-primary-600 hover:text-primary-700 flex items-center gap-1"
              aria-label="Ajouter un conducteur"
            >
              <Plus className="w-4 h-4" />
              Ajouter
            </button>
          )}
        </div>
        {conducteurs.length === 0 ? (
          <p className="text-sm text-gray-500">Aucun conducteur assigne</p>
        ) : (
          <div className="space-y-2">
            {conducteurs.map((user) => (
              <UserRow
                key={user.id}
                user={user}
                canRemove={canEdit}
                onRemove={() => onRemoveUser(user.id, 'conducteur')}
              />
            ))}
          </div>
        )}
      </div>

      {/* Chefs */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-medium text-gray-700">Chefs de chantier</h3>
          {canEdit && (
            <button
              onClick={() => onAddUser('chef')}
              className="text-sm text-primary-600 hover:text-primary-700 flex items-center gap-1"
              aria-label="Ajouter un chef de chantier"
            >
              <Plus className="w-4 h-4" />
              Ajouter
            </button>
          )}
        </div>
        {chefs.length === 0 ? (
          <p className="text-sm text-gray-500">Aucun chef assigne</p>
        ) : (
          <div className="space-y-2">
            {chefs.map((user) => (
              <UserRow
                key={user.id}
                user={user}
                canRemove={canEdit}
                onRemove={() => onRemoveUser(user.id, 'chef')}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
