/**
 * useOfflineStorage - Hook pour la gestion des données hors-ligne
 * FDH-20: Mode Offline (PWA/Service Worker)
 */

import { useState, useEffect, useCallback } from 'react'

const OFFLINE_QUEUE_KEY = 'hub_chantier_offline_queue'
const OFFLINE_CACHE_KEY = 'hub_chantier_offline_cache'

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

/**
 * Hook pour gérer le stockage hors-ligne et la synchronisation
 */
export function useOfflineStorage() {
  const [isOnline, setIsOnline] = useState(navigator.onLine)
  const [pendingItems, setPendingItems] = useState<OfflineQueueItem[]>([])
  const [isSyncing, setIsSyncing] = useState(false)

  // Load pending items from localStorage
  useEffect(() => {
    const stored = localStorage.getItem(OFFLINE_QUEUE_KEY)
    if (stored) {
      try {
        setPendingItems(JSON.parse(stored))
      } catch {
        // Invalid data, clear it
        localStorage.removeItem(OFFLINE_QUEUE_KEY)
      }
    }
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

  // Save pending items to localStorage
  const savePendingItems = useCallback((items: OfflineQueueItem[]) => {
    localStorage.setItem(OFFLINE_QUEUE_KEY, JSON.stringify(items))
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

    const newItems = [...pendingItems, item]
    savePendingItems(newItems)

    return item.id
  }, [pendingItems, savePendingItems])

  // Remove item from queue
  const removeFromQueue = useCallback((id: string) => {
    const newItems = pendingItems.filter(item => item.id !== id)
    savePendingItems(newItems)
  }, [pendingItems, savePendingItems])

  // Clear all pending items
  const clearQueue = useCallback(() => {
    localStorage.removeItem(OFFLINE_QUEUE_KEY)
    setPendingItems([])
  }, [])

  // Cache data for offline use
  const cacheData = useCallback((key: string, data: unknown, ttl: number = 60 * 60 * 1000) => {
    const stored = localStorage.getItem(OFFLINE_CACHE_KEY)
    let cache: OfflineCache = {}

    if (stored) {
      try {
        cache = JSON.parse(stored)
      } catch {
        // Invalid cache, reset
      }
    }

    cache[key] = {
      data,
      timestamp: Date.now(),
      ttl,
    }

    localStorage.setItem(OFFLINE_CACHE_KEY, JSON.stringify(cache))
  }, [])

  // Get cached data
  const getCachedData = useCallback(<T>(key: string): T | null => {
    const stored = localStorage.getItem(OFFLINE_CACHE_KEY)
    if (!stored) return null

    try {
      const cache: OfflineCache = JSON.parse(stored)
      const item = cache[key]

      if (!item) return null

      // Check if expired
      if (Date.now() - item.timestamp > item.ttl) {
        // Remove expired item
        delete cache[key]
        localStorage.setItem(OFFLINE_CACHE_KEY, JSON.stringify(cache))
        return null
      }

      return item.data as T
    } catch {
      return null
    }
  }, [])

  // Clear specific cache entry
  const clearCacheEntry = useCallback((key: string) => {
    const stored = localStorage.getItem(OFFLINE_CACHE_KEY)
    if (!stored) return

    try {
      const cache: OfflineCache = JSON.parse(stored)
      delete cache[key]
      localStorage.setItem(OFFLINE_CACHE_KEY, JSON.stringify(cache))
    } catch {
      // Ignore errors
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
    if (!isOnline || pendingItems.length === 0 || isSyncing) {
      return { success: 0, failed: 0 }
    }

    setIsSyncing(true)
    let success = 0
    let failed = 0

    const remainingItems: OfflineQueueItem[] = []

    for (const item of pendingItems) {
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

    savePendingItems(remainingItems)
    setIsSyncing(false)

    return { success, failed }
  }, [isOnline, pendingItems, isSyncing, savePendingItems])

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
    syncPendingItems,
  }
}

export default useOfflineStorage
