/**
 * Modal Historique des Deliveries
 */

import { useState, useEffect } from 'react'
import { webhooksApi } from '../../api/webhooks'
import type { Webhook, WebhookDelivery } from '../../api/webhooks'
import {
  Loader2,
  CheckCircle2,
  Clock,
  XCircle,
  ChevronRight,
} from 'lucide-react'
import { logger } from '../../services/logger'
import { useFocusTrap } from '../../hooks/useFocusTrap'

interface DeliveryHistoryModalProps {
  webhook: Webhook
  onClose: () => void
}

export default function DeliveryHistoryModal({ webhook, onClose }: DeliveryHistoryModalProps) {
  const focusTrapRef = useFocusTrap({ enabled: true, onClose })
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
    <div ref={focusTrapRef} className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
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
              <Clock className="w-12 h-12 text-gray-600 mx-auto mb-3" />
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

                    <ChevronRight className="w-4 h-4 text-gray-600 ml-2" />
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
