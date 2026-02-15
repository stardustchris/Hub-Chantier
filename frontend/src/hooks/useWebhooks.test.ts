// @vitest-environment jsdom
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'

// Mock dependencies before importing hook
vi.mock('../services/webhooks', () => ({
  webhooksApi: {
    list: vi.fn(),
    create: vi.fn(),
    delete: vi.fn(),
    test: vi.fn(),
    deliveries: vi.fn(),
  },
}))

vi.mock('../services/logger', () => ({
  logger: {
    error: vi.fn(),
    info: vi.fn(),
    warn: vi.fn(),
  },
}))

import { useWebhooks } from './useWebhooks'
import { webhooksApi } from '../services/webhooks'
import type { Webhook } from '../services/webhooks'
import { logger } from '../services/logger'

const mockWebhooks: Webhook[] = [
  {
    id: 'wh-1',
    url: 'https://example.com/webhook1',
    events: ['chantier.created', 'chantier.updated'],
    description: 'Test webhook 1',
    is_active: true,
    last_triggered_at: '2026-01-15T10:00:00Z',
    consecutive_failures: 0,
    created_at: '2026-01-01T00:00:00Z',
  },
  {
    id: 'wh-2',
    url: 'https://example.com/webhook2-very-long-url-that-should-be-truncated-when-displayed',
    events: ['formulaire.submitted'],
    is_active: false,
    consecutive_failures: 3,
    created_at: '2026-01-05T00:00:00Z',
  },
]

// Mock confirm and clipboard
const mockConfirm = vi.fn()
const mockClipboard = { writeText: vi.fn() }

Object.defineProperty(globalThis, 'confirm', { value: mockConfirm, writable: true })
Object.defineProperty(navigator, 'clipboard', { value: mockClipboard, writable: true })

/** Helper to render the hook and wait for initial load to complete */
async function renderAndLoad() {
  const hook = renderHook(() => useWebhooks())
  await waitFor(() => {
    expect(hook.result.current.isLoading).toBe(false)
  })
  return hook
}

describe('useWebhooks', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(webhooksApi.list).mockResolvedValue(mockWebhooks)
    mockConfirm.mockReturnValue(true)
    mockClipboard.writeText.mockResolvedValue(undefined)
  })

  describe('initial state and loading', () => {
    it('should load webhooks on mount', async () => {
      const { result } = renderHook(() => useWebhooks())

      // Initially loading
      expect(result.current.isLoading).toBe(true)

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })

      expect(result.current.webhooks).toEqual(mockWebhooks)
      expect(webhooksApi.list).toHaveBeenCalledTimes(1)
    })

    it('should have correct default modal states', async () => {
      const { result } = await renderAndLoad()

      expect(result.current.showCreateModal).toBe(false)
      expect(result.current.showSecretModal).toBe(false)
      expect(result.current.showDeliveryModal).toBe(false)
      expect(result.current.selectedWebhook).toBeNull()
      expect(result.current.newSecret).toBe('')
      expect(result.current.newWebhook).toBeNull()
      expect(result.current.secretCopied).toBe(false)
    })

    it('should handle load error', async () => {
      vi.mocked(webhooksApi.list).mockRejectedValue(new Error('Network error'))

      const { result } = renderHook(() => useWebhooks())

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })

      expect(logger.error).toHaveBeenCalledWith(
        'Erreur chargement webhooks',
        expect.any(Error),
        expect.objectContaining({ context: 'WebhooksPage', showToast: true })
      )
      expect(result.current.webhooks).toEqual([])
    })
  })

  describe('setShowCreateModal', () => {
    it('should toggle create modal', async () => {
      const { result } = await renderAndLoad()

      act(() => {
        result.current.setShowCreateModal(true)
      })

      expect(result.current.showCreateModal).toBe(true)
    })
  })

  describe('deleteWebhook', () => {
    it('should delete webhook when confirmed', async () => {
      vi.mocked(webhooksApi.delete).mockResolvedValue(undefined)

      const { result } = await renderAndLoad()

      await act(async () => {
        await result.current.deleteWebhook(mockWebhooks[0])
      })

      expect(mockConfirm).toHaveBeenCalled()
      expect(webhooksApi.delete).toHaveBeenCalledWith('wh-1')
      expect(logger.info).toHaveBeenCalledWith(
        expect.stringContaining('supprimé'),
        expect.objectContaining({ context: 'WebhooksPage', showToast: true })
      )
    })

    it('should not delete when user cancels confirm', async () => {
      mockConfirm.mockReturnValue(false)

      const { result } = await renderAndLoad()

      await act(async () => {
        await result.current.deleteWebhook(mockWebhooks[0])
      })

      expect(webhooksApi.delete).not.toHaveBeenCalled()
    })

    it('should handle delete error', async () => {
      vi.mocked(webhooksApi.delete).mockRejectedValue(new Error('Delete failed'))

      const { result } = await renderAndLoad()

      await act(async () => {
        await result.current.deleteWebhook(mockWebhooks[0])
      })

      expect(logger.error).toHaveBeenCalledWith(
        'Erreur suppression webhook',
        expect.any(Error),
        expect.objectContaining({ context: 'WebhooksPage', showToast: true })
      )
    })
  })

  describe('testWebhook', () => {
    it('should test webhook and log success', async () => {
      vi.mocked(webhooksApi.test).mockResolvedValue(undefined)

      const { result } = await renderAndLoad()

      await act(async () => {
        await result.current.testWebhook(mockWebhooks[0])
      })

      expect(webhooksApi.test).toHaveBeenCalledWith('wh-1')
      expect(logger.info).toHaveBeenCalledWith(
        'Test webhook envoyé',
        expect.objectContaining({ context: 'WebhooksPage', showToast: true })
      )
    })

    it('should handle test error', async () => {
      vi.mocked(webhooksApi.test).mockRejectedValue(new Error('Test failed'))

      const { result } = await renderAndLoad()

      await act(async () => {
        await result.current.testWebhook(mockWebhooks[0])
      })

      expect(logger.error).toHaveBeenCalledWith(
        'Erreur test webhook',
        expect.any(Error),
        expect.objectContaining({ context: 'WebhooksPage', showToast: true })
      )
    })
  })

  describe('viewDeliveries', () => {
    it('should set selected webhook and open delivery modal', async () => {
      const { result } = await renderAndLoad()

      act(() => {
        result.current.viewDeliveries(mockWebhooks[0])
      })

      expect(result.current.selectedWebhook).toEqual(mockWebhooks[0])
      expect(result.current.showDeliveryModal).toBe(true)
    })
  })

  describe('onWebhookCreated', () => {
    it('should store secret, open secret modal, close create modal, and reload', async () => {
      const { result } = await renderAndLoad()

      act(() => {
        result.current.setShowCreateModal(true)
      })

      const createdWebhook = mockWebhooks[0]
      act(() => {
        result.current.onWebhookCreated('secret-abc', createdWebhook)
      })

      expect(result.current.newSecret).toBe('secret-abc')
      expect(result.current.newWebhook).toEqual(createdWebhook)
      expect(result.current.showSecretModal).toBe(true)
      expect(result.current.showCreateModal).toBe(false)
    })
  })

  describe('copySecret', () => {
    it('should copy secret to clipboard', async () => {
      const { result } = await renderAndLoad()

      act(() => {
        result.current.onWebhookCreated('my-secret', mockWebhooks[0])
      })

      await act(async () => {
        await result.current.copySecret()
      })

      expect(mockClipboard.writeText).toHaveBeenCalledWith('my-secret')
      expect(result.current.secretCopied).toBe(true)
    })

    it('should reset secretCopied after 3 seconds', async () => {
      vi.useFakeTimers({ shouldAdvanceTime: true })

      const { result } = await renderAndLoad()

      act(() => {
        result.current.onWebhookCreated('my-secret', mockWebhooks[0])
      })

      await act(async () => {
        await result.current.copySecret()
      })

      expect(result.current.secretCopied).toBe(true)

      act(() => {
        vi.advanceTimersByTime(3000)
      })

      expect(result.current.secretCopied).toBe(false)

      vi.useRealTimers()
    })

    it('should handle clipboard error', async () => {
      mockClipboard.writeText.mockRejectedValue(new Error('Clipboard denied'))

      const { result } = await renderAndLoad()

      act(() => {
        result.current.onWebhookCreated('my-secret', mockWebhooks[0])
      })

      await act(async () => {
        await result.current.copySecret()
      })

      expect(logger.error).toHaveBeenCalledWith(
        'Erreur copie presse-papier',
        expect.any(Error),
        expect.objectContaining({ context: 'WebhooksPage' })
      )
    })
  })

  describe('closeSecretModal', () => {
    it('should reset secret state', async () => {
      const { result } = await renderAndLoad()

      act(() => {
        result.current.onWebhookCreated('my-secret', mockWebhooks[0])
      })

      act(() => {
        result.current.closeSecretModal()
      })

      expect(result.current.showSecretModal).toBe(false)
      expect(result.current.newSecret).toBe('')
      expect(result.current.newWebhook).toBeNull()
      expect(result.current.secretCopied).toBe(false)
    })
  })

  describe('closeDeliveryModal', () => {
    it('should close delivery modal and clear selected webhook', async () => {
      const { result } = await renderAndLoad()

      act(() => {
        result.current.viewDeliveries(mockWebhooks[0])
      })

      act(() => {
        result.current.closeDeliveryModal()
      })

      expect(result.current.showDeliveryModal).toBe(false)
      expect(result.current.selectedWebhook).toBeNull()
    })
  })

  describe('formatDate', () => {
    it('should return "Jamais" for null/undefined', async () => {
      const { result } = await renderAndLoad()

      expect(result.current.formatDate(null)).toBe('Jamais')
      expect(result.current.formatDate(undefined)).toBe('Jamais')
    })

    it('should format a valid date string', async () => {
      const { result } = await renderAndLoad()

      const formatted = result.current.formatDate('2026-01-15T10:30:00Z')
      expect(typeof formatted).toBe('string')
      expect(formatted).not.toBe('Jamais')
    })
  })

  describe('truncateUrl', () => {
    it('should return short URLs unchanged', async () => {
      const { result } = await renderAndLoad()

      expect(result.current.truncateUrl('https://short.com')).toBe('https://short.com')
    })

    it('should truncate long URLs', async () => {
      const { result } = await renderAndLoad()

      const longUrl = 'https://example.com/very/long/url/that/exceeds/fifty/characters/definitely'
      const truncated = result.current.truncateUrl(longUrl)
      expect(truncated.length).toBeLessThanOrEqual(53) // 50 + '...'
      expect(truncated).toContain('...')
    })

    it('should respect custom maxLength', async () => {
      const { result } = await renderAndLoad()

      const url = 'https://example.com/path'
      const truncated = result.current.truncateUrl(url, 10)
      expect(truncated).toBe('https://ex...')
    })
  })
})
