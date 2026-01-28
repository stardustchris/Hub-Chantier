/**
 * Service API Keys - Gestion des clés API pour l'API publique v1
 */

import api from './api'

export interface APIKey {
  id: string
  key_prefix: string
  nom: string
  description: string | null
  scopes: string[]
  rate_limit_per_hour: number
  is_active: boolean
  last_used_at: string | null
  expires_at: string | null
  created_at: string
}

export interface CreateAPIKeyRequest {
  nom: string
  description?: string
  scopes?: string[]
  expires_days?: number
}

export interface CreateAPIKeyResponse {
  api_key: string  // SECRET - affiché UNE FOIS
  key_id: string
  key_prefix: string
  nom: string
  created_at: string
  expires_at: string | null
}

/**
 * Service pour gérer les clés API.
 */
export const apiKeysService = {
  /**
   * Liste toutes les clés API de l'utilisateur authentifié.
   *
   * @param includeRevoked - Inclure les clés révoquées (défaut: false)
   * @returns Liste des clés API
   */
  async list(includeRevoked = false): Promise<APIKey[]> {
    const response = await api.get<APIKey[]>('/api/auth/api-keys', {
      params: { include_revoked: includeRevoked },
    })
    return response.data
  },

  /**
   * Crée une nouvelle clé API.
   *
   * IMPORTANT: Le secret (api_key) est retourné UNE SEULE FOIS.
   * Il doit être copié immédiatement car il ne sera plus accessible.
   *
   * @param data - Données de création
   * @returns Clé créée avec secret (une fois)
   */
  async create(data: CreateAPIKeyRequest): Promise<CreateAPIKeyResponse> {
    const response = await api.post<CreateAPIKeyResponse>(
      '/api/auth/api-keys',
      data
    )
    return response.data
  },

  /**
   * Révoque (désactive) une clé API.
   *
   * La clé ne pourra plus être utilisée pour l'authentification.
   * L'historique est conservé pour l'audit.
   *
   * @param keyId - UUID de la clé à révoquer
   */
  async revoke(keyId: string): Promise<void> {
    await api.delete(`/api/auth/api-keys/${keyId}`)
  },
}
