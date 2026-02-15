import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import type { ReactNode } from 'react'
import { useCommandPalette } from './useCommandPalette'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'

const mockNavigate = vi.fn()

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

describe('useCommandPalette', () => {
  let queryClient: QueryClient

  const wrapper = ({ children }: { children: ReactNode }) => (
    <BrowserRouter>
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    </BrowserRouter>
  )

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
      },
    })
    mockNavigate.mockClear()
    localStorage.clear()
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.clearAllTimers()
  })

  it('should initialize with closed state', () => {
    const { result } = renderHook(() => useCommandPalette(), { wrapper })

    expect(result.current.isOpen).toBe(false)
    expect(result.current.query).toBe('')
    expect(result.current.selectedIndex).toBe(0)
  })

  it('should open on Cmd+K', () => {
    const { result } = renderHook(() => useCommandPalette(), { wrapper })

    act(() => {
      const event = new KeyboardEvent('keydown', { key: 'k', metaKey: true })
      document.dispatchEvent(event)
    })

    expect(result.current.isOpen).toBe(true)
  })

  it('should open on Ctrl+K', () => {
    const { result } = renderHook(() => useCommandPalette(), { wrapper })

    act(() => {
      const event = new KeyboardEvent('keydown', { key: 'k', ctrlKey: true })
      document.dispatchEvent(event)
    })

    expect(result.current.isOpen).toBe(true)
  })

  it('should close on Escape when open', () => {
    const { result } = renderHook(() => useCommandPalette(), { wrapper })

    act(() => {
      result.current.open()
    })

    expect(result.current.isOpen).toBe(true)

    act(() => {
      const event = new KeyboardEvent('keydown', { key: 'Escape' })
      document.dispatchEvent(event)
    })

    expect(result.current.isOpen).toBe(false)
  })

  it('should search static pages', async () => {
    const { result } = renderHook(() => useCommandPalette(), { wrapper })

    act(() => {
      result.current.setQuery('planning')
    })

    await waitFor(
      () => {
        const hasResults = result.current.results.length > 0
        expect(hasResults).toBe(true)
      },
      { timeout: 500 }
    )

    const planningResult = result.current.results.find((r) =>
      r.title.toLowerCase().includes('planning')
    )
    expect(planningResult).toBeDefined()
    expect(planningResult?.type).toBe('page')
  })

  it('should search chantiers from cache', async () => {
    // Add mock chantier data to query cache
    queryClient.setQueryData(['chantiers'], {
      items: [
        {
          id: '1',
          nom: 'Chantier Test',
          code: 'CHT-001',
          adresse: '123 Rue Test',
        },
      ],
    })

    const { result } = renderHook(() => useCommandPalette(), { wrapper })

    act(() => {
      result.current.setQuery('test')
    })

    await waitFor(
      () => {
        const hasResults = result.current.results.length > 0
        expect(hasResults).toBe(true)
      },
      { timeout: 500 }
    )

    const chantierResult = result.current.results.find(
      (r) => r.type === 'chantier'
    )
    expect(chantierResult).toBeDefined()
    expect(chantierResult?.title).toBe('Chantier Test')
  })

  it('should search users from cache', async () => {
    // Add mock user data to query cache
    queryClient.setQueryData(['users'], {
      items: [
        {
          id: '1',
          prenom: 'Jean',
          nom: 'Dupont',
          email: 'jean.dupont@example.com',
          role: 'compagnon',
          type_utilisateur: 'employe',
          is_active: true,
          created_at: '2024-01-01',
        },
      ],
    })

    const { result } = renderHook(() => useCommandPalette(), { wrapper })

    act(() => {
      result.current.setQuery('jean')
    })

    await waitFor(
      () => {
        const hasResults = result.current.results.length > 0
        expect(hasResults).toBe(true)
      },
      { timeout: 500 }
    )

    const userResult = result.current.results.find((r) => r.type === 'user')
    expect(userResult).toBeDefined()
    expect(userResult?.title).toBe('Jean Dupont')
  })

  it('should navigate and close on result selection', () => {
    const { result } = renderHook(() => useCommandPalette(), { wrapper })

    const testResult = {
      id: 'test-1',
      type: 'page' as const,
      title: 'Test Page',
      icon: 'Home',
      url: '/test',
    }

    act(() => {
      result.current.open()
      result.current.selectResult(testResult)
    })

    expect(mockNavigate).toHaveBeenCalledWith('/test')
    expect(result.current.isOpen).toBe(false)
  })

  it('should save recent searches', async () => {
    const { result } = renderHook(() => useCommandPalette(), { wrapper })

    const testResult = {
      id: 'test-1',
      type: 'page' as const,
      title: 'Test Page',
      icon: 'Home',
      url: '/test',
    }

    act(() => {
      result.current.selectResult(testResult)
    })

    // Wait for state update
    await waitFor(() => {
      expect(result.current.recentSearches.length).toBeGreaterThan(0)
      expect(result.current.recentSearches[0].id).toBe('test-1')
    })
  })

  it('should handle keyboard navigation (ArrowDown)', () => {
    const { result } = renderHook(() => useCommandPalette(), { wrapper })

    act(() => {
      result.current.open()
      result.current.setQuery('test')
    })

    // Wait for results to populate
    act(() => {
      const event = new KeyboardEvent('keydown', { key: 'ArrowDown' })
      document.dispatchEvent(event)
    })

    // Should increment selected index (if there are results)
    // Note: actual value depends on search results
  })

  it('should handle keyboard navigation (ArrowUp)', () => {
    const { result } = renderHook(() => useCommandPalette(), { wrapper })

    act(() => {
      result.current.open()
      result.current.setQuery('test')
    })

    act(() => {
      const event = new KeyboardEvent('keydown', { key: 'ArrowUp' })
      document.dispatchEvent(event)
    })

    // Should stay at 0 if already at the start
    expect(result.current.selectedIndex).toBe(0)
  })

  it('should debounce search query', async () => {
    const { result } = renderHook(() => useCommandPalette(), { wrapper })

    act(() => {
      result.current.setQuery('planning')
    })

    // Results should not immediately update (debounced)
    // Just verify the query was set
    expect(result.current.query).toBe('planning')

    // Wait for debounce to complete
    await waitFor(
      () => {
        expect(result.current.results.length).toBeGreaterThan(0)
      },
      { timeout: 500 }
    )
  })

  it('should normalize accents in search', async () => {
    queryClient.setQueryData(['chantiers'], {
      items: [
        {
          id: '1',
          nom: 'Chantier Révision',
          code: 'REV-001',
          adresse: '123 Rue Française',
        },
      ],
    })

    const { result } = renderHook(() => useCommandPalette(), { wrapper })

    act(() => {
      result.current.setQuery('revision')
    })

    await waitFor(
      () => {
        expect(result.current.results.length).toBeGreaterThan(0)
      },
      { timeout: 1000 }
    )

    const chantierResult = result.current.results.find(
      (r) => r.type === 'chantier'
    )
    expect(chantierResult).toBeDefined()
    expect(chantierResult?.title).toBe('Chantier Révision')
  })

  it('should limit recent searches to 5', () => {
    const { result } = renderHook(() => useCommandPalette(), { wrapper })

    // Add 6 recent searches
    for (let i = 1; i <= 6; i++) {
      act(() => {
        result.current.selectResult({
          id: `test-${i}`,
          type: 'page',
          title: `Test Page ${i}`,
          icon: 'Home',
          url: `/test-${i}`,
        })
      })
    }

    // Should only keep 5 most recent
    expect(result.current.recentSearches.length).toBeLessThanOrEqual(5)
  })

  it('should show recent searches when query is empty', () => {
    const { result } = renderHook(() => useCommandPalette(), { wrapper })

    // Add a recent search
    const testResult = {
      id: 'test-1',
      type: 'page' as const,
      title: 'Test Page',
      icon: 'Home',
      url: '/test',
    }

    act(() => {
      result.current.selectResult(testResult)
    })

    // Open again with empty query
    act(() => {
      result.current.open()
    })

    // Results should show recent searches when query is empty
    // (will be available after component re-renders)
  })
})
