import { useState, useEffect, useCallback, useMemo } from 'react'
import { format, startOfWeek, addDays } from 'date-fns'
import { pointagesService } from '../services/pointages'
import { usersService } from '../services/users'
import { chantiersService } from '../services/chantiers'
import { logger } from '../services/logger'
import { useAuth } from '../contexts/AuthContext'
import type { Pointage, PointageCreate, PointageUpdate, User, Chantier, VueCompagnon, VueChantier } from '../types'

export type ViewTab = 'compagnons' | 'chantiers'

export function useFeuillesHeures() {
  const { user: currentUser } = useAuth()
  const canEdit = currentUser?.role === 'admin' || currentUser?.role === 'conducteur' || currentUser?.role === 'chef_chantier'
  const isValidateur = currentUser?.role === 'admin' || currentUser?.role === 'conducteur'

  // État principal
  const [currentDate, setCurrentDate] = useState(new Date())

  // Lire l'onglet depuis l'URL au démarrage
  const getInitialTab = (): ViewTab => {
    const params = new URLSearchParams(window.location.search)
    const tab = params.get('tab') as ViewTab | null
    return (tab && ['compagnons', 'chantiers'].includes(tab)) ? tab : 'compagnons'
  }
  const [viewTab, setViewTab] = useState<ViewTab>(getInitialTab())

  // Données
  const [vueCompagnons, setVueCompagnons] = useState<VueCompagnon[]>([])
  const [vueChantiers, setVueChantiers] = useState<VueChantier[]>([])
  const [utilisateurs, setUtilisateurs] = useState<User[]>([])
  const [chantiers, setChantiers] = useState<Chantier[]>([])
  const [heuresPrevuesParChantier, setHeuresPrevuesParChantier] = useState<Record<number, number>>({})

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

  const semaineDebut = useMemo(() => {
    const monday = startOfWeek(currentDate, { weekStartsOn: 1 })
    return format(monday, 'yyyy-MM-dd')
  }, [currentDate])

  const loadData = useCallback(async () => {
    setLoading(true)
    setError('')

    try {
      const [usersData, chantiersData] = await Promise.all([
        usersService.list({ size: 100 }),
        chantiersService.list({ size: 100 }),
      ])

      // Tous les utilisateurs actifs pour le filtre (admin peut s'ajouter)
      const allActive = usersData.items.filter((u) => u.is_active)
      setUtilisateurs(allActive)
      setChantiers(chantiersData.items.filter((c) => c.statut !== 'ferme'))

      // Par défaut : exclure admin/conducteur de la vue (ne travaillent pas sur chantier)
      // Mais si un filtre est actif, respecter la sélection de l'utilisateur
      const ROLES_CHANTIER = ['chef_chantier', 'compagnon']
      const utilisateurIds = filterUtilisateurs.length > 0
        ? filterUtilisateurs
        : allActive.filter((u) => ROLES_CHANTIER.includes(u.role)).map((u) => Number(u.id))
      const chantierIds = filterChantiers.length > 0
        ? filterChantiers
        : chantiersData.items.filter((c) => c.statut !== 'ferme').map((c) => Number(c.id))

      if (viewTab === 'compagnons') {
        const vueData = await pointagesService.getVueCompagnons(semaineDebut, utilisateurIds)
        setVueCompagnons(vueData)
      } else {
        const vueData = await pointagesService.getVueChantiers(semaineDebut, chantierIds)
        setVueChantiers(vueData)

        // Utiliser les heures estimées de la fiche chantier
        const prevuesMap: Record<number, number> = {}
        for (const chantier of chantiersData.items) {
          if (chantier.heures_estimees && chantier.heures_estimees > 0) {
            prevuesMap[Number(chantier.id)] = chantier.heures_estimees
          }
        }
        setHeuresPrevuesParChantier(prevuesMap)
      }
    } catch (err) {
      logger.error('Erreur chargement feuilles heures', err, { context: 'FeuillesHeuresPage' })
      setError('Erreur lors du chargement des donnees')
    } finally {
      setLoading(false)
    }
  }, [semaineDebut, viewTab, filterUtilisateurs, filterChantiers])

  useEffect(() => {
    loadData()
  }, [loadData])

  useEffect(() => {
    localStorage.setItem('timesheet-show-weekend', String(showWeekend))
  }, [showWeekend])

  // Synchroniser l'onglet avec l'URL
  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    params.set('tab', viewTab)
    const newUrl = `${window.location.pathname}?${params.toString()}`
    window.history.replaceState({}, '', newUrl)
  }, [viewTab])

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

  const handleSavePointage = useCallback(async (data: PointageCreate | PointageUpdate) => {
    if (!currentUser) return

    if (editingPointage) {
      await pointagesService.update(editingPointage.id, data as PointageUpdate, Number(currentUser.id))
    } else {
      await pointagesService.create(data as PointageCreate, Number(currentUser.id))
    }
    await loadData()
  }, [currentUser, editingPointage, loadData])

  const handleDeletePointage = useCallback(async () => {
    if (!editingPointage || !currentUser) return
    await pointagesService.delete(editingPointage.id, Number(currentUser.id))
    await loadData()
  }, [editingPointage, currentUser, loadData])

  const handleSignPointage = useCallback(async (signature: string) => {
    if (!editingPointage) return
    await pointagesService.sign(editingPointage.id, signature)
    await loadData()
  }, [editingPointage, loadData])

  const handleSubmitPointage = useCallback(async () => {
    if (!editingPointage) return
    await pointagesService.submit(editingPointage.id)
    await loadData()
  }, [editingPointage, loadData])

  const handleValidatePointage = useCallback(async () => {
    if (!editingPointage || !currentUser) return
    await pointagesService.validate(editingPointage.id, Number(currentUser.id))
    await loadData()
  }, [editingPointage, currentUser, loadData])

  const handleRejectPointage = useCallback(async (motif: string) => {
    if (!editingPointage || !currentUser) return
    await pointagesService.reject(editingPointage.id, motif, Number(currentUser.id))
    await loadData()
  }, [editingPointage, currentUser, loadData])

  const handleExport = useCallback(async () => {
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

      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `feuilles-heures-semaine-${semaineDebut}.xlsx`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (err) {
      logger.error('Erreur export', err, { context: 'FeuillesHeuresPage' })
      setError('Erreur lors de l\'export')
    } finally {
      setIsExporting(false)
    }
  }, [currentUser, semaineDebut, filterUtilisateurs, filterChantiers])

  const handleFilterUtilisateur = useCallback((userId: number) => {
    setFilterUtilisateurs((prev) =>
      prev.includes(userId) ? prev.filter((id) => id !== userId) : [...prev, userId]
    )
  }, [])

  const handleFilterChantier = useCallback((chantierId: number) => {
    setFilterChantiers((prev) =>
      prev.includes(chantierId) ? prev.filter((id) => id !== chantierId) : [...prev, chantierId]
    )
  }, [])

  const clearFilterUtilisateurs = useCallback(() => {
    setFilterUtilisateurs([])
  }, [])

  const clearFilterChantiers = useCallback(() => {
    setFilterChantiers([])
  }, [])

  const closeModal = useCallback(() => {
    setModalOpen(false)
  }, [])

  return {
    // State
    canEdit,
    isValidateur,
    currentDate,
    viewTab,
    loading,
    error,
    isExporting,
    modalOpen,
    editingPointage,
    selectedDate,
    selectedUserId,
    selectedChantierId,
    showFilters,
    filterUtilisateurs,
    filterChantiers,
    showWeekend,

    // Data
    vueCompagnons,
    vueChantiers,
    utilisateurs,
    chantiers,
    heuresPrevuesParChantier,

    // Setters
    setCurrentDate,
    setViewTab,
    setShowFilters,
    setShowWeekend,

    // Handlers
    handleCellClick,
    handleChantierCellClick,
    handlePointageClick,
    handleSavePointage,
    handleDeletePointage,
    handleSignPointage,
    handleSubmitPointage,
    handleValidatePointage,
    handleRejectPointage,
    handleExport,
    handleFilterUtilisateur,
    handleFilterChantier,
    clearFilterUtilisateurs,
    clearFilterChantiers,
    closeModal,
  }
}
