// @vitest-environment jsdom
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useFormulairesFilters } from './useFormulairesFilters'
import type { TemplateFormulaire } from '../types'

const mockTemplates: Partial<TemplateFormulaire>[] = [
  {
    id: 1,
    nom: 'Fiche Securite Chantier',
    categorie: 'securite' as any,
    description: 'desc 1',
    is_active: true,
  },
  {
    id: 2,
    nom: 'Rapport Qualite',
    categorie: 'qualite' as any,
    description: 'desc 2',
    is_active: true,
  },
  {
    id: 3,
    nom: 'Checklist Environnement',
    categorie: 'environnement' as any,
    description: 'desc 3',
    is_active: true,
  },
  {
    id: 4,
    nom: 'Autre Securite Form',
    categorie: 'securite' as any,
    description: 'desc 4',
    is_active: false,
  },
]

describe('useFormulairesFilters', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('initial state', () => {
    it('should have empty search query and no category filter', () => {
      const { result } = renderHook(() => useFormulairesFilters())

      expect(result.current.searchQuery).toBe('')
      expect(result.current.filterCategorie).toBe('')
    })

    it('should return all templates when no filters are applied', () => {
      const { result } = renderHook(() => useFormulairesFilters())

      const filtered = result.current.filterTemplates(mockTemplates as TemplateFormulaire[])
      expect(filtered).toHaveLength(4)
    })
  })

  describe('setSearchQuery', () => {
    it('should update search query', () => {
      const { result } = renderHook(() => useFormulairesFilters())

      act(() => {
        result.current.setSearchQuery('securite')
      })

      expect(result.current.searchQuery).toBe('securite')
    })
  })

  describe('setFilterCategorie', () => {
    it('should update filter categorie', () => {
      const { result } = renderHook(() => useFormulairesFilters())

      act(() => {
        result.current.setFilterCategorie('securite' as any)
      })

      expect(result.current.filterCategorie).toBe('securite')
    })

    it('should allow resetting to empty string', () => {
      const { result } = renderHook(() => useFormulairesFilters())

      act(() => {
        result.current.setFilterCategorie('securite' as any)
      })

      act(() => {
        result.current.setFilterCategorie('')
      })

      expect(result.current.filterCategorie).toBe('')
    })
  })

  describe('filterTemplates', () => {
    it('should filter by search query (case insensitive)', () => {
      const { result } = renderHook(() => useFormulairesFilters())

      act(() => {
        result.current.setSearchQuery('securite')
      })

      const filtered = result.current.filterTemplates(mockTemplates as TemplateFormulaire[])
      expect(filtered).toHaveLength(2)
      expect(filtered[0].nom).toBe('Fiche Securite Chantier')
      expect(filtered[1].nom).toBe('Autre Securite Form')
    })

    it('should filter by category', () => {
      const { result } = renderHook(() => useFormulairesFilters())

      act(() => {
        result.current.setFilterCategorie('qualite' as any)
      })

      const filtered = result.current.filterTemplates(mockTemplates as TemplateFormulaire[])
      expect(filtered).toHaveLength(1)
      expect(filtered[0].nom).toBe('Rapport Qualite')
    })

    it('should combine search query and category filters', () => {
      const { result } = renderHook(() => useFormulairesFilters())

      act(() => {
        result.current.setSearchQuery('fiche')
        result.current.setFilterCategorie('securite' as any)
      })

      const filtered = result.current.filterTemplates(mockTemplates as TemplateFormulaire[])
      expect(filtered).toHaveLength(1)
      expect(filtered[0].nom).toBe('Fiche Securite Chantier')
    })

    it('should return empty array when no templates match', () => {
      const { result } = renderHook(() => useFormulairesFilters())

      act(() => {
        result.current.setSearchQuery('nonexistent')
      })

      const filtered = result.current.filterTemplates(mockTemplates as TemplateFormulaire[])
      expect(filtered).toHaveLength(0)
    })

    it('should handle empty templates array', () => {
      const { result } = renderHook(() => useFormulairesFilters())

      const filtered = result.current.filterTemplates([])
      expect(filtered).toHaveLength(0)
    })

    it('should be case insensitive for search', () => {
      const { result } = renderHook(() => useFormulairesFilters())

      act(() => {
        result.current.setSearchQuery('RAPPORT')
      })

      const filtered = result.current.filterTemplates(mockTemplates as TemplateFormulaire[])
      expect(filtered).toHaveLength(1)
      expect(filtered[0].nom).toBe('Rapport Qualite')
    })

    it('should match partial strings in search', () => {
      const { result } = renderHook(() => useFormulairesFilters())

      act(() => {
        result.current.setSearchQuery('check')
      })

      const filtered = result.current.filterTemplates(mockTemplates as TemplateFormulaire[])
      expect(filtered).toHaveLength(1)
      expect(filtered[0].nom).toBe('Checklist Environnement')
    })
  })
})
