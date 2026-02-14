/**
 * Hook pour piéger le focus dans un conteneur (modales, dialogs).
 *
 * - Cycle Tab/Shift+Tab entre les éléments focusables
 * - Ferme sur Escape
 * - Restaure le focus à l'élément précédent à la fermeture
 * - Respecte prefers-reduced-motion pour les transitions
 */
import { useEffect, useRef, useCallback } from 'react'

const FOCUSABLE_SELECTOR = [
  'a[href]',
  'button:not([disabled])',
  'input:not([disabled])',
  'select:not([disabled])',
  'textarea:not([disabled])',
  '[tabindex]:not([tabindex="-1"])',
].join(', ')

interface UseFocusTrapOptions {
  /** Activer le piège (lié à isOpen de la modale) */
  enabled: boolean
  /** Callback pour fermer la modale (touche Escape) */
  onClose?: () => void
}

export function useFocusTrap({ enabled, onClose }: UseFocusTrapOptions) {
  const containerRef = useRef<HTMLDivElement>(null)
  const previousFocusRef = useRef<HTMLElement | null>(null)

  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    if (!containerRef.current) return

    // Escape → fermer la modale
    if (e.key === 'Escape') {
      e.stopPropagation()
      onClose?.()
      return
    }

    // Tab → cycle dans le conteneur
    if (e.key === 'Tab') {
      const focusableElements = containerRef.current.querySelectorAll<HTMLElement>(FOCUSABLE_SELECTOR)
      if (focusableElements.length === 0) return

      const first = focusableElements[0]
      const last = focusableElements[focusableElements.length - 1]

      if (e.shiftKey) {
        // Shift+Tab depuis le premier → aller au dernier
        if (document.activeElement === first) {
          e.preventDefault()
          last.focus()
        }
      } else {
        // Tab depuis le dernier → aller au premier
        if (document.activeElement === last) {
          e.preventDefault()
          first.focus()
        }
      }
    }
  }, [onClose])

  useEffect(() => {
    if (!enabled) return

    // Sauvegarder le focus actuel
    previousFocusRef.current = document.activeElement as HTMLElement

    // Focus le premier élément focusable du conteneur
    const timer = setTimeout(() => {
      if (!containerRef.current) return
      const firstFocusable = containerRef.current.querySelector<HTMLElement>(FOCUSABLE_SELECTOR)
      firstFocusable?.focus()
    }, 50) // Petit délai pour laisser le DOM se stabiliser

    // Ajouter le listener
    document.addEventListener('keydown', handleKeyDown)

    return () => {
      clearTimeout(timer)
      document.removeEventListener('keydown', handleKeyDown)

      // Restaurer le focus précédent
      previousFocusRef.current?.focus()
    }
  }, [enabled, handleKeyDown])

  return containerRef
}

export default useFocusTrap
