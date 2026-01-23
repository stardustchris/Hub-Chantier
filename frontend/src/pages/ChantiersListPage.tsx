import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { chantiersService } from '../services/chantiers'
import Layout from '../components/Layout'
import {
  Building2,
  Plus,
  Search,
  MapPin,
  Users,
  Clock,
  ChevronRight,
  Loader2,
  X,
  Calendar,
} from 'lucide-react'
import { format } from 'date-fns'
import { fr } from 'date-fns/locale'
import type { Chantier, ChantierStatut, ChantierCreate } from '../types'
import { CHANTIER_STATUTS, USER_COLORS } from '../types'

export default function ChantiersListPage() {
  const [chantiers, setChantiers] = useState<Chantier[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [statutFilter, setStatutFilter] = useState<ChantierStatut | ''>('')
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [showCreateModal, setShowCreateModal] = useState(false)

  useEffect(() => {
    loadChantiers()
  }, [page, search, statutFilter])

  const loadChantiers = async () => {
    try {
      setIsLoading(true)
      const response = await chantiersService.list({
        page,
        size: 12,
        search: search || undefined,
        statut: statutFilter || undefined,
      })
      setChantiers(response.items)
      setTotalPages(response.pages)
    } catch (error) {
      console.error('Error loading chantiers:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleCreateChantier = async (data: ChantierCreate) => {
    await chantiersService.create(data)
    setShowCreateModal(false)
    loadChantiers()
  }

  const filteredChantiers = chantiers

  const getStatutCount = (statut: ChantierStatut) => {
    return chantiers.filter((c) => c.statut === statut).length
  }

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
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          {(Object.entries(CHANTIER_STATUTS) as [ChantierStatut, typeof CHANTIER_STATUTS[ChantierStatut]][]).map(
            ([statut, info]) => (
              <button
                key={statut}
                onClick={() => setStatutFilter(statutFilter === statut ? '' : statut)}
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
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={search}
                onChange={(e) => {
                  setSearch(e.target.value)
                  setPage(1)
                }}
                placeholder="Rechercher un chantier..."
                className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div className="flex gap-2">
              <select
                value={statutFilter}
                onChange={(e) => {
                  setStatutFilter(e.target.value as ChantierStatut | '')
                  setPage(1)
                }}
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
                  onClick={() => {
                    setSearch('')
                    setStatutFilter('')
                    setPage(1)
                  }}
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
        ) : filteredChantiers.length === 0 ? (
          <div className="card text-center py-12">
            <Building2 className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">Aucun chantier trouve</p>
            {(search || statutFilter) && (
              <button
                onClick={() => {
                  setSearch('')
                  setStatutFilter('')
                }}
                className="mt-4 text-primary-600 hover:text-primary-700"
              >
                Effacer les filtres
              </button>
            )}
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
              {filteredChantiers.map((chantier) => (
                <ChantierCard key={chantier.id} chantier={chantier} />
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-center gap-2">
                <button
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="px-4 py-2 border rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                >
                  Precedent
                </button>
                <span className="px-4 py-2 text-gray-600">
                  Page {page} sur {totalPages}
                </span>
                <button
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
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
            onSubmit={handleCreateChantier}
            usedColors={chantiers.map(c => c.couleur).filter(Boolean) as string[]}
          />
        )}
      </div>
    </Layout>
  )
}

interface ChantierCardProps {
  chantier: Chantier
}

function ChantierCard({ chantier }: ChantierCardProps) {
  const statutInfo = CHANTIER_STATUTS[chantier.statut]

  return (
    <Link
      to={`/chantiers/${chantier.id}`}
      className="card hover:shadow-md transition-shadow group"
    >
      {/* Header with color */}
      <div
        className="h-2 -mx-6 -mt-6 mb-4 rounded-t-xl"
        style={{ backgroundColor: chantier.couleur || '#3498DB' }}
      />

      {/* Content */}
      <div className="flex items-start justify-between mb-3">
        <div>
          <span className="text-sm font-mono text-gray-500">{chantier.code}</span>
          <h3 className="font-semibold text-gray-900 group-hover:text-primary-600 transition-colors">
            {chantier.nom}
          </h3>
        </div>
        <span
          className="text-xs px-2 py-1 rounded-full"
          style={{ backgroundColor: statutInfo.color + '20', color: statutInfo.color }}
        >
          {statutInfo.label}
        </span>
      </div>

      {/* Address */}
      <div className="flex items-start gap-2 text-sm text-gray-600 mb-3">
        <MapPin className="w-4 h-4 shrink-0 mt-0.5" />
        <span className="line-clamp-2">{chantier.adresse}</span>
      </div>

      {/* Info */}
      <div className="flex items-center gap-4 text-sm text-gray-500 mb-3">
        {chantier.heures_estimees && (
          <span className="flex items-center gap-1">
            <Clock className="w-4 h-4" />
            {chantier.heures_estimees}h
          </span>
        )}
        {chantier.date_debut_prevue && (
          <span className="flex items-center gap-1">
            <Calendar className="w-4 h-4" />
            {format(new Date(chantier.date_debut_prevue), 'dd MMM', { locale: fr })}
          </span>
        )}
      </div>

      {/* Team */}
      {(chantier.conducteurs?.length > 0 || chantier.chefs?.length > 0) && (
        <div className="flex items-center gap-2 pt-3 border-t">
          <Users className="w-4 h-4 text-gray-400" />
          <div className="flex -space-x-2">
            {[...(chantier.conducteurs || []), ...(chantier.chefs || [])]
              .slice(0, 3)
              .map((user) => (
                <div
                  key={user.id}
                  className="w-7 h-7 rounded-full flex items-center justify-center text-white text-xs font-semibold border-2 border-white"
                  style={{ backgroundColor: user.couleur || '#3498DB' }}
                  title={`${user.prenom} ${user.nom}`}
                >
                  {user.prenom?.[0]}
                  {user.nom?.[0]}
                </div>
              ))}
            {(chantier.conducteurs?.length || 0) + (chantier.chefs?.length || 0) > 3 && (
              <div className="w-7 h-7 rounded-full bg-gray-200 flex items-center justify-center text-gray-600 text-xs font-semibold border-2 border-white">
                +{(chantier.conducteurs?.length || 0) + (chantier.chefs?.length || 0) - 3}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Arrow */}
      <ChevronRight className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-300 group-hover:text-primary-500 transition-colors" />
    </Link>
  )
}

interface CreateChantierModalProps {
  onClose: () => void
  onSubmit: (data: ChantierCreate) => void
  usedColors: string[]
}

function CreateChantierModal({ onClose, onSubmit, usedColors }: CreateChantierModalProps) {
  // Trouver la première couleur non utilisée
  const getAvailableColor = () => {
    const availableColor = USER_COLORS.find(c => !usedColors.includes(c.code))
    return availableColor?.code || USER_COLORS[0].code
  }

  const [formData, setFormData] = useState<ChantierCreate>({
    nom: '',
    adresse: '',
    couleur: getAvailableColor(),
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Validation des dates
  const validateDates = (): boolean => {
    if (formData.date_debut_prevue && formData.date_fin_prevue) {
      if (formData.date_fin_prevue < formData.date_debut_prevue) {
        setError('La date de fin doit être après la date de début')
        return false
      }
    }
    setError(null)
    return true
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateDates()) {
      return
    }

    setIsSubmitting(true)
    setError(null)
    try {
      await onSubmit(formData)
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Erreur lors de la création du chantier')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="fixed inset-0 bg-black/50" onClick={onClose} />
      <div className="relative bg-white rounded-xl shadow-xl w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b px-6 py-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold">Nouveau chantier</h2>
          <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-lg">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nom du chantier *
            </label>
            <input
              type="text"
              required
              value={formData.nom}
              onChange={(e) => setFormData({ ...formData, nom: e.target.value })}
              className="input"
              placeholder="Ex: Residence Les Pins"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Adresse *
            </label>
            <textarea
              required
              value={formData.adresse}
              onChange={(e) => setFormData({ ...formData, adresse: e.target.value })}
              className="input"
              rows={2}
              placeholder="Ex: 12 rue des Lilas, 69003 Lyon"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Couleur
            </label>
            <div className="flex flex-wrap gap-2">
              {USER_COLORS.map((color) => (
                <button
                  key={color.code}
                  type="button"
                  onClick={() => setFormData({ ...formData, couleur: color.code })}
                  className={`w-8 h-8 rounded-full border-2 transition-all ${
                    formData.couleur === color.code
                      ? 'border-gray-900 scale-110'
                      : 'border-transparent'
                  }`}
                  style={{ backgroundColor: color.code }}
                  title={color.name}
                />
              ))}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Contact nom
              </label>
              <input
                type="text"
                value={formData.contact_nom || ''}
                onChange={(e) => setFormData({ ...formData, contact_nom: e.target.value })}
                className="input"
                placeholder="Nom du contact"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Contact telephone
              </label>
              <input
                type="tel"
                value={formData.contact_telephone || ''}
                onChange={(e) => setFormData({ ...formData, contact_telephone: e.target.value })}
                className="input"
                placeholder="06 12 34 56 78"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Date debut prevue
              </label>
              <input
                type="date"
                value={formData.date_debut_prevue || ''}
                onChange={(e) => {
                  setFormData({ ...formData, date_debut_prevue: e.target.value })
                  setError(null)
                }}
                className="input"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Date fin prevue
              </label>
              <input
                type="date"
                value={formData.date_fin_prevue || ''}
                onChange={(e) => {
                  setFormData({ ...formData, date_fin_prevue: e.target.value })
                  setError(null)
                }}
                className="input"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Heures estimees
            </label>
            <input
              type="number"
              value={formData.heures_estimees || ''}
              onChange={(e) =>
                setFormData({ ...formData, heures_estimees: parseInt(e.target.value) || undefined })
              }
              className="input"
              placeholder="Ex: 500"
              min={0}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              value={formData.description || ''}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="input"
              rows={3}
              placeholder="Description du chantier..."
            />
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 btn btn-outline"
            >
              Annuler
            </button>
            <button
              type="submit"
              disabled={isSubmitting || !formData.nom || !formData.adresse}
              className="flex-1 btn btn-primary flex items-center justify-center gap-2"
            >
              {isSubmitting && <Loader2 className="w-4 h-4 animate-spin" />}
              Creer
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
