import { useState, useRef, useEffect } from 'react'
import { MoreVertical, Edit2, Trash2, Copy, ArrowUp, ArrowDown, MessageSquare } from 'lucide-react'

interface Props {
  onEdit: () => void
  onDelete: () => void
  onDuplicate: () => void
  onMoveUp?: () => void
  onMoveDown?: () => void
  onAddNote?: () => void
}

export default function LineKebabMenu({ onEdit, onDelete, onDuplicate, onMoveUp, onMoveDown, onAddNote }: Props) {
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  const items: Array<{ label: string; icon: typeof Edit2; action: () => void; danger?: boolean }> = [
    { label: 'Editer', icon: Edit2, action: onEdit },
    { label: 'Dupliquer', icon: Copy, action: onDuplicate },
    ...(onMoveUp ? [{ label: 'Monter', icon: ArrowUp, action: onMoveUp }] : []),
    ...(onMoveDown ? [{ label: 'Descendre', icon: ArrowDown, action: onMoveDown }] : []),
    ...(onAddNote ? [{ label: 'Ajouter note', icon: MessageSquare, action: onAddNote }] : []),
    { label: 'Supprimer', icon: Trash2, action: onDelete, danger: true },
  ]

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setOpen(!open)}
        className="text-gray-600 hover:text-gray-800 p-1"
      >
        <MoreVertical className="w-4 h-4" />
      </button>
      {open && (
        <div className="absolute right-0 top-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-50 py-1 w-44">
          {items.map(item => (
            <button
              key={item.label}
              onClick={() => { item.action(); setOpen(false) }}
              className={`w-full flex items-center gap-2 px-3 py-2 text-sm hover:bg-gray-50 ${
                item.danger ? 'text-red-600 hover:bg-red-50' : 'text-gray-700'
              }`}
            >
              <item.icon className="w-4 h-4" />
              {item.label}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
