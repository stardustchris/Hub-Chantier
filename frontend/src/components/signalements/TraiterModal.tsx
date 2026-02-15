/**
 * TraiterModal - Modal pour marquer un signalement comme traité
 * Extrait de SignalementDetail pour réduire la complexité
 */

import { useState } from 'react'
import { useFocusTrap } from '../../hooks/useFocusTrap'

interface TraiterModalProps {
  isOpen: boolean
  onClose: () => void
  onConfirm: (commentaire: string) => Promise<void>
  isLoading: boolean
}

export default function TraiterModal({
  isOpen,
  onClose,
  onConfirm,
  isLoading,
}: TraiterModalProps) {
  const [commentaire, setCommentaire] = useState('')
  const focusTrapRef = useFocusTrap({ enabled: isOpen, onClose })

  if (!isOpen) return null

  const handleConfirm = async () => {
    if (!commentaire.trim()) return
    await onConfirm(commentaire.trim())
    setCommentaire('')
  }

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4">
        <div
          className="fixed inset-0 bg-gray-500 bg-opacity-75"
          onClick={onClose}
          aria-hidden="true"
        />
        <div ref={focusTrapRef} role="dialog" aria-modal="true" aria-labelledby="modal-title" className="relative bg-white rounded-lg p-6 max-w-md w-full">
          <h3 id="modal-title" className="text-lg font-semibold text-gray-900 mb-4">
            Marquer comme traité
          </h3>
          <p className="text-sm text-gray-500 mb-3">Les champs marques <span className="text-red-500">*</span> sont obligatoires</p>
          <label htmlFor="commentaire-traite" className="block text-sm font-medium text-gray-700 mb-1">
            Commentaire de résolution <span className="text-red-500">*</span>
          </label>
          <textarea
            id="commentaire-traite"
            value={commentaire}
            onChange={(e) => setCommentaire(e.target.value)}
            placeholder="Décrivez comment le problème a été résolu..."
            rows={4}
            required
            aria-required="true"
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 mb-4"
          />
          <div className="flex justify-end gap-3">
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded hover:bg-gray-50"
            >
              Annuler
            </button>
            <button
              onClick={handleConfirm}
              disabled={isLoading || !commentaire.trim()}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded hover:bg-blue-700 disabled:opacity-50"
            >
              {isLoading ? 'Traitement...' : 'Confirmer'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
