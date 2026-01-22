import { useMemo } from 'react'
import { format, eachDayOfInterval, startOfWeek, endOfWeek, isToday } from 'date-fns'
import { fr } from 'date-fns/locale'
import { ChevronDown, ChevronRight, Copy, Phone } from 'lucide-react'
import type { Affectation, User, Metier } from '../../types'
import { METIERS } from '../../types'
import AffectationBlock from './AffectationBlock'

interface PlanningGridProps {
  currentDate: Date
  affectations: Affectation[]
  utilisateurs: User[]
  onAffectationClick: (affectation: Affectation) => void
  onAffectationDelete: (affectation: Affectation) => void
  onCellClick: (userId: string, date: Date) => void
  onDuplicate: (userId: string) => void
  expandedMetiers: string[]
  onToggleMetier: (metier: string) => void
}

// Grouper les utilisateurs par métier
function groupByMetier(utilisateurs: User[]): Record<string, User[]> {
  const groups: Record<string, User[]> = {}

  utilisateurs.forEach(user => {
    const metier = user.metier || 'autre'
    if (!groups[metier]) {
      groups[metier] = []
    }
    groups[metier].push(user)
  })

  return groups
}

export default function PlanningGrid({
  currentDate,
  affectations,
  utilisateurs,
  onAffectationClick,
  onAffectationDelete,
  onCellClick,
  onDuplicate,
  expandedMetiers,
  onToggleMetier,
}: PlanningGridProps) {
  // Jours de la semaine
  const days = useMemo(() => {
    const start = startOfWeek(currentDate, { weekStartsOn: 1 })
    const end = endOfWeek(currentDate, { weekStartsOn: 1 })
    return eachDayOfInterval({ start, end })
  }, [currentDate])

  // Grouper les utilisateurs par métier
  const groupedUsers = useMemo(() => groupByMetier(utilisateurs), [utilisateurs])

  // Indexer les affectations par utilisateur et date
  const affectationsByUserAndDate = useMemo(() => {
    const index: Record<string, Record<string, Affectation[]>> = {}

    affectations.forEach(aff => {
      if (!index[aff.utilisateur_id]) {
        index[aff.utilisateur_id] = {}
      }
      const dateKey = aff.date
      if (!index[aff.utilisateur_id][dateKey]) {
        index[aff.utilisateur_id][dateKey] = []
      }
      index[aff.utilisateur_id][dateKey].push(aff)
    })

    return index
  }, [affectations])

  const getAffectationsForCell = (userId: string, date: Date): Affectation[] => {
    const dateKey = format(date, 'yyyy-MM-dd')
    return affectationsByUserAndDate[userId]?.[dateKey] || []
  }

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      {/* Header - Jours */}
      <div className="grid grid-cols-[250px_repeat(7,1fr)] border-b bg-gray-50">
        <div className="px-4 py-3 font-medium text-gray-700 border-r">
          Utilisateurs
        </div>
        {days.map(day => (
          <div
            key={day.toISOString()}
            className={`px-2 py-3 text-center border-r last:border-r-0 ${
              isToday(day) ? 'bg-primary-50' : ''
            }`}
          >
            <div className="text-xs text-gray-500 uppercase">
              {format(day, 'EEE', { locale: fr })}
            </div>
            <div className={`text-sm font-medium ${isToday(day) ? 'text-primary-600' : 'text-gray-900'}`}>
              {format(day, 'd MMM', { locale: fr })}
            </div>
          </div>
        ))}
      </div>

      {/* Corps - Groupes de métiers */}
      <div className="divide-y">
        {Object.entries(groupedUsers).map(([metier, users]) => {
          const metierInfo = METIERS[metier as Metier] || { label: metier, color: '#607D8B' }
          const isExpanded = expandedMetiers.includes(metier)

          return (
            <div key={metier}>
              {/* Header du groupe (métier) */}
              <button
                onClick={() => onToggleMetier(metier)}
                className="w-full grid grid-cols-[250px_repeat(7,1fr)] bg-gray-50 hover:bg-gray-100 transition-colors"
              >
                <div className="px-4 py-2 flex items-center gap-2 border-r">
                  {isExpanded ? (
                    <ChevronDown className="w-4 h-4 text-gray-500" />
                  ) : (
                    <ChevronRight className="w-4 h-4 text-gray-500" />
                  )}
                  <span
                    className="px-2 py-0.5 rounded text-xs font-medium text-white"
                    style={{ backgroundColor: metierInfo.color }}
                  >
                    {metierInfo.label}
                  </span>
                  <span className="text-sm text-gray-500">({users.length})</span>
                </div>
                {/* Colonnes vides pour aligner */}
                {days.map(day => (
                  <div key={day.toISOString()} className="border-r last:border-r-0" />
                ))}
              </button>

              {/* Utilisateurs du groupe */}
              {isExpanded && users.map(user => (
                <div
                  key={user.id}
                  className="grid grid-cols-[250px_repeat(7,1fr)] hover:bg-gray-50 transition-colors"
                >
                  {/* Colonne utilisateur */}
                  <div className="px-4 py-3 flex items-center gap-3 border-r">
                    {/* Avatar */}
                    <div
                      className="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-semibold flex-shrink-0"
                      style={{ backgroundColor: user.couleur || '#3498DB' }}
                    >
                      {user.prenom?.[0]}{user.nom?.[0]}
                    </div>

                    {/* Nom */}
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium text-gray-900 truncate">
                        {user.prenom} {user.nom}
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          onDuplicate(user.id)
                        }}
                        className="p-1 rounded hover:bg-gray-200"
                        title="Dupliquer la semaine"
                      >
                        <Copy className="w-4 h-4 text-gray-500" />
                      </button>
                      {user.telephone && (
                        <a
                          href={`tel:${user.telephone}`}
                          onClick={e => e.stopPropagation()}
                          className="p-1 rounded hover:bg-gray-200"
                          title="Appeler"
                        >
                          <Phone className="w-4 h-4 text-gray-500" />
                        </a>
                      )}
                    </div>
                  </div>

                  {/* Cellules des jours */}
                  {days.map(day => {
                    const cellAffectations = getAffectationsForCell(user.id, day)
                    const hasAffectations = cellAffectations.length > 0

                    return (
                      <div
                        key={day.toISOString()}
                        onClick={() => !hasAffectations && onCellClick(user.id, day)}
                        onDoubleClick={() => onCellClick(user.id, day)}
                        className={`p-1 border-r last:border-r-0 min-h-[60px] ${
                          isToday(day) ? 'bg-primary-50/50' : ''
                        } ${
                          !hasAffectations ? 'cursor-pointer hover:bg-gray-100' : ''
                        }`}
                      >
                        <div className="space-y-1">
                          {cellAffectations.map(aff => (
                            <AffectationBlock
                              key={aff.id}
                              affectation={aff}
                              onClick={() => onAffectationClick(aff)}
                              onDelete={() => onAffectationDelete(aff)}
                              compact={cellAffectations.length > 1}
                            />
                          ))}
                        </div>
                      </div>
                    )
                  })}
                </div>
              ))}
            </div>
          )
        })}
      </div>

      {/* Message si aucun utilisateur */}
      {utilisateurs.length === 0 && (
        <div className="p-8 text-center text-gray-500">
          Aucun utilisateur à afficher
        </div>
      )}
    </div>
  )
}
