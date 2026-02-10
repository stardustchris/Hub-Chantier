/**
 * AchatWorkflowActions - Boutons d'actions du workflow achat (FIN-06)
 *
 * Affiche les boutons correspondant au statut de l'achat :
 * - demande -> Valider / Refuser
 * - valide -> Commander
 * - commande -> Livrer
 * - livre -> Facturer
 */

import { useState } from 'react'
import { Check, X, ShoppingCart, Truck, FileText, Loader2 } from 'lucide-react'
import { financierService } from '../../services/financier'
import { useToast } from '../../contexts/ToastContext'
import { logger } from '../../services/logger'
import type { Achat, StatutAchat } from '../../types'

interface AchatWorkflowActionsProps {
  achat: Achat
  onUpdate: (updatedAchat: Achat) => void
}

export default function AchatWorkflowActions({ achat, onUpdate }: AchatWorkflowActionsProps) {
  const { addToast } = useToast()
  const [loading, setLoading] = useState(false)
  const [showRefusModal, setShowRefusModal] = useState(false)
  const [showFactureModal, setShowFactureModal] = useState(false)
  const [motifRefus, setMotifRefus] = useState('')
  const [numeroFacture, setNumeroFacture] = useState('')

  const executeAction = async (
    action: () => Promise<Achat>,
    successMessage: string
  ) => {
    try {
      setLoading(true)
      const updated = await action()
      onUpdate(updated)
      addToast({ message: successMessage, type: 'success' })
    } catch (err) {
      logger.error('Erreur action achat', err, { context: 'AchatWorkflowActions' })
      addToast({ message: 'Erreur lors de l\'action', type: 'error' })
    } finally {
      setLoading(false)
    }
  }

  const handleRefuser = async () => {
    if (!motifRefus.trim()) return
    await executeAction(
      () => financierService.refuserAchat(achat.id, motifRefus),
      'Achat refuse'
    )
    setShowRefusModal(false)
    setMotifRefus('')
  }

  const handleFacturer = async () => {
    if (!numeroFacture.trim()) return
    await executeAction(
      () => financierService.facturerAchat(achat.id, numeroFacture),
      'Achat facture'
    )
    setShowFactureModal(false)
    setNumeroFacture('')
  }

  const actions: Record<StatutAchat, React.ReactNode> = {
    demande: (
      <div className="flex gap-1">
        <button
          onClick={() => executeAction(() => financierService.validerAchat(achat.id), 'Achat valide')}
          disabled={loading}
          className="flex items-center gap-1 px-2 py-1 text-xs bg-green-100 text-green-700 hover:bg-green-200 rounded transition-colors disabled:opacity-50"
          title="Valider" aria-label="Valider l'achat"
        >
          {loading ? <Loader2 size={12} className="animate-spin" /> : <Check size={12} />}
          Valider
        </button>
        <button
          onClick={() => setShowRefusModal(true)}
          disabled={loading}
          className="flex items-center gap-1 px-2 py-1 text-xs bg-red-100 text-red-700 hover:bg-red-200 rounded transition-colors disabled:opacity-50"
          title="Refuser" aria-label="Refuser l'achat"
        >
          <X size={12} />
          Refuser
        </button>
      </div>
    ),
    valide: (
      <button
        onClick={() => executeAction(() => financierService.commanderAchat(achat.id), 'Achat commande')}
        disabled={loading}
        className="flex items-center gap-1 px-2 py-1 text-xs bg-blue-100 text-blue-700 hover:bg-blue-200 rounded transition-colors disabled:opacity-50"
        title="Commander" aria-label="Commander l'achat"
      >
        {loading ? <Loader2 size={12} className="animate-spin" /> : <ShoppingCart size={12} />}
        Commander
      </button>
    ),
    commande: (
      <button
        onClick={() => executeAction(() => financierService.livrerAchat(achat.id), 'Achat livre')}
        disabled={loading}
        className="flex items-center gap-1 px-2 py-1 text-xs bg-purple-100 text-purple-700 hover:bg-purple-200 rounded transition-colors disabled:opacity-50"
        title="Livrer" aria-label="Marquer l'achat comme livre"
      >
        {loading ? <Loader2 size={12} className="animate-spin" /> : <Truck size={12} />}
        Livrer
      </button>
    ),
    livre: (
      <button
        onClick={() => setShowFactureModal(true)}
        disabled={loading}
        className="flex items-center gap-1 px-2 py-1 text-xs bg-gray-100 text-gray-700 hover:bg-gray-200 rounded transition-colors disabled:opacity-50"
        title="Facturer" aria-label="Facturer l'achat"
      >
        <FileText size={12} />
        Facturer
      </button>
    ),
    refuse: null,
    facture: null,
  }

  return (
    <>
      {actions[achat.statut]}

      {/* Modal refus */}
      {showRefusModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" onClick={() => setShowRefusModal(false)}>
          <div className="bg-white rounded-lg shadow-xl max-w-sm w-full p-6" onClick={e => e.stopPropagation()}>
            <h3 className="font-semibold text-gray-900 mb-3">Motif du refus</h3>
            <textarea
              value={motifRefus}
              onChange={(e) => setMotifRefus(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
              placeholder="Saisissez le motif du refus..."
              rows={3}
              autoFocus
            />
            <div className="flex justify-end gap-2 mt-4">
              <button
                onClick={() => setShowRefusModal(false)}
                className="px-3 py-1.5 text-gray-600 hover:bg-gray-100 rounded text-sm"
              >
                Annuler
              </button>
              <button
                onClick={handleRefuser}
                disabled={!motifRefus.trim() || loading}
                className="px-3 py-1.5 bg-red-600 text-white rounded hover:bg-red-700 text-sm disabled:opacity-50"
              >
                {loading ? 'Refus en cours...' : 'Confirmer le refus'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal facturation */}
      {showFactureModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" onClick={() => setShowFactureModal(false)}>
          <div className="bg-white rounded-lg shadow-xl max-w-sm w-full p-6" onClick={e => e.stopPropagation()}>
            <h3 className="font-semibold text-gray-900 mb-3">Numero de facture</h3>
            <input
              type="text"
              value={numeroFacture}
              onChange={(e) => setNumeroFacture(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Ex: FAC-2026-001"
              autoFocus
            />
            <div className="flex justify-end gap-2 mt-4">
              <button
                onClick={() => setShowFactureModal(false)}
                className="px-3 py-1.5 text-gray-600 hover:bg-gray-100 rounded text-sm"
              >
                Annuler
              </button>
              <button
                onClick={handleFacturer}
                disabled={!numeroFacture.trim() || loading}
                className="px-3 py-1.5 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm disabled:opacity-50"
              >
                {loading ? 'Enregistrement...' : 'Enregistrer la facture'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
