/**
 * Modal de creation de webhook
 */

import { useState } from 'react'
import { webhooksApi } from '../../api/webhooks'
import type { Webhook, CreateWebhookRequest } from '../../api/webhooks'
import { Plus, Loader2, XCircle } from 'lucide-react'
import { logger } from '../../services/logger'

// Evenements disponibles
const AVAILABLE_EVENTS = [
  '*',
  'chantier.*',
  'heures.*',
  'affectation.*',
  'signalement.*',
  'document.*',
]

interface CreateWebhookModalProps {
  onClose: () => void
  onCreated: (secret: string, webhook: Webhook) => void
}

export default function CreateWebhookModal({ onClose, onCreated }: CreateWebhookModalProps) {
  const [url, setUrl] = useState('')
  const [description, setDescription] = useState('')
  const [selectedEvents, setSelectedEvents] = useState<string[]>([])
  const [customEvent, setCustomEvent] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const toggleEvent = (event: string) => {
    setSelectedEvents((prev) =>
      prev.includes(event) ? prev.filter((e) => e !== event) : [...prev, event]
    )
  }

  const addCustomEvent = () => {
    if (customEvent.trim() && !selectedEvents.includes(customEvent.trim())) {
      setSelectedEvents((prev) => [...prev, customEvent.trim()])
      setCustomEvent('')
    }
  }

  const removeEvent = (event: string) => {
    setSelectedEvents((prev) => prev.filter((e) => e !== event))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    // Validation URL HTTPS
    if (!url.trim()) {
      alert('L\'URL est requise')
      return
    }

    try {
      const urlObj = new URL(url)
      if (urlObj.protocol !== 'https:') {
        alert('L\'URL doit utiliser HTTPS')
        return
      }
    } catch {
      alert('URL invalide')
      return
    }

    if (selectedEvents.length === 0) {
      alert('Au moins un événement est requis')
      return
    }

    try {
      setIsSubmitting(true)
      const data: CreateWebhookRequest = {
        url: url.trim(),
        events: selectedEvents,
        description: description.trim() || undefined,
      }
      const result = await webhooksApi.create(data)
      onCreated(result.secret, result.webhook)
    } catch (error) {
      logger.error('Erreur création webhook', error, {
        context: 'CreateWebhookModal',
        showToast: true,
      })
      setIsSubmitting(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-lg w-full p-6 max-h-[90vh] overflow-y-auto">
        <h2 className="text-xl font-bold mb-4">Créer un Webhook</h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* URL */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              URL <span className="text-red-500">*</span>
            </label>
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="https://example.com/webhook"
              required
            />
            <p className="text-xs text-gray-500 mt-1">
              Doit utiliser HTTPS pour la sécurité
            </p>
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description (optionnel)
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Synchronisation avec système externe..."
              rows={2}
            />
          </div>

          {/* Evenements predefinis */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Événements <span className="text-red-500">*</span>
            </label>
            <div className="grid grid-cols-2 gap-2 mb-2">
              {AVAILABLE_EVENTS.map((event) => (
                <label
                  key={event}
                  className="flex items-center gap-2 p-2 border rounded cursor-pointer hover:bg-gray-50"
                >
                  <input
                    type="checkbox"
                    checked={selectedEvents.includes(event)}
                    onChange={() => toggleEvent(event)}
                    className="w-4 h-4 text-blue-600"
                  />
                  <span className="text-sm font-mono">{event}</span>
                </label>
              ))}
            </div>

            {/* Evenement personnalise */}
            <div className="flex gap-2">
              <input
                type="text"
                value={customEvent}
                onChange={(e) => setCustomEvent(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addCustomEvent())}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                placeholder="Pattern personnalisé..."
              />
              <button
                type="button"
                onClick={addCustomEvent}
                className="px-3 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors text-sm"
              >
                Ajouter
              </button>
            </div>

            {/* Evenements selectionnes */}
            {selectedEvents.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-1">
                {selectedEvents.map((event) => (
                  <span
                    key={event}
                    className="inline-flex items-center gap-1 text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded-full"
                  >
                    <span className="font-mono">{event}</span>
                    <button
                      type="button"
                      onClick={() => removeEvent(event)}
                      className="hover:text-blue-900"
                    >
                      <XCircle className="w-3 h-3" />
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              disabled={isSubmitting}
            >
              Annuler
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2 disabled:opacity-50"
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Création...
                </>
              ) : (
                <>
                  <Plus className="w-4 h-4" />
                  Créer
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
