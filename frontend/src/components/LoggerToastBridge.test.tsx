import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render } from '@testing-library/react'
import { LoggerToastBridge } from './LoggerToastBridge'
import { ToastProvider, useToast } from '../contexts/ToastContext'
import { logger, onLog } from '../services/logger'

// Mock the logger module
vi.mock('../services/logger', () => ({
  logger: {
    error: vi.fn(),
    warn: vi.fn(),
    info: vi.fn(),
    debug: vi.fn(),
  },
  onLog: vi.fn(),
}))

// Mock useToast
const mockAddToast = vi.fn()
vi.mock('../contexts/ToastContext', async () => {
  const actual = await vi.importActual('../contexts/ToastContext')
  return {
    ...actual,
    useToast: () => ({
      addToast: mockAddToast,
      toasts: [],
      removeToast: vi.fn(),
      showUndoToast: vi.fn(),
    }),
  }
})

describe('LoggerToastBridge', () => {
  let logCallback: ((entry: any) => void) | null = null
  let unsubscribeMock: ReturnType<typeof vi.fn>

  beforeEach(() => {
    vi.clearAllMocks()
    unsubscribeMock = vi.fn()
    vi.mocked(onLog).mockImplementation((callback) => {
      logCallback = callback
      return unsubscribeMock
    })
  })

  afterEach(() => {
    logCallback = null
  })

  it('should subscribe to logger on mount', () => {
    render(<LoggerToastBridge />)
    expect(onLog).toHaveBeenCalled()
  })

  it('should unsubscribe on unmount', () => {
    const { unmount } = render(<LoggerToastBridge />)
    unmount()
    expect(unsubscribeMock).toHaveBeenCalled()
  })

  it('should not add toast when showToast is false', () => {
    render(<LoggerToastBridge />)

    // Simulate a log entry without showToast
    if (logCallback) {
      logCallback({
        level: 'error',
        message: 'Test error',
        options: { showToast: false },
      })
    }

    expect(mockAddToast).not.toHaveBeenCalled()
  })

  it('should not add toast when showToast is undefined', () => {
    render(<LoggerToastBridge />)

    if (logCallback) {
      logCallback({
        level: 'error',
        message: 'Test error',
        options: {},
      })
    }

    expect(mockAddToast).not.toHaveBeenCalled()
  })

  it('should add error toast when showToast is true', () => {
    render(<LoggerToastBridge />)

    if (logCallback) {
      logCallback({
        level: 'error',
        message: 'Test error',
        options: { showToast: true },
      })
    }

    expect(mockAddToast).toHaveBeenCalledWith(
      expect.objectContaining({
        type: 'error',
        message: 'Test error',
      })
    )
  })

  it('should add warning toast for warn level', () => {
    render(<LoggerToastBridge />)

    if (logCallback) {
      logCallback({
        level: 'warn',
        message: 'Test warning',
        options: { showToast: true },
      })
    }

    expect(mockAddToast).toHaveBeenCalledWith(
      expect.objectContaining({
        type: 'warning',
        message: 'Test warning',
      })
    )
  })

  it('should add info toast for info level', () => {
    render(<LoggerToastBridge />)

    if (logCallback) {
      logCallback({
        level: 'info',
        message: 'Test info',
        options: { showToast: true },
      })
    }

    expect(mockAddToast).toHaveBeenCalledWith(
      expect.objectContaining({
        type: 'info',
        message: 'Test info',
      })
    )
  })

  it('should include error message when Error object is provided', () => {
    render(<LoggerToastBridge />)

    const error = new Error('Specific error')
    if (logCallback) {
      logCallback({
        level: 'error',
        message: 'Operation failed',
        error: error,
        options: { showToast: true },
      })
    }

    expect(mockAddToast).toHaveBeenCalledWith(
      expect.objectContaining({
        type: 'error',
        message: 'Operation failed: Specific error',
      })
    )
  })

  it('should use longer duration for error toasts', () => {
    render(<LoggerToastBridge />)

    if (logCallback) {
      logCallback({
        level: 'error',
        message: 'Test error',
        options: { showToast: true },
      })
    }

    expect(mockAddToast).toHaveBeenCalledWith(
      expect.objectContaining({
        duration: 8000,
      })
    )
  })

  it('should use shorter duration for non-error toasts', () => {
    render(<LoggerToastBridge />)

    if (logCallback) {
      logCallback({
        level: 'info',
        message: 'Test info',
        options: { showToast: true },
      })
    }

    expect(mockAddToast).toHaveBeenCalledWith(
      expect.objectContaining({
        duration: 5000,
      })
    )
  })

  it('should render null (no visible output)', () => {
    const { container } = render(<LoggerToastBridge />)
    expect(container.firstChild).toBeNull()
  })
})
