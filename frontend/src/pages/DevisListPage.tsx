/**
 * DevisListPage - Liste des devis avec recherche, filtres et pagination
 * Module Devis (Module 20) - DEV-03
 */

import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import Layout from '../components/Layout'
import DevisStatusBadge from '../components/devis/DevisStatusBadge'
import DevisForm from '../components/devis/DevisForm'
import { devisService } from '../services/devis'
import type { Devis, DevisCreate, DevisUpdate, StatutDevis } from '../types'
import { STATUT_DEVIS_CONFIG } from '../types'
import {
  Loader2,
  AlertCircle,
  Plus,
  Search,
  Filter,
  ArrowUpDown,
  ChevronLeft,
  ChevronRight,
  X,
  FileText,
} from 'lucide-react'

const formatEUR = (value: number) =>
  new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(value)

const PAGE_SIZE = 20

type SortField = 'numero' | 'client_nom' | 'objet' | 'montant_total_ht' | 'date_creation' | 'statut'
type SortDirection = 'asc' | 'desc'

const ALL_STATUTS = Object.keys(STATUT_DEVIS_CONFIG) as StatutDevis[]

export default function DevisListPage() {
  const navigate = useNavigate()
  const [devisList, setDevisList] = useState<Devis[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Recherche et filtres
  const [search, setSearch] = useState('')
  const [selectedStatuts, setSelectedStatuts] = useState<StatutDevis[]>([])
  const [dateDebut, setDateDebut] = useState('')
  const [dateFin, setDateFin] = useState('')
  const [montantMin, setMontantMin] = useState('')
  const [montantMax, setMontantMax] = useState('')
  const [showFilters, setShowFilters] = useState(false)

  // Tri et pagination
  const [sortBy, setSortBy] = useState<SortField>('date_creation')
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc')
  const [page, setPage] = useState(0)

  // Modal creation
  const [showCreateForm, setShowCreateForm] = useState(false)

  const loadDevis = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      const params: Record<string, unknown> = {
        limit: PAGE_SIZE,
        offset: page * PAGE_SIZE,
        sort_by: sortBy,
        sort_direction: sortDirection,
      }

      if (search) params.search = search
      if (selectedStatuts.length === 1) params.statut = selectedStatuts[0]
      if (dateDebut) params.date_debut = dateDebut
      if (dateFin) params.date_fin = dateFin
      if (montantMin) params.montant_min = Number(montantMin)
      if (montantMax) params.montant_max = Number(montantMax)

      const result = await devisService.listDevis(params as Parameters<typeof devisService.listDevis>[0])
      setDevisList(result.items)
      setTotal(result.total)
    } catch {
      setError('Erreur lors du chargement des devis')
    } finally {
      setLoading(false)
    }
  }, [page, sortBy, sortDirection, search, selectedStatuts, dateDebut, dateFin, montantMin, montantMax])

  useEffect(() => {
    loadDevis()
  }, [loadDevis])

  const handleSort = (field: SortField) => {
    if (sortBy === field) {
      setSortDirection((d) => (d === 'asc' ? 'desc' : 'asc'))
    } else {
      setSortBy(field)
      setSortDirection('asc')
    }
    setPage(0)
  }

  const handleSearch = () => {
    setPage(0)
    loadDevis()
  }

  const toggleStatut = (statut: StatutDevis) => {
    setSelectedStatuts((prev) =>
      prev.includes(statut) ? prev.filter((s) => s !== statut) : [...prev, statut]
    )
    setPage(0)
  }

  const clearFilters = () => {
    setSelectedStatuts([])
    setDateDebut('')
    setDateFin('')
    setMontantMin('')
    setMontantMax('')
    setSearch('')
    setPage(0)
  }

  const handleCreateDevis = async (data: DevisCreate | DevisUpdate) => {
    const created = await devisService.createDevis(data as DevisCreate)
    setShowCreateForm(false)
    navigate(`/devis/${created.id}`)
  }

  const totalPages = Math.ceil(total / PAGE_SIZE)
  const hasActiveFilters = selectedStatuts.length > 0 || dateDebut || dateFin || montantMin || montantMax

  const renderSortButton = (field: SortField, label: string) => (
    <button
      onClick={() => handleSort(field)}
      className={`flex items-center gap-1 text-xs font-medium ${
        sortBy === field ? 'text-blue-600' : 'text-gray-500 hover:text-gray-700'
      }`}
    >
      {label}
      <ArrowUpDown size={12} />
    </button>
  )

  return (
    <Layout>
      <div className="space-y-6" role="main" aria-label="Liste des devis">
        {/* Header */}
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-bold text-gray-900">Devis</h1>
          <button
            onClick={() => setShowCreateForm(true)}
            className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
          >
            <Plus className="w-4 h-4" />
            Nouveau devis
          </button>
        </div>

        {/* Barre de recherche + filtre */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                onKeyDown={(e) => { if (e.key === 'Enter') handleSearch() }}
                placeholder="Rechercher par client, numero, objet..."
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`inline-flex items-center gap-2 px-4 py-2 text-sm rounded-lg border transition-colors ${
                hasActiveFilters
                  ? 'border-blue-300 bg-blue-50 text-blue-700'
                  : 'border-gray-300 text-gray-700 hover:bg-gray-50'
              }`}
            >
              <Filter className="w-4 h-4" />
              Filtres
              {hasActiveFilters && (
                <span className="bg-blue-600 text-white text-xs px-1.5 py-0.5 rounded-full">
                  {selectedStatuts.length + (dateDebut ? 1 : 0) + (dateFin ? 1 : 0) + (montantMin ? 1 : 0) + (montantMax ? 1 : 0)}
                </span>
              )}
            </button>
            {hasActiveFilters && (
              <button
                onClick={clearFilters}
                className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg"
                aria-label="Effacer les filtres"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>

          {/* Panneau filtres */}
          {showFilters && (
            <div className="mt-4 pt-4 border-t border-gray-200 space-y-4">
              {/* Statuts */}
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-2">Statut</label>
                <div className="flex flex-wrap gap-2">
                  {ALL_STATUTS.map((statut) => {
                    const config = STATUT_DEVIS_CONFIG[statut]
                    const isSelected = selectedStatuts.includes(statut)
                    return (
                      <button
                        key={statut}
                        onClick={() => toggleStatut(statut)}
                        className={`px-3 py-1 text-xs rounded-full border transition-colors ${
                          isSelected
                            ? 'border-transparent font-medium'
                            : 'border-gray-200 text-gray-600 hover:bg-gray-50'
                        }`}
                        style={isSelected ? {
                          backgroundColor: config.couleur + '20',
                          color: config.couleur,
                        } : undefined}
                      >
                        {config.label}
                      </button>
                    )
                  })}
                </div>
              </div>

              {/* Dates et montants */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Date debut</label>
                  <input
                    type="date"
                    value={dateDebut}
                    onChange={(e) => { setDateDebut(e.target.value); setPage(0) }}
                    className="w-full border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Date fin</label>
                  <input
                    type="date"
                    value={dateFin}
                    onChange={(e) => { setDateFin(e.target.value); setPage(0) }}
                    className="w-full border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Montant min</label>
                  <input
                    type="number"
                    min="0"
                    step="100"
                    value={montantMin}
                    onChange={(e) => { setMontantMin(e.target.value); setPage(0) }}
                    placeholder="0"
                    className="w-full border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Montant max</label>
                  <input
                    type="number"
                    min="0"
                    step="100"
                    value={montantMax}
                    onChange={(e) => { setMontantMax(e.target.value); setPage(0) }}
                    placeholder="Illimite"
                    className="w-full border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Loading */}
        {loading && (
          <div className="flex items-center justify-center py-16">
            <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-start gap-2" role="alert">
            <AlertCircle className="flex-shrink-0 mt-0.5" size={18} />
            <div>
              <p>{error}</p>
              <button onClick={loadDevis} className="text-sm underline mt-1">Reessayer</button>
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
                    <th className="px-4 py-3 text-left">{renderSortButton('numero', 'Numero')}</th>
                    <th className="px-4 py-3 text-left">{renderSortButton('client_nom', 'Client')}</th>
                    <th className="px-4 py-3 text-left">{renderSortButton('objet', 'Objet')}</th>
                    <th className="px-4 py-3 text-right">{renderSortButton('montant_total_ht', 'Montant HT')}</th>
                    <th className="px-4 py-3 text-center">{renderSortButton('statut', 'Statut')}</th>
                    <th className="px-4 py-3 text-left">{renderSortButton('date_creation', 'Date creation')}</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {devisList.map((devis) => (
                    <tr
                      key={devis.id}
                      onClick={() => navigate(`/devis/${devis.id}`)}
                      className="hover:bg-gray-50 transition-colors cursor-pointer"
                    >
                      <td className="px-4 py-3 font-mono text-xs text-gray-500">{devis.numero}</td>
                      <td className="px-4 py-3 font-medium text-gray-900">{devis.client_nom}</td>
                      <td className="px-4 py-3 text-gray-700 max-w-xs truncate">{devis.objet}</td>
                      <td className="px-4 py-3 text-right font-medium">{formatEUR(Number(devis.montant_total_ht))}</td>
                      <td className="px-4 py-3 text-center">
                        <DevisStatusBadge statut={devis.statut} />
                      </td>
                      <td className="px-4 py-3 text-gray-500">
                        {devis.date_creation ? new Date(devis.date_creation).toLocaleDateString('fr-FR') : '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {devisList.length === 0 && (
                <div className="text-center py-12 text-gray-500">
                  <FileText className="w-12 h-12 mx-auto text-gray-300 mb-3" />
                  <p className="font-medium">Aucun devis trouve</p>
                  <p className="text-sm mt-1">
                    {hasActiveFilters
                      ? 'Essayez de modifier vos filtres'
                      : 'Creez votre premier devis pour commencer'}
                  </p>
                </div>
              )}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-between px-4 py-3 border-t border-gray-200">
                <p className="text-sm text-gray-500">
                  {page * PAGE_SIZE + 1} - {Math.min((page + 1) * PAGE_SIZE, total)} sur {total} devis
                </p>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setPage((p) => Math.max(0, p - 1))}
                    disabled={page === 0}
                    className="p-2 rounded-lg hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
                    aria-label="Page precedente"
                  >
                    <ChevronLeft className="w-4 h-4" />
                  </button>
                  <span className="text-sm text-gray-700">
                    Page {page + 1} / {totalPages}
                  </span>
                  <button
                    onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
                    disabled={page >= totalPages - 1}
                    className="p-2 rounded-lg hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
                    aria-label="Page suivante"
                  >
                    <ChevronRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Modal creation */}
        {showCreateForm && (
          <DevisForm
            onSubmit={handleCreateDevis}
            onCancel={() => setShowCreateForm(false)}
          />
        )}
      </div>
    </Layout>
  )
}
