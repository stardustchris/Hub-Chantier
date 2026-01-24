import { useEffect } from 'react'
import { useToast } from '../contexts/ToastContext'
import { onLog } from '../services/logger'

/**
 * Bridge component that connects the logger service to the Toast system.
 * When a log with showToast: true is emitted, it displays a toast notification.
 */
export function LoggerToastBridge() {
  const { addToast } = useToast()

  useEffect(() => {
    // Subscribe to log events
    const unsubscribe = onLog((entry) => {
      // Only show toast if explicitly requested
      if (!entry.options?.showToast) return

      // Map log level to toast type
      const typeMap: Record<string, 'success' | 'error' | 'warning' | 'info'> = {
        error: 'error',
        warn: 'warning',
        info: 'info',
        debug: 'info',
      }

      const toastType = typeMap[entry.level] || 'info'

      // Format user-friendly message
      let message = entry.message
      if (entry.error instanceof Error) {
        message = `${entry.message}: ${entry.error.message}`
      }

      addToast({
        type: toastType,
        message,
        duration: entry.level === 'error' ? 8000 : 5000,
      })
    })

    return unsubscribe
  }, [addToast])

  return null
}

export default LoggerToastBridge
