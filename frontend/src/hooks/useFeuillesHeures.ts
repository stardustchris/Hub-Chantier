import { useState, useEffect, useCallback, useMemo } from 'react'
import { format, startOfWeek, addDays } from 'date-fns'
import { pointagesService } from '../services/pointages'
import { usersService } from '../services/users'
import { chantiersService } from '../services/chantiers'
import { logger } from '../services/logger'
import { useAuth } from '../contexts/AuthContext'
import { useMultiSelect } from './useMultiSelect'
import type { Pointage, PointageCreate, PointageUpdate, User, Chantier, VueCompagnon, VueChantier } from '../types'

export type ViewTab = 'compagnons' | 'chantiers'

export function useFeuillesHeures() {
  const { user: currentUser } = useAuth()
  const canEdit = currentUser?.role === 'admin' || currentUser?.role === 'conducteur' || currentUser?.role === 'chef_chantier'
  const isValidateur = currentUser?.role === 'admin' || currentUser?.role === 'conducteur' || currentUser?.role === 'chef_chantier'

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
  const [isBatchValidating, setIsBatchValidating] = useState(false)
  const [isBatchRejecting, setIsBatchRejecting] = useState(false)
  const [batchSuccess, setBatchSuccess] = useState<string>('')

  // Multi-select pour validation batch
  const multiSelect = useMultiSelect<number>()

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
      const chantiersActifs = chantiersData.items.filter((c) => c.statut !== 'ferme')

      // Chef de chantier : restreindre aux chantiers dont il est chef
      const isChef = currentUser?.role === 'chef_chantier'
      const mesChantiers = isChef
        ? chantiersActifs.filter((c) =>
            c.chefs?.some((chef) => String(chef.id) === String(currentUser?.id))
          )
        : chantiersActifs

      setUtilisateurs(allActive)
      setChantiers(mesChantiers)

      // Visibilité par rôle :
      // - compagnon : uniquement lui-même
      // - chef_chantier : compagnons de ses chantiers + lui-même
      // - conducteur : tous les compagnons/chefs
      // - admin : tous les compagnons/chefs + lui-même
      const ROLES_CHANTIER = ['chef_chantier', 'compagnon']

      // Chef : restreindre les chantier_ids à ses chantiers même si pas de filtre actif
      const mesChantierIds = mesChantiers.map((c) => Number(c.id))

      const currentUserId = currentUser?.id ? Number(currentUser.id) : null
      const isAdmin = currentUser?.role === 'admin'
      const isCompagnon = currentUser?.role === 'compagnon'

      let defaultIds: number[]
      if (isCompagnon && currentUserId) {
        // Compagnon : ne voit que sa propre feuille
        defaultIds = [currentUserId]
      } else {
        defaultIds = allActive.filter((u) => ROLES_CHANTIER.includes(u.role)).map((u) => Number(u.id))
        // L'admin voit aussi sa propre feuille
        if (isAdmin && currentUserId && !defaultIds.includes(currentUserId)) {
          defaultIds.push(currentUserId)
        }
      }

      const utilisateurIds = filterUtilisateurs.length > 0
        ? filterUtilisateurs
        : defaultIds
      const chantierIds = filterChantiers.length > 0
        ? filterChantiers.filter((id) => !isChef || mesChantierIds.includes(id))
        : mesChantierIds

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
  }, [semaineDebut, viewTab, filterUtilisateurs, filterChantiers, currentUser?.id, currentUser?.role])

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

  // Récupérer tous les pointages sélectionnables (statut 'soumis')
  const selectablePointages = useMemo(() => {
    const pointages: Pointage[] = []
    if (viewTab === 'compagnons') {
      vueCompagnons?.forEach((vue) => {
        vue.chantiers?.forEach((chantier) => {
          Object.values(chantier.pointages_par_jour).forEach((pointagesJour) => {
            pointagesJour.forEach((p) => {
              if (p.statut === 'soumis') {
                pointages.push(p)
              }
            })
          })
        })
      })
    }
    return pointages
  }, [vueCompagnons, viewTab])

  // Handler validation batch
  const handleBatchValidate = useCallback(async () => {
    if (!currentUser || multiSelect.count === 0) return

    setIsBatchValidating(true)
    setBatchSuccess('')
    setError('')

    try {
      const result = await pointagesService.validateBatch(
        multiSelect.selectedArray,
        Number(currentUser.id)
      )

      if (result.failed.length === 0) {
        setBatchSuccess(`${result.success.length} pointage${result.success.length > 1 ? 's validés' : ' validé'}`)
      } else {
        setBatchSuccess(
          `${result.success.length} validé${result.success.length > 1 ? 's' : ''}, ${result.failed.length} échoué${result.failed.length > 1 ? 's' : ''}`
        )
        if (result.success.length === 0) {
          setError('Aucun pointage n\'a pu être validé')
        }
      }

      multiSelect.deselectAll()
      await loadData()
    } catch (err) {
      logger.error('Erreur validation batch', err, { context: 'FeuillesHeuresPage' })
      setError('Erreur lors de la validation en lot')
    } finally {
      setIsBatchValidating(false)
    }
  }, [currentUser, multiSelect, loadData])

  // Handler rejet batch
  const handleBatchReject = useCallback(async () => {
    if (!currentUser || multiSelect.count === 0) return

    // Demander le motif de rejet
    const motif = prompt('Motif du rejet (requis):')
    if (!motif || motif.trim() === '') {
      return // Annulé ou motif vide
    }

    setIsBatchRejecting(true)
    setBatchSuccess('')
    setError('')

    try {
      const result = await pointagesService.rejectBatch(
        multiSelect.selectedArray,
        motif.trim(),
        Number(currentUser.id)
      )

      if (result.failed.length === 0) {
        setBatchSuccess(`${result.success.length} pointage${result.success.length > 1 ? 's rejetés' : ' rejeté'}`)
      } else {
        setBatchSuccess(
          `${result.success.length} rejeté${result.success.length > 1 ? 's' : ''}, ${result.failed.length} échoué${result.failed.length > 1 ? 's' : ''}`
        )
        if (result.success.length === 0) {
          setError('Aucun pointage n\'a pu être rejeté')
        }
      }

      multiSelect.deselectAll()
      await loadData()
    } catch (err) {
      logger.error('Erreur rejet batch', err, { context: 'FeuillesHeuresPage' })
      setError('Erreur lors du rejet en lot')
    } finally {
      setIsBatchRejecting(false)
    }
  }, [currentUser, multiSelect, loadData])

  // Sélectionner tous les pointages sélectionnables
  const handleSelectAll = useCallback(() => {
    const ids = selectablePointages.map((p) => p.id)
    multiSelect.selectAll(ids)
  }, [selectablePointages, multiSelect])

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
    isBatchValidating,
    isBatchRejecting,
    batchSuccess,

    // Data
    vueCompagnons,
    vueChantiers,
    utilisateurs,
    chantiers,
    heuresPrevuesParChantier,
    selectablePointages,

    // Multi-select
    multiSelect,

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
    handleBatchValidate,
    handleBatchReject,
    handleSelectAll,
  }
}
