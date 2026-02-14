/**
 * UserCard - Carte utilisateur pour les listes
 * P1-7: Memoized pour éviter re-renders inutiles
 */

import { memo } from 'react'
import { Link } from 'react-router-dom'
import {
  Phone,
  Mail,
  ChevronRight,
  UserCheck,
  UserX,
} from 'lucide-react'
import type { User, UserRole } from '../../types'
import { ROLES, METIERS } from '../../types'
import type { Metier } from '../../types'

interface UserCardProps {
  user: User
  canEdit: boolean
  onToggleActive: () => void
}

export const UserCard = memo(function UserCard({ user, canEdit, onToggleActive }: UserCardProps) {
  const roleInfo = ROLES[user.role as UserRole]
  const metierInfo = user.metier ? METIERS[user.metier as Metier] : null

  return (
    <div className={`card relative ${!user.is_active ? 'opacity-60' : ''}`}>
      <Link to={`/utilisateurs/${user.id}`} className="block">
        {/* Header */}
        <div className="flex items-start gap-4 mb-4">
          <div
            className="w-12 h-12 rounded-full flex items-center justify-center text-white font-semibold text-lg"
            style={{ backgroundColor: user.couleur || '#3498DB' }}
          >
            {user.prenom?.[0]}
            {user.nom?.[0]}
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-gray-900 truncate">
              {user.prenom} {user.nom}
            </h3>
            <div className="flex flex-wrap items-center gap-2 mt-1">
              {roleInfo && (
                <span
                  className="text-xs px-2 py-0.5 rounded-full"
                  style={{ backgroundColor: roleInfo.color + '20', color: roleInfo.color }}
                >
                  {roleInfo.label}
                </span>
              )}
              {metierInfo && (
                <span
                  className="text-xs px-2 py-0.5 rounded-full"
                  style={{ backgroundColor: metierInfo.color + '20', color: metierInfo.color }}
                >
                  {metierInfo.label}
                </span>
              )}
              {!user.is_active && (
                <span className="text-xs px-2 py-0.5 rounded-full bg-red-100 text-red-700">
                  Desactive
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Contact info */}
        <div className="space-y-2 text-sm">
          <div className="flex items-center gap-2 text-gray-600">
            <Mail className="w-4 h-4 text-gray-600" />
            <span className="truncate">{user.email}</span>
          </div>
          {user.telephone && (
            <div className="flex items-center gap-2 text-gray-600">
              <Phone className="w-4 h-4 text-gray-600" />
              <span>{user.telephone}</span>
            </div>
          )}
        </div>

        {/* Arrow */}
        <ChevronRight className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
      </Link>

      {/* Toggle active button */}
      {canEdit && (
        <button
          onClick={(e) => {
            e.preventDefault()
            onToggleActive()
          }}
          className={`absolute top-4 right-10 p-1 rounded ${
            user.is_active
              ? 'text-green-600 hover:bg-green-50'
              : 'text-red-600 hover:bg-red-50'
          }`}
          title={user.is_active ? 'Desactiver' : 'Activer'}
        >
          {user.is_active ? <UserCheck className="w-5 h-5" /> : <UserX className="w-5 h-5" />}
        </button>
      )}
    </div>
  )
})

export default UserCard
