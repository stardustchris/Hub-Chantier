import { useState, useEffect, useCallback, useMemo } from 'react'
import { format, startOfWeek, endOfWeek, startOfMonth, endOfMonth, addWeeks } from 'date-fns'
import { planningService } from '../services/planning'
import { usersService } from '../services/users'
import { chantiersService } from '../services/chantiers'
import { logger } from '../services/logger'
import { useAuth } from '../contexts/AuthContext'
import type { Affectation, AffectationCreate, AffectationUpdate, User, Chantier } from '../types'
import { PLANNING_CATEGORIES } from '../types'

export type ViewMode = 'semaine' | 'mois'
export type ViewTab = 'utilisateurs' | 'chantiers'

export function usePlanning() {
  const { user: currentUser } = useAuth()
  const canEdit = currentUser?.role === 'admin' || currentUser?.role === 'conducteur'

  // État principal
  const [currentDate, setCurrentDate] = useState(new Date())

  // Lire le mode depuis l'URL au démarrage
  const getInitialMode = (): ViewMode => {
    const params = new URLSearchParams(window.location.search)
    const mode = params.get('mode') as ViewMode | null
    return (mode && ['semaine', 'mois'].includes(mode)) ? mode : 'semaine'
  }
  const [viewMode, setViewMode] = useState<ViewMode>(getInitialMode())

  // Lire l'onglet depuis l'URL au démarrage
  const getInitialTab = (): ViewTab => {
    const params = new URLSearchParams(window.location.search)
    const tab = params.get('tab') as ViewTab | null
    return (tab && ['utilisateurs', 'chantiers'].includes(tab)) ? tab : 'utilisateurs'
  }
  const [viewTab, setViewTab] = useState<ViewTab>(getInitialTab())

  // Données
  const [affectations, setAffectations] = useState<Affectation[]>([])
  const [utilisateurs, setUtilisateurs] = useState<User[]>([])
  const [chantiers, setChantiers] = useState<Chantier[]>([])
  const [nonPlanifiesCount, setNonPlanifiesCount] = useState(0)

  // UI
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [expandedMetiers, setExpandedMetiers] = useState<string[]>(Object.keys(PLANNING_CATEGORIES))

  // Modal
  const [modalOpen, setModalOpen] = useState(false)
  const [editingAffectation, setEditingAffectation] = useState<Affectation | null>(null)
  const [selectedDate, setSelectedDate] = useState<Date | undefined>()
  const [selectedUserId, setSelectedUserId] = useState<string | undefined>()
  const [selectedChantierId, setSelectedChantierId] = useState<string | undefined>()

  // Filtres
  const [showFilters, setShowFilters] = useState(false)
  const [filterMetiers, setFilterMetiers] = useState<string[]>([])
  const [filterChantier, setFilterChantier] = useState<string>('')
  const [showNonPlanifiesOnly, setShowNonPlanifiesOnly] = useState(false)
  const [showWeekend, setShowWeekend] = useState(() => {
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
      // Effacer l'erreur explicitement apres succes (important pour les race conditions)
      setError('')
    } catch (err) {
      logger.error('Erreur chargement planning', err, { context: 'PlanningPage' })
      setError('Erreur lors du chargement du planning')
    } finally {
      setLoading(false)
    }
  }, [getDateRange])

  // Recharger uniquement les affectations (sans loader pour eviter le scroll reset)
  const reloadAffectations = useCallback(async () => {
    try {
      const { date_debut, date_fin } = getDateRange()
      const [affectationsData, nonPlanifiesData] = await Promise.all([
        planningService.getAffectations({ date_debut, date_fin }),
        planningService.getNonPlanifies(date_debut, date_fin),
      ])
      setAffectations(affectationsData)
      setNonPlanifiesCount(nonPlanifiesData.count)
    } catch (err) {
      logger.error('Erreur rechargement affectations', err, { context: 'PlanningPage' })
    }
  }, [getDateRange])

  // Charger les données quand la date ou le mode de vue change
  // On utilise les valeurs directement plutôt que loadData pour éviter les boucles infinies
  useEffect(() => {
    loadData()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentDate, viewMode])

  // Persist weekend toggle
  useEffect(() => {
    localStorage.setItem('planning-show-weekend', String(showWeekend))
  }, [showWeekend])

  // Synchroniser l'onglet et le mode avec l'URL
  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    params.set('tab', viewTab)
    params.set('mode', viewMode)
    const newUrl = `${window.location.pathname}?${params.toString()}`
    window.history.replaceState({}, '', newUrl)
  }, [viewTab, viewMode])

  // Filter affectations by chantier
  const filteredAffectations = useMemo(() => {
    if (!filterChantier) return affectations
    return affectations.filter(a => String(a.chantier_id) === filterChantier)
  }, [affectations, filterChantier])

  // Filtrer les utilisateurs
  const filteredUtilisateurs = useMemo(() => utilisateurs.filter(user => {
    // Exclure les employés du planning
    if (user.type_utilisateur === 'employe') {
      return false
    }

    if (filterMetiers.length > 0 && !filterMetiers.includes(user.metier || 'autre')) {
      return false
    }

    if (filterChantier) {
      const hasAffectationForChantier = affectations.some(
        a => String(a.chantier_id) === filterChantier && a.utilisateur_id === user.id
      )
      if (!hasAffectationForChantier) return false
    }

    if (showNonPlanifiesOnly) {
      const hasAffectation = affectations.some(a => a.utilisateur_id === user.id)
      if (hasAffectation) return false
    }

    return true
  }), [utilisateurs, filterMetiers, filterChantier, showNonPlanifiesOnly, affectations])

  // Handlers
  const openCreateModal = useCallback(() => {
    setEditingAffectation(null)
    // Définir la date du jour par défaut pour les nouvelles affectations
    setSelectedDate(new Date())
    setSelectedUserId(undefined)
    setSelectedChantierId(undefined)
    setModalOpen(true)
  }, [])

  const handleCellClick = useCallback((userId: string, date: Date) => {
    if (!canEdit) return
    setSelectedUserId(userId)
    setSelectedDate(date)
    setEditingAffectation(null)
    setModalOpen(true)
  }, [canEdit])

  const handleAffectationClick = useCallback((affectation: Affectation) => {
    if (!canEdit) return
    setEditingAffectation(affectation)
    setSelectedDate(undefined)
    setSelectedUserId(undefined)
    setModalOpen(true)
  }, [canEdit])

  const handleAffectationDelete = useCallback(async (affectation: Affectation) => {
    if (!canEdit) return

    try {
      await planningService.delete(affectation.id)
      await reloadAffectations()
    } catch (err) {
      logger.error('Erreur suppression', err, { context: 'PlanningPage' })
      setError('Erreur lors de la suppression')
    }
  }, [canEdit, reloadAffectations])

  // Suppression depuis le modal (sans confirmation car le modal la gère)
  const handleAffectationDeleteFromModal = useCallback(async (affectation: Affectation) => {
    if (!canEdit) return

    try {
      await planningService.delete(affectation.id)
      await reloadAffectations()
    } catch (err) {
      logger.error('Erreur suppression', err, { context: 'PlanningPage' })
      throw err // Remonter l'erreur pour que le modal puisse l'afficher
    }
  }, [canEdit, reloadAffectations])

  // Suppression multiple (utilisée par le resize pour réduire)
  const handleAffectationsDelete = useCallback(async (affectationsToDelete: Affectation[]) => {
    if (!canEdit || affectationsToDelete.length === 0) return

    // Mise à jour optimiste: supprimer localement d'abord pour une UI fluide
    const idsToDelete = new Set(affectationsToDelete.map(a => a.id))
    setAffectations(prev => prev.filter(a => !idsToDelete.has(a.id)))

    try {
      // Supprimer les affectations une par une pour éviter les erreurs de concurrence
      for (const aff of affectationsToDelete) {
        await planningService.delete(aff.id)
      }
      // Recharger en arrière-plan pour synchroniser (sans bloquer l'UI)
      reloadAffectations()
    } catch (err: unknown) {
      const axiosError = err as { response?: { status?: number; data?: { detail?: string } } }
      const detail = axiosError?.response?.data?.detail || 'Erreur lors de la suppression'
      logger.error('Erreur suppression multiple', err, { context: 'PlanningPage' })
      setError(detail)
      // En cas d'erreur, recharger pour restaurer l'état correct
      reloadAffectations()
    }
  }, [canEdit, reloadAffectations])

  const handleSaveAffectation = useCallback(async (data: AffectationCreate | AffectationUpdate) => {
    if (editingAffectation) {
      await planningService.update(editingAffectation.id, data as AffectationUpdate)
    } else {
      await planningService.create(data as AffectationCreate)
    }
    await reloadAffectations()
  }, [editingAffectation, reloadAffectations])

  const handleDuplicate = useCallback(async (userId: string) => {
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
      await reloadAffectations()
    } catch (err) {
      logger.error('Erreur duplication', err, { context: 'PlanningPage' })
      setError('Erreur lors de la duplication')
    }
  }, [canEdit, getDateRange, currentDate, reloadAffectations])

  const handleToggleMetier = useCallback((metier: string) => {
    setExpandedMetiers(prev =>
      prev.includes(metier)
        ? prev.filter(m => m !== metier)
        : [...prev, metier]
    )
  }, [])

  const handleAffectationMove = useCallback(async (affectationId: string, newDate: string, newUserId?: string) => {
    if (!canEdit) return

    try {
      await planningService.move(affectationId, newDate, newUserId)
      await reloadAffectations()
    } catch (err: unknown) {
      // Distinguer les erreurs de validation des erreurs système
      const axiosError = err as { response?: { status?: number; data?: { detail?: string } } }
      if (axiosError?.response?.status === 400) {
        // Erreur de validation (conflit, données invalides)
        const detail = axiosError.response?.data?.detail || 'Impossible de déplacer l\'affectation'
        setError(detail)
      } else if (axiosError?.response?.status === 404) {
        setError('Affectation non trouvée')
      } else {
        logger.error('Erreur deplacement', err, { context: 'PlanningPage' })
        setError('Erreur lors du déplacement de l\'affectation')
      }
    }
  }, [canEdit, reloadAffectations])

  const handleAffectationResize = useCallback(async (affectationId: string, newStartDate: string, newEndDate: string) => {
    if (!canEdit) return

    try {
      await planningService.resize(affectationId, newStartDate, newEndDate)
      await reloadAffectations()
    } catch (err: unknown) {
      const axiosError = err as { response?: { status?: number; data?: { detail?: string } } }
      if (axiosError?.response?.status === 400) {
        const detail = axiosError.response?.data?.detail || 'Impossible de redimensionner l\'affectation'
        setError(detail)
      } else if (axiosError?.response?.status === 404) {
        setError('Affectation non trouvée')
      } else {
        logger.error('Erreur redimensionnement', err, { context: 'PlanningPage' })
        setError('Erreur lors du redimensionnement de l\'affectation')
      }
    }
  }, [canEdit, reloadAffectations])

  const handleChantierCellClick = useCallback((chantierId: string, date: Date) => {
    if (!canEdit) return
    setSelectedChantierId(chantierId)
    setSelectedDate(date)
    setSelectedUserId(undefined)
    setEditingAffectation(null)
    setModalOpen(true)
  }, [canEdit])

  const handleDuplicateChantier = useCallback(async (chantierId: string) => {
    if (!canEdit) return
    const { date_debut: source_date_debut, date_fin: source_date_fin } = getDateRange()
    const nextWeekStart = addWeeks(startOfWeek(currentDate, { weekStartsOn: 1 }), 1)

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
      await reloadAffectations()
    } catch (err) {
      logger.error('Erreur duplication chantier', err, { context: 'PlanningPage' })
      setError('Erreur lors de la duplication')
    }
  }, [canEdit, getDateRange, currentDate, affectations, reloadAffectations])

  const toggleFilterMetier = useCallback((metier: string) => {
    setFilterMetiers(prev =>
      prev.includes(metier)
        ? prev.filter(m => m !== metier)
        : [...prev, metier]
    )
  }, [])

  const clearFilterMetiers = useCallback(() => {
    setFilterMetiers([])
  }, [])

  const closeModal = useCallback(() => {
    setModalOpen(false)
  }, [])

  return {
    // State
    canEdit,
    currentDate,
    viewMode,
    viewTab,
    loading,
    error,
    expandedMetiers,
    modalOpen,
    editingAffectation,
    selectedDate,
    selectedUserId,
    selectedChantierId,
    showFilters,
    filterMetiers,
    filterChantier,
    showNonPlanifiesOnly,
    showWeekend,
    nonPlanifiesCount,

    // Data
    affectations,
    utilisateurs,
    chantiers,
    filteredAffectations,
    filteredUtilisateurs,

    // Setters
    setCurrentDate,
    setViewMode,
    setViewTab,
    setShowFilters,
    setFilterChantier,
    setShowNonPlanifiesOnly,
    setShowWeekend,

    // Handlers
    openCreateModal,
    closeModal,
    handleCellClick,
    handleAffectationClick,
    handleAffectationDelete,
    handleAffectationDeleteFromModal,
    handleAffectationsDelete,
    handleSaveAffectation,
    handleDuplicate,
    handleToggleMetier,
    handleAffectationMove,
    handleAffectationResize,
    handleChantierCellClick,
    handleDuplicateChantier,
    toggleFilterMetier,
    clearFilterMetiers,
  }
}
