/**
 * Hook pour gérer les indices progressifs
 * Affiche des hints les 3 premières visites d'une page, puis les masque
 * Stockage dans localStorage pour persister entre les sessions
 */

import { useState, useCallback } from 'react'

const STORAGE_KEY = 'hub_page_visits'
const MAX_HINT_VISITS = 3

interface PageVisits {
  [page: string]: number
}

export function useProgressiveHint() {
  const [pageVisits, setPageVisits] = useState<PageVisits>(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      return stored ? JSON.parse(stored) : {}
    } catch {
      return {}
    }
  })

  /**
   * Enregistre une visite pour la page courante
   */
  const recordVisit = useCallback((page: string) => {
    setPageVisits((prev) => {
      const newVisits = {
        ...prev,
        [page]: (prev[page] || 0) + 1,
      }
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(newVisits))
      } catch (error) {
        console.warn('Failed to save page visits to localStorage:', error)
      }
      return newVisits
    })
  }, [])

  /**
   * Détermine si le hint doit être affiché pour une page
   * @param page - Nom de la page (généralement le pathname)
   * @returns true si le hint doit être affiché (visites < 3)
   */
  const shouldShowHint = useCallback((page: string): boolean => {
    const visits = pageVisits[page] || 0
    return visits < MAX_HINT_VISITS
  }, [pageVisits])

  /**
   * Obtient le nombre de visites pour une page
   */
  const getVisitCount = useCallback((page: string): number => {
    return pageVisits[page] || 0
  }, [pageVisits])

  /**
   * Réinitialise les visites pour une page (utile pour debug/tests)
   */
  const resetVisits = useCallback((page?: string) => {
    if (page) {
      setPageVisits((prev) => {
        const newVisits = { ...prev }
        delete newVisits[page]
        try {
          localStorage.setItem(STORAGE_KEY, JSON.stringify(newVisits))
        } catch (error) {
          console.warn('Failed to save page visits to localStorage:', error)
        }
        return newVisits
      })
    } else {
      setPageVisits({})
      try {
        localStorage.removeItem(STORAGE_KEY)
      } catch (error) {
        console.warn('Failed to remove page visits from localStorage:', error)
      }
    }
  }, [])

  return {
    recordVisit,
    shouldShowHint,
    getVisitCount,
    resetVisits,
  }
}

export default useProgressiveHint
