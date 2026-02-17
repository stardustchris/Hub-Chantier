import { useState, useCallback } from 'react'
import { useListPage } from '../hooks/useListPage'
import { useCreateChantier } from '../hooks/useCreateChantier'
import { logger } from '../services/logger'
import Layout from '../components/Layout'
import { ChantierCard, CreateChantierModal, TempContact, TempPhase } from '../components/chantiers'
import { useDocumentTitle } from '../hooks/useDocumentTitle'
import {
  Building2,
  Plus,
  Search,
  Loader2,
  X,
} from 'lucide-react'
import type { Chantier, ChantierStatut, ChantierCreate } from '../types'
import { CHANTIER_STATUTS } from '../types'

// Note: Le filtrage des chantiers spéciaux (CONGES, MALADIE, etc.)
// est maintenant fait côté backend via le paramètre exclude_special=true

export default function ChantiersListPage() {
  // Document title
  useDocumentTitle('Chantiers')

  const [showCreateModal, setShowCreateModal] = useState(false)

  const {
    allChantiers,
    fetchChantiers,
    handleCreateChantier,
  } = useCreateChantier()

  // Use the reusable list hook for pagination, search, and loading
  const {
    items: chantiers,
    isLoading,
    page,
    setPage,
    totalPages,
    search,
    setSearch,
    filters,
    setFilter,
    clearFilters,
    reload,
  } = useListPage<Chantier>({
    fetchItems: fetchChantiers,
    pageSize: 12,
  })

  const statutFilter = (filters.statut as ChantierStatut | undefined) || ''

  const handleCreate = useCallback(async (
    data: ChantierCreate,
    contacts: TempContact[],
    phases: TempPhase[]
  ) => {
    try {
      await handleCreateChantier(data, contacts, phases, async () => {
        setShowCreateModal(false)
        await reload()
      })
    } catch (error) {
      logger.error('Error creating chantier', error, { context: 'ChantiersListPage' })
      throw error
    }
  }, [handleCreateChantier, reload])

  const handleSetStatutFilter = useCallback((statut: ChantierStatut | '') => {
    setFilter('statut', statut || undefined)
  }, [setFilter])

  const handleClearFilters = useCallback(() => {
    clearFilters()
  }, [clearFilters])

  // Use allChantiers for counters (not filtered chantiers)
  const getStatutCount = useCallback((statut: ChantierStatut) => {
    return allChantiers.filter((c) => c.statut === statut).length
  }, [allChantiers])

  return (
    <Layout>
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Chantiers</h1>
            <p className="text-gray-600">Gerez vos projets de construction</p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="btn btn-primary flex items-center gap-2"
          >
            <Plus className="w-5 h-5" />
            Nouveau chantier
          </button>
        </div>

        {/* Stats cards */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
          {/* All button */}
          <button
            onClick={() => handleSetStatutFilter('')}
            className={`card text-left transition-all ${
              statutFilter === '' ? 'ring-2 ring-primary-500' : ''
            }`}
          >
            <div className="flex items-center gap-3">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: '#6B7280' }}
              />
              <div>
                <p className="text-2xl font-bold text-gray-900">{allChantiers.length}</p>
                <p className="text-xs text-gray-500">Tous</p>
              </div>
            </div>
          </button>
          {(Object.entries(CHANTIER_STATUTS) as [ChantierStatut, typeof CHANTIER_STATUTS[ChantierStatut]][]).map(
            ([statut, info]) => (
              <button
                key={statut}
                onClick={() => handleSetStatutFilter(statutFilter === statut ? '' : statut)}
                className={`card text-left transition-all ${
                  statutFilter === statut ? 'ring-2 ring-primary-500' : ''
                }`}
              >
                <div className="flex items-center gap-3">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: info.color }}
                  />
                  <div>
                    <p className="text-2xl font-bold text-gray-900">{getStatutCount(statut)}</p>
                    <p className="text-xs text-gray-500">{info.label}</p>
                  </div>
                </div>
              </button>
            )
          )}
        </div>

        {/* Search and filters */}
        <div className="card mb-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-600" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Rechercher un chantier..."
                className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div className="flex gap-2">
              <select
                value={statutFilter}
                onChange={(e) => handleSetStatutFilter(e.target.value as ChantierStatut | '')}
                className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500"
              >
                <option value="">Tous les statuts</option>
                {(Object.entries(CHANTIER_STATUTS) as [ChantierStatut, typeof CHANTIER_STATUTS[ChantierStatut]][]).map(
                  ([statut, info]) => (
                    <option key={statut} value={statut}>
                      {info.label}
                    </option>
                  )
                )}
              </select>
              {(search || statutFilter) && (
                <button
                  onClick={handleClearFilters}
                  className="px-3 py-2 text-gray-500 hover:text-gray-700"
                >
                  <X className="w-5 h-5" />
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Chantiers grid */}
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
          </div>
        ) : chantiers.length === 0 ? (
          <div className="card text-center py-12">
            <Building2 className="w-12 h-12 text-gray-500 mx-auto mb-4" />
            <p className="text-gray-500">Aucun chantier trouve</p>
            {(search || statutFilter) && (
              <button
                onClick={handleClearFilters}
                className="mt-4 text-primary-600 hover:text-primary-700"
              >
                Effacer les filtres
              </button>
            )}
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
              {chantiers.map((chantier) => (
                <ChantierCard key={chantier.id} chantier={chantier} />
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-center gap-2">
                <button
                  onClick={() => setPage(Math.max(1, page - 1))}
                  disabled={page === 1}
                  className="px-4 py-2 border rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                >
                  Precedent
                </button>
                <span className="px-4 py-2 text-gray-600">
                  Page {page} sur {totalPages}
                </span>
                <button
                  onClick={() => setPage(Math.min(totalPages, page + 1))}
                  disabled={page === totalPages}
                  className="px-4 py-2 border rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                >
                  Suivant
                </button>
              </div>
            )}
          </>
        )}

        {/* Create Modal */}
        {showCreateModal && (
          <CreateChantierModal
            onClose={() => setShowCreateModal(false)}
            onSubmit={handleCreate}
            usedColors={chantiers.map(c => c.couleur).filter(Boolean) as string[]}
          />
        )}
      </div>
    </Layout>
  )
}
