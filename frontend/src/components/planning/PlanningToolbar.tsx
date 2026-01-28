import { Plus, Filter, Users, Building2, AlertCircle } from 'lucide-react'
import { METIERS } from '../../types'
import type { ViewTab } from '../../hooks/usePlanning'
import type { Chantier } from '../../types'

interface PlanningToolbarProps {
  canEdit: boolean
  viewTab: ViewTab
  onViewTabChange: (tab: ViewTab) => void
  nonPlanifiesCount: number
  showNonPlanifiesOnly: boolean
  onToggleNonPlanifies: () => void
  filterChantier: string
  onFilterChantierChange: (value: string) => void
  chantiers: Chantier[]
  showFilters: boolean
  onToggleFilters: () => void
  filterMetiers: string[]
  showWeekend: boolean
  onToggleWeekend: (value: boolean) => void
  onCreateClick: () => void
}

export function PlanningToolbar({
  canEdit,
  viewTab,
  onViewTabChange,
  nonPlanifiesCount,
  showNonPlanifiesOnly,
  onToggleNonPlanifies,
  filterChantier,
  onFilterChantierChange,
  chantiers,
  showFilters,
  onToggleFilters,
  filterMetiers,
  showWeekend,
  onToggleWeekend,
  onCreateClick,
}: PlanningToolbarProps) {
  return (
    <>
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Planning</h1>
          <p className="text-gray-600 text-sm sm:text-base">
            Gestion des affectations des équipes aux chantiers
          </p>
        </div>

        {canEdit && (
          <button onClick={onCreateClick} className="btn btn-primary whitespace-nowrap">
            <Plus className="w-5 h-5 mr-2" />
            <span className="hidden sm:inline">Créer une affectation</span>
            <span className="sm:hidden">Créer</span>
          </button>
        )}
      </div>

      {/* Onglets de vue */}
      <div className="flex flex-wrap items-center gap-2 sm:gap-4">
        <div className="flex rounded-lg bg-gray-100 p-1">
          <button
            onClick={() => onViewTabChange('utilisateurs')}
            className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              viewTab === 'utilisateurs'
                ? 'bg-white text-gray-900 shadow'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <Users className="w-4 h-4" />
            Utilisateurs
          </button>
          <button
            onClick={() => onViewTabChange('chantiers')}
            className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              viewTab === 'chantiers'
                ? 'bg-white text-gray-900 shadow'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <Building2 className="w-4 h-4" />
            Chantiers
          </button>
        </div>

        {/* Badge non planifiés */}
        {nonPlanifiesCount > 0 && (
          <button
            onClick={onToggleNonPlanifies}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
              showNonPlanifiesOnly
                ? 'bg-orange-100 text-orange-700'
                : 'bg-orange-50 text-orange-600 hover:bg-orange-100'
            }`}
          >
            <AlertCircle className="w-4 h-4" />
            {nonPlanifiesCount} non planifié{nonPlanifiesCount > 1 ? 's' : ''}
          </button>
        )}

        {/* Filtre par chantier */}
        <select
          value={filterChantier}
          onChange={(e) => onFilterChantierChange(e.target.value)}
          className="px-2 sm:px-3 py-2 rounded-lg text-xs sm:text-sm border border-gray-200 bg-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500 max-w-[150px] sm:max-w-none"
        >
          <option value="">Tous les chantiers</option>
          {chantiers.map((chantier) => (
            <option key={chantier.id} value={chantier.id}>
              {chantier.nom}
            </option>
          ))}
        </select>

        {/* Bouton filtres */}
        <button
          onClick={onToggleFilters}
          className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
            showFilters || filterMetiers.length > 0
              ? 'bg-primary-100 text-primary-700'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
        >
          <Filter className="w-4 h-4" />
          Filtres
          {filterMetiers.length > 0 && (
            <span className="bg-primary-600 text-white text-xs px-1.5 py-0.5 rounded-full">
              {filterMetiers.length}
            </span>
          )}
        </button>

        {/* Toggle weekend */}
        <label className="flex items-center gap-2 px-2 sm:px-3 py-2 rounded-lg text-xs sm:text-sm bg-gray-100 cursor-pointer hover:bg-gray-200 transition-colors whitespace-nowrap">
          <input
            type="checkbox"
            checked={showWeekend}
            onChange={(e) => onToggleWeekend(e.target.checked)}
            className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
          />
          <span className="text-gray-700">Weekend</span>
        </label>
      </div>
    </>
  )
}

interface PlanningFiltersPanelProps {
  show: boolean
  filterMetiers: string[]
  onToggleMetier: (metier: string) => void
  onClear: () => void
}

export function PlanningFiltersPanel({
  show,
  filterMetiers,
  onToggleMetier,
  onClear,
}: PlanningFiltersPanelProps) {
  if (!show) return null

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <div className="flex flex-wrap gap-2">
        <span className="text-sm font-medium text-gray-700 mr-2">Métiers :</span>
        {Object.entries(METIERS).map(([key, { label, color }]) => (
          <button
            key={key}
            onClick={() => onToggleMetier(key)}
            className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
              filterMetiers.includes(key)
                ? 'text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
            style={filterMetiers.includes(key) ? { backgroundColor: color } : undefined}
          >
            {label}
          </button>
        ))}
        {filterMetiers.length > 0 && (
          <button
            onClick={onClear}
            className="text-xs text-gray-500 hover:text-gray-700 ml-2"
          >
            Effacer
          </button>
        )}
      </div>
    </div>
  )
}
