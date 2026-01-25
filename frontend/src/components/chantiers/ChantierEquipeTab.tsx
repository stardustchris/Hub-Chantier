/**
 * Composant ChantierEquipeTab - Onglet Equipe de la page chantier
 * Affiche l'équipe assignée au chantier, séparée par catégorie
 */

import { Plus } from 'lucide-react'
import UserRow from './UserRow'
import type { User } from '../../types'

interface ChantierEquipeTabProps {
  conducteurs: User[]
  chefs: User[]
  ouvriers: User[]
  canEdit: boolean
  onAddUser: (type: 'conducteur' | 'chef' | 'ouvrier') => void
  onRemoveUser: (userId: string, type: 'conducteur' | 'chef' | 'ouvrier') => void
}

export default function ChantierEquipeTab({
  conducteurs,
  chefs,
  ouvriers,
  canEdit,
  onAddUser,
  onRemoveUser,
}: ChantierEquipeTabProps) {
  // Séparer les ouvriers par type_utilisateur
  const compagnons = ouvriers.filter(u => u.type_utilisateur === 'employe' || !u.type_utilisateur)
  const interimaires = ouvriers.filter(u => u.type_utilisateur === 'interimaire')
  const sousTraitants = ouvriers.filter(u => u.type_utilisateur === 'sous_traitant')

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h2 className="font-semibold text-gray-900">Equipe</h2>
      </div>

      {/* Conducteurs */}
      <div className="mb-6">
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
      <div className="mb-6">
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

      {/* Compagnons (Ouvriers employés) */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-medium text-gray-700">Compagnons</h3>
          {canEdit && (
            <button
              onClick={() => onAddUser('ouvrier')}
              className="text-sm text-primary-600 hover:text-primary-700 flex items-center gap-1"
              aria-label="Ajouter un compagnon"
            >
              <Plus className="w-4 h-4" />
              Ajouter
            </button>
          )}
        </div>
        {compagnons.length === 0 ? (
          <p className="text-sm text-gray-500">Aucun compagnon assigne</p>
        ) : (
          <div className="space-y-2">
            {compagnons.map((user) => (
              <UserRow
                key={user.id}
                user={user}
                canRemove={canEdit}
                onRemove={() => onRemoveUser(user.id, 'ouvrier')}
              />
            ))}
          </div>
        )}
      </div>

      {/* Intérimaires */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-medium text-gray-700">
            <span className="inline-flex items-center gap-2">
              Interimaires
              <span className="px-2 py-0.5 rounded text-xs font-medium bg-orange-100 text-orange-700">
                {interimaires.length}
              </span>
            </span>
          </h3>
        </div>
        {interimaires.length === 0 ? (
          <p className="text-sm text-gray-500">Aucun interimaire assigne</p>
        ) : (
          <div className="space-y-2">
            {interimaires.map((user) => (
              <UserRow
                key={user.id}
                user={user}
                canRemove={canEdit}
                onRemove={() => onRemoveUser(user.id, 'ouvrier')}
                badge={{ label: 'Interimaire', color: 'bg-orange-100 text-orange-700' }}
              />
            ))}
          </div>
        )}
      </div>

      {/* Sous-traitants */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-medium text-gray-700">
            <span className="inline-flex items-center gap-2">
              Sous-traitants
              <span className="px-2 py-0.5 rounded text-xs font-medium bg-purple-100 text-purple-700">
                {sousTraitants.length}
              </span>
            </span>
          </h3>
        </div>
        {sousTraitants.length === 0 ? (
          <p className="text-sm text-gray-500">Aucun sous-traitant assigne</p>
        ) : (
          <div className="space-y-2">
            {sousTraitants.map((user) => (
              <UserRow
                key={user.id}
                user={user}
                canRemove={canEdit}
                onRemove={() => onRemoveUser(user.id, 'ouvrier')}
                badge={{ label: 'Sous-traitant', color: 'bg-purple-100 text-purple-700' }}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
