import { useEffect, useState } from 'react'
import { useToast, Toast as ToastType } from '../contexts/ToastContext'

// Inline SVG icons to avoid lucide-react in initial bundle
const CheckIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
)

const AlertIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
)

const WarningIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
  </svg>
)

const InfoIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
)

const CloseIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
  </svg>
)

const ICONS = {
  success: CheckIcon,
  error: AlertIcon,
  warning: WarningIcon,
  info: InfoIcon,
}

const COLORS = {
  success: {
    bg: 'bg-green-50',
    border: 'border-green-200',
    text: 'text-green-800',
    icon: 'text-green-500',
    progress: 'bg-green-500',
  },
  error: {
    bg: 'bg-red-50',
    border: 'border-red-200',
    text: 'text-red-800',
    icon: 'text-red-500',
    progress: 'bg-red-500',
  },
  warning: {
    bg: 'bg-yellow-50',
    border: 'border-yellow-200',
    text: 'text-yellow-800',
    icon: 'text-yellow-500',
    progress: 'bg-yellow-500',
  },
  info: {
    bg: 'bg-blue-50',
    border: 'border-blue-200',
    text: 'text-blue-800',
    icon: 'text-blue-500',
    progress: 'bg-blue-500',
  },
}

function ToastItem({ toast, duration = 5000 }: { toast: ToastType; duration?: number }) {
  const { removeToast } = useToast()
  const [progress, setProgress] = useState(100)
  const Icon = ICONS[toast.type]
  const colors = COLORS[toast.type]

  useEffect(() => {
    if (toast.action && duration > 0) {
      // Animate progress bar
      const interval = setInterval(() => {
        setProgress((prev) => {
          const next = prev - (100 / (duration / 100))
          return next < 0 ? 0 : next
        })
      }, 100)

      return () => clearInterval(interval)
    }
  }, [toast.action, duration])

  return (
    <div
      className={`flex items-start gap-3 p-4 rounded-lg border shadow-lg ${colors.bg} ${colors.border} min-w-[320px] max-w-md relative overflow-hidden`}
    >
      <Icon className={`w-5 h-5 shrink-0 ${colors.icon}`} />
      <div className="flex-1">
        <p className={`text-sm font-medium ${colors.text}`}>{toast.message}</p>
        {toast.action && (
          <button
            onClick={toast.action.onClick}
            className={`mt-2 text-sm font-semibold ${colors.text} hover:underline`}
          >
            {toast.action.label}
          </button>
        )}
      </div>
      <button
        onClick={() => removeToast(toast.id)}
        className={`p-1 rounded hover:bg-black/5 ${colors.text}`}
        aria-label="Fermer la notification"
      >
        <CloseIcon className="w-4 h-4" />
      </button>

      {/* Progress bar for undo toasts */}
      {toast.action && (
        <div className="absolute bottom-0 left-0 right-0 h-1 bg-black/10">
          <div
            className={`h-full ${colors.progress} transition-all duration-100 ease-linear`}
            style={{ width: `${progress}%` }}
          />
        </div>
      )}
    </div>
  )
}

export default function ToastContainer() {
  const { toasts } = useToast()

  if (toasts.length === 0) return null

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2">
      {toasts.map((toast) => (
        <ToastItem key={toast.id} toast={toast} />
      ))}
    </div>
  )
}
