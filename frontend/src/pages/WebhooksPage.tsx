/**
 * Page de gestion des Webhooks
 */

import Layout from '../components/Layout'
import {
  Webhook as WebhookIcon,
  Plus,
  Trash2,
  Loader2,
  ExternalLink,
  Send,
  Clock,
  AlertTriangle,
} from 'lucide-react'
import { useWebhooks } from '../hooks/useWebhooks'
import { CreateWebhookModal, SecretModal, DeliveryHistoryModal } from '../components/webhooks'

export default function WebhooksPage() {
  const {
    webhooks,
    isLoading,
    showCreateModal,
    showSecretModal,
    showDeliveryModal,
    selectedWebhook,
    newSecret,
    newWebhook,
    secretCopied,
    setShowCreateModal,
    copySecret,
    deleteWebhook,
    testWebhook,
    viewDeliveries,
    onWebhookCreated,
    closeSecretModal,
    closeDeliveryModal,
    formatDate,
    truncateUrl,
  } = useWebhooks()

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

                  {/* Evenements */}
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

      {/* Modal Creation */}
      {showCreateModal && (
        <CreateWebhookModal
          onClose={() => setShowCreateModal(false)}
          onCreated={onWebhookCreated}
        />
      )}

      {/* Modal Secret (UNE FOIS) */}
      {showSecretModal && newWebhook && (
        <SecretModal
          secret={newSecret}
          webhook={newWebhook}
          copied={secretCopied}
          onCopy={copySecret}
          onClose={closeSecretModal}
        />
      )}

      {/* Modal Historique Deliveries */}
      {showDeliveryModal && selectedWebhook && (
        <DeliveryHistoryModal
          webhook={selectedWebhook}
          onClose={closeDeliveryModal}
        />
      )}
    </Layout>
  )
}
