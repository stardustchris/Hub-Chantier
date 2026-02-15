import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'

/**
 * Hook pour réinitialiser le focus et le scroll lors du changement de route
 * Améliore l'accessibilité pour les lecteurs d'écran
 */
export function useRouteChangeReset() {
  const { pathname } = useLocation()

  useEffect(() => {
    // Reset focus to top of page for screen readers
    const main = document.getElementById('main-content')
    if (main) {
      main.focus({ preventScroll: false })
      main.setAttribute('tabindex', '-1')
    }

    // Scroll to top
    window.scrollTo(0, 0)
  }, [pathname])
}
