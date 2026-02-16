import { useState, useEffect, useCallback, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQueryClient } from '@tanstack/react-query'
import type { Chantier, User } from '../types'

export interface SearchResult {
  id: string
  type: 'chantier' | 'user' | 'document' | 'page'
  title: string
  subtitle?: string
  icon: string
  url: string
}

interface StaticPage {
  name: string
  url: string
  icon: string
}

const STATIC_PAGES: StaticPage[] = [
  { name: 'Tableau de bord', url: '/', icon: 'Home' },
  { name: 'Chantiers', url: '/chantiers', icon: 'Building2' },
  { name: 'Utilisateurs', url: '/utilisateurs', icon: 'Users' },
  { name: 'Planning', url: '/planning', icon: 'Calendar' },
  { name: 'Feuilles d\'heures', url: '/feuilles-heures', icon: 'Clock' },
  { name: 'Documents', url: '/documents', icon: 'FileText' },
  { name: 'Formulaires', url: '/formulaires', icon: 'FileText' },
  { name: 'Logistique', url: '/logistique', icon: 'Truck' },
  { name: 'Devis', url: '/devis', icon: 'FileText' },
  { name: 'Finances', url: '/finances', icon: 'BarChart3' },
  { name: 'Budgets', url: '/budgets', icon: 'Euro' },
  { name: 'Achats', url: '/achats', icon: 'ShoppingCart' },
  { name: 'Fournisseurs', url: '/fournisseurs', icon: 'Handshake' },
  { name: 'Parametres', url: '/security', icon: 'Settings' },
]

const RECENT_SEARCHES_KEY = 'hub-chantier-recent-searches'
const MAX_RECENT_SEARCHES = 5

// Normalize string for fuzzy search (remove accents, lowercase)
function normalizeString(str: string): string {
  return str
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
}

// Simple fuzzy search scoring
function calculateScore(query: string, target: string): number {
  const normalizedQuery = normalizeString(query)
  const normalizedTarget = normalizeString(target)

  if (normalizedTarget === normalizedQuery) return 100
  if (normalizedTarget.startsWith(normalizedQuery)) return 90
  if (normalizedTarget.includes(normalizedQuery)) return 70

  // Check if all characters of query appear in order in target
  let queryIndex = 0
  for (let i = 0; i < normalizedTarget.length && queryIndex < normalizedQuery.length; i++) {
    if (normalizedTarget[i] === normalizedQuery[queryIndex]) {
      queryIndex++
    }
  }
  if (queryIndex === normalizedQuery.length) return 50

  return 0
}

export function useCommandPalette() {
  const [isOpen, setIsOpen] = useState(false)
  const [query, setQuery] = useState('')
  const [selectedIndex, setSelectedIndex] = useState(0)
  const [recentSearches, setRecentSearches] = useState<SearchResult[]>([])
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  // Load recent searches from localStorage
  useEffect(() => {
    try {
      const stored = localStorage.getItem(RECENT_SEARCHES_KEY)
      if (stored) {
        setRecentSearches(JSON.parse(stored))
      }
    } catch (error) {
      console.error('Failed to load recent searches:', error)
    }
  }, [])

  // Save recent searches to localStorage
  const saveRecentSearch = useCallback((result: SearchResult) => {
    setRecentSearches((prev) => {
      const filtered = prev.filter((r) => r.id !== result.id)
      const updated = [result, ...filtered].slice(0, MAX_RECENT_SEARCHES)
      try {
        localStorage.setItem(RECENT_SEARCHES_KEY, JSON.stringify(updated))
      } catch (error) {
        console.error('Failed to save recent search:', error)
      }
      return updated
    })
  }, [])

  // Get cached data from TanStack Query
  const getCachedChantiers = useCallback((): Chantier[] => {
    const data = queryClient.getQueryData<{ items: Chantier[] }>(['chantiers'])
    return data?.items || []
  }, [queryClient])

  const getCachedUsers = useCallback((): User[] => {
    const data = queryClient.getQueryData<{ items: User[] }>(['users'])
    return data?.items || []
  }, [queryClient])

  // Search function
  const search = useCallback(
    (searchQuery: string): SearchResult[] => {
      if (!searchQuery.trim()) return recentSearches

      const results: Array<SearchResult & { score: number }> = []

      // Search in static pages
      STATIC_PAGES.forEach((page) => {
        const score = calculateScore(searchQuery, page.name)
        if (score > 0) {
          results.push({
            id: `page-${page.url}`,
            type: 'page',
            title: page.name,
            icon: page.icon,
            url: page.url,
            score,
          })
        }
      })

      // Search in chantiers
      const chantiers = getCachedChantiers()
      chantiers.forEach((chantier) => {
        const titleScore = calculateScore(searchQuery, chantier.nom)
        const codeScore = chantier.code
          ? calculateScore(searchQuery, chantier.code)
          : 0
        const score = Math.max(titleScore, codeScore)

        if (score > 0) {
          results.push({
            id: `chantier-${chantier.id}`,
            type: 'chantier',
            title: chantier.nom,
            subtitle: chantier.code || chantier.adresse,
            icon: 'Building2',
            url: `/chantiers/${chantier.id}`,
            score,
          })
        }
      })

      // Search in users
      const users = getCachedUsers()
      users.forEach((user) => {
        const nameScore = calculateScore(
          searchQuery,
          `${user.prenom} ${user.nom}`
        )
        const emailScore = calculateScore(searchQuery, user.email)
        const score = Math.max(nameScore, emailScore)

        if (score > 0) {
          results.push({
            id: `user-${user.id}`,
            type: 'user',
            title: `${user.prenom} ${user.nom}`,
            subtitle: user.email,
            icon: 'Users',
            url: `/utilisateurs/${user.id}`,
            score,
          })
        }
      })

      // Sort by score (descending) and return top results
      return results.sort((a, b) => b.score - a.score).slice(0, 10)
    },
    [getCachedChantiers, getCachedUsers, recentSearches]
  )

  // Debounced search results
  const [debouncedQuery, setDebouncedQuery] = useState('')
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(query)
    }, 300)

    return () => clearTimeout(timer)
  }, [query])

  const results = useMemo(
    () => search(debouncedQuery),
    [debouncedQuery, search]
  )

  // Reset selected index when results change
  useEffect(() => {
    setSelectedIndex(0)
  }, [results])

  // Keyboard navigation
  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      if (!isOpen) return

      switch (event.key) {
        case 'ArrowDown':
          event.preventDefault()
          setSelectedIndex((prev) => Math.min(prev + 1, results.length - 1))
          break
        case 'ArrowUp':
          event.preventDefault()
          setSelectedIndex((prev) => Math.max(prev - 1, 0))
          break
        case 'Enter':
          event.preventDefault()
          if (results[selectedIndex]) {
            selectResult(results[selectedIndex])
          }
          break
        case 'Escape':
          event.preventDefault()
          close()
          break
      }
    },
    [isOpen, results, selectedIndex]
  )

  // Global keyboard shortcut (Cmd+K / Ctrl+K)
  useEffect(() => {
    const handleGlobalKeyDown = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key === 'k') {
        event.preventDefault()
        setIsOpen((prev) => !prev)
      }
    }

    document.addEventListener('keydown', handleGlobalKeyDown)
    return () => document.removeEventListener('keydown', handleGlobalKeyDown)
  }, [])

  // Attach keyboard navigation when open
  useEffect(() => {
    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown)
      return () => document.removeEventListener('keydown', handleKeyDown)
    }
  }, [isOpen, handleKeyDown])

  const open = useCallback(() => {
    setIsOpen(true)
    setQuery('')
    setSelectedIndex(0)
  }, [])

  const close = useCallback(() => {
    setIsOpen(false)
    setQuery('')
    setSelectedIndex(0)
  }, [])

  const selectResult = useCallback(
    (result: SearchResult) => {
      saveRecentSearch(result)
      navigate(result.url)
      close()
    },
    [navigate, close, saveRecentSearch]
  )

  return {
    isOpen,
    query,
    setQuery,
    results,
    selectedIndex,
    setSelectedIndex,
    recentSearches,
    open,
    close,
    selectResult,
  }
}
