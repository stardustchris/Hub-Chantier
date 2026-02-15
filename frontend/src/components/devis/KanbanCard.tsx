/**
 * KanbanCard - Carte de devis draggable dans le kanban
 */

import { useSortable } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { User, Euro, GripVertical } from 'lucide-react'
import type { DevisRecent } from '../../types'
import { formatEUR } from '../../utils/format'

interface KanbanCardProps {
  devis: DevisRecent
  onClick?: () => void
  isDragging?: boolean
}

export default function KanbanCard({
  devis,
  onClick,
  isDragging = false,
}: KanbanCardProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
  } = useSortable({
    id: devis.id,
  })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  }

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...attributes}
      className="bg-white rounded-lg border border-gray-200 hover:shadow-md transition-all cursor-pointer group touch-manipulation"
      role="button"
      tabIndex={0}
      aria-label={`Devis ${devis.numero} - ${devis.objet}`}
      onClick={onClick}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault()
          onClick?.()
        }
      }}
    >
      <div className="flex items-start gap-2 p-3">
        {/* Drag handle */}
        <button
          {...listeners}
          className="flex-shrink-0 p-1 -m-1 text-gray-600 hover:text-gray-900 opacity-0 group-hover:opacity-100 transition-opacity focus:opacity-100 min-w-[44px] min-h-[44px] flex items-center justify-center"
          aria-label="Déplacer le devis"
          onClick={(e) => e.stopPropagation()}
        >
          <GripVertical className="w-4 h-4" />
        </button>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between mb-2">
            <span className="text-xs font-mono text-gray-600">{devis.numero}</span>
          </div>
          <p className="text-sm font-medium text-gray-900 line-clamp-2 mb-2">
            {devis.objet}
          </p>
          <div className="space-y-1.5 text-xs text-gray-500">
            <div className="flex items-center gap-1.5">
              <User className="w-3.5 h-3.5 flex-shrink-0" />
              <span className="truncate">{devis.client_nom}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Euro className="w-3.5 h-3.5 flex-shrink-0" />
              <span className="font-medium text-gray-700">
                {formatEUR(Number(devis.montant_total_ht))}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
