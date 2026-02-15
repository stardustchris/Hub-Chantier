/**
 * Page de gestion des cles API pour l'API publique v1
 */

import Layout from '../components/Layout'
import { CreateAPIKeyModal, APIKeySecretModal } from '../components/apikeys'
import { useAPIKeys, formatDate, isExpiringSoon, isExpired } from '../hooks/useAPIKeys'
import {
  Key,
  Plus,
  Trash2,
  Loader2,
  AlertTriangle,
} from 'lucide-react'
import { useDocumentTitle } from '../hooks/useDocumentTitle'

export default function APIKeysPage() {
  useDocumentTitle('Clés API')
  const {
    apiKeys,
    isLoading,
    showCreateModal,
    setShowCreateModal,
    showSecretModal,
    newSecret,
    newKeyInfo,
    secretCopied,
    copySecret,
    revokeKey,
    onKeyCreated,
    closeSecretModal,
  } = useAPIKeys()

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

      {/* Liste des cles */}
      {isLoading ? (
        <div className="flex justify-center items-center h-64">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        </div>
      ) : apiKeys.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <Key className="w-12 h-12 text-gray-600 mx-auto mb-3" />
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

      {/* Modal Creation */}
      {showCreateModal && (
        <CreateAPIKeyModal
          onClose={() => setShowCreateModal(false)}
          onCreated={onKeyCreated}
        />
      )}

      {/* Modal Secret (UNE FOIS) */}
      {showSecretModal && newKeyInfo && (
        <APIKeySecretModal
          secret={newSecret}
          keyInfo={newKeyInfo}
          copied={secretCopied}
          onCopy={copySecret}
          onClose={closeSecretModal}
        />
      )}
    </Layout>
  )
}
