/**
 * useKeyboardShortcuts - Hook global pour les raccourcis clavier
 * Section 4.4 - Raccourcis clavier
 *
 * Raccourcis disponibles:
 * - Alt+P → /planning
 * - Alt+H → /feuilles-heures
 * - Alt+D → /documents
 * - Alt+C → /chantiers
 * - Alt+F → /finances
 * - ? → Afficher l'aide des raccourcis
 */

import { useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'

export interface UseKeyboardShortcutsOptions {
  onShowHelp?: () => void
}

export interface UseKeyboardShortcutsReturn {
  // Pas de méthodes exposées pour l'instant, juste l'écoute des événements
}

/**
 * Hook qui écoute les raccourcis clavier globaux
 * @param options Options du hook
 */
export function useKeyboardShortcuts(
  options: UseKeyboardShortcutsOptions = {}
): UseKeyboardShortcutsReturn {
  const navigate = useNavigate()
  const { onShowHelp } = options

  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      // Vérifier si on est dans un champ de saisie
      const target = e.target as HTMLElement
      const isInputField =
        target.tagName === 'INPUT' ||
        target.tagName === 'TEXTAREA' ||
        target.tagName === 'SELECT' ||
        target.isContentEditable

      // Si on est dans un input/textarea/select, ne pas traiter les raccourcis
      // (sauf pour ? qui peut être utile même dans un champ)
      if (isInputField && e.key !== '?') {
        return
      }

      // Raccourcis avec Alt
      if (e.altKey && !e.ctrlKey && !e.shiftKey && !e.metaKey) {
        switch (e.key.toLowerCase()) {
          case 'p':
            e.preventDefault()
            navigate('/planning')
            break
          case 'h':
            e.preventDefault()
            navigate('/feuilles-heures')
            break
          case 'd':
            e.preventDefault()
            navigate('/documents')
            break
          case 'c':
            e.preventDefault()
            navigate('/chantiers')
            break
          case 'f':
            e.preventDefault()
            navigate('/finances')
            break
          default:
            // Ne rien faire pour les autres touches
            break
        }
      }

      // Raccourci ? pour afficher l'aide (seulement si pas dans un input)
      if (e.key === '?' && !isInputField && !e.altKey && !e.ctrlKey && !e.shiftKey && !e.metaKey) {
        e.preventDefault()
        if (onShowHelp) {
          onShowHelp()
        }
      }
    },
    [navigate, onShowHelp]
  )

  useEffect(() => {
    // Écouter les événements clavier sur le document
    document.addEventListener('keydown', handleKeyDown)

    return () => {
      document.removeEventListener('keydown', handleKeyDown)
    }
  }, [handleKeyDown])

  return {}
}
