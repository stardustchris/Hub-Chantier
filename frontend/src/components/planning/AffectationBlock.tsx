import { StickyNote } from 'lucide-react'
import type { Affectation, Chantier } from '../../types'

interface AffectationBlockProps {
  affectation: Affectation
  chantier?: Chantier
  onClick?: () => void
  onDragStart?: (e: React.DragEvent) => void
  isDragging?: boolean
}

/**
 * Bloc coloré représentant une affectation dans la grille planning (PLN-17, PLN-18, PLN-19).
 */
export function AffectationBlock({
  affectation,
  chantier,
  onClick,
  onDragStart,
  isDragging = false,
}: AffectationBlockProps) {
  const backgroundColor = chantier?.couleur || '#3498DB'
  const hasNote = !!affectation.note

  const formatTime = (time?: string) => {
    if (!time) return ''
    return time.substring(0, 5) // HH:MM
  }

  const timeDisplay =
    affectation.heure_debut && affectation.heure_fin
      ? `${formatTime(affectation.heure_debut)} - ${formatTime(affectation.heure_fin)}`
      : affectation.heure_debut
        ? `À partir de ${formatTime(affectation.heure_debut)}`
        : affectation.heure_fin
          ? `Jusqu'à ${formatTime(affectation.heure_fin)}`
          : 'Journée'

  return (
    <div
      className={`
        rounded-md px-2 py-1 text-xs text-white cursor-pointer
        transition-all duration-200 hover:opacity-90 hover:shadow-md
        ${isDragging ? 'opacity-50 scale-95' : ''}
      `}
      style={{ backgroundColor }}
      onClick={onClick}
      draggable
      onDragStart={onDragStart}
    >
      <div className="flex items-center justify-between gap-1">
        <span className="font-medium truncate">{timeDisplay}</span>
        {hasNote && <StickyNote className="w-3 h-3 flex-shrink-0" />}
      </div>
      <div className="truncate opacity-90">{chantier?.nom || `Chantier ${affectation.chantier_id}`}</div>
    </div>
  )
}
