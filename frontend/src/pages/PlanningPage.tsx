import React, { useState, useEffect, useCallback } from 'react'
import { Plus, Filter, Users, Building2, Wrench, ChevronDown, ChevronRight, Copy, Search } from 'lucide-react'
import {
  format,
  startOfWeek,
  endOfWeek,
  addWeeks,
  subWeeks,
  eachDayOfInterval,
  isSameDay,
  addDays,
} from 'date-fns'
import { fr } from 'date-fns/locale'
import Layout from '../components/Layout'
import { WeekNavigation } from '../components/planning/WeekNavigation'
import { UserRow } from '../components/planning/UserRow'
import { AffectationForm } from '../components/planning/AffectationForm'
import { planningService } from '../services/planning'
import { usersService } from '../services/users'
import { chantiersService } from '../services/chantiers'
import type { User, Chantier, Affectation, AffectationCreate, AffectationUpdate, Metier } from '../types'
import { METIERS } from '../types'

type ViewTab = 'utilisateurs' | 'chantiers' | 'interventions'
type UserFilter = 'tous' | 'planifies' | 'non_planifies'

/**
 * Page Planning Opérationnel (CDC Section 5 - PLN-01 à PLN-28).
 */
export default function PlanningPage() {
  // État de la vue
  const [activeTab, setActiveTab] = useState<ViewTab>('utilisateurs')
  const [currentDate, setCurrentDate] = useState(new Date())
  const [userFilter, setUserFilter] = useState<UserFilter>('tous')
  const [searchQuery, setSearchQuery] = useState('')
  const [collapsedGroups, setCollapsedGroups] = useState<Set<string>>(new Set())

  // Données
  const [users, setUsers] = useState<User[]>([])
  const [chantiers, setChantiers] = useState<Chantier[]>([])
  const [affectations, setAffectations] = useState<Affectation[]>([])
  const [utilisateursNonPlanifies, setUtilisateursNonPlanifies] = useState<number[]>([])
  const [isLoading, setIsLoading] = useState(true)

  // Modal
  const [isFormOpen, setIsFormOpen] = useState(false)
  const [selectedAffectation, setSelectedAffectation] = useState<Affectation | null>(null)
  const [preselectedUser, setPreselectedUser] = useState<User | null>(null)
  const [preselectedDate, setPreselectedDate] = useState<Date | null>(null)
  const [isDuplicateModalOpen, setIsDuplicateModalOpen] = useState(false)
  const [duplicateUserId, setDuplicateUserId] = useState<string>('')

  // Drag & Drop
  const [draggedAffectation, setDraggedAffectation] = useState<Affectation | null>(null)

  // Calculs de dates
  const weekStart = startOfWeek(currentDate, { weekStartsOn: 1 })
  const weekEnd = endOfWeek(currentDate, { weekStartsOn: 1 })
  const weekDays = eachDayOfInterval({ start: weekStart, end: weekEnd })

  // Chargement des données
  const loadData = useCallback(async () => {
    setIsLoading(true)
    try {
      const dateDebut = format(weekStart, 'yyyy-MM-dd')
      const dateFin = format(weekEnd, 'yyyy-MM-dd')

      const [usersRes, chantiersRes, affectationsRes] = await Promise.all([
        usersService.list({ size: 500 }),
        chantiersService.list({ size: 500 }),
        planningService.list({ date_debut: dateDebut, date_fin: dateFin, limit: 1000 }),
      ])

      setUsers(usersRes.items)
      setChantiers(chantiersRes.items)
      setAffectations(affectationsRes.affectations)

      // Charger les utilisateurs non planifiés pour aujourd'hui
      try {
        const nonPlanifies = await planningService.getUtilisateursNonPlanifies(format(new Date(), 'yyyy-MM-dd'))
        setUtilisateursNonPlanifies(nonPlanifies)
      } catch {
        setUtilisateursNonPlanifies([])
      }
    } catch (error) {
      console.error('Erreur chargement planning:', error)
    } finally {
      setIsLoading(false)
    }
  }, [weekStart, weekEnd])

  useEffect(() => {
    loadData()
  }, [loadData])

  // Navigation temporelle
  const handlePrevWeek = () => setCurrentDate((d) => subWeeks(d, 1))
  const handleNextWeek = () => setCurrentDate((d) => addWeeks(d, 1))
  const handleToday = () => setCurrentDate(new Date())

  // Grouper les utilisateurs par métier (PLN-12, PLN-13)
  const groupedUsers = users.reduce(
    (groups, user) => {
      if (!user.is_active) return groups
      const metier = user.metier || 'autre'
      if (!groups[metier]) groups[metier] = []
      groups[metier].push(user)
      return groups
    },
    {} as Record<string, User[]>
  )

  // Filtrer les utilisateurs (PLN-04, PLN-22)
  const filterUsers = (userList: User[]) => {
    let filtered = userList

    // Filtre recherche
    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(
        (u) =>
          u.nom.toLowerCase().includes(query) ||
          u.prenom.toLowerCase().includes(query) ||
          u.email.toLowerCase().includes(query)
      )
    }

    // Filtre planifiés/non planifiés
    if (userFilter === 'planifies') {
      const userIdsWithAffectation = new Set(affectations.map((a) => a.utilisateur_id))
      filtered = filtered.filter((u) => userIdsWithAffectation.has(parseInt(u.id)))
    } else if (userFilter === 'non_planifies') {
      const userIdsWithAffectation = new Set(affectations.map((a) => a.utilisateur_id))
      filtered = filtered.filter((u) => !userIdsWithAffectation.has(parseInt(u.id)))
    }

    return filtered
  }

  // Map des chantiers par ID
  const chantiersMap = new Map(chantiers.map((c) => [parseInt(c.id), c]))

  // Gestion du modal
  const handleCreateClick = () => {
    setSelectedAffectation(null)
    setPreselectedUser(null)
    setPreselectedDate(null)
    setIsFormOpen(true)
  }

  const handleCellClick = (user: User, date: Date) => {
    setSelectedAffectation(null)
    setPreselectedUser(user)
    setPreselectedDate(date)
    setIsFormOpen(true)
  }

  const handleAffectationClick = (affectation: Affectation) => {
    setSelectedAffectation(affectation)
    setPreselectedUser(null)
    setPreselectedDate(null)
    setIsFormOpen(true)
  }

  // CRUD
  const handleSubmit = async (data: AffectationCreate | AffectationUpdate) => {
    if (selectedAffectation) {
      await planningService.update(selectedAffectation.id, data as AffectationUpdate)
    } else {
      await planningService.create(data as AffectationCreate)
    }
    await loadData()
  }

  const handleDelete = async () => {
    if (selectedAffectation) {
      await planningService.delete(selectedAffectation.id)
      await loadData()
    }
  }

  // Drag & Drop (PLN-27)
  const handleDragStart = (affectation: Affectation) => {
    setDraggedAffectation(affectation)
  }

  const handleDrop = async (date: Date, userId: number) => {
    if (!draggedAffectation) return

    try {
      await planningService.deplacer(draggedAffectation.id, {
        nouvelle_date: format(date, 'yyyy-MM-dd'),
        // Si on déplace vers un autre utilisateur, on garde le même chantier
      })
      await loadData()
    } catch (error) {
      console.error('Erreur déplacement:', error)
    } finally {
      setDraggedAffectation(null)
    }
  }

  // Duplication semaine (PLN-16)
  const handleOpenDuplicateModal = () => {
    setDuplicateUserId('')
    setIsDuplicateModalOpen(true)
  }

  const handleConfirmDuplicate = async () => {
    if (!duplicateUserId) return

    try {
      await planningService.dupliquer({
        utilisateur_id: parseInt(duplicateUserId),
        date_source_debut: format(weekStart, 'yyyy-MM-dd'),
        date_source_fin: format(weekEnd, 'yyyy-MM-dd'),
        date_cible_debut: format(addDays(weekEnd, 1), 'yyyy-MM-dd'),
      })
      setIsDuplicateModalOpen(false)
      handleNextWeek()
      await loadData()
    } catch (error) {
      console.error('Erreur duplication:', error)
    }
  }

  // Toggle groupe (PLN-14)
  const toggleGroup = (metier: string) => {
    setCollapsedGroups((prev) => {
      const next = new Set(prev)
      if (next.has(metier)) {
        next.delete(metier)
      } else {
        next.add(metier)
      }
      return next
    })
  }

  return (
    <Layout>
      <div className="h-full flex flex-col">
        {/* Header */}
        <div className="bg-white border-b px-4 py-3">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-xl font-semibold">Planning Opérationnel</h1>
            <button onClick={handleCreateClick} className="btn btn-primary flex items-center gap-2">
              <Plus className="w-4 h-4" />
              Créer
            </button>
          </div>

          {/* Onglets (PLN-01) */}
          <div className="flex items-center gap-6 mb-4">
            <div className="flex border-b">
              <button
                onClick={() => setActiveTab('chantiers')}
                className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === 'chantiers'
                    ? 'border-primary text-primary'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <Building2 className="w-4 h-4 inline mr-2" />
                Chantiers
              </button>
              <button
                onClick={() => setActiveTab('utilisateurs')}
                className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === 'utilisateurs'
                    ? 'border-primary text-primary'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <Users className="w-4 h-4 inline mr-2" />
                Utilisateurs
              </button>
              <button
                onClick={() => setActiveTab('interventions')}
                className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === 'interventions'
                    ? 'border-primary text-primary'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <Wrench className="w-4 h-4 inline mr-2" />
                Interventions
              </button>
            </div>
          </div>

          {/* Filtres et navigation */}
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center gap-3">
              {/* Filtre utilisateurs (PLN-04) */}
              <select
                value={userFilter}
                onChange={(e) => setUserFilter(e.target.value as UserFilter)}
                className="input py-1.5 text-sm"
              >
                <option value="tous">Tous les utilisateurs</option>
                <option value="planifies">Planifiés</option>
                <option value="non_planifies">Non planifiés ({utilisateursNonPlanifies.length})</option>
              </select>

              {/* Recherche (PLN-22) */}
              <div className="relative">
                <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Rechercher..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="input py-1.5 pl-9 text-sm w-48"
                />
              </div>

              {/* Duplication (PLN-16) */}
              <button
                onClick={handleOpenDuplicateModal}
                className="btn btn-outline py-1.5 text-sm flex items-center gap-1"
                title="Dupliquer la semaine"
              >
                <Copy className="w-4 h-4" />
              </button>
            </div>

            {/* Navigation semaine (PLN-09, PLN-10) */}
            <WeekNavigation
              currentDate={currentDate}
              onPrevWeek={handlePrevWeek}
              onNextWeek={handleNextWeek}
              onToday={handleToday}
            />
          </div>
        </div>

        {/* Grille calendrier */}
        <div className="flex-1 overflow-auto bg-gray-50 p-4">
          {isLoading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
            </div>
          ) : activeTab === 'utilisateurs' ? (
            <div className="bg-white rounded-lg shadow overflow-hidden">
              <table className="w-full">
                <thead>
                  <tr className="bg-gray-50 border-b">
                    <th className="p-2 text-left text-sm font-medium text-gray-600 sticky left-0 bg-gray-50 z-20 min-w-[200px]">
                      Utilisateur
                    </th>
                    {weekDays.map((day) => (
                      <th
                        key={day.toISOString()}
                        className={`p-2 text-center text-sm font-medium min-w-[120px] ${
                          isSameDay(day, new Date()) ? 'bg-blue-50 text-blue-600' : 'text-gray-600'
                        }`}
                      >
                        <div>{format(day, 'EEEE', { locale: fr })}</div>
                        <div className="text-xs">{format(day, 'd MMM', { locale: fr })}</div>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(groupedUsers).map(([metier, metierUsers]) => {
                    const filteredUsers = filterUsers(metierUsers)
                    if (filteredUsers.length === 0) return null

                    const metierInfo = METIERS[metier as Metier] || { label: metier, color: '#607D8B' }
                    const isCollapsed = collapsedGroups.has(metier)

                    return (
                      <React.Fragment key={metier}>
                        {/* Header groupe métier (PLN-12, PLN-13, PLN-14) */}
                        <tr
                          className="bg-gray-100 cursor-pointer hover:bg-gray-200"
                          onClick={() => toggleGroup(metier)}
                        >
                          <td colSpan={8} className="p-2">
                            <div className="flex items-center gap-2">
                              {isCollapsed ? (
                                <ChevronRight className="w-4 h-4" />
                              ) : (
                                <ChevronDown className="w-4 h-4" />
                              )}
                              <span
                                className="px-2 py-0.5 rounded text-white text-xs font-medium"
                                style={{ backgroundColor: metierInfo.color }}
                              >
                                {metierInfo.label}
                              </span>
                              <span className="text-sm text-gray-500">({filteredUsers.length})</span>
                            </div>
                          </td>
                        </tr>

                        {/* Lignes utilisateurs */}
                        {!isCollapsed &&
                          filteredUsers.map((user) => (
                            <UserRow
                              key={user.id}
                              user={user}
                              weekDays={weekDays}
                              affectations={affectations.filter((a) => a.utilisateur_id === parseInt(user.id))}
                              chantiers={chantiersMap}
                              onAffectationClick={handleAffectationClick}
                              onCellClick={handleCellClick}
                              onDragStart={handleDragStart}
                              onDrop={handleDrop}
                            />
                          ))}
                      </React.Fragment>
                    )
                  })}
                </tbody>
              </table>
            </div>
          ) : activeTab === 'chantiers' ? (
            <div className="text-center py-12 text-gray-500">
              Vue Chantiers - En développement
            </div>
          ) : (
            <div className="text-center py-12 text-gray-500">
              Vue Interventions - En développement
            </div>
          )}
        </div>

        {/* Modal création/édition */}
        <AffectationForm
          isOpen={isFormOpen}
          onClose={() => setIsFormOpen(false)}
          onSubmit={handleSubmit}
          onDelete={selectedAffectation ? handleDelete : undefined}
          affectation={selectedAffectation}
          preselectedUser={preselectedUser}
          preselectedDate={preselectedDate}
          users={users}
          chantiers={chantiers}
        />

        {/* Modal duplication semaine (PLN-16) */}
        {isDuplicateModalOpen && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl w-full max-w-md p-6">
              <h3 className="text-lg font-semibold mb-4">Dupliquer la semaine</h3>
              <p className="text-sm text-gray-600 mb-4">
                Sélectionnez un utilisateur pour dupliquer ses affectations de cette semaine vers la semaine suivante.
              </p>
              <select
                value={duplicateUserId}
                onChange={(e) => setDuplicateUserId(e.target.value)}
                className="input w-full mb-4"
              >
                <option value="">Sélectionner un utilisateur</option>
                {users.filter(u => u.is_active).map((user) => (
                  <option key={user.id} value={user.id}>
                    {user.prenom} {user.nom}
                  </option>
                ))}
              </select>
              <div className="flex justify-end gap-2">
                <button
                  onClick={() => setIsDuplicateModalOpen(false)}
                  className="btn btn-outline"
                >
                  Annuler
                </button>
                <button
                  onClick={handleConfirmDuplicate}
                  disabled={!duplicateUserId}
                  className="btn btn-primary disabled:opacity-50"
                >
                  Dupliquer
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  )
}
