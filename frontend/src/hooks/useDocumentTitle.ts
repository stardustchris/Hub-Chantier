import { useEffect } from 'react'

/**
 * Hook pour mettre à jour le titre du document (onglet navigateur)
 * Facilite la navigation multi-onglets et l'accessibilité
 */
export function useDocumentTitle(title: string) {
  useEffect(() => {
    const previousTitle = document.title
    document.title = title ? `${title} — Hub Chantier` : 'Hub Chantier'

    return () => {
      document.title = previousTitle
    }
  }, [title])
}
