/**
 * Tests unitaires pour useListPage hook
 */

import { describe, it, expect, vi, beforeEach, afterEach, type Mock } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { useListPage, type PaginatedResponse, type ListParams } from './useListPage'

interface TestItem {
  id: string
  name: string
}

type FetchItemsFn = (params: ListParams) => Promise<PaginatedResponse<TestItem>>

describe('useListPage', () => {
  let mockFetchItems: Mock<FetchItemsFn>
  let consoleErrorSpy: ReturnType<typeof vi.spyOn>

  beforeEach(() => {
    vi.clearAllMocks()
    // Supprime les console.error pour les tests d'erreur attendus
    consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
    mockFetchItems = vi.fn().mockResolvedValue({
      items: [{ id: '1', name: 'Item 1' }],
      total: 1,
      page: 1,
      size: 12,
      pages: 1,
    })
  })

  afterEach(() => {
    consoleErrorSpy.mockRestore()
  })

  it('charge les items automatiquement au mount', async () => {
    const { result } = renderHook(() =>
      useListPage<TestItem>({
        fetchItems: mockFetchItems,
      })
    )

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(mockFetchItems).toHaveBeenCalled()
    expect(result.current.items).toHaveLength(1)
    expect(result.current.items[0].name).toBe('Item 1')
  })

  it('ne charge pas automatiquement si autoLoad=false', async () => {
    renderHook(() =>
      useListPage<TestItem>({
        fetchItems: mockFetchItems,
        autoLoad: false,
      })
    )

    // Wait a bit to ensure no call was made
    await new Promise((r) => setTimeout(r, 100))

    expect(mockFetchItems).not.toHaveBeenCalled()
  })

  it('gere les erreurs de chargement', async () => {
    mockFetchItems.mockRejectedValue(new Error('Network error'))

    const { result } = renderHook(() =>
      useListPage<TestItem>({
        fetchItems: mockFetchItems,
      })
    )

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(result.current.error).toBe('Network error')
    expect(result.current.items).toHaveLength(0)
  })

  it('recharge quand setPage est appele', async () => {
    mockFetchItems.mockResolvedValue({
      items: [{ id: '1', name: 'Page 1' }],
      total: 20,
      page: 1,
      size: 12,
      pages: 2,
    })

    const { result } = renderHook(() =>
      useListPage<TestItem>({
        fetchItems: mockFetchItems,
      })
    )

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    mockFetchItems.mockResolvedValue({
      items: [{ id: '2', name: 'Page 2' }],
      total: 20,
      page: 2,
      size: 12,
      pages: 2,
    })

    act(() => {
      result.current.setPage(2)
    })

    await waitFor(() => {
      expect(result.current.page).toBe(2)
    })

    expect(mockFetchItems).toHaveBeenLastCalledWith(
      expect.objectContaining({ page: 2 })
    )
  })

  it('reset page quand search change', async () => {
    const { result } = renderHook(() =>
      useListPage<TestItem>({
        fetchItems: mockFetchItems,
      })
    )

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    await act(async () => {
      result.current.setPage(3)
    })

    await act(async () => {
      result.current.setSearch('test')
    })

    // Attendre que le reload soit termine
    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(result.current.page).toBe(1)
    expect(result.current.search).toBe('test')
  })

  it('reset page quand filter change', async () => {
    const { result } = renderHook(() =>
      useListPage<TestItem>({
        fetchItems: mockFetchItems,
      })
    )

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    await act(async () => {
      result.current.setPage(3)
    })

    await act(async () => {
      result.current.setFilter('status', 'active')
    })

    // Attendre que le reload soit termine
    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(result.current.page).toBe(1)
    expect(result.current.filters.status).toBe('active')
  })

  it('clearFilters reset tous les filtres et la recherche', async () => {
    const { result } = renderHook(() =>
      useListPage<TestItem>({
        fetchItems: mockFetchItems,
      })
    )

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    await act(async () => {
      result.current.setSearch('test')
      result.current.setFilter('status', 'active')
      result.current.setPage(3)
    })

    await act(async () => {
      result.current.clearFilters()
    })

    // Attendre que le reload soit termine
    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(result.current.search).toBe('')
    expect(result.current.filters).toEqual({})
    expect(result.current.page).toBe(1)
  })

  it('appelle reload manuellement', async () => {
    const { result } = renderHook(() =>
      useListPage<TestItem>({
        fetchItems: mockFetchItems,
      })
    )

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    const callCount = mockFetchItems.mock.calls.length

    await act(async () => {
      await result.current.reload()
    })

    expect(mockFetchItems).toHaveBeenCalledTimes(callCount + 1)
  })

  it('cree un item et recharge la liste', async () => {
    const mockCreateItem = vi.fn().mockResolvedValue({ id: '2', name: 'New Item' })

    const { result } = renderHook(() =>
      useListPage<TestItem, { name: string }>({
        fetchItems: mockFetchItems,
        createItem: mockCreateItem,
      })
    )

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    const callCount = mockFetchItems.mock.calls.length

    await act(async () => {
      const newItem = await result.current.create({ name: 'New Item' })
      expect(newItem).toEqual({ id: '2', name: 'New Item' })
    })

    expect(mockCreateItem).toHaveBeenCalledWith({ name: 'New Item' })
    expect(mockFetchItems).toHaveBeenCalledTimes(callCount + 1)
  })

  it('supprime un item et recharge la liste', async () => {
    const mockDeleteItem = vi.fn().mockResolvedValue(undefined)

    const { result } = renderHook(() =>
      useListPage<TestItem>({
        fetchItems: mockFetchItems,
        deleteItem: mockDeleteItem,
      })
    )

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    const callCount = mockFetchItems.mock.calls.length

    await act(async () => {
      const success = await result.current.remove('1')
      expect(success).toBe(true)
    })

    expect(mockDeleteItem).toHaveBeenCalledWith('1')
    expect(mockFetchItems).toHaveBeenCalledTimes(callCount + 1)
  })

  it('retourne false si deleteItem echoue', async () => {
    const mockDeleteItem = vi.fn().mockRejectedValue(new Error('Delete failed'))

    const { result } = renderHook(() =>
      useListPage<TestItem>({
        fetchItems: mockFetchItems,
        deleteItem: mockDeleteItem,
      })
    )

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    let success: boolean
    await act(async () => {
      success = await result.current.remove('1')
    })

    expect(success!).toBe(false)
    expect(result.current.error).toBe('Delete failed')
  })

  it('utilise la taille de page configuree', async () => {
    const { result } = renderHook(() =>
      useListPage<TestItem>({
        fetchItems: mockFetchItems,
        pageSize: 20,
      })
    )

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(mockFetchItems).toHaveBeenCalledWith(
      expect.objectContaining({ size: 20 })
    )
  })
})
