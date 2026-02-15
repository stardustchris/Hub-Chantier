import { renderHook, act } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { useMultiSelect } from './useMultiSelect'

describe('useMultiSelect', () => {
  it('should initialize with empty selection', () => {
    const { result } = renderHook(() => useMultiSelect<number>())

    expect(result.current.count).toBe(0)
    expect(result.current.selectedArray).toEqual([])
  })

  it('should toggle item selection', () => {
    const { result } = renderHook(() => useMultiSelect<number>())

    act(() => {
      result.current.toggleItem(1)
    })

    expect(result.current.count).toBe(1)
    expect(result.current.isSelected(1)).toBe(true)

    act(() => {
      result.current.toggleItem(1)
    })

    expect(result.current.count).toBe(0)
    expect(result.current.isSelected(1)).toBe(false)
  })

  it('should select all items', () => {
    const { result } = renderHook(() => useMultiSelect<number>())

    act(() => {
      result.current.selectAll([1, 2, 3])
    })

    expect(result.current.count).toBe(3)
    expect(result.current.selectedArray.sort()).toEqual([1, 2, 3])
  })

  it('should deselect all items', () => {
    const { result } = renderHook(() => useMultiSelect<number>())

    act(() => {
      result.current.selectAll([1, 2, 3])
    })

    expect(result.current.count).toBe(3)

    act(() => {
      result.current.deselectAll()
    })

    expect(result.current.count).toBe(0)
    expect(result.current.selectedArray).toEqual([])
  })

  it('should work with string IDs', () => {
    const { result } = renderHook(() => useMultiSelect<string>())

    act(() => {
      result.current.toggleItem('a')
      result.current.toggleItem('b')
    })

    expect(result.current.count).toBe(2)
    expect(result.current.isSelected('a')).toBe(true)
    expect(result.current.isSelected('b')).toBe(true)
    expect(result.current.isSelected('c')).toBe(false)
  })
})
