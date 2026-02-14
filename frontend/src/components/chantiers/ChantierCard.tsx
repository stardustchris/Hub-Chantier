/**
 * ChantierCard - Carte de chantier pour les listes
 * P1-7: Memoized pour éviter re-renders inutiles
 */

import { memo } from 'react'
import { Link } from 'react-router-dom'
import {
  MapPin,
  Users,
  Clock,
  ChevronRight,
  Calendar,
  Building2,
} from 'lucide-react'
import { formatDateDayMonth } from '../../utils/dates'
import type { Chantier } from '../../types'
import { CHANTIER_STATUTS } from '../../types'

interface ChantierCardProps {
  chantier: Chantier
}

export const ChantierCard = memo(function ChantierCard({ chantier }: ChantierCardProps) {
  const statutInfo = CHANTIER_STATUTS[chantier.statut]

  return (
    <Link
      to={`/chantiers/${chantier.id}`}
      className="card hover:shadow-md transition-shadow group"
    >
      {/* Header with color */}
      <div
        className="h-2 -mx-6 -mt-6 mb-4 rounded-t-xl"
        style={{ backgroundColor: chantier.couleur || '#3498DB' }}
      />

      {/* Content */}
      <div className="flex items-start justify-between mb-3">
        <div>
          <span className="text-sm font-mono text-gray-500">{chantier.code}</span>
          <h3 className="font-semibold text-gray-900 group-hover:text-primary-600 transition-colors">
            {chantier.nom}
          </h3>
        </div>
        <span
          className="text-xs px-2 py-1 rounded-full"
          style={{ backgroundColor: statutInfo.color + '20', color: statutInfo.color }}
        >
          {statutInfo.label}
        </span>
      </div>

      {/* Address */}
      <div className="flex items-start gap-2 text-sm text-gray-600 mb-3">
        <MapPin className="w-4 h-4 shrink-0 mt-0.5" />
        <span className="line-clamp-2">{chantier.adresse}</span>
      </div>

      {/* Maitre d'ouvrage */}
      {chantier.maitre_ouvrage && (
        <div className="flex items-center gap-2 text-sm text-gray-600 mb-3">
          <Building2 className="w-4 h-4 shrink-0" />
          <span className="line-clamp-1">{chantier.maitre_ouvrage}</span>
        </div>
      )}

      {/* Info */}
      <div className="flex items-center gap-4 text-sm text-gray-500 mb-3">
        {chantier.heures_estimees && (
          <span className="flex items-center gap-1">
            <Clock className="w-4 h-4" />
            {chantier.heures_estimees}h
          </span>
        )}
        {chantier.date_debut_prevue && (
          <span className="flex items-center gap-1">
            <Calendar className="w-4 h-4" />
            {formatDateDayMonth(chantier.date_debut_prevue)}
          </span>
        )}
      </div>

      {/* Team */}
      {(chantier.conducteurs?.length > 0 || chantier.chefs?.length > 0) && (
        <div className="flex items-center gap-2 pt-3 border-t">
          <Users className="w-4 h-4 text-gray-600" />
          <div className="flex -space-x-2">
            {[...(chantier.conducteurs || []), ...(chantier.chefs || [])]
              .slice(0, 3)
              .map((user) => (
                <div
                  key={user.id}
                  className="w-7 h-7 rounded-full flex items-center justify-center text-white text-xs font-semibold border-2 border-white"
                  style={{ backgroundColor: user.couleur || '#3498DB' }}
                  title={`${user.prenom} ${user.nom}`}
                >
                  {user.prenom?.[0]}
                  {user.nom?.[0]}
                </div>
              ))}
            {(chantier.conducteurs?.length || 0) + (chantier.chefs?.length || 0) > 3 && (
              <div className="w-7 h-7 rounded-full bg-gray-200 flex items-center justify-center text-gray-600 text-xs font-semibold border-2 border-white">
                +{(chantier.conducteurs?.length || 0) + (chantier.chefs?.length || 0) - 3}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Arrow */}
      <ChevronRight className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500 group-hover:text-primary-500 transition-colors" />
    </Link>
  )
})

export default ChantierCard
