/**
 * Page de gestion des Webhooks
 */

import { useState, useEffect, useCallback } from 'react'
import { webhooksApi } from '../api/webhooks'
import type { Webhook, WebhookDelivery, CreateWebhookRequest } from '../api/webhooks'
import Layout from '../components/Layout'
import {
  Webhook as WebhookIcon,
  Plus,
  Trash2,
  Loader2,
  Copy,
  CheckCircle2,
  AlertTriangle,
  Info,
  ExternalLink,
  Send,
  Clock,
  XCircle,
  ChevronRight,
} from 'lucide-react'
import { logger } from '../services/logger'

// Événements disponibles
const AVAILABLE_EVENTS = [
  '*',
  'chantier.*',
  'heures.*',
  'affectation.*',
  'signalement.*',
  'document.*',
]

export default function WebhooksPage() {
  const [webhooks, setWebhooks] = useState<Webhook[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showSecretModal, setShowSecretModal] = useState(false)
  const [showDeliveryModal, setShowDeliveryModal] = useState(false)
  const [selectedWebhook, setSelectedWebhook] = useState<Webhook | null>(null)
  const [newSecret, setNewSecret] = useState<string>('')
  const [newWebhook, setNewWebhook] = useState<Webhook | null>(null)
  const [secretCopied, setSecretCopied] = useState(false)

  // Charger les webhooks
  const loadWebhooks = useCallback(async () => {
    try {
      setIsLoading(true)
      const data = await webhooksApi.list()
      setWebhooks(data)
    } catch (error) {
      logger.error('Erreur chargement webhooks', error, {
        context: 'WebhooksPage',
        showToast: true,
      })
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    loadWebhooks()
  }, [loadWebhooks])

  // Copier secret dans presse-papier
  const copySecret = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(newSecret)
      setSecretCopied(true)
      setTimeout(() => setSecretCopied(false), 3000)
    } catch (error) {
      logger.error('Erreur copie presse-papier', error, {
        context: 'WebhooksPage',
        showToast: true,
      })
    }
  }, [newSecret])

  // Supprimer un webhook
  const deleteWebhook = useCallback(
    async (webhook: Webhook) => {
      if (
        !confirm(
          `Supprimer ce webhook?\n\nURL: ${webhook.url}\nÉvénements: ${webhook.events.join(', ')}\n\n⚠️ Cette action est irréversible.`
        )
      ) {
        return
      }

      try {
        await webhooksApi.delete(webhook.id)
        logger.info(`Webhook "${webhook.url}" supprimé`, {
          context: 'WebhooksPage',
          showToast: true,
        })
        loadWebhooks()
      } catch (error) {
        logger.error('Erreur suppression webhook', error, {
          context: 'WebhooksPage',
          showToast: true,
        })
      }
    },
    [loadWebhooks]
  )

  // Tester un webhook
  const testWebhook = useCallback(async (webhook: Webhook) => {
    try {
      await webhooksApi.test(webhook.id)
      logger.info('Test webhook envoyé', {
        context: 'WebhooksPage',
        showToast: true,
      })
      // Rafraîchir après 2 secondes pour voir le résultat
      setTimeout(() => {
        if (selectedWebhook?.id === webhook.id) {
          setSelectedWebhook(webhook)
        }
      }, 2000)
    } catch (error) {
      logger.error('Erreur test webhook', error, {
        context: 'WebhooksPage',
        showToast: true,
      })
    }
  }, [selectedWebhook])

  // Afficher l'historique des deliveries
  const viewDeliveries = useCallback((webhook: Webhook) => {
    setSelectedWebhook(webhook)
    setShowDeliveryModal(true)
  }, [])

  // Formater date
  const formatDate = (dateStr: string | undefined | null) => {
    if (!dateStr) return 'Jamais'
    return new Date(dateStr).toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  // Tronquer URL
  const truncateUrl = (url: string, maxLength = 50) => {
    if (url.length <= maxLength) return url
    return url.substring(0, maxLength) + '...'
  }

  return (
    <Layout>
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
              <WebhookIcon className="w-7 h-7" />
              Gestion des Webhooks
            </h1>
            <p className="text-sm text-gray-600 mt-1">
              Recevez des notifications en temps réel sur vos événements
            </p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="w-4 h-4" />
            Créer un Webhook
          </button>
        </div>
      </div>

      {/* Liste des webhooks */}
      {isLoading ? (
        <div className="flex justify-center items-center h-64">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        </div>
      ) : webhooks.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <WebhookIcon className="w-12 h-12 text-gray-400 mx-auto mb-3" />
          <p className="text-gray-600">Aucun webhook configuré</p>
          <p className="text-sm text-gray-500 mt-1">
            Créez votre premier webhook pour recevoir des notifications
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {webhooks.map((webhook) => (
            <div
              key={webhook.id}
              className={`border rounded-lg p-4 ${
                !webhook.is_active
                  ? 'bg-gray-50 border-gray-300 opacity-60'
                  : webhook.consecutive_failures > 0
                  ? 'bg-yellow-50 border-yellow-300'
                  : 'bg-white border-gray-200'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  {/* URL + Statut */}
                  <div className="flex items-center gap-2 mb-2">
                    <ExternalLink className="w-4 h-4 text-gray-400" />
                    <a
                      href={webhook.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="font-semibold text-gray-900 hover:text-blue-600"
                      title={webhook.url}
                    >
                      {truncateUrl(webhook.url)}
                    </a>
                    {webhook.is_active ? (
                      <span className="text-xs px-2 py-0.5 bg-green-100 text-green-700 rounded-full">
                        Actif
                      </span>
                    ) : (
                      <span className="text-xs px-2 py-0.5 bg-gray-200 text-gray-700 rounded-full">
                        Inactif
                      </span>
                    )}
                    {webhook.consecutive_failures > 0 && (
                      <span className="text-xs px-2 py-0.5 bg-yellow-200 text-yellow-800 rounded-full flex items-center gap-1">
                        <AlertTriangle className="w-3 h-3" />
                        {webhook.consecutive_failures} échec(s)
                      </span>
                    )}
                  </div>

                  {/* Description */}
                  {webhook.description && (
                    <p className="text-sm text-gray-600 mb-2">{webhook.description}</p>
                  )}

                  {/* Événements */}
                  <div className="mb-3">
                    <span className="text-sm text-gray-500">Événements: </span>
                    <div className="inline-flex flex-wrap gap-1 mt-1">
                      {webhook.events.map((event) => (
                        <span
                          key={event}
                          className="text-xs px-2 py-0.5 bg-blue-100 text-blue-700 rounded-full"
                        >
                          {event}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Infos */}
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-sm">
                    <div>
                      <span className="text-gray-500">Créé le:</span>
                      <p className="text-gray-900">{formatDate(webhook.created_at)}</p>
                    </div>
                    <div>
                      <span className="text-gray-500">Dernier déclenchement:</span>
                      <p className="text-gray-900">
                        {formatDate(webhook.last_triggered_at)}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div className="ml-4 flex gap-2">
                  <button
                    onClick={() => viewDeliveries(webhook)}
                    className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                    title="Voir l'historique"
                  >
                    <Clock className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => testWebhook(webhook)}
                    className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                    title="Tester"
                  >
                    <Send className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => deleteWebhook(webhook)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    title="Supprimer"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal Création */}
      {showCreateModal && (
        <CreateWebhookModal
          onClose={() => setShowCreateModal(false)}
          onCreated={(secret, webhook) => {
            setNewSecret(secret)
            setNewWebhook(webhook)
            setShowSecretModal(true)
            setShowCreateModal(false)
            loadWebhooks()
          }}
        />
      )}

      {/* Modal Secret (UNE FOIS) */}
      {showSecretModal && newWebhook && (
        <SecretModal
          secret={newSecret}
          webhook={newWebhook}
          copied={secretCopied}
          onCopy={copySecret}
          onClose={() => {
            setShowSecretModal(false)
            setNewSecret('')
            setNewWebhook(null)
            setSecretCopied(false)
          }}
        />
      )}

      {/* Modal Historique Deliveries */}
      {showDeliveryModal && selectedWebhook && (
        <DeliveryHistoryModal
          webhook={selectedWebhook}
          onClose={() => {
            setShowDeliveryModal(false)
            setSelectedWebhook(null)
          }}
        />
      )}
    </Layout>
  )
}

/**
 * Modal de création de webhook
 */
function CreateWebhookModal({
  onClose,
  onCreated,
}: {
  onClose: () => void
  onCreated: (secret: string, webhook: Webhook) => void
}) {
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

          {/* Événements prédéfinis */}
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

            {/* Événement personnalisé */}
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

            {/* Événements sélectionnés */}
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

/**
 * Modal d'affichage du secret (UNE FOIS)
 */
function SecretModal({
  secret,
  webhook,
  copied,
  onCopy,
  onClose,
}: {
  secret: string
  webhook: Webhook
  copied: boolean
  onCopy: () => void
  onClose: () => void
}) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-2xl w-full p-6">
        {/* Succès */}
        <div className="bg-green-50 border-l-4 border-green-400 p-4 mb-4">
          <div className="flex items-start">
            <CheckCircle2 className="w-5 h-5 text-green-600 mt-0.5 mr-3" />
            <div>
              <h3 className="text-sm font-medium text-green-800 mb-1">
                Webhook créé avec succès!
              </h3>
              <p className="text-sm text-green-700">
                Votre webhook est maintenant actif et prêt à recevoir des événements.
              </p>
            </div>
          </div>
        </div>

        {/* Alerte Secret */}
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-4">
          <div className="flex items-start">
            <AlertTriangle className="w-5 h-5 text-yellow-600 mt-0.5 mr-3" />
            <div>
              <h3 className="text-sm font-medium text-yellow-800 mb-1">
                Votre secret (copiez-le maintenant, il ne sera plus affiché)
              </h3>
              <p className="text-sm text-yellow-700">
                Stockez ce secret de manière sécurisée. Vous en aurez besoin pour vérifier les signatures HMAC des événements.
              </p>
            </div>
          </div>
        </div>

        {/* Secret */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Secret Webhook
          </label>
          <div className="flex gap-2">
            <div className="flex-1 font-mono text-sm bg-gray-100 px-3 py-2 rounded-lg border border-gray-300 overflow-x-auto">
              {secret}
            </div>
            <button
              onClick={onCopy}
              className={`px-4 py-2 rounded-lg transition-colors flex items-center gap-2 ${
                copied
                  ? 'bg-green-600 text-white'
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              }`}
            >
              {copied ? (
                <>
                  <CheckCircle2 className="w-4 h-4" />
                  Copié
                </>
              ) : (
                <>
                  <Copy className="w-4 h-4" />
                  Copier
                </>
              )}
            </button>
          </div>
        </div>

        {/* Infos Webhook */}
        <div className="bg-gray-50 rounded-lg p-4 mb-4">
          <h4 className="text-sm font-medium text-gray-900 mb-2">Détails du webhook</h4>
          <dl className="space-y-1 text-sm">
            <div className="flex">
              <dt className="text-gray-500 w-24">URL:</dt>
              <dd className="text-gray-900 font-mono break-all">{webhook.url}</dd>
            </div>
            <div className="flex">
              <dt className="text-gray-500 w-24">Événements:</dt>
              <dd className="text-gray-900">{webhook.events.join(', ')}</dd>
            </div>
          </dl>
        </div>

        {/* Documentation */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
          <div className="flex items-start">
            <Info className="w-5 h-5 text-blue-600 mt-0.5 mr-3" />
            <div className="text-sm text-blue-800">
              <p className="font-medium mb-1">Vérification de signature HMAC-SHA256</p>
              <code className="block bg-white px-2 py-1 rounded text-xs mt-2 overflow-x-auto">
                const signature = req.headers['x-webhook-signature']<br/>
                const computed = crypto.createHmac('sha256', secret).update(body).digest('hex')<br/>
                const valid = signature === computed
              </code>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors"
          >
            Fermer
          </button>
        </div>
      </div>
    </div>
  )
}

/**
 * Modal Historique des Deliveries
 */
function DeliveryHistoryModal({
  webhook,
  onClose,
}: {
  webhook: Webhook
  onClose: () => void
}) {
  const [deliveries, setDeliveries] = useState<WebhookDelivery[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const loadDeliveries = async () => {
      try {
        setIsLoading(true)
        const data = await webhooksApi.deliveries(webhook.id)
        setDeliveries(data)
      } catch (error) {
        logger.error('Erreur chargement deliveries', error, {
          context: 'DeliveryHistoryModal',
          showToast: true,
        })
      } finally {
        setIsLoading(false)
      }
    }
    loadDeliveries()
  }, [webhook.id])

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    })
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full p-6 max-h-[90vh] flex flex-col">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xl font-bold">Historique des Deliveries</h2>
            <p className="text-sm text-gray-600 font-mono mt-1">{webhook.url}</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <XCircle className="w-5 h-5" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto">
          {isLoading ? (
            <div className="flex justify-center items-center h-64">
              <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
            </div>
          ) : deliveries.length === 0 ? (
            <div className="text-center py-12 bg-gray-50 rounded-lg">
              <Clock className="w-12 h-12 text-gray-400 mx-auto mb-3" />
              <p className="text-gray-600">Aucune delivery pour ce webhook</p>
            </div>
          ) : (
            <div className="space-y-2">
              {deliveries.map((delivery) => (
                <div
                  key={delivery.id}
                  className={`border rounded-lg p-3 ${
                    delivery.success
                      ? 'bg-green-50 border-green-200'
                      : 'bg-red-50 border-red-200'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        {delivery.success ? (
                          <CheckCircle2 className="w-4 h-4 text-green-600" />
                        ) : (
                          <XCircle className="w-4 h-4 text-red-600" />
                        )}
                        <span className="font-mono text-sm font-medium">
                          {delivery.event_type}
                        </span>
                        {delivery.attempt > 1 && (
                          <span className="text-xs px-2 py-0.5 bg-yellow-100 text-yellow-800 rounded-full">
                            Tentative {delivery.attempt}
                          </span>
                        )}
                      </div>

                      <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
                        <div>
                          <span className="text-gray-500">Date:</span>
                          <p className="text-gray-900">{formatDate(delivery.delivered_at)}</p>
                        </div>
                        {delivery.status_code && (
                          <div>
                            <span className="text-gray-500">Statut HTTP:</span>
                            <p className="text-gray-900">{delivery.status_code}</p>
                          </div>
                        )}
                        {delivery.response_time_ms !== undefined && (
                          <div>
                            <span className="text-gray-500">Temps:</span>
                            <p className="text-gray-900">{delivery.response_time_ms} ms</p>
                          </div>
                        )}
                        <div>
                          <span className="text-gray-500">Résultat:</span>
                          <p
                            className={
                              delivery.success ? 'text-green-700' : 'text-red-700'
                            }
                          >
                            {delivery.success ? 'Succès' : 'Échec'}
                          </p>
                        </div>
                      </div>

                      {delivery.error_message && (
                        <div className="mt-2 text-xs">
                          <span className="text-gray-500">Erreur: </span>
                          <span className="text-red-700 font-mono">
                            {delivery.error_message}
                          </span>
                        </div>
                      )}
                    </div>

                    <ChevronRight className="w-4 h-4 text-gray-400 ml-2" />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="flex justify-end mt-4 pt-4 border-t">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors"
          >
            Fermer
          </button>
        </div>
      </div>
    </div>
  )
}
