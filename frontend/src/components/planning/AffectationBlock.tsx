import { FileText, X } from 'lucide-react'
import type { Affectation } from '../../types'

interface AffectationBlockProps {
  affectation: Affectation
  onClick?: () => void
  onDelete?: () => void
  compact?: boolean
  // PLN-27: Drag & drop support
  draggable?: boolean
  onDragStart?: (e: React.DragEvent) => void
  onDragEnd?: () => void
}

export default function AffectationBlock({
  affectation,
  onClick,
  onDelete,
  compact = false,
  draggable = false,
  onDragStart,
  onDragEnd,
}: AffectationBlockProps) {
  const backgroundColor = affectation.chantier_couleur || '#3498DB'
  const hasNote = !!affectation.note

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation()
    onDelete?.()
  }

  if (compact) {
    return (
      <div
        className={`rounded px-2 py-1 text-xs text-white cursor-pointer hover:opacity-90 transition-opacity truncate ${draggable ? 'cursor-grab active:cursor-grabbing' : ''}`}
        style={{ backgroundColor }}
        onClick={onClick}
        title={`${affectation.chantier_nom || 'Chantier'} ${affectation.heure_debut ? `${affectation.heure_debut} - ${affectation.heure_fin}` : ''}`}
        draggable={draggable}
        onDragStart={onDragStart}
        onDragEnd={onDragEnd}
      >
        {affectation.chantier_nom || 'Chantier'}
      </div>
    )
  }

  return (
    <div
      className={`rounded-lg px-3 py-2 text-white cursor-pointer hover:opacity-90 transition-opacity relative group ${draggable ? 'cursor-grab active:cursor-grabbing' : ''}`}
      style={{ backgroundColor }}
      onClick={onClick}
      draggable={draggable}
      onDragStart={onDragStart}
      onDragEnd={onDragEnd}
    >
      {/* Bouton supprimer */}
      {onDelete && (
        <button
          onClick={handleDelete}
          className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
        >
          <X className="w-3 h-3" />
        </button>
      )}

      {/* Horaires */}
      {affectation.heure_debut && affectation.heure_fin && (
        <div className="text-xs font-medium opacity-90 flex items-center gap-1">
          {affectation.heure_debut} - {affectation.heure_fin}
          {hasNote && <FileText className="w-3 h-3" />}
        </div>
      )}

      {/* Nom du chantier */}
      <div className="text-sm font-semibold truncate">
        {affectation.chantier_nom || 'Chantier'}
      </div>
    </div>
  )
}
