/**
 * Tests for useProgressiveHint hook
 * Vérifie le tracking des visites et l'affichage progressif des hints
 */

import { renderHook, act } from '@testing-library/react'
import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { useProgressiveHint } from './useProgressiveHint'

describe('useProgressiveHint', () => {
  beforeEach(() => {
    // Nettoyer le localStorage avant chaque test
    localStorage.clear()
  })

  afterEach(() => {
    localStorage.clear()
  })

  it('should initialize with empty visits', () => {
    const { result } = renderHook(() => useProgressiveHint())

    expect(result.current.getVisitCount('/unique-path-1')).toBe(0)
    expect(result.current.shouldShowHint('/unique-path-1')).toBe(true)
  })

  it('should record page visits', () => {
    const { result } = renderHook(() => useProgressiveHint())

    act(() => {
      result.current.recordVisit('/unique-path-2')
    })

    expect(result.current.getVisitCount('/unique-path-2')).toBe(1)
  })

  it('should increment visit count on multiple visits', () => {
    const { result } = renderHook(() => useProgressiveHint())

    act(() => {
      result.current.recordVisit('/unique-path-3')
      result.current.recordVisit('/unique-path-3')
      result.current.recordVisit('/unique-path-3')
    })

    expect(result.current.getVisitCount('/unique-path-3')).toBe(3)
  })

  it('should show hint for first 3 visits', () => {
    const { result } = renderHook(() => useProgressiveHint())
    const testPath = '/unique-path-4'

    // Visite 0 (avant enregistrement)
    expect(result.current.shouldShowHint(testPath)).toBe(true)

    // Visite 1
    act(() => {
      result.current.recordVisit(testPath)
    })
    expect(result.current.shouldShowHint(testPath)).toBe(true)

    // Visite 2
    act(() => {
      result.current.recordVisit(testPath)
    })
    expect(result.current.shouldShowHint(testPath)).toBe(true)

    // Visite 3
    act(() => {
      result.current.recordVisit(testPath)
    })
    expect(result.current.shouldShowHint(testPath)).toBe(true)

    // Visite 4 - hint ne doit plus s'afficher
    act(() => {
      result.current.recordVisit(testPath)
    })
    expect(result.current.shouldShowHint(testPath)).toBe(false)
  })

  it('should track visits independently per page', () => {
    const { result } = renderHook(() => useProgressiveHint())

    act(() => {
      result.current.recordVisit('/unique-path-5')
      result.current.recordVisit('/unique-path-5')
      result.current.recordVisit('/unique-path-6')
    })

    expect(result.current.getVisitCount('/unique-path-5')).toBe(2)
    expect(result.current.getVisitCount('/unique-path-6')).toBe(1)
    expect(result.current.shouldShowHint('/unique-path-5')).toBe(true)
    expect(result.current.shouldShowHint('/unique-path-6')).toBe(true)
  })

  it('should reset visits for a specific page', () => {
    const { result } = renderHook(() => useProgressiveHint())

    act(() => {
      result.current.recordVisit('/unique-path-7')
      result.current.recordVisit('/unique-path-8')
    })

    expect(result.current.getVisitCount('/unique-path-7')).toBe(1)
    expect(result.current.getVisitCount('/unique-path-8')).toBe(1)

    act(() => {
      result.current.resetVisits('/unique-path-7')
    })

    expect(result.current.getVisitCount('/unique-path-7')).toBe(0)
    expect(result.current.getVisitCount('/unique-path-8')).toBe(1)
  })

  it('should reset all visits when no page specified', () => {
    const { result } = renderHook(() => useProgressiveHint())

    act(() => {
      result.current.recordVisit('/unique-path-9')
      result.current.recordVisit('/unique-path-10')
    })

    expect(result.current.getVisitCount('/unique-path-9')).toBe(1)
    expect(result.current.getVisitCount('/unique-path-10')).toBe(1)

    act(() => {
      result.current.resetVisits()
    })

    expect(result.current.getVisitCount('/unique-path-9')).toBe(0)
    expect(result.current.getVisitCount('/unique-path-10')).toBe(0)
  })

  it('should handle corrupted localStorage data', () => {
    // Données corrompues dans localStorage
    localStorage.setItem('hub_page_visits', 'invalid json')

    const { result } = renderHook(() => useProgressiveHint())

    // Doit démarrer avec des visites vides
    expect(result.current.getVisitCount('/unique-path-11')).toBe(0)
  })
})
