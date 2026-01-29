// @vitest-environment jsdom
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'

// Mock dependencies before importing hook
vi.mock('../services/apiKeys', () => ({
  apiKeysService: {
    list: vi.fn(),
    create: vi.fn(),
    revoke: vi.fn(),
  },
}))

vi.mock('../services/logger', () => ({
  logger: {
    error: vi.fn(),
    info: vi.fn(),
    warn: vi.fn(),
  },
}))

import { useAPIKeys, formatDate, isExpiringSoon, isExpired } from './useAPIKeys'
import { apiKeysService } from '../services/apiKeys'
import type { APIKey } from '../services/apiKeys'
import { logger } from '../services/logger'

const mockAPIKeys: APIKey[] = [
  {
    id: 'key-1',
    key_prefix: 'hc_abc',
    nom: 'Production Key',
    description: 'Main production key',
    scopes: ['read', 'write'],
    rate_limit_per_hour: 1000,
    is_active: true,
    last_used_at: '2026-01-20T10:00:00Z',
    expires_at: '2026-12-31T23:59:59Z',
    created_at: '2026-01-01T00:00:00Z',
  },
  {
    id: 'key-2',
    key_prefix: 'hc_def',
    nom: 'Test Key',
    description: null,
    scopes: ['read'],
    rate_limit_per_hour: 100,
    is_active: false,
    last_used_at: null,
    expires_at: null,
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
  const hook = renderHook(() => useAPIKeys())
  await waitFor(() => {
    expect(hook.result.current.isLoading).toBe(false)
  })
  return hook
}

describe('useAPIKeys', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(apiKeysService.list).mockResolvedValue(mockAPIKeys)
    mockConfirm.mockReturnValue(true)
    mockClipboard.writeText.mockResolvedValue(undefined)
  })

  describe('initial state and loading', () => {
    it('should load API keys on mount', async () => {
      const { result } = renderHook(() => useAPIKeys())

      expect(result.current.isLoading).toBe(true)

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })

      expect(result.current.apiKeys).toEqual(mockAPIKeys)
      expect(apiKeysService.list).toHaveBeenCalledTimes(1)
    })

    it('should have correct default modal states', async () => {
      const { result } = await renderAndLoad()

      expect(result.current.showCreateModal).toBe(false)
      expect(result.current.showSecretModal).toBe(false)
      expect(result.current.newSecret).toBe('')
      expect(result.current.newKeyInfo).toBeNull()
      expect(result.current.secretCopied).toBe(false)
    })

    it('should handle load error', async () => {
      vi.mocked(apiKeysService.list).mockRejectedValue(new Error('Network error'))

      const { result } = renderHook(() => useAPIKeys())

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })

      expect(logger.error).toHaveBeenCalledWith(
        'Erreur chargement cles API',
        expect.any(Error),
        expect.objectContaining({ context: 'APIKeysPage', showToast: true })
      )
      expect(result.current.apiKeys).toEqual([])
    })
  })

  describe('setShowCreateModal', () => {
    it('should toggle create modal', async () => {
      const { result } = await renderAndLoad()

      act(() => {
        result.current.setShowCreateModal(true)
      })

      expect(result.current.showCreateModal).toBe(true)

      act(() => {
        result.current.setShowCreateModal(false)
      })

      expect(result.current.showCreateModal).toBe(false)
    })
  })

  describe('revokeKey', () => {
    it('should revoke key when confirmed', async () => {
      vi.mocked(apiKeysService.revoke).mockResolvedValue(undefined)

      const { result } = await renderAndLoad()

      await act(async () => {
        await result.current.revokeKey('key-1', 'Production Key')
      })

      expect(mockConfirm).toHaveBeenCalled()
      expect(apiKeysService.revoke).toHaveBeenCalledWith('key-1')
      expect(logger.info).toHaveBeenCalledWith(
        expect.stringContaining('Production Key'),
        expect.objectContaining({ context: 'APIKeysPage', showToast: true })
      )
    })

    it('should not revoke when user cancels confirm', async () => {
      mockConfirm.mockReturnValue(false)

      const { result } = await renderAndLoad()

      await act(async () => {
        await result.current.revokeKey('key-1', 'Production Key')
      })

      expect(apiKeysService.revoke).not.toHaveBeenCalled()
    })

    it('should handle revoke error', async () => {
      vi.mocked(apiKeysService.revoke).mockRejectedValue(new Error('Revoke failed'))

      const { result } = await renderAndLoad()

      await act(async () => {
        await result.current.revokeKey('key-1', 'Production Key')
      })

      expect(logger.error).toHaveBeenCalledWith(
        'Erreur revocation cle',
        expect.any(Error),
        expect.objectContaining({ context: 'APIKeysPage', showToast: true })
      )
    })
  })

  describe('onKeyCreated', () => {
    it('should store secret and key info, open secret modal, close create modal, reload keys', async () => {
      const { result } = await renderAndLoad()

      act(() => {
        result.current.setShowCreateModal(true)
      })

      const keyInfo = { key_prefix: 'hc_xyz', nom: 'New Key', expires_at: null }
      act(() => {
        result.current.onKeyCreated('secret-xyz-123', keyInfo)
      })

      expect(result.current.newSecret).toBe('secret-xyz-123')
      expect(result.current.newKeyInfo).toEqual(keyInfo)
      expect(result.current.showSecretModal).toBe(true)
      expect(result.current.showCreateModal).toBe(false)
      // loadAPIKeys should have been called again
      expect(apiKeysService.list).toHaveBeenCalled()
    })
  })

  describe('copySecret', () => {
    it('should copy secret to clipboard and set copied state', async () => {
      const { result } = await renderAndLoad()

      act(() => {
        result.current.onKeyCreated('my-api-secret', {
          key_prefix: 'hc_test',
          nom: 'Test',
          expires_at: null,
        })
      })

      await act(async () => {
        await result.current.copySecret()
      })

      expect(mockClipboard.writeText).toHaveBeenCalledWith('my-api-secret')
      expect(result.current.secretCopied).toBe(true)
    })

    it('should reset secretCopied after 3 seconds', async () => {
      vi.useFakeTimers({ shouldAdvanceTime: true })

      const { result } = await renderAndLoad()

      act(() => {
        result.current.onKeyCreated('my-api-secret', {
          key_prefix: 'hc_test',
          nom: 'Test',
          expires_at: null,
        })
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
        result.current.onKeyCreated('my-secret', {
          key_prefix: 'hc_test',
          nom: 'Test',
          expires_at: null,
        })
      })

      await act(async () => {
        await result.current.copySecret()
      })

      expect(logger.error).toHaveBeenCalledWith(
        'Erreur copie presse-papier',
        expect.any(Error),
        expect.objectContaining({ context: 'APIKeysPage' })
      )
    })
  })

  describe('closeSecretModal', () => {
    it('should reset all secret state', async () => {
      const { result } = await renderAndLoad()

      act(() => {
        result.current.onKeyCreated('my-secret', {
          key_prefix: 'hc_test',
          nom: 'Test',
          expires_at: null,
        })
      })

      act(() => {
        result.current.closeSecretModal()
      })

      expect(result.current.showSecretModal).toBe(false)
      expect(result.current.newSecret).toBe('')
      expect(result.current.newKeyInfo).toBeNull()
      expect(result.current.secretCopied).toBe(false)
    })
  })
})

describe('formatDate (exported helper)', () => {
  it('should return "Jamais" for null', () => {
    expect(formatDate(null)).toBe('Jamais')
  })

  it('should format a valid date string', () => {
    const formatted = formatDate('2026-01-15T10:30:00Z')
    expect(typeof formatted).toBe('string')
    expect(formatted).not.toBe('Jamais')
  })
})

describe('isExpiringSoon (exported helper)', () => {
  it('should return false for null', () => {
    expect(isExpiringSoon(null)).toBe(false)
  })

  it('should return true for dates within 7 days', () => {
    const soon = new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString()
    expect(isExpiringSoon(soon)).toBe(true)
  })

  it('should return false for dates more than 7 days away', () => {
    const farFuture = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString()
    expect(isExpiringSoon(farFuture)).toBe(false)
  })

  it('should return false for past dates', () => {
    const past = new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString()
    expect(isExpiringSoon(past)).toBe(false)
  })
})

describe('isExpired (exported helper)', () => {
  it('should return false for null', () => {
    expect(isExpired(null)).toBe(false)
  })

  it('should return true for past dates', () => {
    const past = new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString()
    expect(isExpired(past)).toBe(true)
  })

  it('should return false for future dates', () => {
    const future = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString()
    expect(isExpired(future)).toBe(false)
  })
})
