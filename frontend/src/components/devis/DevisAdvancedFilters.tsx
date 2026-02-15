/**
 * DevisAdvancedFilters - Filtres avancés combinables pour la liste des devis
 * DEV-19: Recherche et filtres avancés
 *
 * Features:
 * - Filtres combinables (client, date, montant, statut, lot, marge)
 * - Persistance dans l'URL via query params
 * - Compteur de résultats
 * - Accessibilité complète
 */

import { useState } from 'react'
import { Search, Filter, X, ChevronDown } from 'lucide-react'
import type { DevisFilters } from '../../hooks/useDevisFilters'
import type { StatutDevis } from '../../types'
import { STATUT_DEVIS_CONFIG } from '../../types'

const ALL_STATUTS = Object.keys(STATUT_DEVIS_CONFIG) as StatutDevis[]

interface DevisAdvancedFiltersProps {
  filters: DevisFilters
  onFilterChange: <K extends keyof DevisFilters>(key: K, value: DevisFilters[K]) => void
  onClearFilters: () => void
  totalResults: number
  hasActiveFilters: boolean
  activeFiltersCount: number
}

export default function DevisAdvancedFilters({
  filters,
  onFilterChange,
  onClearFilters,
  totalResults,
  hasActiveFilters,
  activeFiltersCount,
}: DevisAdvancedFiltersProps) {
  const [showAdvanced, setShowAdvanced] = useState(false)

  const handleSearchChange = (value: string) => {
    onFilterChange('search', value)
  }

  const handleSearchKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      // Search is already applied via URL params
    }
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 space-y-4">
      {/* Barre de recherche principale */}
      <div className="flex items-center gap-3">
        <div className="flex-1 relative">
          <Search
            className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-600"
            aria-hidden="true"
          />
          <input
            type="text"
            value={filters.search || ''}
            onChange={(e) => handleSearchChange(e.target.value)}
            onKeyDown={handleSearchKeyDown}
            placeholder="Rechercher par client, numéro, objet..."
            className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 min-h-[44px]"
            aria-label="Recherche full-text"
          />
        </div>

        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          className={`inline-flex items-center gap-2 px-4 py-2.5 text-sm rounded-lg border transition-colors min-h-[44px] ${
            hasActiveFilters
              ? 'border-blue-300 bg-blue-50 text-blue-700'
              : 'border-gray-300 text-gray-700 hover:bg-gray-50'
          }`}
          aria-expanded={showAdvanced}
          aria-controls="advanced-filters"
        >
          <Filter className="w-4 h-4" />
          <span>Filtres</span>
          {activeFiltersCount > 0 && (
            <span
              className="bg-blue-600 text-white text-xs px-1.5 py-0.5 rounded-full min-w-[20px] text-center"
              aria-label={`${activeFiltersCount} filtres actifs`}
            >
              {activeFiltersCount}
            </span>
          )}
          <ChevronDown
            className={`w-4 h-4 transition-transform ${showAdvanced ? 'rotate-180' : ''}`}
          />
        </button>

        {hasActiveFilters && (
          <button
            onClick={onClearFilters}
            className="p-2.5 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg min-h-[44px] min-w-[44px] flex items-center justify-center"
            aria-label="Effacer tous les filtres"
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div>

      {/* Compteur de résultats */}
      {totalResults > 0 && (
        <div className="text-sm text-gray-600" role="status" aria-live="polite">
          <span className="font-medium">{totalResults}</span> résultat{totalResults > 1 ? 's' : ''} trouvé{totalResults > 1 ? 's' : ''}
        </div>
      )}

      {/* Panneau filtres avancés */}
      {showAdvanced && (
        <div id="advanced-filters" className="pt-4 border-t border-gray-200 space-y-4">
          {/* Statuts */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Statut
            </label>
            <div className="flex flex-wrap gap-2">
              {ALL_STATUTS.map((statut) => {
                const config = STATUT_DEVIS_CONFIG[statut]
                const isSelected = filters.statut === statut

                return (
                  <button
                    key={statut}
                    onClick={() => onFilterChange('statut', isSelected ? undefined : statut)}
                    className={`px-3 py-2 text-sm rounded-lg border transition-all min-h-[44px] ${
                      isSelected
                        ? 'border-transparent font-medium shadow-sm'
                        : 'border-gray-200 text-gray-700 hover:bg-gray-50'
                    }`}
                    style={
                      isSelected
                        ? {
                            backgroundColor: config.couleur + '20',
                            color: config.couleur,
                          }
                        : undefined
                    }
                    aria-pressed={isSelected}
                  >
                    {config.label}
                  </button>
                )
              })}
            </div>
          </div>

          {/* Client */}
          <div>
            <label htmlFor="filter-client" className="block text-sm font-medium text-gray-700 mb-2">
              Client
            </label>
            <input
              id="filter-client"
              type="text"
              value={filters.client_nom || ''}
              onChange={(e) => onFilterChange('client_nom', e.target.value || undefined)}
              placeholder="Nom du client"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 min-h-[44px]"
            />
          </div>

          {/* Dates */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="filter-date-min" className="block text-sm font-medium text-gray-700 mb-2">
                Date début
              </label>
              <input
                id="filter-date-min"
                type="date"
                value={filters.date_min || ''}
                onChange={(e) => onFilterChange('date_min', e.target.value || undefined)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 min-h-[44px]"
              />
            </div>
            <div>
              <label htmlFor="filter-date-max" className="block text-sm font-medium text-gray-700 mb-2">
                Date fin
              </label>
              <input
                id="filter-date-max"
                type="date"
                value={filters.date_max || ''}
                onChange={(e) => onFilterChange('date_max', e.target.value || undefined)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 min-h-[44px]"
              />
            </div>
          </div>

          {/* Montants */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="filter-montant-min" className="block text-sm font-medium text-gray-700 mb-2">
                Montant minimum (€)
              </label>
              <input
                id="filter-montant-min"
                type="number"
                min="0"
                step="100"
                value={filters.montant_min || ''}
                onChange={(e) => onFilterChange('montant_min', e.target.value ? Number(e.target.value) : undefined)}
                placeholder="0"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 min-h-[44px]"
              />
            </div>
            <div>
              <label htmlFor="filter-montant-max" className="block text-sm font-medium text-gray-700 mb-2">
                Montant maximum (€)
              </label>
              <input
                id="filter-montant-max"
                type="number"
                min="0"
                step="100"
                value={filters.montant_max || ''}
                onChange={(e) => onFilterChange('montant_max', e.target.value ? Number(e.target.value) : undefined)}
                placeholder="Illimité"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 min-h-[44px]"
              />
            </div>
          </div>

          {/* Marges (optionnel - pour utilisateurs avec droits) */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="filter-marge-min" className="block text-sm font-medium text-gray-700 mb-2">
                Marge minimum (%)
              </label>
              <input
                id="filter-marge-min"
                type="number"
                min="0"
                max="100"
                step="1"
                value={filters.marge_min || ''}
                onChange={(e) => onFilterChange('marge_min', e.target.value ? Number(e.target.value) : undefined)}
                placeholder="0"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 min-h-[44px]"
              />
            </div>
            <div>
              <label htmlFor="filter-marge-max" className="block text-sm font-medium text-gray-700 mb-2">
                Marge maximum (%)
              </label>
              <input
                id="filter-marge-max"
                type="number"
                min="0"
                max="100"
                step="1"
                value={filters.marge_max || ''}
                onChange={(e) => onFilterChange('marge_max', e.target.value ? Number(e.target.value) : undefined)}
                placeholder="100"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 min-h-[44px]"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
