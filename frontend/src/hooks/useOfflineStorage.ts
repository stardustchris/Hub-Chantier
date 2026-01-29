/**
 * useOfflineStorage - Hook pour la gestion des données hors-ligne
 * FDH-20: Mode Offline (PWA/Service Worker)
 *
 * Sécurité: Les données sont chiffrées via AES-GCM (Web Crypto API)
 * avant stockage dans localStorage. Fallback base64 si SubtleCrypto
 * n'est pas disponible.
 */

import { useState, useEffect, useCallback, useRef } from 'react'
import { logger } from '../services/logger'

const OFFLINE_QUEUE_KEY = 'hub_chantier_offline_queue'
const OFFLINE_CACHE_KEY = 'hub_chantier_offline_cache'

/**
 * Identifiant fixe utilisé pour dériver la clé de chiffrement.
 * Ce n'est pas un secret absolu (accessible côté client), mais cela
 * empêche la lecture directe des données en cas d'exfiltration brute
 * du localStorage (attaque XSS basique).
 */
const ENCRYPTION_SALT = 'hub-chantier-offline-v1'

// ─── Types ───────────────────────────────────────────────────────────

export interface OfflineQueueItem {
  id: string
  timestamp: number
  type: 'create' | 'update' | 'delete'
  endpoint: string
  method: string
  data: unknown
  retryCount: number
}

export interface OfflineCache {
  [key: string]: {
    data: unknown
    timestamp: number
    ttl: number // Time to live in ms
  }
}

// ─── Chiffrement / Déchiffrement ─────────────────────────────────────

const hasSubtleCrypto =
  typeof globalThis.crypto !== 'undefined' &&
  typeof globalThis.crypto.subtle !== 'undefined'

/**
 * Dérive une clé AES-GCM à partir du salt fixe via PBKDF2.
 */
async function deriveKey(): Promise<CryptoKey> {
  const encoder = new TextEncoder()
  const keyMaterial = await crypto.subtle.importKey(
    'raw',
    encoder.encode(ENCRYPTION_SALT),
    'PBKDF2',
    false,
    ['deriveKey']
  )

  return crypto.subtle.deriveKey(
    {
      name: 'PBKDF2',
      salt: encoder.encode('hub-chantier-salt'),
      iterations: 100_000,
      hash: 'SHA-256',
    },
    keyMaterial,
    { name: 'AES-GCM', length: 256 },
    false,
    ['encrypt', 'decrypt']
  )
}

/**
 * Chiffre une chaîne JSON avec AES-GCM.
 * Format stocké : iv(base64):ciphertext(base64)
 */
async function encryptData(plaintext: string): Promise<string> {
  if (!hasSubtleCrypto) {
    // Fallback : encodage base64
    return btoa(unescape(encodeURIComponent(plaintext)))
  }

  try {
    const key = await deriveKey()
    const iv = crypto.getRandomValues(new Uint8Array(12))
    const encoder = new TextEncoder()

    const cipherBuffer = await crypto.subtle.encrypt(
      { name: 'AES-GCM', iv },
      key,
      encoder.encode(plaintext)
    )

    const ivBase64 = btoa(String.fromCharCode(...iv))
    const cipherBase64 = btoa(
      String.fromCharCode(...new Uint8Array(cipherBuffer))
    )

    return `${ivBase64}:${cipherBase64}`
  } catch (error) {
    logger.warn('[OfflineStorage] Chiffrement échoué, fallback base64', error)
    return btoa(unescape(encodeURIComponent(plaintext)))
  }
}

/**
 * Déchiffre une chaîne précédemment chiffrée par `encryptData`.
 */
async function decryptData(stored: string): Promise<string> {
  if (!hasSubtleCrypto) {
    // Fallback : décodage base64
    return decodeURIComponent(escape(atob(stored)))
  }

  // Détection du format : si pas de ":" c'est du base64 pur (fallback ou données legacy)
  if (!stored.includes(':')) {
    try {
      return decodeURIComponent(escape(atob(stored)))
    } catch {
      // Données en clair héritées (avant migration)
      return stored
    }
  }

  try {
    const [ivBase64, cipherBase64] = stored.split(':')
    const key = await deriveKey()

    const iv = Uint8Array.from(atob(ivBase64), (c) => c.charCodeAt(0))
    const cipherBytes = Uint8Array.from(atob(cipherBase64), (c) =>
      c.charCodeAt(0)
    )

    const plainBuffer = await crypto.subtle.decrypt(
      { name: 'AES-GCM', iv },
      key,
      cipherBytes
    )

    return new TextDecoder().decode(plainBuffer)
  } catch (error) {
    logger.warn('[OfflineStorage] Déchiffrement échoué, tentative brute', error)
    // Tentative de lecture en clair (données pré-migration)
    try {
      JSON.parse(stored)
      return stored
    } catch {
      return stored
    }
  }
}

// ─── Fonction publique de nettoyage ──────────────────────────────────

/**
 * Purge toutes les données offline (queue + cache).
 * À appeler au logout pour ne pas laisser de données chiffrées
 * accessibles à un autre utilisateur.
 */
export function clearAllOfflineData(): void {
  localStorage.removeItem(OFFLINE_QUEUE_KEY)
  localStorage.removeItem(OFFLINE_CACHE_KEY)
  logger.info('[OfflineStorage] Toutes les données offline ont été purgées')
}

// ─── Hook ────────────────────────────────────────────────────────────

/**
 * Hook pour gérer le stockage hors-ligne et la synchronisation
 */
export function useOfflineStorage() {
  const [isOnline, setIsOnline] = useState(navigator.onLine)
  const [pendingItems, setPendingItems] = useState<OfflineQueueItem[]>([])
  const [isSyncing, setIsSyncing] = useState(false)

  // Ref pour accéder aux pendingItems à jour dans les callbacks async
  const pendingItemsRef = useRef(pendingItems)
  pendingItemsRef.current = pendingItems

  // Load pending items from localStorage (async decryption)
  useEffect(() => {
    const loadQueue = async () => {
      const stored = localStorage.getItem(OFFLINE_QUEUE_KEY)
      if (!stored) return

      try {
        const decrypted = await decryptData(stored)
        setPendingItems(JSON.parse(decrypted))
      } catch {
        logger.warn('[OfflineStorage] Données queue invalides, suppression')
        localStorage.removeItem(OFFLINE_QUEUE_KEY)
      }
    }

    loadQueue()
  }, [])

  // Listen for online/offline events
  useEffect(() => {
    const handleOnline = () => setIsOnline(true)
    const handleOffline = () => setIsOnline(false)

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  // Save pending items to localStorage (chiffré)
  const savePendingItems = useCallback(async (items: OfflineQueueItem[]) => {
    try {
      const encrypted = await encryptData(JSON.stringify(items))
      localStorage.setItem(OFFLINE_QUEUE_KEY, encrypted)
    } catch (error) {
      logger.error('[OfflineStorage] Échec sauvegarde queue chiffrée', error)
    }
    setPendingItems(items)
  }, [])

  // Add item to offline queue
  const addToQueue = useCallback((
    type: OfflineQueueItem['type'],
    endpoint: string,
    method: string,
    data: unknown
  ): string => {
    const item: OfflineQueueItem = {
      id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      timestamp: Date.now(),
      type,
      endpoint,
      method,
      data,
      retryCount: 0,
    }

    const newItems = [...pendingItemsRef.current, item]
    savePendingItems(newItems)

    return item.id
  }, [savePendingItems])

  // Remove item from queue
  const removeFromQueue = useCallback((id: string) => {
    const newItems = pendingItemsRef.current.filter(item => item.id !== id)
    savePendingItems(newItems)
  }, [savePendingItems])

  // Clear all pending items
  const clearQueue = useCallback(() => {
    localStorage.removeItem(OFFLINE_QUEUE_KEY)
    setPendingItems([])
  }, [])

  // Cache data for offline use (chiffré)
  const cacheData = useCallback(async (key: string, data: unknown, ttl: number = 60 * 60 * 1000) => {
    let cache: OfflineCache = {}

    const stored = localStorage.getItem(OFFLINE_CACHE_KEY)
    if (stored) {
      try {
        const decrypted = await decryptData(stored)
        cache = JSON.parse(decrypted)
      } catch {
        logger.warn('[OfflineStorage] Cache invalide, réinitialisation')
      }
    }

    cache[key] = {
      data,
      timestamp: Date.now(),
      ttl,
    }

    try {
      const encrypted = await encryptData(JSON.stringify(cache))
      localStorage.setItem(OFFLINE_CACHE_KEY, encrypted)
    } catch (error) {
      logger.error('[OfflineStorage] Échec sauvegarde cache chiffré', error)
    }
  }, [])

  // Get cached data (déchiffré)
  const getCachedData = useCallback(async <T>(key: string): Promise<T | null> => {
    const stored = localStorage.getItem(OFFLINE_CACHE_KEY)
    if (!stored) return null

    try {
      const decrypted = await decryptData(stored)
      const cache: OfflineCache = JSON.parse(decrypted)
      const item = cache[key]

      if (!item) return null

      // Check if expired
      if (Date.now() - item.timestamp > item.ttl) {
        // Remove expired item
        delete cache[key]
        try {
          const encrypted = await encryptData(JSON.stringify(cache))
          localStorage.setItem(OFFLINE_CACHE_KEY, encrypted)
        } catch (error) {
          logger.error('[OfflineStorage] Échec mise à jour cache après expiration', error)
        }
        return null
      }

      return item.data as T
    } catch {
      return null
    }
  }, [])

  // Clear specific cache entry
  const clearCacheEntry = useCallback(async (key: string) => {
    const stored = localStorage.getItem(OFFLINE_CACHE_KEY)
    if (!stored) return

    try {
      const decrypted = await decryptData(stored)
      const cache: OfflineCache = JSON.parse(decrypted)
      delete cache[key]
      const encrypted = await encryptData(JSON.stringify(cache))
      localStorage.setItem(OFFLINE_CACHE_KEY, encrypted)
    } catch (error) {
      logger.error('[OfflineStorage] Échec suppression entrée cache', error)
    }
  }, [])

  // Clear entire cache
  const clearCache = useCallback(() => {
    localStorage.removeItem(OFFLINE_CACHE_KEY)
  }, [])

  // Sync pending items when online
  const syncPendingItems = useCallback(async (
    syncFn: (item: OfflineQueueItem) => Promise<boolean>
  ): Promise<{ success: number; failed: number }> => {
    if (!isOnline || pendingItemsRef.current.length === 0 || isSyncing) {
      return { success: 0, failed: 0 }
    }

    setIsSyncing(true)
    let success = 0
    let failed = 0

    const remainingItems: OfflineQueueItem[] = []

    for (const item of pendingItemsRef.current) {
      try {
        const result = await syncFn(item)
        if (result) {
          success++
        } else {
          // Increment retry count and keep in queue
          item.retryCount++
          if (item.retryCount < 3) {
            remainingItems.push(item)
          } else {
            failed++
          }
        }
      } catch {
        item.retryCount++
        if (item.retryCount < 3) {
          remainingItems.push(item)
        } else {
          failed++
        }
      }
    }

    await savePendingItems(remainingItems)
    setIsSyncing(false)

    return { success, failed }
  }, [isOnline, isSyncing, savePendingItems])

  return {
    isOnline,
    pendingItems,
    pendingCount: pendingItems.length,
    isSyncing,
    addToQueue,
    removeFromQueue,
    clearQueue,
    cacheData,
    getCachedData,
    clearCacheEntry,
    clearCache,
    clearAllOfflineData,
    syncPendingItems,
  }
}

export default useOfflineStorage
