/**
 * useFormulairesFilters - Hook pour la gestion des filtres formulaires
 *
 * Responsabilités :
 * - Gestion recherche (search query)
 * - Gestion filtre catégorie
 * - Filtrage des templates
 */

import { useState, useMemo } from 'react'
import type { TemplateFormulaire, CategorieFormulaire } from '../types'

export interface UseFormulairesFiltersReturn {
  // Filter state
  searchQuery: string
  filterCategorie: CategorieFormulaire | ''
  setSearchQuery: (query: string) => void
  setFilterCategorie: (categorie: CategorieFormulaire | '') => void

  // Filtered data
  filterTemplates: (templates: TemplateFormulaire[]) => TemplateFormulaire[]
}

export function useFormulairesFilters(): UseFormulairesFiltersReturn {
  const [searchQuery, setSearchQuery] = useState('')
  const [filterCategorie, setFilterCategorie] = useState<CategorieFormulaire | ''>('')

  // Filter function (memoized for performance)
  const filterTemplates = useMemo(() => {
    return (templates: TemplateFormulaire[]) => {
      return templates.filter((template) => {
        // Filter by search query
        if (searchQuery && !template.nom.toLowerCase().includes(searchQuery.toLowerCase())) {
          return false
        }

        // Filter by category (if specified)
        if (filterCategorie && template.categorie !== filterCategorie) {
          return false
        }

        return true
      })
    }
  }, [searchQuery, filterCategorie])

  return {
    // Filter state
    searchQuery,
    filterCategorie,
    setSearchQuery,
    setFilterCategorie,

    // Filtered data
    filterTemplates,
  }
}
