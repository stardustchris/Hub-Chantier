/**
 * KanbanColumn - Colonne de kanban avec drop zone
 */

import { useDroppable } from '@dnd-kit/core'
import type { ReactNode } from 'react'

interface KanbanColumnProps {
  id: string
  title: string
  count: number
  color: string
  children: ReactNode
}

export default function KanbanColumn({
  id,
  title,
  count,
  color,
  children,
}: KanbanColumnProps) {
  const { setNodeRef, isOver } = useDroppable({
    id,
  })

  return (
    <div
      ref={setNodeRef}
      className={`w-72 flex-shrink-0 bg-gray-50 rounded-xl transition-colors ${
        isOver ? 'ring-2 ring-blue-500 bg-blue-50' : ''
      }`}
      role="region"
      aria-label={`Colonne ${title}`}
    >
      {/* Column header */}
      <div
        className="px-4 py-3 rounded-t-xl border-b-2"
        style={{ borderBottomColor: color }}
      >
        <div className="flex items-center justify-between">
          <span className="text-sm font-semibold text-gray-700">{title}</span>
          <span
            className="px-2 py-0.5 rounded-full text-xs font-bold"
            style={{
              backgroundColor: color + '20',
              color: color,
            }}
            aria-label={`${count} devis`}
          >
            {count}
          </span>
        </div>
      </div>

      {/* Cards container */}
      <div className="p-2 space-y-2 max-h-[500px] overflow-y-auto">
        {children}
      </div>
    </div>
  )
}
