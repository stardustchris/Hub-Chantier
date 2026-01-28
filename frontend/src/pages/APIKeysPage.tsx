/**
 * Page de gestion des clés API pour l'API publique v1
 */

import { useState, useEffect, useCallback } from 'react'
import { apiKeysService } from '../services/apiKeys'
import type { APIKey, CreateAPIKeyRequest } from '../services/apiKeys'
import Layout from '../components/Layout'
import {
  Key,
  Plus,
  Trash2,
  Loader2,
  Copy,
  CheckCircle2,
  AlertTriangle,
  Info,
} from 'lucide-react'
import { logger } from '../services/logger'

export default function APIKeysPage() {
  const [apiKeys, setApiKeys] = useState<APIKey[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showSecretModal, setShowSecretModal] = useState(false)
  const [newSecret, setNewSecret] = useState<string>('')
  const [newKeyInfo, setNewKeyInfo] = useState<{
    key_prefix: string
    nom: string
    expires_at: string | null
  } | null>(null)
  const [secretCopied, setSecretCopied] = useState(false)

  // Charger les clés API
  const loadAPIKeys = useCallback(async () => {
    try {
      setIsLoading(true)
      const keys = await apiKeysService.list()
      setApiKeys(keys)
    } catch (error) {
      logger.error('Erreur chargement clés API', error, {
        context: 'APIKeysPage',
        showToast: true,
      })
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    loadAPIKeys()
  }, [loadAPIKeys])

  // Copier secret dans presse-papier
  const copySecret = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(newSecret)
      setSecretCopied(true)
      setTimeout(() => setSecretCopied(false), 3000)
    } catch (error) {
      logger.error('Erreur copie presse-papier', error, {
        context: 'APIKeysPage',
        showToast: true,
      })
    }
  }, [newSecret])

  // Révoquer une clé
  const revokeKey = useCallback(
    async (keyId: string, keyName: string) => {
      if (
        !confirm(
          `Êtes-vous sûr de vouloir révoquer la clé "${keyName}" ?\n\nCette action est irréversible. La clé ne pourra plus être utilisée pour l'authentification.`
        )
      ) {
        return
      }

      try {
        await apiKeysService.revoke(keyId)
        logger.info(`Clé API "${keyName}" révoquée`, {
          context: 'APIKeysPage',
          showToast: true,
        })
        loadAPIKeys()
      } catch (error) {
        logger.error('Erreur révocation clé', error, {
          context: 'APIKeysPage',
          showToast: true,
        })
      }
    },
    [loadAPIKeys]
  )

  // Formater date
  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return 'Jamais'
    return new Date(dateStr).toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  // Vérifier si clé expire bientôt
  const isExpiringSoon = (expiresAt: string | null) => {
    if (!expiresAt) return false
    const daysUntilExpiration =
      (new Date(expiresAt).getTime() - Date.now()) / (1000 * 60 * 60 * 24)
    return daysUntilExpiration > 0 && daysUntilExpiration < 7
  }

  const isExpired = (expiresAt: string | null) => {
    if (!expiresAt) return false
    return new Date(expiresAt).getTime() < Date.now()
  }

  return (
    <Layout>
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
              <Key className="w-7 h-7" />
              Clés API
            </h1>
            <p className="text-sm text-gray-600 mt-1">
              Gérez vos clés d'authentification pour l'API publique
            </p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="w-4 h-4" />
            Créer une clé
          </button>
        </div>
      </div>

      {/* Liste des clés */}
      {isLoading ? (
        <div className="flex justify-center items-center h-64">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        </div>
      ) : apiKeys.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <Key className="w-12 h-12 text-gray-400 mx-auto mb-3" />
          <p className="text-gray-600">Aucune clé API</p>
          <p className="text-sm text-gray-500 mt-1">
            Créez votre première clé pour commencer
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {apiKeys.map((key) => (
            <div
              key={key.id}
              className={`border rounded-lg p-4 ${
                !key.is_active
                  ? 'bg-gray-50 border-gray-300 opacity-60'
                  : isExpired(key.expires_at)
                  ? 'bg-red-50 border-red-300'
                  : isExpiringSoon(key.expires_at)
                  ? 'bg-yellow-50 border-yellow-300'
                  : 'bg-white border-gray-200'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  {/* Nom + Statut */}
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="font-semibold text-gray-900">{key.nom}</h3>
                    {!key.is_active && (
                      <span className="text-xs px-2 py-0.5 bg-gray-200 text-gray-700 rounded-full">
                        Révoquée
                      </span>
                    )}
                    {key.is_active && isExpired(key.expires_at) && (
                      <span className="text-xs px-2 py-0.5 bg-red-200 text-red-800 rounded-full flex items-center gap-1">
                        <AlertTriangle className="w-3 h-3" />
                        Expirée
                      </span>
                    )}
                    {key.is_active && isExpiringSoon(key.expires_at) && (
                      <span className="text-xs px-2 py-0.5 bg-yellow-200 text-yellow-800 rounded-full flex items-center gap-1">
                        <AlertTriangle className="w-3 h-3" />
                        Expire bientôt
                      </span>
                    )}
                  </div>

                  {/* Description */}
                  {key.description && (
                    <p className="text-sm text-gray-600 mb-2">
                      {key.description}
                    </p>
                  )}

                  {/* Key prefix */}
                  <div className="font-mono text-sm text-gray-700 bg-gray-100 px-2 py-1 rounded inline-block mb-3">
                    {key.key_prefix}...
                  </div>

                  {/* Infos */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                    <div>
                      <span className="text-gray-500">Scopes:</span>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {key.scopes.map((scope) => (
                          <span
                            key={scope}
                            className="text-xs px-2 py-0.5 bg-blue-100 text-blue-700 rounded-full"
                          >
                            {scope}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div>
                      <span className="text-gray-500">Créée le:</span>
                      <p className="text-gray-900">{formatDate(key.created_at)}</p>
                    </div>
                    <div>
                      <span className="text-gray-500">Dernière utilisation:</span>
                      <p className="text-gray-900">
                        {formatDate(key.last_used_at)}
                      </p>
                    </div>
                    <div>
                      <span className="text-gray-500">Expire le:</span>
                      <p
                        className={
                          isExpiringSoon(key.expires_at)
                            ? 'text-yellow-700 font-medium'
                            : isExpired(key.expires_at)
                            ? 'text-red-700 font-medium'
                            : 'text-gray-900'
                        }
                      >
                        {formatDate(key.expires_at)}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Actions */}
                {key.is_active && (
                  <button
                    onClick={() => revokeKey(key.id, key.nom)}
                    className="ml-4 p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    title="Révoquer cette clé"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal Création */}
      {showCreateModal && (
        <CreateAPIKeyModal
          onClose={() => setShowCreateModal(false)}
          onCreated={(secret, keyInfo) => {
            setNewSecret(secret)
            setNewKeyInfo(keyInfo)
            setShowSecretModal(true)
            setShowCreateModal(false)
            loadAPIKeys()
          }}
        />
      )}

      {/* Modal Secret (UNE FOIS) */}
      {showSecretModal && newKeyInfo && (
        <SecretModal
          secret={newSecret}
          keyInfo={newKeyInfo}
          copied={secretCopied}
          onCopy={copySecret}
          onClose={() => {
            setShowSecretModal(false)
            setNewSecret('')
            setNewKeyInfo(null)
            setSecretCopied(false)
          }}
        />
      )}
    </Layout>
  )
}

/**
 * Modal de création de clé API
 */
function CreateAPIKeyModal({
  onClose,
  onCreated,
}: {
  onClose: () => void
  onCreated: (
    secret: string,
    keyInfo: { key_prefix: string; nom: string; expires_at: string | null }
  ) => void
}) {
  const [nom, setNom] = useState('')
  const [description, setDescription] = useState('')
  const [scopes, setScopes] = useState<string[]>(['read'])
  const [expiresDays, setExpiresDays] = useState(90)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const availableScopes = [
    'read',
    'write',
    'chantiers:read',
    'chantiers:write',
    'planning:read',
    'planning:write',
    'documents:read',
    'documents:write',
  ]

  const toggleScope = (scope: string) => {
    setScopes((prev) =>
      prev.includes(scope) ? prev.filter((s) => s !== scope) : [...prev, scope]
    )
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!nom.trim()) {
      alert('Le nom est requis')
      return
    }

    if (scopes.length === 0) {
      alert('Au moins un scope est requis')
      return
    }

    try {
      setIsSubmitting(true)
      const data: CreateAPIKeyRequest = {
        nom: nom.trim(),
        description: description.trim() || undefined,
        scopes,
        expires_days: expiresDays,
      }
      const result = await apiKeysService.create(data)
      onCreated(result.api_key, {
        key_prefix: result.key_prefix,
        nom: result.nom,
        expires_at: result.expires_at,
      })
    } catch (error) {
      logger.error('Erreur création clé API', error, {
        context: 'CreateAPIKeyModal',
        showToast: true,
      })
      setIsSubmitting(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-lg w-full p-6">
        <h2 className="text-xl font-bold mb-4">Créer une clé API</h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Nom */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nom <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={nom}
              onChange={(e) => setNom(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Clé de production"
              maxLength={255}
              required
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Utilisée pour le système de synchronisation..."
              rows={2}
            />
          </div>

          {/* Scopes */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Permissions (Scopes) <span className="text-red-500">*</span>
            </label>
            <div className="grid grid-cols-2 gap-2">
              {availableScopes.map((scope) => (
                <label
                  key={scope}
                  className="flex items-center gap-2 p-2 border rounded cursor-pointer hover:bg-gray-50"
                >
                  <input
                    type="checkbox"
                    checked={scopes.includes(scope)}
                    onChange={() => toggleScope(scope)}
                    className="w-4 h-4 text-blue-600"
                  />
                  <span className="text-sm">{scope}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Expiration */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Expiration (jours)
            </label>
            <input
              type="number"
              value={expiresDays}
              onChange={(e) => setExpiresDays(parseInt(e.target.value) || 90)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              min={1}
              max={3650}
            />
            <p className="text-xs text-gray-500 mt-1">
              La clé expirera automatiquement après {expiresDays} jours
            </p>
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
  keyInfo,
  copied,
  onCopy,
  onClose,
}: {
  secret: string
  keyInfo: { key_prefix: string; nom: string; expires_at: string | null }
  copied: boolean
  onCopy: () => void
  onClose: () => void
}) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-2xl w-full p-6">
        {/* Alerte */}
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-4">
          <div className="flex items-start">
            <AlertTriangle className="w-5 h-5 text-yellow-600 mt-0.5 mr-3" />
            <div>
              <h3 className="text-sm font-medium text-yellow-800 mb-1">
                Secret affiché une seule fois
              </h3>
              <p className="text-sm text-yellow-700">
                Copiez ce secret maintenant. Il ne sera plus jamais accessible
                après la fermeture de cette fenêtre.
              </p>
            </div>
          </div>
        </div>

        {/* Infos */}
        <div className="mb-4">
          <h2 className="text-xl font-bold mb-1">Clé API créée</h2>
          <p className="text-sm text-gray-600">
            Nom: <span className="font-medium">{keyInfo.nom}</span>
          </p>
        </div>

        {/* Secret */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Clé API Secret
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

        {/* Instructions */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
          <div className="flex items-start">
            <Info className="w-5 h-5 text-blue-600 mt-0.5 mr-3" />
            <div className="text-sm text-blue-800">
              <p className="font-medium mb-1">Comment utiliser cette clé :</p>
              <code className="block bg-white px-2 py-1 rounded text-xs mt-2">
                curl -H "Authorization: Bearer {secret}" https://api.hub-chantier.fr/api/v1/...
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
