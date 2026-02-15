/**
 * ProgressiveHintBanner - Bannière d'indices progressifs
 * Affiche un indice contextuel pour les 3 premières visites d'une page
 * Peut être fermé manuellement
 */

import { useState, useEffect } from 'react'
import { Info, X } from 'lucide-react'
import { useProgressiveHint } from '../../hooks/useProgressiveHint'

interface ProgressiveHintBannerProps {
  /** Identifiant unique de la page (généralement le pathname) */
  pageId: string
  /** Message d'indice à afficher */
  message: string
  /** Classe CSS additionnelle optionnelle */
  className?: string
}

export default function ProgressiveHintBanner({ pageId, message, className = '' }: ProgressiveHintBannerProps) {
  const { shouldShowHint, recordVisit } = useProgressiveHint()
  const [isVisible, setIsVisible] = useState(false)

  // Enregistrer la visite au montage (une seule fois par pageId)
  useEffect(() => {
    recordVisit(pageId)
  }, [pageId, recordVisit])

  // Mettre à jour la visibilité quand shouldShowHint change
  useEffect(() => {
    setIsVisible(shouldShowHint(pageId))
  }, [pageId, shouldShowHint])

  // Ne rien afficher si le hint ne doit pas être visible
  if (!isVisible) {
    return null
  }

  const handleDismiss = () => {
    setIsVisible(false)
  }

  return (
    <div
      className={`bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-start gap-3 ${className}`}
      role="status"
      aria-live="polite"
    >
      <Info className="w-5 h-5 text-blue-600 mt-0.5 shrink-0" />
      <p className="text-sm text-blue-900 flex-1">
        {message}
      </p>
      <button
        onClick={handleDismiss}
        className="min-w-[48px] min-h-[48px] -mt-2 -mr-2 flex items-center justify-center rounded-lg hover:bg-blue-100 text-blue-600 transition-colors"
        aria-label="Fermer l'indice"
      >
        <X className="w-4 h-4" />
      </button>
    </div>
  )
}

ProgressiveHintBanner.displayName = 'ProgressiveHintBanner'
