import { useState, useEffect, useCallback, useMemo } from 'react'
import { format, startOfWeek, endOfWeek, startOfMonth, endOfMonth, addWeeks } from 'date-fns'
import { Plus, Filter, Users, Building2, AlertCircle } from 'lucide-react'
import Layout from '../components/Layout'
import { PlanningGrid, PlanningChantierGrid, WeekNavigation, AffectationModal } from '../components/planning'
import { planningService } from '../services/planning'
import { usersService } from '../services/users'
import { chantiersService } from '../services/chantiers'
import { useAuth } from '../contexts/AuthContext'
import type { Affectation, AffectationCreate, AffectationUpdate, User, Chantier } from '../types'
import { METIERS } from '../types'

type ViewTab = 'utilisateurs' | 'chantiers'

export default function PlanningPage() {
  const { user: currentUser } = useAuth()
  const canEdit = currentUser?.role === 'admin' || currentUser?.role === 'conducteur'

  // État principal
  const [currentDate, setCurrentDate] = useState(new Date())
  const [viewMode, setViewMode] = useState<'semaine' | 'mois'>('semaine')
  const [viewTab, setViewTab] = useState<ViewTab>('utilisateurs')

  // Données
  const [affectations, setAffectations] = useState<Affectation[]>([])
  const [utilisateurs, setUtilisateurs] = useState<User[]>([])
  const [chantiers, setChantiers] = useState<Chantier[]>([])
  const [nonPlanifiesCount, setNonPlanifiesCount] = useState(0)

  // UI
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [expandedMetiers, setExpandedMetiers] = useState<string[]>(Object.keys(METIERS))

  // Modal
  const [modalOpen, setModalOpen] = useState(false)
  const [editingAffectation, setEditingAffectation] = useState<Affectation | null>(null)
  const [selectedDate, setSelectedDate] = useState<Date | undefined>()
  const [selectedUserId, setSelectedUserId] = useState<string | undefined>()
  const [selectedChantierId, setSelectedChantierId] = useState<string | undefined>()

  // Filtres
  const [showFilters, setShowFilters] = useState(false)
  const [filterMetiers, setFilterMetiers] = useState<string[]>([])
  const [filterChantier, setFilterChantier] = useState<string>('') // PLN-05
  const [showNonPlanifiesOnly, setShowNonPlanifiesOnly] = useState(false)
  const [showWeekend, setShowWeekend] = useState(() => {
    // PLN-06: Persist in localStorage
    const saved = localStorage.getItem('planning-show-weekend')
    return saved !== null ? saved === 'true' : true
  })

  // Calculer les dates de début et fin de la période
  const getDateRange = useCallback(() => {
    let start: Date
    let end: Date

    if (viewMode === 'mois') {
      start = startOfMonth(currentDate)
      end = endOfMonth(currentDate)
    } else {
      start = startOfWeek(currentDate, { weekStartsOn: 1 })
      end = endOfWeek(currentDate, { weekStartsOn: 1 })
    }

    return {
      date_debut: format(start, 'yyyy-MM-dd'),
      date_fin: format(end, 'yyyy-MM-dd'),
    }
  }, [currentDate, viewMode])

  // Charger les données
  const loadData = useCallback(async () => {
    setLoading(true)
    setError('')

    try {
      const { date_debut, date_fin } = getDateRange()

      // Charger en parallèle
      const [affectationsData, usersData, chantiersData, nonPlanifiesData] = await Promise.all([
        planningService.getAffectations({ date_debut, date_fin }),
        usersService.list({ size: 100 }),
        chantiersService.list({ size: 100 }),
        planningService.getNonPlanifies(date_debut, date_fin),
      ])

      setAffectations(affectationsData)
      setUtilisateurs(usersData.items.filter(u => u.is_active))
      setChantiers(chantiersData.items.filter(c => c.statut !== 'ferme'))
      setNonPlanifiesCount(nonPlanifiesData.count)
    } catch (err) {
      console.error('Erreur chargement planning:', err)
      setError('Erreur lors du chargement du planning')
    } finally {
      setLoading(false)
    }
  }, [getDateRange])

  useEffect(() => {
    loadData()
  }, [loadData])

  // PLN-06: Persist weekend toggle
  useEffect(() => {
    localStorage.setItem('planning-show-weekend', String(showWeekend))
  }, [showWeekend])

  // PLN-05: Filter affectations by chantier
  const filteredAffectations = useMemo(() => {
    if (!filterChantier) return affectations
    return affectations.filter(a => String(a.chantier_id) === filterChantier)
  }, [affectations, filterChantier])

  // Filtrer les utilisateurs (memoized pour performance)
  const filteredUtilisateurs = useMemo(() => utilisateurs.filter(user => {
    // Filtre par métier
    if (filterMetiers.length > 0 && !filterMetiers.includes(user.metier || 'autre')) {
      return false
    }

    // PLN-05: Filtre par chantier - montrer seulement les utilisateurs affectés à ce chantier
    if (filterChantier) {
      const hasAffectationForChantier = affectations.some(
        a => String(a.chantier_id) === filterChantier && a.utilisateur_id === user.id
      )
      if (!hasAffectationForChantier) return false
    }

    // Filtre non planifiés uniquement
    if (showNonPlanifiesOnly) {
      const hasAffectation = affectations.some(a => a.utilisateur_id === user.id)
      if (hasAffectation) return false
    }

    return true
  }), [utilisateurs, filterMetiers, filterChantier, showNonPlanifiesOnly, affectations])

  // Handlers
  const handleCellClick = (userId: string, date: Date) => {
    if (!canEdit) return
    setSelectedUserId(userId)
    setSelectedDate(date)
    setEditingAffectation(null)
    setModalOpen(true)
  }

  const handleAffectationClick = (affectation: Affectation) => {
    if (!canEdit) return
    setEditingAffectation(affectation)
    setSelectedDate(undefined)
    setSelectedUserId(undefined)
    setModalOpen(true)
  }

  const handleAffectationDelete = async (affectation: Affectation) => {
    if (!canEdit) return
    if (!confirm('Supprimer cette affectation ?')) return

    try {
      await planningService.delete(affectation.id)
      await loadData()
    } catch (err) {
      console.error('Erreur suppression:', err)
      setError('Erreur lors de la suppression')
    }
  }

  const handleSaveAffectation = async (data: AffectationCreate | AffectationUpdate) => {
    if (editingAffectation) {
      await planningService.update(editingAffectation.id, data as AffectationUpdate)
    } else {
      await planningService.create(data as AffectationCreate)
    }
    await loadData()
  }

  const handleDuplicate = async (userId: string) => {
    if (!canEdit) return
    const { date_debut: source_date_debut, date_fin: source_date_fin } = getDateRange()
    const nextWeekStart = addWeeks(startOfWeek(currentDate, { weekStartsOn: 1 }), 1)

    if (!confirm(`Dupliquer les affectations de cette semaine vers la semaine prochaine ?`)) {
      return
    }

    try {
      await planningService.duplicate({
        utilisateur_id: userId,
        source_date_debut,
        source_date_fin,
        target_date_debut: format(nextWeekStart, 'yyyy-MM-dd'),
      })
      await loadData()
    } catch (err) {
      console.error('Erreur duplication:', err)
      setError('Erreur lors de la duplication')
    }
  }

  const handleToggleMetier = (metier: string) => {
    setExpandedMetiers(prev =>
      prev.includes(metier)
        ? prev.filter(m => m !== metier)
        : [...prev, metier]
    )
  }

  // PLN-27: Drag & drop - déplacer une affectation
  const handleAffectationMove = async (affectationId: string, newDate: string, newUserId?: string) => {
    if (!canEdit) return

    try {
      await planningService.move(affectationId, newDate, newUserId)
      await loadData()
    } catch (err) {
      console.error('Erreur déplacement:', err)
      setError('Erreur lors du déplacement de l\'affectation')
    }
  }

  // Vue Chantiers: Clic sur une cellule chantier/jour
  const handleChantierCellClick = (chantierId: string, date: Date) => {
    if (!canEdit) return
    setSelectedChantierId(chantierId)
    setSelectedDate(date)
    setSelectedUserId(undefined)
    setEditingAffectation(null)
    setModalOpen(true)
  }

  // Vue Chantiers: Dupliquer les affectations d'un chantier vers la semaine suivante
  const handleDuplicateChantier = async (chantierId: string) => {
    if (!canEdit) return
    const { date_debut: source_date_debut, date_fin: source_date_fin } = getDateRange()
    const nextWeekStart = addWeeks(startOfWeek(currentDate, { weekStartsOn: 1 }), 1)

    // Trouver tous les utilisateurs affectés à ce chantier cette semaine
    const usersOnChantier = [...new Set(
      affectations
        .filter(a => String(a.chantier_id) === chantierId)
        .map(a => a.utilisateur_id)
    )]

    if (usersOnChantier.length === 0) {
      setError('Aucune affectation à dupliquer pour ce chantier')
      return
    }

    if (!confirm(`Dupliquer ${usersOnChantier.length} affectation(s) de ce chantier vers la semaine prochaine ?`)) {
      return
    }

    try {
      // Dupliquer pour chaque utilisateur affecté
      await Promise.all(
        usersOnChantier.map(userId =>
          planningService.duplicate({
            utilisateur_id: userId,
            source_date_debut,
            source_date_fin,
            target_date_debut: format(nextWeekStart, 'yyyy-MM-dd'),
          })
        )
      )
      await loadData()
    } catch (err) {
      console.error('Erreur duplication chantier:', err)
      setError('Erreur lors de la duplication')
    }
  }

  return (
    <Layout>
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Planning</h1>
            <p className="text-gray-600">
              Gestion des affectations des équipes aux chantiers
            </p>
          </div>

          {canEdit && (
            <button
              onClick={() => {
                setEditingAffectation(null)
                setSelectedDate(undefined)
                setSelectedUserId(undefined)
                setModalOpen(true)
              }}
              className="btn btn-primary"
            >
              <Plus className="w-5 h-5 mr-2" />
              Créer une affectation
            </button>
          )}
        </div>

        {/* Onglets de vue */}
        <div className="flex items-center gap-4">
          <div className="flex rounded-lg bg-gray-100 p-1">
            <button
              onClick={() => setViewTab('utilisateurs')}
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
              onClick={() => setViewTab('chantiers')}
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
              onClick={() => setShowNonPlanifiesOnly(!showNonPlanifiesOnly)}
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

          {/* PLN-05: Filtre par chantier */}
          <select
            value={filterChantier}
            onChange={(e) => setFilterChantier(e.target.value)}
            className="px-3 py-2 rounded-lg text-sm border border-gray-200 bg-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
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
            onClick={() => setShowFilters(!showFilters)}
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

          {/* PLN-06: Toggle weekend */}
          <label className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm bg-gray-100 cursor-pointer hover:bg-gray-200 transition-colors">
            <input
              type="checkbox"
              checked={showWeekend}
              onChange={(e) => setShowWeekend(e.target.checked)}
              className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
            <span className="text-gray-700">Weekend</span>
          </label>
        </div>

        {/* Filtres (dépliable) */}
        {showFilters && (
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex flex-wrap gap-2">
              <span className="text-sm font-medium text-gray-700 mr-2">Métiers :</span>
              {Object.entries(METIERS).map(([key, { label, color }]) => (
                <button
                  key={key}
                  onClick={() => {
                    setFilterMetiers(prev =>
                      prev.includes(key)
                        ? prev.filter(m => m !== key)
                        : [...prev, key]
                    )
                  }}
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
                  onClick={() => setFilterMetiers([])}
                  className="text-xs text-gray-500 hover:text-gray-700 ml-2"
                >
                  Effacer
                </button>
              )}
            </div>
          </div>
        )}

        {/* Navigation semaine */}
        <WeekNavigation
          currentDate={currentDate}
          onDateChange={setCurrentDate}
          viewMode={viewMode}
          onViewModeChange={setViewMode}
        />

        {/* Erreur */}
        {error && (
          <div className="bg-red-50 text-red-700 p-4 rounded-lg">
            {error}
          </div>
        )}

        {/* Grille du planning */}
        {loading ? (
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <div className="animate-spin w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full mx-auto" />
            <p className="mt-4 text-gray-600">Chargement du planning...</p>
          </div>
        ) : viewTab === 'utilisateurs' ? (
          <PlanningGrid
            currentDate={currentDate}
            affectations={filteredAffectations}
            utilisateurs={filteredUtilisateurs}
            onAffectationClick={handleAffectationClick}
            onAffectationDelete={handleAffectationDelete}
            onCellClick={handleCellClick}
            onDuplicate={handleDuplicate}
            expandedMetiers={expandedMetiers}
            onToggleMetier={handleToggleMetier}
            showWeekend={showWeekend}
            viewMode={viewMode}
            onAffectationMove={canEdit ? handleAffectationMove : undefined}
          />
        ) : (
          <PlanningChantierGrid
            currentDate={currentDate}
            affectations={filteredAffectations}
            chantiers={chantiers}
            onAffectationClick={handleAffectationClick}
            onCellClick={handleChantierCellClick}
            onDuplicateChantier={handleDuplicateChantier}
            showWeekend={showWeekend}
            viewMode={viewMode}
            onAffectationMove={canEdit ? handleAffectationMove : undefined}
          />
        )}

        {/* Modal création/édition */}
        <AffectationModal
          isOpen={modalOpen}
          onClose={() => setModalOpen(false)}
          onSave={handleSaveAffectation}
          affectation={editingAffectation}
          utilisateurs={utilisateurs}
          chantiers={chantiers}
          selectedDate={selectedDate}
          selectedUserId={selectedUserId}
          selectedChantierId={selectedChantierId}
        />
      </div>
    </Layout>
  )
}
