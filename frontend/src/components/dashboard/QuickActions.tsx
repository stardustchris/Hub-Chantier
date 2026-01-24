/**
 * QuickActions - Boutons d'actions rapides
 * CDC Section 2.2 - Actions rapides contextuelles
 */

import { Clock, CheckCircle, FileText, Camera } from 'lucide-react'

interface QuickAction {
  id: string
  label: string
  icon: 'clock' | 'check' | 'file' | 'camera'
  color: string
  onClick?: () => void
}

interface QuickActionsProps {
  actions?: QuickAction[]
  onActionClick?: (actionId: string) => void
}

const defaultActions: QuickAction[] = [
  { id: 'hours', label: 'Mes heures', icon: 'clock', color: 'blue' },
  { id: 'tasks', label: 'Mes taches', icon: 'check', color: 'green' },
  { id: 'docs', label: 'Documents', icon: 'file', color: 'purple' },
  { id: 'photo', label: 'Photo', icon: 'camera', color: 'orange' },
]

const iconMap = {
  clock: Clock,
  check: CheckCircle,
  file: FileText,
  camera: Camera,
}

const colorMap = {
  blue: { bg: 'bg-blue-100', text: 'text-blue-600' },
  green: { bg: 'bg-green-100', text: 'text-green-600' },
  purple: { bg: 'bg-purple-100', text: 'text-purple-600' },
  orange: { bg: 'bg-orange-100', text: 'text-orange-600' },
}

export default function QuickActions({
  actions = defaultActions,
  onActionClick,
}: QuickActionsProps) {
  return (
    <div>
      <h2 className="font-semibold text-gray-800 mb-3">Actions rapides</h2>
      <div className="grid grid-cols-4 gap-3">
        {actions.map((action) => {
          const Icon = iconMap[action.icon]
          const colors = colorMap[action.color as keyof typeof colorMap] || colorMap.blue

          return (
            <button
              key={action.id}
              onClick={() => {
                action.onClick?.()
                onActionClick?.(action.id)
              }}
              className="bg-white rounded-2xl p-4 flex flex-col items-center shadow-md hover:shadow-lg transition-shadow"
            >
              <div className={`w-12 h-12 rounded-full ${colors.bg} flex items-center justify-center mb-2`}>
                <Icon className={`w-6 h-6 ${colors.text}`} />
              </div>
              <span className="text-sm text-gray-700 font-medium text-center">{action.label}</span>
            </button>
          )
        })}
      </div>
    </div>
  )
}
