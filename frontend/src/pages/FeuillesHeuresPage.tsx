import { useState, useEffect, useCallback, useMemo } from 'react'
import { format, startOfWeek, addDays } from 'date-fns'
import { Filter, Users, Building2 } from 'lucide-react'
import Layout from '../components/Layout'
import {
  TimesheetWeekNavigation,
  TimesheetGrid,
  TimesheetChantierGrid,
  PointageModal,
} from '../components/pointages'
import { pointagesService } from '../services/pointages'
import { usersService } from '../services/users'
import { chantiersService } from '../services/chantiers'
import { useAuth } from '../contexts/AuthContext'
import type {
  Pointage,
  PointageCreate,
  PointageUpdate,
  User,
  Chantier,
  VueCompagnon,
  VueChantier,
} from '../types'

type ViewTab = 'compagnons' | 'chantiers'

export default function FeuillesHeuresPage() {
  const { user: currentUser } = useAuth()
  const canEdit =
    currentUser?.role === 'administrateur' ||
    currentUser?.role === 'conducteur' ||
    currentUser?.role === 'chef_chantier'
  const isValidateur =
    currentUser?.role === 'administrateur' || currentUser?.role === 'conducteur'

  // Etat principal
  const [currentDate, setCurrentDate] = useState(new Date())
  const [viewTab, setViewTab] = useState<ViewTab>('compagnons')

  // Donnees
  const [vueCompagnons, setVueCompagnons] = useState<VueCompagnon[]>([])
  const [vueChantiers, setVueChantiers] = useState<VueChantier[]>([])
  const [utilisateurs, setUtilisateurs] = useState<User[]>([])
  const [chantiers, setChantiers] = useState<Chantier[]>([])

  // UI
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [isExporting, setIsExporting] = useState(false)

  // Modal
  const [modalOpen, setModalOpen] = useState(false)
  const [editingPointage, setEditingPointage] = useState<Pointage | null>(null)
  const [selectedDate, setSelectedDate] = useState<Date | undefined>()
  const [selectedUserId, setSelectedUserId] = useState<number | undefined>()
  const [selectedChantierId, setSelectedChantierId] = useState<number | undefined>()

  // Filtres
  const [showFilters, setShowFilters] = useState(false)
  const [filterUtilisateurs, setFilterUtilisateurs] = useState<number[]>([])
  const [filterChantiers, setFilterChantiers] = useState<number[]>([])
  const [showWeekend, setShowWeekend] = useState(() => {
    const saved = localStorage.getItem('timesheet-show-weekend')
    return saved !== null ? saved === 'true' : false
  })

  // Calculer la date de debut de semaine (lundi)
  const semaineDebut = useMemo(() => {
    const monday = startOfWeek(currentDate, { weekStartsOn: 1 })
    return format(monday, 'yyyy-MM-dd')
  }, [currentDate])

  // Charger les donnees
  const loadData = useCallback(async () => {
    setLoading(true)
    setError('')

    try {
      // Charger en parallele
      const [usersData, chantiersData] = await Promise.all([
        usersService.list({ size: 100 }),
        chantiersService.list({ size: 100 }),
      ])

      setUtilisateurs(usersData.items.filter((u) => u.is_active))
      setChantiers(chantiersData.items.filter((c) => c.statut !== 'ferme'))

      // Charger les vues selon l'onglet actif
      const utilisateurIds =
        filterUtilisateurs.length > 0
          ? filterUtilisateurs
          : usersData.items.filter((u) => u.is_active).map((u) => Number(u.id))
      const chantierIds =
        filterChantiers.length > 0
          ? filterChantiers
          : chantiersData.items.filter((c) => c.statut !== 'ferme').map((c) => Number(c.id))

      if (viewTab === 'compagnons') {
        const vueData = await pointagesService.getVueCompagnons(semaineDebut, utilisateurIds)
        setVueCompagnons(vueData)
      } else {
        const vueData = await pointagesService.getVueChantiers(semaineDebut, chantierIds)
        setVueChantiers(vueData)
      }
    } catch (err) {
      console.error('Erreur chargement feuilles heures:', err)
      setError('Erreur lors du chargement des donnees')
    } finally {
      setLoading(false)
    }
  }, [semaineDebut, viewTab, filterUtilisateurs, filterChantiers])

  useEffect(() => {
    loadData()
  }, [loadData])

  // Persist weekend toggle
  useEffect(() => {
    localStorage.setItem('timesheet-show-weekend', String(showWeekend))
  }, [showWeekend])

  // Handlers (memoized pour performance)
  const handleCellClick = useCallback((utilisateurId: number, chantierId: number | null, date: Date) => {
    if (!canEdit) return
    setSelectedUserId(utilisateurId)
    setSelectedChantierId(chantierId || undefined)
    setSelectedDate(date)
    setEditingPointage(null)
    setModalOpen(true)
  }, [canEdit])

  const handleChantierCellClick = useCallback((chantierId: number, date: Date) => {
    if (!canEdit) return
    setSelectedChantierId(chantierId)
    setSelectedDate(date)
    setSelectedUserId(undefined)
    setEditingPointage(null)
    setModalOpen(true)
  }, [canEdit])

  const handlePointageClick = useCallback((pointage: Pointage) => {
    setEditingPointage(pointage)
    setSelectedDate(undefined)
    setSelectedUserId(undefined)
    setSelectedChantierId(undefined)
    setModalOpen(true)
  }, [])

  const handleSavePointage = async (data: PointageCreate | PointageUpdate) => {
    if (!currentUser) return

    if (editingPointage) {
      await pointagesService.update(editingPointage.id, data as PointageUpdate, Number(currentUser.id))
    } else {
      await pointagesService.create(data as PointageCreate, Number(currentUser.id))
    }
    await loadData()
  }

  const handleDeletePointage = async () => {
    if (!editingPointage || !currentUser) return
    await pointagesService.delete(editingPointage.id, Number(currentUser.id))
    await loadData()
  }

  const handleSignPointage = async (signature: string) => {
    if (!editingPointage) return
    await pointagesService.sign(editingPointage.id, signature)
    await loadData()
  }

  const handleSubmitPointage = async () => {
    if (!editingPointage) return
    await pointagesService.submit(editingPointage.id)
    await loadData()
  }

  const handleValidatePointage = async () => {
    if (!editingPointage || !currentUser) return
    await pointagesService.validate(editingPointage.id, Number(currentUser.id))
    await loadData()
  }

  const handleRejectPointage = async (motif: string) => {
    if (!editingPointage || !currentUser) return
    await pointagesService.reject(editingPointage.id, motif, Number(currentUser.id))
    await loadData()
  }

  const handleExport = async () => {
    if (!currentUser) return

    setIsExporting(true)
    try {
      const weekEnd = addDays(new Date(semaineDebut), 6)

      const blob = await pointagesService.export(
        {
          format_export: 'xlsx',
          date_debut: semaineDebut,
          date_fin: format(weekEnd, 'yyyy-MM-dd'),
          utilisateur_ids: filterUtilisateurs.length > 0 ? filterUtilisateurs : undefined,
          chantier_ids: filterChantiers.length > 0 ? filterChantiers : undefined,
          inclure_variables_paie: true,
          inclure_signatures: true,
        },
        Number(currentUser.id)
      )

      // Telecharger le fichier
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `feuilles-heures-semaine-${semaineDebut}.xlsx`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (err) {
      console.error('Erreur export:', err)
      setError('Erreur lors de l\'export')
    } finally {
      setIsExporting(false)
    }
  }

  const handleFilterUtilisateur = (userId: number) => {
    setFilterUtilisateurs((prev) =>
      prev.includes(userId) ? prev.filter((id) => id !== userId) : [...prev, userId]
    )
  }

  const handleFilterChantier = (chantierId: number) => {
    setFilterChantiers((prev) =>
      prev.includes(chantierId) ? prev.filter((id) => id !== chantierId) : [...prev, chantierId]
    )
  }

  return (
    <Layout>
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Feuilles d'heures</h1>
            <p className="text-gray-600">Saisie et validation des heures travaillees</p>
          </div>
        </div>

        {/* Onglets de vue (FDH-01) */}
        <div className="flex items-center gap-4">
          <div className="flex rounded-lg bg-gray-100 p-1">
            <button
              onClick={() => setViewTab('compagnons')}
              className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                viewTab === 'compagnons'
                  ? 'bg-white text-gray-900 shadow'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Users className="w-4 h-4" />
              Compagnons
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

          {/* Bouton filtres (FDH-04) */}
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
              showFilters || filterUtilisateurs.length > 0 || filterChantiers.length > 0
                ? 'bg-primary-100 text-primary-700'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            <Filter className="w-4 h-4" />
            Filtres
            {(filterUtilisateurs.length > 0 || filterChantiers.length > 0) && (
              <span className="bg-primary-600 text-white text-xs px-1.5 py-0.5 rounded-full">
                {filterUtilisateurs.length + filterChantiers.length}
              </span>
            )}
          </button>

          {/* Toggle weekend */}
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

        {/* Filtres depliables (FDH-04) */}
        {showFilters && (
          <div className="bg-white rounded-lg shadow p-4 space-y-4">
            {/* Filtre utilisateurs */}
            <div>
              <span className="text-sm font-medium text-gray-700 mr-2">Utilisateurs :</span>
              <div className="flex flex-wrap gap-2 mt-2">
                {utilisateurs.map((user) => (
                  <button
                    key={user.id}
                    onClick={() => handleFilterUtilisateur(Number(user.id))}
                    aria-label={`Filtrer par ${user.prenom} ${user.nom}`}
                    aria-pressed={filterUtilisateurs.includes(Number(user.id))}
                    className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                      filterUtilisateurs.includes(Number(user.id))
                        ? 'bg-primary-600 text-white'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    {user.prenom} {user.nom}
                  </button>
                ))}
                {filterUtilisateurs.length > 0 && (
                  <button
                    onClick={() => setFilterUtilisateurs([])}
                    className="text-xs text-gray-500 hover:text-gray-700 ml-2"
                  >
                    Effacer
                  </button>
                )}
              </div>
            </div>

            {/* Filtre chantiers */}
            <div>
              <span className="text-sm font-medium text-gray-700 mr-2">Chantiers :</span>
              <div className="flex flex-wrap gap-2 mt-2">
                {chantiers.map((chantier) => (
                  <button
                    key={chantier.id}
                    onClick={() => handleFilterChantier(Number(chantier.id))}
                    aria-label={`Filtrer par chantier ${chantier.nom}`}
                    aria-pressed={filterChantiers.includes(Number(chantier.id))}
                    className={`flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                      filterChantiers.includes(Number(chantier.id))
                        ? 'text-white'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                    style={
                      filterChantiers.includes(Number(chantier.id))
                        ? { backgroundColor: chantier.couleur || '#3498DB' }
                        : undefined
                    }
                  >
                    <span
                      className="w-2 h-2 rounded-full"
                      style={{ backgroundColor: chantier.couleur || '#9E9E9E' }}
                    />
                    {chantier.nom}
                  </button>
                ))}
                {filterChantiers.length > 0 && (
                  <button
                    onClick={() => setFilterChantiers([])}
                    className="text-xs text-gray-500 hover:text-gray-700 ml-2"
                  >
                    Effacer
                  </button>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Navigation semaine (FDH-02) */}
        <TimesheetWeekNavigation
          currentDate={currentDate}
          onDateChange={setCurrentDate}
          onExport={handleExport}
          isExporting={isExporting}
        />

        {/* Erreur */}
        {error && (
          <div className="bg-red-50 text-red-700 p-4 rounded-lg">{error}</div>
        )}

        {/* Grille */}
        {loading ? (
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <div className="animate-spin w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full mx-auto" />
            <p className="mt-4 text-gray-600">Chargement des feuilles d'heures...</p>
          </div>
        ) : viewTab === 'compagnons' ? (
          <TimesheetGrid
            currentDate={currentDate}
            vueCompagnons={vueCompagnons}
            onCellClick={handleCellClick}
            onPointageClick={handlePointageClick}
            showWeekend={showWeekend}
            canEdit={canEdit}
          />
        ) : (
          <TimesheetChantierGrid
            currentDate={currentDate}
            vueChantiers={vueChantiers}
            onCellClick={handleChantierCellClick}
            onPointageClick={handlePointageClick}
            showWeekend={showWeekend}
            canEdit={canEdit}
          />
        )}

        {/* Modal creation/edition */}
        <PointageModal
          isOpen={modalOpen}
          onClose={() => setModalOpen(false)}
          onSave={handleSavePointage}
          onDelete={editingPointage ? handleDeletePointage : undefined}
          onSign={editingPointage ? handleSignPointage : undefined}
          onSubmit={editingPointage ? handleSubmitPointage : undefined}
          onValidate={isValidateur && editingPointage ? handleValidatePointage : undefined}
          onReject={isValidateur && editingPointage ? handleRejectPointage : undefined}
          pointage={editingPointage}
          chantiers={chantiers}
          selectedDate={selectedDate}
          selectedUserId={selectedUserId}
          selectedChantierId={selectedChantierId}
          isValidateur={isValidateur}
        />
      </div>
    </Layout>
  )
}
