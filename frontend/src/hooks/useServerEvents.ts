/**
 * Hook SSE (Server-Sent Events) pour notifications temps réel.
 *
 * Remplace le polling 30s par un stream SSE unidirectionnel.
 * Reconnexion automatique via EventSource natif du navigateur.
 * Invalide les caches TanStack Query quand des événements arrivent.
 */

import { useEffect, useRef, useState, useCallback } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { logger } from '../services/logger'

/** Map event_type → query keys à invalider */
const EVENT_QUERY_MAP: Record<string, string[][]> = {
  'notification.created': [['notifications']],
  'comment.added': [['notifications'], ['feed']],
  'like.added': [['notifications'], ['feed']],
  'chantier.created': [['chantiers']],
  'chantier.statut_changed': [['chantiers'], ['notifications']],
  'affectation.created': [['planning'], ['notifications']],
  'affectation.updated': [['planning']],
  'affectation.deleted': [['planning']],
  'pointage.submitted': [['pointages'], ['notifications']],
  'pointage.validated': [['pointages'], ['feuilles-heures'], ['notifications']],
  'pointage.rejected': [['pointages'], ['notifications']],
  'document.added': [['documents'], ['notifications']],
  'signalement.created': [['signalements'], ['notifications']],
  'tache.assigned': [['taches'], ['notifications']],
}

/** Fallback: invalide notifications pour tout event non mappé */
const DEFAULT_INVALIDATION: string[][] = [['notifications']]

interface UseServerEventsReturn {
  isConnected: boolean
  eventsReceived: number
}

export function useServerEvents(): UseServerEventsReturn {
  const queryClient = useQueryClient()
  const eventSourceRef = useRef<EventSource | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [eventsReceived, setEventsReceived] = useState(0)
  const reconnectAttempts = useRef(0)

  const handleEvent = useCallback(
    (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data)
        const eventType: string = data.event_type || event.type || ''

        // Trouver les query keys à invalider
        const queryKeys = EVENT_QUERY_MAP[eventType] || DEFAULT_INVALIDATION

        // Invalider les caches TanStack Query
        queryKeys.forEach((key) => {
          queryClient.invalidateQueries({ queryKey: key })
        })

        setEventsReceived((prev) => prev + 1)

        logger.info('SSE event received', { eventType, queryKeys })
      } catch (err) {
        logger.error('SSE event parse error', err, { context: 'useServerEvents' })
      }
    },
    [queryClient]
  )

  useEffect(() => {
    // Ne pas se connecter si offline
    if (!navigator.onLine) return

    const connect = () => {
      const es = new EventSource('/api/notifications/stream')
      eventSourceRef.current = es

      es.onopen = () => {
        setIsConnected(true)
        reconnectAttempts.current = 0
        logger.info('SSE connected')
      }

      // Écouter tous les types d'événements via onmessage (events sans type spécifique)
      es.onmessage = handleEvent

      // Écouter les événements typés (event: xxx\n)
      Object.keys(EVENT_QUERY_MAP).forEach((eventType) => {
        es.addEventListener(eventType, handleEvent as EventListener)
      })

      es.onerror = () => {
        setIsConnected(false)
        es.close()
        eventSourceRef.current = null

        // Reconnexion avec backoff exponentiel (max 30s)
        const delay = Math.min(1000 * 2 ** reconnectAttempts.current, 30000)
        reconnectAttempts.current++
        logger.info(`SSE reconnecting in ${delay}ms (attempt ${reconnectAttempts.current})`)
        setTimeout(connect, delay)
      }
    }

    connect()

    // Écouter online/offline
    const handleOnline = () => {
      if (!eventSourceRef.current || eventSourceRef.current.readyState === EventSource.CLOSED) {
        reconnectAttempts.current = 0
        connect()
      }
    }
    const handleOffline = () => {
      eventSourceRef.current?.close()
      eventSourceRef.current = null
      setIsConnected(false)
    }

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    return () => {
      eventSourceRef.current?.close()
      eventSourceRef.current = null
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [handleEvent])

  return { isConnected, eventsReceived }
}
