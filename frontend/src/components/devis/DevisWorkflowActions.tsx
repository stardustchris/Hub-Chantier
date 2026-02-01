import { useState } from 'react'
import {
  Send,
  CheckCircle,
  Eye,
  MessageSquare,
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
  onEnvoyer?: () => Promise<void>
  onMarquerVu?: () => Promise<void>
  onNegocier?: () => Promise<void>
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
  needsMotif?: boolean
}

export default function DevisWorkflowActions({
  statut,
  onSoumettre,
  onValider,
  onEnvoyer,
  onMarquerVu,
  onNegocier,
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
    if (!showMotifModal) return
    try {
      setLoading(showMotifModal.action)
      await showMotifModal.callback(motif || undefined)
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
            label: 'Approuver',
            icon: CheckCircle,
            color: '#10B981',
            bgColor: '#D1FAE5',
            action: () => handleAction('valider', onValider),
          })
        }
        break

      case 'approuve':
        if (onEnvoyer) {
          actions.push({
            label: 'Envoyer au client',
            icon: Send,
            color: '#3B82F6',
            bgColor: '#DBEAFE',
            action: () => handleAction('envoyer', onEnvoyer),
          })
        }
        break

      case 'envoye':
        if (onMarquerVu) {
          actions.push({
            label: 'Marquer comme vu',
            icon: Eye,
            color: '#8B5CF6',
            bgColor: '#EDE9FE',
            action: () => handleAction('vu', onMarquerVu),
          })
        }
        break

      case 'vu':
        if (onNegocier) {
          actions.push({
            label: 'En negociation',
            icon: MessageSquare,
            color: '#F97316',
            bgColor: '#FED7AA',
            action: () => handleAction('negocier', onNegocier),
          })
        }
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
        break

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
        if (onPerdu) {
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
              placeholder="Indiquez le motif (optionnel)..."
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
                disabled={loading !== null}
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
