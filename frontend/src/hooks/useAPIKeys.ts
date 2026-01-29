/**
 * Hook de gestion des cles API pour l'API publique v1
 * Extrait de APIKeysPage - logique metier et state management
 */

import { useState, useEffect, useCallback } from 'react'
import { apiKeysService } from '../services/apiKeys'
import type { APIKey } from '../services/apiKeys'
import { logger } from '../services/logger'

export function useAPIKeys() {
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

  // Charger les cles API
  const loadAPIKeys = useCallback(async () => {
    try {
      setIsLoading(true)
      const keys = await apiKeysService.list()
      setApiKeys(keys)
    } catch (error) {
      logger.error('Erreur chargement cles API', error, {
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

  // Revoquer une cle
  const revokeKey = useCallback(
    async (keyId: string, keyName: string) => {
      if (
        !confirm(
          `Etes-vous sur de vouloir revoquer la cle "${keyName}" ?\n\nCette action est irreversible. La cle ne pourra plus etre utilisee pour l'authentification.`
        )
      ) {
        return
      }

      try {
        await apiKeysService.revoke(keyId)
        logger.info(`Cle API "${keyName}" revoquee`, {
          context: 'APIKeysPage',
          showToast: true,
        })
        loadAPIKeys()
      } catch (error) {
        logger.error('Erreur revocation cle', error, {
          context: 'APIKeysPage',
          showToast: true,
        })
      }
    },
    [loadAPIKeys]
  )

  // Callback apres creation d'une cle
  const onKeyCreated = useCallback(
    (secret: string, keyInfo: { key_prefix: string; nom: string; expires_at: string | null }) => {
      setNewSecret(secret)
      setNewKeyInfo(keyInfo)
      setShowSecretModal(true)
      setShowCreateModal(false)
      loadAPIKeys()
    },
    [loadAPIKeys]
  )

  // Fermer la modal secret
  const closeSecretModal = useCallback(() => {
    setShowSecretModal(false)
    setNewSecret('')
    setNewKeyInfo(null)
    setSecretCopied(false)
  }, [])

  return {
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
  }
}

// Helpers exportes pour les composants de presentation

export function formatDate(dateStr: string | null): string {
  if (!dateStr) return 'Jamais'
  return new Date(dateStr).toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function isExpiringSoon(expiresAt: string | null): boolean {
  if (!expiresAt) return false
  const daysUntilExpiration =
    (new Date(expiresAt).getTime() - Date.now()) / (1000 * 60 * 60 * 24)
  return daysUntilExpiration > 0 && daysUntilExpiration < 7
}

export function isExpired(expiresAt: string | null): boolean {
  if (!expiresAt) return false
  return new Date(expiresAt).getTime() < Date.now()
}
