/**
 * Tests pour le hook useServerEvents (SSE temps réel).
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'

// Mock logger
vi.mock('../services/logger', () => ({
  logger: {
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
    debug: vi.fn(),
  },
}))

// Mock TanStack Query
const mockInvalidateQueries = vi.fn()
vi.mock('@tanstack/react-query', () => ({
  useQueryClient: () => ({
    invalidateQueries: mockInvalidateQueries,
  }),
}))

import { useServerEvents } from './useServerEvents'

// Mock EventSource
class MockEventSource {
  static CONNECTING = 0
  static OPEN = 1
  static CLOSED = 2

  url: string
  readyState: number = MockEventSource.CONNECTING
  onopen: ((event: Event) => void) | null = null
  onmessage: ((event: MessageEvent) => void) | null = null
  onerror: ((event: Event) => void) | null = null

  private eventListeners: Map<string, EventListener[]> = new Map()

  constructor(url: string) {
    this.url = url
    // Simulate async open
    setTimeout(() => {
      this.readyState = MockEventSource.OPEN
      this.onopen?.(new Event('open'))
    }, 0)
  }

  addEventListener(type: string, listener: EventListener) {
    if (!this.eventListeners.has(type)) {
      this.eventListeners.set(type, [])
    }
    this.eventListeners.get(type)!.push(listener)
  }

  removeEventListener(type: string, listener: EventListener) {
    const listeners = this.eventListeners.get(type) || []
    const index = listeners.indexOf(listener)
    if (index !== -1) listeners.splice(index, 1)
  }

  close() {
    this.readyState = MockEventSource.CLOSED
  }

  // Helper: simulate receiving a message
  simulateMessage(data: string) {
    const event = new MessageEvent('message', { data })
    this.onmessage?.(event)
  }

  // Helper: simulate typed event
  simulateTypedEvent(type: string, data: string) {
    const event = new MessageEvent(type, { data })
    const listeners = this.eventListeners.get(type) || []
    listeners.forEach((l) => l(event))
  }

  // Helper: simulate error
  simulateError() {
    this.readyState = MockEventSource.CLOSED
    this.onerror?.(new Event('error'))
  }
}

let mockEventSourceInstance: MockEventSource | null = null

describe('useServerEvents', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers()
    mockEventSourceInstance = null

    // Setup navigator.onLine
    Object.defineProperty(navigator, 'onLine', {
      writable: true,
      value: true,
    })

    // Setup EventSource mock
    vi.stubGlobal('EventSource', class extends MockEventSource {
      constructor(url: string) {
        super(url)
        mockEventSourceInstance = this
      }

      static CONNECTING = MockEventSource.CONNECTING
      static OPEN = MockEventSource.OPEN
      static CLOSED = MockEventSource.CLOSED
    })
  })

  afterEach(() => {
    vi.useRealTimers()
    vi.unstubAllGlobals()
  })

  it('se connecte au stream SSE', () => {
    renderHook(() => useServerEvents())
    expect(mockEventSourceInstance).not.toBeNull()
    expect(mockEventSourceInstance!.url).toBe('/api/notifications/stream')
  })

  it('retourne isConnected=false initialement', () => {
    const { result } = renderHook(() => useServerEvents())
    expect(result.current.isConnected).toBe(false)
  })

  it('passe isConnected=true après onopen', async () => {
    const { result } = renderHook(() => useServerEvents())

    await act(async () => {
      vi.advanceTimersByTime(10)
    })

    expect(result.current.isConnected).toBe(true)
  })

  it('invalide les query keys pour notification.created', async () => {
    const { result } = renderHook(() => useServerEvents())

    await act(async () => {
      vi.advanceTimersByTime(10)
    })

    act(() => {
      mockEventSourceInstance!.simulateMessage(
        JSON.stringify({ event_type: 'notification.created' })
      )
    })

    expect(mockInvalidateQueries).toHaveBeenCalledWith({ queryKey: ['notifications'] })
    expect(result.current.eventsReceived).toBe(1)
  })

  it('invalide plusieurs query keys pour comment.added', async () => {
    renderHook(() => useServerEvents())

    await act(async () => {
      vi.advanceTimersByTime(10)
    })

    act(() => {
      mockEventSourceInstance!.simulateMessage(
        JSON.stringify({ event_type: 'comment.added' })
      )
    })

    expect(mockInvalidateQueries).toHaveBeenCalledWith({ queryKey: ['notifications'] })
    expect(mockInvalidateQueries).toHaveBeenCalledWith({ queryKey: ['feed'] })
  })

  it('invalide planning + notifications pour affectation.created', async () => {
    renderHook(() => useServerEvents())

    await act(async () => {
      vi.advanceTimersByTime(10)
    })

    act(() => {
      mockEventSourceInstance!.simulateMessage(
        JSON.stringify({ event_type: 'affectation.created' })
      )
    })

    expect(mockInvalidateQueries).toHaveBeenCalledWith({ queryKey: ['planning'] })
    expect(mockInvalidateQueries).toHaveBeenCalledWith({ queryKey: ['notifications'] })
  })

  it('utilise DEFAULT_INVALIDATION pour event_type inconnu', async () => {
    renderHook(() => useServerEvents())

    await act(async () => {
      vi.advanceTimersByTime(10)
    })

    act(() => {
      mockEventSourceInstance!.simulateMessage(
        JSON.stringify({ event_type: 'unknown.event' })
      )
    })

    expect(mockInvalidateQueries).toHaveBeenCalledWith({ queryKey: ['notifications'] })
    expect(mockInvalidateQueries).toHaveBeenCalledTimes(1)
  })

  it('incrémente eventsReceived à chaque message', async () => {
    const { result } = renderHook(() => useServerEvents())

    await act(async () => {
      vi.advanceTimersByTime(10)
    })

    act(() => {
      mockEventSourceInstance!.simulateMessage(JSON.stringify({ event_type: 'test.1' }))
    })
    act(() => {
      mockEventSourceInstance!.simulateMessage(JSON.stringify({ event_type: 'test.2' }))
    })

    expect(result.current.eventsReceived).toBe(2)
  })

  it('gère les erreurs de parsing JSON', async () => {
    renderHook(() => useServerEvents())

    await act(async () => {
      vi.advanceTimersByTime(10)
    })

    // Should not throw
    act(() => {
      mockEventSourceInstance!.simulateMessage('invalid-json')
    })

    expect(mockInvalidateQueries).not.toHaveBeenCalled()
  })

  it('ne se connecte pas quand offline', () => {
    Object.defineProperty(navigator, 'onLine', { value: false })
    renderHook(() => useServerEvents())
    expect(mockEventSourceInstance).toBeNull()
  })

  it('ferme la connexion au unmount', async () => {
    const { unmount } = renderHook(() => useServerEvents())

    await act(async () => {
      vi.advanceTimersByTime(10)
    })

    const closeSpy = vi.spyOn(mockEventSourceInstance!, 'close')
    unmount()
    expect(closeSpy).toHaveBeenCalled()
  })

  it('passe isConnected=false après erreur', async () => {
    const { result } = renderHook(() => useServerEvents())

    await act(async () => {
      vi.advanceTimersByTime(10)
    })

    expect(result.current.isConnected).toBe(true)

    act(() => {
      mockEventSourceInstance!.simulateError()
    })

    expect(result.current.isConnected).toBe(false)
  })

  it('tente une reconnexion après erreur', async () => {
    renderHook(() => useServerEvents())

    await act(async () => {
      vi.advanceTimersByTime(10)
    })

    const firstInstance = mockEventSourceInstance!

    act(() => {
      firstInstance.simulateError()
    })

    // Reconnexion après 1s (2^0 * 1000)
    await act(async () => {
      vi.advanceTimersByTime(1100)
    })

    // Should have created a new EventSource
    expect(mockEventSourceInstance).not.toBe(firstInstance)
  })
})
