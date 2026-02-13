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
  badge?: string
  onClick?: () => void
}

interface QuickActionsProps {
  actions?: QuickAction[]
  onActionClick?: (actionId: string) => void
  tasksBadge?: string
}

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

const defaultActions: QuickAction[] = [
  { id: 'hours', label: 'Mes heures', icon: 'clock', color: 'blue' },
  { id: 'tasks', label: 'Mes taches', icon: 'check', color: 'green' },
  { id: 'docs', label: 'Documents', icon: 'file', color: 'purple' },
  { id: 'photo', label: 'Photo', icon: 'camera', color: 'orange' },
]

export default function QuickActions({
  actions,
  onActionClick,
  tasksBadge,
}: QuickActionsProps) {
  const displayActions = actions || defaultActions.map(a => {
    if (a.id === 'tasks' && tasksBadge) {
      return { ...a, badge: tasksBadge }
    }
    return a
  })

  return (
    <div>
      <h2 className="font-semibold text-gray-800 mb-3">Actions rapides</h2>
      <div className="grid grid-cols-4 gap-3">
        {displayActions.map((action) => {
          const Icon = iconMap[action.icon]
          const colors = colorMap[action.color as keyof typeof colorMap] || colorMap.blue

          return (
            <button
              key={action.id}
              onClick={() => {
                action.onClick?.()
                onActionClick?.(action.id)
              }}
              className="bg-white rounded-2xl p-4 flex flex-col items-center shadow-md hover-lift relative min-w-[56px] min-h-[56px]"
            >
              <div className={`w-14 h-14 rounded-full ${colors.bg} flex items-center justify-center mb-2 relative`}>
                <Icon className={`w-6 h-6 ${colors.text}`} />
                {action.badge && (
                  <span className="absolute -top-1 -right-1 bg-green-600 text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center">
                    {action.badge}
                  </span>
                )}
              </div>
              <span className="text-sm text-gray-700 font-medium text-center">{action.label}</span>
            </button>
          )
        })}
      </div>
    </div>
  )
}
