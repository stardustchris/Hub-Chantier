import { useState } from 'react'
import {
  Send,
  CheckCircle,
  RotateCcw,
  ThumbsUp,
  ThumbsDown,
  XCircle,
  Loader2,
} from 'lucide-react'
import type { StatutDevis } from '../../types'

interface DevisWorkflowActionsProps {
  statut: StatutDevis
  onSoumettre?: () => Promise<void>
  onValider?: () => Promise<void>
  onRetournerBrouillon?: () => Promise<void>
  onAccepter?: () => Promise<void>
  onRefuser?: (motif?: string) => Promise<void>
  onPerdu?: (motif?: string) => Promise<void>
}

interface ActionButton {
  label: string
  icon: typeof Send
  color: string
  bgColor: string
  action: () => Promise<void>
}

export default function DevisWorkflowActions({
  statut,
  onSoumettre,
  onValider,
  onRetournerBrouillon,
  onAccepter,
  onRefuser,
  onPerdu,
}: DevisWorkflowActionsProps) {
  const [loading, setLoading] = useState<string | null>(null)
  const [showMotifModal, setShowMotifModal] = useState<{ action: string; callback: (motif?: string) => Promise<void> } | null>(null)
  const [motif, setMotif] = useState('')

  const handleAction = async (key: string, action: () => Promise<void>) => {
    try {
      setLoading(key)
      await action()
    } finally {
      setLoading(null)
    }
  }

  const handleMotifAction = async () => {
    if (!showMotifModal || !motif.trim()) return
    try {
      setLoading(showMotifModal.action)
      await showMotifModal.callback(motif)
    } finally {
      setLoading(null)
      setShowMotifModal(null)
      setMotif('')
    }
  }

  const getActions = (): ActionButton[] => {
    const actions: ActionButton[] = []

    switch (statut) {
      case 'brouillon':
        if (onSoumettre) {
          actions.push({
            label: 'Soumettre en validation',
            icon: Send,
            color: '#F59E0B',
            bgColor: '#FEF3C7',
            action: () => handleAction('soumettre', onSoumettre),
          })
        }
        break

      case 'en_validation':
        if (onValider) {
          actions.push({
            label: 'Valider et envoyer',
            icon: CheckCircle,
            color: '#10B981',
            bgColor: '#D1FAE5',
            action: () => handleAction('valider', onValider),
          })
        }
        if (onRetournerBrouillon) {
          actions.push({
            label: 'Retourner en brouillon',
            icon: RotateCcw,
            color: '#6B7280',
            bgColor: '#F3F4F6',
            action: () => handleAction('retourner', onRetournerBrouillon),
          })
        }
        break

      case 'envoye':
      case 'vu':
      case 'en_negociation':
        if (onAccepter) {
          actions.push({
            label: 'Accepter',
            icon: ThumbsUp,
            color: '#059669',
            bgColor: '#D1FAE5',
            action: () => handleAction('accepter', onAccepter),
          })
        }
        if (onRefuser) {
          actions.push({
            label: 'Refuser',
            icon: ThumbsDown,
            color: '#EF4444',
            bgColor: '#FEE2E2',
            action: async () => {
              setShowMotifModal({ action: 'refuser', callback: onRefuser })
            },
          })
        }
        if (statut === 'en_negociation' && onPerdu) {
          actions.push({
            label: 'Marquer perdu',
            icon: XCircle,
            color: '#991B1B',
            bgColor: '#FEE2E2',
            action: async () => {
              setShowMotifModal({ action: 'perdu', callback: onPerdu })
            },
          })
        }
        break
    }

    return actions
  }

  const actions = getActions()
  if (actions.length === 0) return null

  return (
    <>
      <div className="flex flex-wrap gap-2">
        {actions.map((action) => {
          const Icon = action.icon
          const isLoading = loading !== null
          return (
            <button
              key={action.label}
              onClick={action.action}
              disabled={isLoading}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
              style={{
                backgroundColor: action.bgColor,
                color: action.color,
              }}
            >
              {loading === action.label ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Icon className="w-4 h-4" />
              )}
              {action.label}
            </button>
          )
        })}
      </div>

      {/* Modal motif */}
      {showMotifModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className="bg-white rounded-xl shadow-xl p-6 w-full max-w-md mx-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              {showMotifModal.action === 'refuser' ? 'Motif du refus' : 'Motif de la perte'}
            </h3>
            <textarea
              value={motif}
              onChange={(e) => setMotif(e.target.value)}
              placeholder="Indiquez le motif (obligatoire)..."
              maxLength={1000}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              rows={3}
            />
            <div className="flex justify-end gap-2 mt-4">
              <button
                onClick={() => { setShowMotifModal(null); setMotif('') }}
                className="px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg"
              >
                Annuler
              </button>
              <button
                onClick={handleMotifAction}
                disabled={loading !== null || !motif.trim()}
                className="px-4 py-2 text-sm text-white bg-red-600 hover:bg-red-700 rounded-lg disabled:opacity-50"
              >
                {loading ? 'En cours...' : 'Confirmer'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
