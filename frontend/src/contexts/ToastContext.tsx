import { createContext, useContext, useState, useCallback, ReactNode } from 'react'

export interface Toast {
  id: string
  message: string
  type: 'success' | 'error' | 'warning' | 'info'
  duration?: number
  action?: {
    label: string
    onClick: () => void
  }
}

interface ToastContextType {
  toasts: Toast[]
  addToast: (toast: Omit<Toast, 'id'>) => string
  removeToast: (id: string) => void
  showUndoToast: (message: string, onUndo: () => void, onConfirm: () => void, duration?: number) => void
}

const ToastContext = createContext<ToastContextType | undefined>(undefined)

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([])
  const [pendingActions, setPendingActions] = useState<Map<string, NodeJS.Timeout>>(new Map())

  const addToast = useCallback((toast: Omit<Toast, 'id'>) => {
    const id = Math.random().toString(36).substring(2, 9)
    const newToast = { ...toast, id }

    setToasts((prev) => [...prev, newToast])

    // Auto-remove after duration (default 5 seconds)
    const duration = toast.duration ?? 5000
    if (duration > 0) {
      setTimeout(() => {
        removeToast(id)
      }, duration)
    }

    return id
  }, [])

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))

    // Clear any pending action
    const timeout = pendingActions.get(id)
    if (timeout) {
      clearTimeout(timeout)
      setPendingActions((prev) => {
        const next = new Map(prev)
        next.delete(id)
        return next
      })
    }
  }, [pendingActions])

  const showUndoToast = useCallback((
    message: string,
    onUndo: () => void,
    onConfirm: () => void,
    duration = 5000
  ) => {
    const id = Math.random().toString(36).substring(2, 9)

    const newToast: Toast = {
      id,
      message,
      type: 'warning',
      duration: 0, // Don't auto-remove, we handle it manually
      action: {
        label: 'Annuler',
        onClick: () => {
          // Cancel the pending action
          const timeout = pendingActions.get(id)
          if (timeout) {
            clearTimeout(timeout)
          }
          onUndo()
          removeToast(id)
        },
      },
    }

    setToasts((prev) => [...prev, newToast])

    // Schedule the confirm action
    const timeout = setTimeout(() => {
      onConfirm()
      removeToast(id)
    }, duration)

    setPendingActions((prev) => {
      const next = new Map(prev)
      next.set(id, timeout)
      return next
    })
  }, [pendingActions, removeToast])

  return (
    <ToastContext.Provider value={{ toasts, addToast, removeToast, showUndoToast }}>
      {children}
    </ToastContext.Provider>
  )
}

export function useToast() {
  const context = useContext(ToastContext)
  if (context === undefined) {
    throw new Error('useToast must be used within a ToastProvider')
  }
  return context
}
