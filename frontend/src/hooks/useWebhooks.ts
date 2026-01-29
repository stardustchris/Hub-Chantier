/**
 * Hook de gestion des webhooks
 * Extrait la logique metier de WebhooksPage
 */

import { useState, useEffect, useCallback } from 'react'
import { webhooksApi } from '../api/webhooks'
import type { Webhook } from '../api/webhooks'
import { logger } from '../services/logger'

export function useWebhooks() {
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

  // Callback apres creation
  const onWebhookCreated = useCallback(
    (secret: string, webhook: Webhook) => {
      setNewSecret(secret)
      setNewWebhook(webhook)
      setShowSecretModal(true)
      setShowCreateModal(false)
      loadWebhooks()
    },
    [loadWebhooks]
  )

  // Fermer le modal secret
  const closeSecretModal = useCallback(() => {
    setShowSecretModal(false)
    setNewSecret('')
    setNewWebhook(null)
    setSecretCopied(false)
  }, [])

  // Fermer le modal delivery
  const closeDeliveryModal = useCallback(() => {
    setShowDeliveryModal(false)
    setSelectedWebhook(null)
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

  return {
    // State
    webhooks,
    isLoading,
    showCreateModal,
    showSecretModal,
    showDeliveryModal,
    selectedWebhook,
    newSecret,
    newWebhook,
    secretCopied,

    // Actions
    setShowCreateModal,
    loadWebhooks,
    copySecret,
    deleteWebhook,
    testWebhook,
    viewDeliveries,
    onWebhookCreated,
    closeSecretModal,
    closeDeliveryModal,

    // Helpers
    formatDate,
    truncateUrl,
  }
}
