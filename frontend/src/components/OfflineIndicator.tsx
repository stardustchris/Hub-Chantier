/**
 * OfflineIndicator - Indicateur de mode hors-ligne
 * FDH-20: Mode Offline (PWA/Service Worker)
 */

import { useState, useEffect, memo } from 'react'
import { WifiOff, RefreshCw, CheckCircle } from 'lucide-react'

interface OfflineIndicatorProps {
  className?: string
}

function OfflineIndicator({ className = '' }: OfflineIndicatorProps) {
  const [isOnline, setIsOnline] = useState(navigator.onLine)
  const [showReconnected, setShowReconnected] = useState(false)
  const [wasOffline, setWasOffline] = useState(false)

  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true)
      if (wasOffline) {
        setShowReconnected(true)
        // Hide "reconnected" message after 3 seconds
        setTimeout(() => setShowReconnected(false), 3000)
      }
    }

    const handleOffline = () => {
      setIsOnline(false)
      setWasOffline(true)
    }

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [wasOffline])

  // Sync pending data when back online
  useEffect(() => {
    if (isOnline && wasOffline) {
      // Trigger sync of any pending offline data
      if ('serviceWorker' in navigator) {
        navigator.serviceWorker.ready.then((registration) => {
          // Check if sync is supported
          if ('sync' in registration) {
            (registration as any).sync?.register('sync-pending-data').catch(() => {
              // Background sync not supported or failed
            })
          }
        }).catch(() => {
          // Service worker not ready
        })
      }
    }
  }, [isOnline, wasOffline])

  if (isOnline && !showReconnected) {
    return null
  }

  return (
    <div
      className={`fixed bottom-4 left-1/2 -translate-x-1/2 z-50 animate-slide-up ${className}`}
      role="status"
      aria-live="polite"
    >
      {!isOnline ? (
        <div className="flex items-center gap-3 px-4 py-3 bg-amber-100 border border-amber-300 rounded-lg shadow-lg">
          <WifiOff className="w-5 h-5 text-amber-600" />
          <div>
            <p className="font-medium text-amber-800">Mode hors-ligne</p>
            <p className="text-sm text-amber-700">
              Vos modifications seront synchronisees a la reconnexion
            </p>
          </div>
          <button
            onClick={() => window.location.reload()}
            className="p-2 hover:bg-amber-200 rounded-lg transition-colors"
            aria-label="Recharger la page"
          >
            <RefreshCw className="w-4 h-4 text-amber-700" />
          </button>
        </div>
      ) : (
        <div className="flex items-center gap-3 px-4 py-3 bg-green-100 border border-green-300 rounded-lg shadow-lg">
          <CheckCircle className="w-5 h-5 text-green-600" />
          <p className="font-medium text-green-800">Connexion retablie</p>
        </div>
      )}
    </div>
  )
}

export default memo(OfflineIndicator)
