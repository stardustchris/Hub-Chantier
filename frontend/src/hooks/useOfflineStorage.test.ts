/**
 * Tests pour useOfflineStorage
 * FDH-20: Mode Offline (PWA/Service Worker)
 */

// @vitest-environment jsdom

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { useOfflineStorage } from './useOfflineStorage'

// Mock logger to avoid console noise
vi.mock('../services/logger', () => ({
  logger: { info: vi.fn(), warn: vi.fn(), error: vi.fn() },
}))

describe('useOfflineStorage', () => {
  let originalOnLine: boolean

  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    originalOnLine = navigator.onLine

    // Mock navigator.onLine
    Object.defineProperty(navigator, 'onLine', {
      configurable: true,
      get: () => true,
    })
  })

  afterEach(() => {
    localStorage.clear()
    Object.defineProperty(navigator, 'onLine', {
      configurable: true,
      get: () => originalOnLine,
    })
  })

  describe('Etat initial', () => {
    it('retourne isOnline true par defaut', () => {
      const { result } = renderHook(() => useOfflineStorage())
      expect(result.current.isOnline).toBe(true)
    })

    it('retourne une liste vide de pendingItems', () => {
      const { result } = renderHook(() => useOfflineStorage())
      expect(result.current.pendingItems).toEqual([])
    })

    it('retourne pendingCount a 0', () => {
      const { result } = renderHook(() => useOfflineStorage())
      expect(result.current.pendingCount).toBe(0)
    })

    it('retourne isSyncing false', () => {
      const { result } = renderHook(() => useOfflineStorage())
      expect(result.current.isSyncing).toBe(false)
    })
  })

  describe('Queue hors-ligne', () => {
    it('ajoute un element a la queue', async () => {
      const { result } = renderHook(() => useOfflineStorage())

      act(() => {
        result.current.addToQueue('create', '/api/pointages', 'POST', { data: 'test' })
      })

      await waitFor(() => {
        expect(result.current.pendingItems).toHaveLength(1)
      })
      expect(result.current.pendingCount).toBe(1)
    })

    it('retourne l\'id de l\'element ajoute', () => {
      const { result } = renderHook(() => useOfflineStorage())

      let id: string = ''
      act(() => {
        id = result.current.addToQueue('create', '/api/test', 'POST', {})
      })

      expect(id).toBeTruthy()
      expect(typeof id).toBe('string')
    })

    it('supprime un element de la queue', async () => {
      const { result } = renderHook(() => useOfflineStorage())

      let id: string = ''
      act(() => {
        id = result.current.addToQueue('create', '/api/test', 'POST', {})
      })

      await waitFor(() => {
        expect(result.current.pendingCount).toBe(1)
      })

      act(() => {
        result.current.removeFromQueue(id)
      })

      await waitFor(() => {
        expect(result.current.pendingCount).toBe(0)
      })
    })

    it('vide toute la queue', async () => {
      const { result } = renderHook(() => useOfflineStorage())

      act(() => {
        result.current.addToQueue('create', '/api/test1', 'POST', {})
      })

      await waitFor(() => {
        expect(result.current.pendingCount).toBe(1)
      })

      act(() => {
        result.current.addToQueue('create', '/api/test2', 'POST', {})
      })

      await waitFor(() => {
        expect(result.current.pendingCount).toBe(2)
      })

      act(() => {
        result.current.clearQueue()
      })

      expect(result.current.pendingCount).toBe(0)
    })
  })

  describe('Cache de donnees', () => {
    it('retourne null pour une cle inexistante', async () => {
      const { result } = renderHook(() => useOfflineStorage())

      let cached: unknown = 'not-null'
      await act(async () => {
        cached = await result.current.getCachedData('nonexistent')
      })
      expect(cached).toBeNull()
    })

    it('vide tout le cache', async () => {
      const { result } = renderHook(() => useOfflineStorage())

      await act(async () => {
        await result.current.cacheData('key1', { a: 1 })
      })

      act(() => {
        result.current.clearCache()
      })

      let cached: unknown = 'not-null'
      await act(async () => {
        cached = await result.current.getCachedData('key1')
      })
      expect(cached).toBeNull()
    })
  })

  describe('Synchronisation', () => {
    it('synchronise les elements en attente', async () => {
      const { result } = renderHook(() => useOfflineStorage())

      act(() => {
        result.current.addToQueue('create', '/api/test', 'POST', {})
      })

      await waitFor(() => {
        expect(result.current.pendingCount).toBe(1)
      })

      const syncFn = vi.fn().mockResolvedValue(true)

      let syncResult: { success: number; failed: number } = { success: 0, failed: 0 }
      await act(async () => {
        syncResult = await result.current.syncPendingItems(syncFn)
      })

      expect(syncFn).toHaveBeenCalledTimes(1)
      expect(syncResult.success).toBe(1)
      expect(syncResult.failed).toBe(0)
      expect(result.current.pendingCount).toBe(0)
    })

    it('garde les elements en echec dans la queue', async () => {
      const { result } = renderHook(() => useOfflineStorage())

      act(() => {
        result.current.addToQueue('create', '/api/test', 'POST', {})
      })

      await waitFor(() => {
        expect(result.current.pendingCount).toBe(1)
      })

      const syncFn = vi.fn().mockResolvedValue(false)

      await act(async () => {
        await result.current.syncPendingItems(syncFn)
      })

      // Item should still be in queue (with incremented retry count)
      expect(result.current.pendingCount).toBe(1)
    })

    it('ne synchronise pas si hors-ligne', async () => {
      Object.defineProperty(navigator, 'onLine', {
        configurable: true,
        get: () => false,
      })

      const { result } = renderHook(() => useOfflineStorage())

      // Trigger offline event to update state
      act(() => {
        window.dispatchEvent(new Event('offline'))
      })

      act(() => {
        result.current.addToQueue('create', '/api/test', 'POST', {})
      })

      await waitFor(() => {
        expect(result.current.pendingCount).toBe(1)
      })

      const syncFn = vi.fn().mockResolvedValue(true)

      await act(async () => {
        await result.current.syncPendingItems(syncFn)
      })

      // Should not have called sync function
      expect(syncFn).not.toHaveBeenCalled()
    })
  })

  describe('Evenements online/offline', () => {
    it('detecte le passage hors-ligne', () => {
      const { result } = renderHook(() => useOfflineStorage())

      expect(result.current.isOnline).toBe(true)

      Object.defineProperty(navigator, 'onLine', {
        configurable: true,
        get: () => false,
      })

      act(() => {
        window.dispatchEvent(new Event('offline'))
      })

      expect(result.current.isOnline).toBe(false)
    })

    it('detecte le retour en ligne', () => {
      Object.defineProperty(navigator, 'onLine', {
        configurable: true,
        get: () => false,
      })

      const { result } = renderHook(() => useOfflineStorage())

      act(() => {
        window.dispatchEvent(new Event('offline'))
      })

      expect(result.current.isOnline).toBe(false)

      Object.defineProperty(navigator, 'onLine', {
        configurable: true,
        get: () => true,
      })

      act(() => {
        window.dispatchEvent(new Event('online'))
      })

      expect(result.current.isOnline).toBe(true)
    })
  })
})
