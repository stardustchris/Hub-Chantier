import { X } from 'lucide-react'
import type { User } from '../../types'
import { ROLES } from '../../types'
import type { UserRole } from '../../types'

interface UserRowProps {
  user: User
  canRemove: boolean
  onRemove: () => void
  badge?: { label: string; color: string }
}

export default function UserRow({ user, canRemove, onRemove, badge }: UserRowProps) {
  const roleInfo = ROLES[user.role as UserRole]

  return (
    <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
      <div className="flex items-center gap-3">
        <div
          className="w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-semibold"
          style={{ backgroundColor: user.couleur || '#3498DB' }}
          aria-hidden="true"
        >
          {user.prenom?.[0]}
          {user.nom?.[0]}
        </div>
        <div>
          <p className="font-medium text-sm">
            {user.prenom} {user.nom}
          </p>
          <div className="flex items-center gap-2">
            {roleInfo && (
              <span
                className="text-xs px-2 py-0.5 rounded-full"
                style={{ backgroundColor: roleInfo.color + '20', color: roleInfo.color }}
              >
                {roleInfo.label}
              </span>
            )}
            {badge && (
              <span className={`text-xs px-2 py-0.5 rounded-full ${badge.color}`}>
                {badge.label}
              </span>
            )}
          </div>
        </div>
      </div>
      {canRemove && (
        <button
          onClick={onRemove}
          className="p-1 text-gray-600 hover:text-red-500"
          aria-label={`Retirer ${user.prenom} ${user.nom}`}
        >
          <X className="w-4 h-4" />
        </button>
      )}
    </div>
  )
}
