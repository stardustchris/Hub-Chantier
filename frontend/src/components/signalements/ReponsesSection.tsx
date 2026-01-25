/**
 * ReponsesSection - Section des réponses d'un signalement
 * Extrait de SignalementDetail pour réduire la complexité
 */

import { useState } from 'react'
import type { Reponse } from '../../types/signalements'
import { formatDateDayMonthYearTime } from '../../utils/dates'

interface ReponsesSectionProps {
  reponses: Reponse[]
  canReply: boolean
  onAddReponse: (contenu: string) => Promise<void>
}

export default function ReponsesSection({
  reponses,
  canReply,
  onAddReponse,
}: ReponsesSectionProps) {
  const [newReponse, setNewReponse] = useState('')
  const [sending, setSending] = useState(false)

  const handleSubmit = async () => {
    if (!newReponse.trim()) return

    setSending(true)
    try {
      await onAddReponse(newReponse.trim())
      setNewReponse('')
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="border-t border-gray-200 pt-6">
      <h3 className="text-sm font-medium text-gray-700 mb-4">
        Réponses ({reponses.length})
      </h3>

      {reponses.length === 0 ? (
        <p className="text-gray-500 text-sm mb-4">Aucune réponse pour le moment.</p>
      ) : (
        <div className="space-y-4 mb-4">
          {reponses.map((reponse) => (
            <div
              key={reponse.id}
              className={`p-4 rounded-lg ${
                reponse.est_resolution
                  ? 'bg-green-50 border border-green-200'
                  : 'bg-gray-50 border border-gray-200'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-900">
                  {reponse.auteur_nom || `Utilisateur #${reponse.auteur_id}`}
                </span>
                <span className="text-xs text-gray-500">
                  {formatDateDayMonthYearTime(reponse.created_at)}
                </span>
              </div>
              <p className="text-sm text-gray-700 whitespace-pre-wrap">{reponse.contenu}</p>
              {reponse.photo_url && (
                <img
                  src={reponse.photo_url}
                  alt="Photo de la réponse"
                  className="mt-2 max-w-xs h-auto rounded border border-gray-200"
                />
              )}
              {reponse.est_resolution && (
                <span className="inline-block mt-2 px-2 py-0.5 text-xs font-medium text-green-800 bg-green-200 rounded">
                  Résolution
                </span>
              )}
            </div>
          ))}
        </div>
      )}

      {canReply && (
        <div className="flex gap-2">
          <textarea
            value={newReponse}
            onChange={(e) => setNewReponse(e.target.value)}
            placeholder="Ajouter une réponse..."
            rows={2}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 text-sm"
          />
          <button
            onClick={handleSubmit}
            disabled={sending || !newReponse.trim()}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed self-end"
          >
            {sending ? '...' : 'Envoyer'}
          </button>
        </div>
      )}
    </div>
  )
}
