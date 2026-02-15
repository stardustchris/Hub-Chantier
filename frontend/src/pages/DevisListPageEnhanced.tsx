/**
 * DevisListPageEnhanced - Liste des devis avec recherche et filtres avancés
 * DEV-19: Recherche et filtres avancés
 * Utilise les filtres persistés dans l'URL via query params
 */

import { useNavigate } from 'react-router-dom'
import Layout from '../components/Layout'
import DevisStatusBadge from '../components/devis/DevisStatusBadge'
import DevisAdvancedFilters from '../components/devis/DevisAdvancedFilters'
import { useDevisFilters } from '../hooks/useDevisFilters'
import { formatEUR } from '../utils/format'
import {
  Loader2,
  AlertCircle,
  Plus,
  ChevronLeft,
  ChevronRight,
  FileText,
} from 'lucide-react'

export default function DevisListPageEnhanced() {
  const navigate = useNavigate()

  const {
    // Data
    devis,
    totalResults,

    // State
    loading,
    error,

    // Filters
    filters,
    setFilter,
    clearFilters,
    hasActiveFilters,
    activeFiltersCount,

    // Pagination
    page,
    pageSize,
    totalPages,
    setPage,
  } = useDevisFilters()

  return (
    <Layout>
      <div className="space-y-6" role="main" aria-label="Liste des devis">
        {/* Header */}
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-bold text-gray-900">Devis</h1>
          <button
            onClick={() => navigate('/devis/nouveau')}
            className="inline-flex items-center gap-2 px-4 py-2.5 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors min-h-[44px]"
          >
            <Plus className="w-4 h-4" />
            Nouveau devis
          </button>
        </div>

        {/* Filtres avancés */}
        <DevisAdvancedFilters
          filters={filters}
          onFilterChange={setFilter}
          onClearFilters={clearFilters}
          totalResults={totalResults}
          hasActiveFilters={hasActiveFilters}
          activeFiltersCount={activeFiltersCount}
        />

        {/* Loading */}
        {loading && (
          <div className="flex items-center justify-center py-16">
            <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
          </div>
        )}

        {/* Error */}
        {error && (
          <div
            className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-start gap-2"
            role="alert"
          >
            <AlertCircle className="flex-shrink-0 mt-0.5" size={18} />
            <div>
              <p>{error}</p>
            </div>
          </div>
        )}

        {/* Tableau */}
        {!loading && !error && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm" aria-label="Liste des devis">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">
                      Numéro
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">
                      Client
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">
                      Objet
                    </th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500">
                      Montant HT
                    </th>
                    <th className="px-4 py-3 text-center text-xs font-medium text-gray-500">
                      Statut
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">
                      Date création
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {devis.map((d) => (
                    <tr
                      key={d.id}
                      onClick={() => navigate(`/devis/${d.id}`)}
                      className="hover:bg-gray-50 transition-colors cursor-pointer"
                      role="button"
                      tabIndex={0}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' || e.key === ' ') {
                          e.preventDefault()
                          navigate(`/devis/${d.id}`)
                        }
                      }}
                    >
                      <td className="px-4 py-3 font-mono text-xs text-gray-500">
                        {d.numero}
                      </td>
                      <td className="px-4 py-3 font-medium text-gray-900">
                        {d.client_nom}
                      </td>
                      <td className="px-4 py-3 text-gray-700 max-w-xs truncate">
                        {d.objet}
                      </td>
                      <td className="px-4 py-3 text-right font-medium">
                        {formatEUR(Number(d.montant_total_ht))}
                      </td>
                      <td className="px-4 py-3 text-center">
                        <DevisStatusBadge statut={d.statut} />
                      </td>
                      <td className="px-4 py-3 text-gray-500">
                        {d.date_creation
                          ? new Date(d.date_creation).toLocaleDateString('fr-FR')
                          : '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {devis.length === 0 && (
                <div className="text-center py-12 text-gray-500">
                  <FileText className="w-12 h-12 mx-auto text-gray-500 mb-3" />
                  <p className="font-medium">Aucun devis trouvé</p>
                  <p className="text-sm mt-1">
                    {hasActiveFilters
                      ? 'Essayez de modifier vos filtres'
                      : 'Créez votre premier devis pour commencer'}
                  </p>
                </div>
              )}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-between px-4 py-3 border-t border-gray-200 bg-gray-50">
                <p className="text-sm text-gray-700">
                  Page {page} sur {totalPages} ({totalResults} résultat
                  {totalResults > 1 ? 's' : ''})
                </p>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setPage(page - 1)}
                    disabled={page === 1}
                    className="p-2 rounded-lg hover:bg-white disabled:opacity-50 disabled:cursor-not-allowed transition-colors min-h-[44px] min-w-[44px] flex items-center justify-center"
                    aria-label="Page précédente"
                  >
                    <ChevronLeft className="w-5 h-5" />
                  </button>
                  <span className="text-sm text-gray-700 px-2">
                    {page} / {totalPages}
                  </span>
                  <button
                    onClick={() => setPage(page + 1)}
                    disabled={page >= totalPages}
                    className="p-2 rounded-lg hover:bg-white disabled:opacity-50 disabled:cursor-not-allowed transition-colors min-h-[44px] min-w-[44px] flex items-center justify-center"
                    aria-label="Page suivante"
                  >
                    <ChevronRight className="w-5 h-5" />
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </Layout>
  )
}
