import { useState } from 'react'
import { format, isSameDay } from 'date-fns'
import type { User, Affectation, Chantier } from '../../types'
import { AffectationBlock } from './AffectationBlock'
import { METIERS } from '../../types'

interface UserRowProps {
  user: User
  weekDays: Date[]
  affectations: Affectation[]
  chantiers: Map<number, Chantier>
  onAffectationClick: (affectation: Affectation) => void
  onCellClick: (user: User, date: Date) => void
  onDragStart: (affectation: Affectation) => void
  onDrop: (date: Date, userId: number) => void
}

/**
 * Ligne utilisateur dans la grille planning (PLN-15, PLN-20).
 */
export function UserRow({
  user,
  weekDays,
  affectations,
  chantiers,
  onAffectationClick,
  onCellClick,
  onDragStart,
  onDrop,
}: UserRowProps) {
  const [dragOverDay, setDragOverDay] = useState<string | null>(null)
  const userColor = user.couleur || '#607D8B'
  const initials = `${user.prenom?.charAt(0) || '?'}${user.nom?.charAt(0) || '?'}`.toUpperCase()
  const metierInfo = user.metier ? METIERS[user.metier] : null

  const getAffectationsForDay = (date: Date) => {
    const dateStr = format(date, 'yyyy-MM-dd')
    return affectations.filter((a) => a.date_affectation === dateStr)
  }

  const handleDragOver = (e: React.DragEvent, dayKey: string) => {
    e.preventDefault()
    setDragOverDay(dayKey)
  }

  const handleDragLeave = () => {
    setDragOverDay(null)
  }

  const handleDrop = (e: React.DragEvent, date: Date) => {
    e.preventDefault()
    setDragOverDay(null)
    onDrop(date, parseInt(user.id))
  }

  const handleKeyDown = (e: React.KeyboardEvent, day: Date) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      onCellClick(user, day)
    }
  }

  return (
    <tr className="border-b border-gray-100 hover:bg-gray-50/50">
      {/* Colonne utilisateur (PLN-15) */}
      <td className="p-2 sticky left-0 bg-white z-10 min-w-[200px]">
        <div className="flex items-center gap-2">
          {/* Avatar avec initiales et couleur */}
          <div
            className="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-medium flex-shrink-0"
            style={{ backgroundColor: userColor }}
          >
            {initials}
          </div>
          <div className="min-w-0">
            <div className="font-medium text-sm truncate">
              {user.prenom} {user.nom}
            </div>
            {metierInfo && (
              <div
                className="text-xs px-1.5 py-0.5 rounded inline-block"
                style={{ backgroundColor: `${metierInfo.color}20`, color: metierInfo.color }}
              >
                {metierInfo.label}
              </div>
            )}
          </div>
        </div>
      </td>

      {/* Cellules jours (PLN-20, PLN-21) */}
      {weekDays.map((day) => {
        const dayKey = day.toISOString()
        const dayAffectations = getAffectationsForDay(day)
        const isToday = isSameDay(day, new Date())
        const isDragOver = dragOverDay === dayKey

        return (
          <td
            key={dayKey}
            className={`
              p-1 border-l border-gray-100 min-w-[120px] align-top cursor-pointer
              ${isToday ? 'bg-blue-50/50' : ''}
              ${isDragOver ? 'bg-blue-100' : ''}
              focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-inset
            `}
            tabIndex={0}
            onDragOver={(e) => handleDragOver(e, dayKey)}
            onDragLeave={handleDragLeave}
            onDrop={(e) => handleDrop(e, day)}
            onDoubleClick={() => onCellClick(user, day)}
            onKeyDown={(e) => handleKeyDown(e, day)}
          >
            <div className="space-y-1">
              {dayAffectations.map((affectation) => (
                <AffectationBlock
                  key={affectation.id}
                  affectation={affectation}
                  chantier={chantiers.get(affectation.chantier_id)}
                  onClick={() => onAffectationClick(affectation)}
                  onDragStart={() => onDragStart(affectation)}
                />
              ))}
            </div>
          </td>
        )
      })}
    </tr>
  )
}
