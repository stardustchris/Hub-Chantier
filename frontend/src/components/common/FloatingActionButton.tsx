/**
 * FloatingActionButton - Bouton d'actions rapides mobiles
 * Phase 1 UX - Urgences terrain
 */

import { useState } from 'react'
import { Clock, Camera, AlertTriangle, ClipboardList, Plus, X } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

interface FABAction {
  id: string
  label: string
  icon: typeof Clock
  color: string
  href?: string
  onClick?: () => void
}

const actions: FABAction[] = [
  { id: 'pointer', label: 'Pointer', icon: Clock, color: 'bg-green-600', href: '/feuilles-heures' },
  { id: 'photo', label: 'Photo rapide', icon: Camera, color: 'bg-orange-500' },
  { id: 'signalement', label: 'Signalement', icon: AlertTriangle, color: 'bg-red-600' },
  { id: 'saisir', label: 'Saisir heures', icon: ClipboardList, color: 'bg-blue-600', href: '/feuilles-heures' },
]

export default function FloatingActionButton() {
  const [isOpen, setIsOpen] = useState(false)
  const navigate = useNavigate()

  const handleAction = (action: FABAction) => {
    if (action.href) {
      navigate(action.href)
    } else if (action.onClick) {
      action.onClick()
    }
    setIsOpen(false)
  }

  return (
    <>
      {/* Overlay sombre quand menu ouvert */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/30 z-40 lg:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Menu des actions (apparait vers le haut) */}
      {isOpen && (
        <nav aria-label="Actions rapides" className="fixed bottom-24 right-4 z-50 flex flex-col gap-3 lg:hidden">
          {actions.map((action, index) => {
            const Icon = action.icon
            return (
              <button
                key={action.id}
                onClick={() => handleAction(action)}
                className={`${action.color} text-white rounded-full shadow-lg flex items-center gap-3 pr-4 pl-2 py-2 transition-all animate-fade-in`}
                style={{
                  animationDelay: `${index * 50}ms`,
                  animationFillMode: 'both',
                }}
                aria-label={action.label}
              >
                <div className="w-12 h-12 flex items-center justify-center">
                  <Icon className="w-6 h-6" />
                </div>
                <span className="font-medium text-sm whitespace-nowrap">{action.label}</span>
              </button>
            )
          })}
        </nav>
      )}

      {/* Bouton principal FAB */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`fixed bottom-4 right-4 z-50 w-14 h-14 rounded-full shadow-xl flex items-center justify-center transition-all lg:hidden ${
          isOpen ? 'bg-gray-800 rotate-45' : 'bg-primary-600'
        }`}
        aria-label={isOpen ? 'Fermer le menu' : 'Actions rapides'}
        aria-expanded={isOpen}
      >
        {isOpen ? (
          <X className="w-6 h-6 text-white" />
        ) : (
          <Plus className="w-6 h-6 text-white" />
        )}
      </button>
    </>
  )
}
