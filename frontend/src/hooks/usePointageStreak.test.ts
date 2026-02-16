/**
 * Tests pour usePointageStreak
 */

import { renderHook, act } from '@testing-library/react'
import { usePointageStreak } from './usePointageStreak'

describe('usePointageStreak', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('should initialize with streak 0 when no history', () => {
    const { result } = renderHook(() => usePointageStreak())
    expect(result.current.streak).toBe(0)
    expect(result.current.history).toEqual([])
  })

  it('should record today and calculate streak', () => {
    const { result } = renderHook(() => usePointageStreak())

    act(() => {
      result.current.recordToday()
    })

    expect(result.current.history.length).toBe(1)
    expect(result.current.streak).toBe(1)
  })

  it('should not create duplicates when recording same day', () => {
    const { result } = renderHook(() => usePointageStreak())

    act(() => {
      result.current.recordToday()
      result.current.recordToday()
    })

    expect(result.current.history.length).toBe(1)
  })

  it('should expose recordToday function', () => {
    const { result } = renderHook(() => usePointageStreak())

    expect(typeof result.current.recordToday).toBe('function')
    expect(result.current.history).toBeDefined()
    expect(result.current.streak).toBeDefined()
  })
})
