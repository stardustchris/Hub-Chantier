/**
 * API Webhooks - Gestion des webhooks pour les événements temps réel
 */

import api from '../services/api'

export interface Webhook {
  id: string
  url: string
  events: string[]
  description?: string
  is_active: boolean
  last_triggered_at?: string
  consecutive_failures: number
  created_at: string
}

export interface CreateWebhookRequest {
  url: string
  events: string[]
  description?: string
}

export interface CreateWebhookResponse {
  webhook: Webhook
  secret: string // Affiché UNE SEULE FOIS
}

export interface WebhookDelivery {
  id: string
  webhook_id: string
  event_type: string
  attempt: number
  success: boolean
  status_code?: number
  response_time_ms?: number
  error_message?: string
  delivered_at: string
}

/**
 * Service pour gérer les webhooks.
 */
export const webhooksApi = {
  /**
   * Liste tous les webhooks de l'utilisateur.
   *
   * @returns Liste des webhooks
   */
  async list(): Promise<Webhook[]> {
    const response = await api.get<{ total: number; webhooks: Webhook[] }>('/api/v1/webhooks')
    return response.data.webhooks
  },

  /**
   * Crée un nouveau webhook.
   *
   * IMPORTANT: Le secret est retourné UNE SEULE FOIS.
   * Il doit être copié immédiatement car il ne sera plus accessible.
   *
   * @param data - Données de création
   * @returns Webhook créé avec secret (une fois)
   */
  async create(data: CreateWebhookRequest): Promise<CreateWebhookResponse> {
    const response = await api.post<{
      id: string
      url: string
      events: string[]
      description?: string
      secret: string
      created_at: string
    }>('/api/v1/webhooks', data)

    // Transformer la réponse backend pour correspondre à l'interface frontend
    return {
      secret: response.data.secret,
      webhook: {
        id: response.data.id,
        url: response.data.url,
        events: response.data.events,
        description: response.data.description,
        is_active: true,
        last_triggered_at: undefined,
        consecutive_failures: 0,
        created_at: response.data.created_at,
      },
    }
  },

  /**
   * Supprime un webhook.
   *
   * @param id - UUID du webhook à supprimer
   */
  async delete(id: string): Promise<void> {
    await api.delete(`/api/v1/webhooks/${id}`)
  },

  /**
   * Teste un webhook en envoyant un événement de test.
   *
   * @param id - UUID du webhook à tester
   */
  async test(id: string): Promise<void> {
    await api.post(`/api/v1/webhooks/${id}/test`)
  },

  /**
   * Récupère l'historique des deliveries d'un webhook.
   *
   * @param id - UUID du webhook
   * @param limit - Nombre de deliveries à récupérer
   * @returns Liste des deliveries
   */
  async deliveries(id: string, limit = 50): Promise<WebhookDelivery[]> {
    const response = await api.get<{ total: number; deliveries: WebhookDelivery[] }>(
      `/api/v1/webhooks/${id}/deliveries?limit=${limit}`
    )
    return response.data.deliveries
  },
}

export default webhooksApi
