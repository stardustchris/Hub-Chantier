/**
 * Composant AffectationBlock - Bloc d'affectation dans le planning
 * Optimisé avec React.memo pour éviter les re-renders dans les grilles
 */

import { memo, useCallback } from 'react'
import { FileText, X, GripVertical } from 'lucide-react'
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
  // Resize support
  resizable?: boolean
  onResizeStart?: (direction: 'left' | 'right', e: React.MouseEvent) => void
  isResizing?: boolean
  // Hauteur proportionnelle a la duree
  proportionalHeight?: boolean
  cellHeight?: number // Hauteur de la cellule en pixels (pour une journee complete)
}

/**
 * Calcule la duree en heures entre deux horaires (format "HH:MM")
 */
function calculateDurationHours(heureDebut: string, heureFin: string): number {
  const [startH, startM] = heureDebut.split(':').map(Number)
  const [endH, endM] = heureFin.split(':').map(Number)
  const startMinutes = startH * 60 + startM
  const endMinutes = endH * 60 + endM
  return (endMinutes - startMinutes) / 60
}

// Journee de travail standard: 8h (ex: 08:00 - 17:00 avec 1h pause)
const FULL_DAY_HOURS = 8

const AffectationBlock = memo(function AffectationBlock({
  affectation,
  onClick,
  onDelete,
  compact = false,
  draggable = false,
  onDragStart,
  onDragEnd,
  resizable = false,
  onResizeStart,
  isResizing = false,
  proportionalHeight = false,
  cellHeight = 60,
}: AffectationBlockProps) {
  const backgroundColor = affectation.chantier_couleur || '#3498DB'
  const hasNote = !!affectation.note

  // Calculer la hauteur proportionnelle si les horaires sont definis
  let heightStyle: React.CSSProperties = {}
  if (proportionalHeight && affectation.heure_debut && affectation.heure_fin) {
    const durationHours = calculateDurationHours(affectation.heure_debut, affectation.heure_fin)
    const heightPercent = Math.min(durationHours / FULL_DAY_HOURS, 1)
    const minHeight = 24 // Hauteur minimale pour rester lisible
    const calculatedHeight = Math.max(cellHeight * heightPercent, minHeight)
    heightStyle = { height: `${calculatedHeight}px`, minHeight: `${minHeight}px` }
  }

  const handleDelete = useCallback((e: React.MouseEvent) => {
    e.stopPropagation()
    onDelete?.()
  }, [onDelete])

  const handleResizeStart = useCallback((direction: 'left' | 'right', e: React.MouseEvent) => {
    e.stopPropagation()
    e.preventDefault()
    onResizeStart?.(direction, e)
  }, [onResizeStart])

  if (compact) {
    return (
      <div
        className={`w-full max-w-full rounded px-2 py-1 text-xs text-white cursor-pointer hover:opacity-90 transition-opacity truncate ${draggable ? 'cursor-grab active:cursor-grabbing' : ''}`}
        style={{ backgroundColor, ...heightStyle }}
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
      className={`w-full max-w-full rounded-lg px-2 py-1.5 text-white cursor-pointer hover:opacity-90 transition-opacity relative group overflow-hidden ${draggable ? 'cursor-grab active:cursor-grabbing' : ''} ${isResizing ? 'ring-2 ring-white' : ''}`}
      style={{ backgroundColor, ...heightStyle }}
      onClick={onClick}
      draggable={draggable && !isResizing}
      onDragStart={onDragStart}
      onDragEnd={onDragEnd}
    >
      {/* Poignée de resize gauche */}
      {resizable && (
        <div
          className="absolute left-0 top-0 bottom-0 w-2 cursor-ew-resize opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center hover:bg-white/30"
          onMouseDown={(e) => handleResizeStart('left', e)}
        >
          <GripVertical className="w-3 h-3 opacity-70" />
        </div>
      )}

      {/* Poignée de resize droite */}
      {resizable && (
        <div
          className="absolute right-0 top-0 bottom-0 w-2 cursor-ew-resize opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center hover:bg-white/30"
          onMouseDown={(e) => handleResizeStart('right', e)}
        >
          <GripVertical className="w-3 h-3 opacity-70" />
        </div>
      )}

      {/* Bouton supprimer */}
      {onDelete && (
        <button
          onClick={handleDelete}
          className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity z-10"
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
})

export default AffectationBlock
