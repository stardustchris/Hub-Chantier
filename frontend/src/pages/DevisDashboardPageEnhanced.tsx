/**
 * DevisDashboardPageEnhanced - Dashboard pipeline commercial avec kanban drag & drop
 * DEV-17: Tableau de bord devis (vue kanban)
 */

import { AlertCircle, Loader2, FileText, Euro, TrendingUp, Filter, X } from 'lucide-react'
import Layout from '../components/Layout'
import DevisKanbanDnD from '../components/devis/DevisKanbanDnD'
import { useDevisKanban } from '../hooks/useDevisKanban'
import { formatEUR } from '../utils/format'

export default function DevisDashboardPageEnhanced() {
  const {
    // Data
    devis,
    kpi,
    devisParStatut,

    // State
    loading,
    error,

    // Actions
    reload,
    moveDevis,

    // Filters
    filters,
    setFilter,
    clearFilters,
    hasActiveFilters,
  } = useDevisKanban()

  return (
    <Layout>
      <div className="space-y-6" role="main" aria-label="Dashboard pipeline devis">
        {/* Header */}
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-bold text-gray-900">Pipeline Commercial</h1>
          {!loading && (
            <button
              onClick={reload}
              className="text-sm text-blue-600 hover:text-blue-800 transition-colors min-h-[44px] px-3"
            >
              Actualiser
            </button>
          )}
        </div>

        {/* Filtres rapides */}
        <div className="flex items-center gap-3 flex-wrap">
          <div className="flex items-center gap-2 text-sm text-gray-700">
            <Filter className="w-4 h-4" />
            <span className="font-medium">Filtres rapides:</span>
          </div>

          <div className="flex items-center gap-2">
            <input
              type="date"
              value={filters.date_debut || ''}
              onChange={(e) => setFilter('date_debut', e.target.value || undefined)}
              className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 min-h-[44px]"
              aria-label="Date début"
            />
            <span className="text-gray-600">-</span>
            <input
              type="date"
              value={filters.date_fin || ''}
              onChange={(e) => setFilter('date_fin', e.target.value || undefined)}
              className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 min-h-[44px]"
              aria-label="Date fin"
            />
          </div>

          <input
            type="text"
            value={filters.client_nom || ''}
            onChange={(e) => setFilter('client_nom', e.target.value || undefined)}
            placeholder="Filtrer par client..."
            className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 min-h-[44px]"
            aria-label="Filtrer par client"
          />

          {hasActiveFilters && (
            <button
              onClick={clearFilters}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm text-red-600 hover:text-red-700 border border-red-200 rounded-lg hover:bg-red-50 transition-colors min-h-[44px]"
            >
              <X className="w-4 h-4" />
              Effacer
            </button>
          )}
        </div>

        {/* Error */}
        {error && (
          <div
            className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-start gap-2"
            role="alert"
          >
            <AlertCircle className="flex-shrink-0 mt-0.5" size={18} />
            <div>
              <p>{error}</p>
              <button onClick={reload} className="text-sm underline mt-1">
                Réessayer
              </button>
            </div>
          </div>
        )}

        {/* KPI Cards */}
        {!loading && kpi && (
          <div
            className="grid grid-cols-1 md:grid-cols-3 gap-4"
            role="region"
            aria-label="Indicateurs clés"
          >
            <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Devis en cours</p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">
                    {kpi.nb_envoye + kpi.nb_vu + kpi.nb_en_negociation + kpi.nb_en_validation}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">{kpi.nb_total} devis au total</p>
                </div>
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                  <FileText className="w-6 h-6 text-blue-600" />
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Montant pipeline</p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">
                    {formatEUR(kpi.total_pipeline_ht)}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    Accepté: {formatEUR(kpi.total_accepte_ht)}
                  </p>
                </div>
                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                  <Euro className="w-6 h-6 text-green-600" />
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Taux de conversion</p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">
                    {kpi.taux_conversion.toFixed(1)}%
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    {kpi.nb_accepte} accepté{kpi.nb_accepte > 1 ? 's' : ''} / {kpi.nb_refuse}{' '}
                    refusé{kpi.nb_refuse > 1 ? 's' : ''}
                  </p>
                </div>
                <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                  <TrendingUp className="w-6 h-6 text-purple-600" />
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Vue Kanban avec drag & drop */}
        <div
          className="bg-white rounded-xl shadow-sm border border-gray-200 p-6"
          role="region"
          aria-label="Vue kanban des devis"
        >
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Pipeline par statut (glissez-déposez pour changer le statut)
          </h2>

          {loading ? (
            <div className="flex items-center justify-center py-16">
              <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
            </div>
          ) : (
            <DevisKanbanDnD
              devis={devis}
              devisParStatut={devisParStatut}
              onMoveDevis={moveDevis}
              loading={loading}
            />
          )}
        </div>
      </div>
    </Layout>
  )
}
