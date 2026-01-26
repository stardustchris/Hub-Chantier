import { useMemo, useState, useCallback, useEffect, useRef } from 'react'
import { format, eachDayOfInterval, startOfWeek, endOfWeek, startOfMonth, endOfMonth, isToday, isWeekend, addDays } from 'date-fns'
import { fr } from 'date-fns/locale'
import { ChevronDown, ChevronRight, Copy, Phone } from 'lucide-react'
import type { Affectation, User, PlanningCategory } from '../../types'
import { PLANNING_CATEGORIES } from '../../types'
import AffectationBlock from './AffectationBlock'

interface PlanningGridProps {
  currentDate: Date
  affectations: Affectation[]
  utilisateurs: User[]
  onAffectationClick: (affectation: Affectation) => void
  onAffectationDelete: (affectation: Affectation) => void
  onCellClick: (userId: string, date: Date) => void
  onDuplicate: (userId: string) => void
  expandedMetiers: string[]
  onToggleMetier: (metier: string) => void
  showWeekend?: boolean // PLN-06
  onAffectationMove?: (affectationId: string, newDate: string, newUserId?: string) => void // PLN-27
  onAffectationResize?: (affectationId: string, newStartDate: string, newEndDate: string) => void // Resize support (extension)
  onAffectationsDelete?: (affectations: Affectation[]) => Promise<void> // Resize support (reduction)
  viewMode?: 'semaine' | 'mois' // PLN-05: Vue semaine ou mois
}

// Resize state
interface ResizeState {
  affectation: Affectation
  direction: 'left' | 'right'
  startX: number
  cellWidth: number
  originalDate: string
  startTime: number // Timestamp pour ignorer les mouseup trop rapides (clics)
  // Pré-calculé au démarrage pour éviter les recalculs pendant le drag
  userAffectations: Affectation[]
  existingDates: Set<string>
  affectationsByDate: Map<string, Affectation>
  lastDaysDelta: number // Pour éviter les updates inutiles
}

// Preview state pour le resize
interface ResizePreview {
  datesToAdd: string[]    // Dates à ajouter (extension) - affichées en couleur du chantier
  datesToRemove: string[] // Dates à supprimer (réduction) - affichées en rouge
}

// Grouper les utilisateurs par catégorie (role/type_utilisateur)
function groupByCategory(utilisateurs: User[]): Record<PlanningCategory, User[]> {
  const groups: Record<string, User[]> = {
    conducteur: [],
    chef_chantier: [],
    compagnon: [],
    interimaire: [],
    sous_traitant: [],
  }

  utilisateurs.forEach(user => {
    // Déterminer la catégorie basée sur role et type_utilisateur
    if (user.role === 'conducteur') {
      groups.conducteur.push(user)
    } else if (user.role === 'chef_chantier') {
      groups.chef_chantier.push(user)
    } else if (user.type_utilisateur === 'interimaire') {
      groups.interimaire.push(user)
    } else if (user.type_utilisateur === 'sous_traitant') {
      groups.sous_traitant.push(user)
    } else {
      // Compagnon par défaut (employés avec role compagnon)
      groups.compagnon.push(user)
    }
  })

  // Retourner seulement les groupes non vides
  return Object.fromEntries(
    Object.entries(groups).filter(([_, users]) => users.length > 0)
  ) as Record<PlanningCategory, User[]>
}

export default function PlanningGrid({
  currentDate,
  affectations,
  utilisateurs,
  onAffectationClick,
  onAffectationDelete,
  onCellClick,
  onDuplicate,
  expandedMetiers,
  onToggleMetier,
  showWeekend = true,
  onAffectationMove,
  onAffectationResize,
  onAffectationsDelete,
  viewMode = 'semaine',
}: PlanningGridProps) {
  // PLN-27: Drag state
  const [draggedAffectation, setDraggedAffectation] = useState<Affectation | null>(null)
  const [dragOverCell, setDragOverCell] = useState<string | null>(null)

  // Resize state
  const [resizeState, setResizeState] = useState<ResizeState | null>(null)
  const [resizePreview, setResizePreview] = useState<ResizePreview>({ datesToAdd: [], datesToRemove: [] })
  const gridRef = useRef<HTMLDivElement>(null)

  // PLN-05/PLN-06: Jours selon le mode de vue (semaine ou mois)
  const days = useMemo(() => {
    let start: Date
    let end: Date
    if (viewMode === 'mois') {
      start = startOfMonth(currentDate)
      end = endOfMonth(currentDate)
    } else {
      start = startOfWeek(currentDate, { weekStartsOn: 1 })
      end = endOfWeek(currentDate, { weekStartsOn: 1 })
    }
    const allDays = eachDayOfInterval({ start, end })
    return showWeekend ? allDays : allDays.filter(day => !isWeekend(day))
  }, [currentDate, showWeekend, viewMode])

  // PLN-27: Drag handlers
  const handleDragStart = useCallback((e: React.DragEvent, affectation: Affectation) => {
    setDraggedAffectation(affectation)
    e.dataTransfer.effectAllowed = 'move'
    e.dataTransfer.setData('text/plain', affectation.id)
  }, [])

  const handleDragOver = useCallback((e: React.DragEvent, cellKey: string) => {
    e.preventDefault()
    e.dataTransfer.dropEffect = 'move'
    setDragOverCell(cellKey)
  }, [])

  const handleDragLeave = useCallback(() => {
    setDragOverCell(null)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent, userId: string, date: Date) => {
    e.preventDefault()
    setDragOverCell(null)

    if (draggedAffectation && onAffectationMove) {
      const newDate = format(date, 'yyyy-MM-dd')
      // Only move if date or user changed
      if (draggedAffectation.date !== newDate || String(draggedAffectation.utilisateur_id) !== userId) {
        onAffectationMove(draggedAffectation.id, newDate, userId)
      }
    }
    setDraggedAffectation(null)
  }, [draggedAffectation, onAffectationMove])

  const handleDragEnd = useCallback(() => {
    setDraggedAffectation(null)
    setDragOverCell(null)
  }, [])

  // Resize handlers
  const handleResizeStart = useCallback((affectation: Affectation, direction: 'left' | 'right', e: React.MouseEvent) => {
    // Permettre le resize si on peut étendre OU supprimer
    if (!onAffectationResize && !onAffectationsDelete) return

    // Calculer la largeur d'une cellule (approximation basée sur la grille)
    const gridElement = gridRef.current
    if (!gridElement) return

    const cells = gridElement.querySelectorAll('[data-cell-day]')
    if (cells.length === 0) return

    const firstCell = cells[0] as HTMLElement
    const cellWidth = firstCell.offsetWidth

    // Pré-calculer les données pour éviter les recalculs pendant le drag
    const userAffectations = affectations.filter(
      a => a.utilisateur_id === affectation.utilisateur_id &&
           a.chantier_id === affectation.chantier_id
    )
    const existingDates = new Set(userAffectations.map(a => a.date))
    const affectationsByDate = new Map(userAffectations.map(a => [a.date, a]))

    setResizeState({
      affectation,
      direction,
      startX: e.clientX,
      cellWidth,
      originalDate: affectation.date,
      startTime: Date.now(),
      userAffectations,
      existingDates,
      affectationsByDate,
      lastDaysDelta: 0,
    })
  }, [onAffectationResize, onAffectationsDelete, affectations])

  const handleResizeMove = useCallback((e: MouseEvent) => {
    if (!resizeState) return

    const deltaX = e.clientX - resizeState.startX
    const daysDelta = Math.round(deltaX / resizeState.cellWidth)

    // Éviter les re-renders si le daysDelta n'a pas changé
    if (daysDelta === resizeState.lastDaysDelta) return

    // Mettre à jour lastDaysDelta (mutation directe OK car on va setState juste après)
    resizeState.lastDaysDelta = daysDelta

    const originalDate = new Date(resizeState.originalDate)
    const datesToAdd: string[] = []
    const datesToRemove: string[] = []

    // Utiliser les données pré-calculées
    const { existingDates, userAffectations } = resizeState

    if (resizeState.direction === 'right') {
      if (daysDelta > 0) {
        // Extension vers la droite - ajouter des jours après l'affectation
        for (let i = 1; i <= daysDelta; i++) {
          const dateStr = format(addDays(originalDate, i), 'yyyy-MM-dd')
          if (!existingDates.has(dateStr)) {
            datesToAdd.push(dateStr)
          }
        }
      } else if (daysDelta < 0) {
        // Réduction depuis la droite - supprimer les affectations ENTRE targetDate et originalDate
        const originalDateStr = resizeState.originalDate
        const targetDate = addDays(originalDate, daysDelta)
        const targetDateStr = format(targetDate, 'yyyy-MM-dd')

        // Supprimer les affectations > targetDate ET <= originalDate
        for (const aff of userAffectations) {
          if (aff.date > targetDateStr && aff.date <= originalDateStr) {
            datesToRemove.push(aff.date)
          }
        }
      }
    } else if (resizeState.direction === 'left') {
      if (daysDelta < 0) {
        // Extension vers la gauche - ajouter des jours avant l'affectation
        for (let i = daysDelta; i < 0; i++) {
          const dateStr = format(addDays(originalDate, i), 'yyyy-MM-dd')
          if (!existingDates.has(dateStr)) {
            datesToAdd.push(dateStr)
          }
        }
      } else if (daysDelta > 0) {
        // Réduction depuis la gauche - supprimer les affectations ENTRE originalDate et targetDate
        const originalDateStr = resizeState.originalDate
        const targetDate = addDays(originalDate, daysDelta)
        const targetDateStr = format(targetDate, 'yyyy-MM-dd')

        // Supprimer les affectations >= originalDate ET < targetDate
        for (const aff of userAffectations) {
          if (aff.date >= originalDateStr && aff.date < targetDateStr) {
            datesToRemove.push(aff.date)
          }
        }
      }
    }

    setResizePreview({ datesToAdd, datesToRemove })
  }, [resizeState])

  const handleResizeEnd = useCallback(async (e: MouseEvent) => {
    if (!resizeState) {
      setResizeState(null)
      setResizePreview({ datesToAdd: [], datesToRemove: [] })
      return
    }

    const elapsed = Date.now() - resizeState.startTime
    const movement = Math.abs(e.clientX - resizeState.startX)

    // Ignorer les mouseup trop rapides ou sans mouvement significatif (c'est un clic, pas un drag)
    if (elapsed < 100 || movement < 10) {
      setResizeState(null)
      setResizePreview({ datesToAdd: [], datesToRemove: [] })
      return
    }

    const deltaX = e.clientX - resizeState.startX
    const daysDelta = Math.round(deltaX / resizeState.cellWidth)

    if (daysDelta !== 0) {
      const originalDate = new Date(resizeState.originalDate)

      // Utiliser les données pré-calculées
      const { userAffectations } = resizeState

      if (resizeState.direction === 'right') {
        if (daysDelta > 0 && onAffectationResize) {
          // Extension vers la droite - ajouter des jours après l'affectation
          const newEndDate = addDays(originalDate, daysDelta)
          onAffectationResize(
            resizeState.affectation.id,
            resizeState.originalDate,
            format(newEndDate, 'yyyy-MM-dd')
          )
        } else if (daysDelta < 0 && onAffectationsDelete) {
          // Réduction depuis la droite - supprimer les affectations ENTRE targetDate et originalDate
          const originalDateStr = resizeState.originalDate
          const targetDate = addDays(originalDate, daysDelta)
          const targetDateStr = format(targetDate, 'yyyy-MM-dd')

          // Supprimer les affectations > targetDate ET <= originalDate
          const affectationsToDelete = userAffectations.filter(
            aff => aff.date > targetDateStr && aff.date <= originalDateStr
          )

          if (affectationsToDelete.length > 0) {
            // Demander confirmation si on supprime toutes les affectations
            if (affectationsToDelete.length === userAffectations.length) {
              const chantierNom = resizeState.affectation.chantier_nom || 'ce chantier'
              const confirmed = window.confirm(
                `Supprimer toutes les affectations (${affectationsToDelete.length}) pour ${chantierNom} ?`
              )
              if (!confirmed) {
                setResizeState(null)
                setResizePreview({ datesToAdd: [], datesToRemove: [] })
                return
              }
            }
            await onAffectationsDelete(affectationsToDelete)
          }
        }
      } else if (resizeState.direction === 'left') {
        if (daysDelta < 0 && onAffectationResize) {
          // Extension vers la gauche - ajouter des jours avant l'affectation
          const newStartDate = addDays(originalDate, daysDelta)
          onAffectationResize(
            resizeState.affectation.id,
            format(newStartDate, 'yyyy-MM-dd'),
            resizeState.originalDate
          )
        } else if (daysDelta > 0 && onAffectationsDelete) {
          // Réduction depuis la gauche - supprimer les affectations ENTRE originalDate et targetDate
          const originalDateStr = resizeState.originalDate
          const targetDate = addDays(originalDate, daysDelta)
          const targetDateStr = format(targetDate, 'yyyy-MM-dd')

          // Supprimer les affectations >= originalDate ET < targetDate
          const affectationsToDelete = userAffectations.filter(
            aff => aff.date >= originalDateStr && aff.date < targetDateStr
          )

          if (affectationsToDelete.length > 0) {
            // Demander confirmation si on supprime toutes les affectations
            if (affectationsToDelete.length === userAffectations.length) {
              const chantierNom = resizeState.affectation.chantier_nom || 'ce chantier'
              const confirmed = window.confirm(
                `Supprimer toutes les affectations (${affectationsToDelete.length}) pour ${chantierNom} ?`
              )
              if (!confirmed) {
                setResizeState(null)
                setResizePreview({ datesToAdd: [], datesToRemove: [] })
                return
              }
            }
            await onAffectationsDelete(affectationsToDelete)
          }
        }
      }
    }

    setResizeState(null)
    setResizePreview({ datesToAdd: [], datesToRemove: [] })
  }, [resizeState, onAffectationResize, onAffectationsDelete])

  // Écouter les événements mouse globalement pendant le resize
  useEffect(() => {
    if (!resizeState) return

    const handleMouseMove = (e: MouseEvent) => handleResizeMove(e)
    const handleMouseUp = (e: MouseEvent) => handleResizeEnd(e)

    document.addEventListener('mousemove', handleMouseMove)
    document.addEventListener('mouseup', handleMouseUp)

    return () => {
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
    }
  }, [resizeState, handleResizeMove, handleResizeEnd])

  // Grouper les utilisateurs par catégorie (role/type)
  const groupedUsers = useMemo(() => groupByCategory(utilisateurs), [utilisateurs])

  // Trier les catégories par ordre défini
  const sortedCategories = useMemo(() => {
    return Object.entries(groupedUsers).sort(([catA], [catB]) => {
      const orderA = PLANNING_CATEGORIES[catA as PlanningCategory]?.order || 99
      const orderB = PLANNING_CATEGORIES[catB as PlanningCategory]?.order || 99
      return orderA - orderB
    })
  }, [groupedUsers])

  // Indexer les affectations par utilisateur et date
  const affectationsByUserAndDate = useMemo(() => {
    const index: Record<string, Record<string, Affectation[]>> = {}

    affectations.forEach(aff => {
      if (!index[aff.utilisateur_id]) {
        index[aff.utilisateur_id] = {}
      }
      const dateKey = aff.date
      if (!index[aff.utilisateur_id][dateKey]) {
        index[aff.utilisateur_id][dateKey] = []
      }
      index[aff.utilisateur_id][dateKey].push(aff)
    })

    return index
  }, [affectations])

  const getAffectationsForCell = (userId: string, date: Date): Affectation[] => {
    const dateKey = format(date, 'yyyy-MM-dd')
    return affectationsByUserAndDate[userId]?.[dateKey] || []
  }

  // PLN-05/PLN-06: Dynamic grid columns based on view mode and weekend visibility
  const gridStyle = useMemo(() => {
    const numDays = days.length
    if (viewMode === 'mois') {
      // Pour le mois, colonne fixe pour utilisateurs + colonnes dynamiques pour les jours
      return { gridTemplateColumns: `200px repeat(${numDays}, minmax(40px, 1fr))` }
    }
    return { gridTemplateColumns: showWeekend ? '250px repeat(7, 1fr)' : '250px repeat(5, 1fr)' }
  }, [days.length, viewMode, showWeekend])

  // Mode mois = affichage compact
  const isMonthView = viewMode === 'mois'

  return (
    <div ref={gridRef} className={`bg-white rounded-lg shadow overflow-hidden ${isMonthView ? 'overflow-x-auto' : ''} ${resizeState ? 'select-none' : ''}`}>
      {/* Header - Jours */}
      <div className={`grid border-b bg-gray-50 ${isMonthView ? 'min-w-max' : ''}`} style={gridStyle}>
        <div className={`${isMonthView ? 'px-2' : 'px-4'} py-3 font-medium text-gray-700 border-r`}>
          Utilisateurs
        </div>
        {days.map(day => (
          <div
            key={day.toISOString()}
            className={`px-1 py-2 text-center border-r last:border-r-0 ${
              isToday(day) ? 'bg-primary-50' : ''
            }`}
          >
            <div className={`text-xs text-gray-500 uppercase ${isMonthView ? 'text-[10px]' : ''}`}>
              {format(day, isMonthView ? 'EEEEE' : 'EEE', { locale: fr })}
            </div>
            <div className={`font-medium ${isToday(day) ? 'text-primary-600' : 'text-gray-900'} ${isMonthView ? 'text-xs' : 'text-sm'}`}>
              {format(day, isMonthView ? 'd' : 'd MMM', { locale: fr })}
            </div>
          </div>
        ))}
      </div>

      {/* Corps - Groupes par catégorie */}
      <div className="divide-y">
        {sortedCategories.map(([category, users]) => {
          const categoryInfo = PLANNING_CATEGORIES[category as PlanningCategory] || { label: category, color: '#607D8B' }
          const isExpanded = expandedMetiers.includes(category)

          return (
            <div key={category}>
              {/* Header du groupe (catégorie) */}
              <button
                onClick={() => onToggleMetier(category)}
                className="w-full grid bg-gray-50 hover:bg-gray-100 transition-colors" style={gridStyle}
              >
                <div className="px-4 py-2 flex items-center gap-2 border-r">
                  {isExpanded ? (
                    <ChevronDown className="w-4 h-4 text-gray-500" />
                  ) : (
                    <ChevronRight className="w-4 h-4 text-gray-500" />
                  )}
                  <span
                    className="px-2 py-0.5 rounded text-xs font-medium text-white"
                    style={{ backgroundColor: categoryInfo.color }}
                  >
                    {categoryInfo.label}
                  </span>
                  <span className="text-sm text-gray-500">({users.length})</span>
                </div>
                {/* Colonnes vides pour aligner */}
                {days.map(day => (
                  <div key={day.toISOString()} className="border-r last:border-r-0" />
                ))}
              </button>

              {/* Utilisateurs du groupe */}
              {isExpanded && users.map(user => (
                <div
                  key={user.id}
                  className="group/row grid hover:bg-gray-50 transition-colors" style={gridStyle}
                >
                  {/* Colonne utilisateur */}
                  <div className="px-4 py-3 flex items-center gap-3 border-r">
                    {/* Avatar */}
                    <div
                      className="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-semibold flex-shrink-0"
                      style={{ backgroundColor: user.couleur || '#3498DB' }}
                    >
                      {user.prenom?.[0]}{user.nom?.[0]}
                    </div>

                    {/* Nom */}
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium text-gray-900 truncate">
                        {user.prenom} {user.nom}
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-1 opacity-0 group-hover/row:opacity-100 transition-opacity">
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          onDuplicate(user.id)
                        }}
                        className="p-1 rounded hover:bg-gray-200"
                        title="Dupliquer la semaine"
                      >
                        <Copy className="w-4 h-4 text-gray-500" />
                      </button>
                      {user.telephone && (
                        <a
                          href={`tel:${user.telephone}`}
                          onClick={e => e.stopPropagation()}
                          className="p-1 rounded hover:bg-gray-200"
                          title="Appeler"
                        >
                          <Phone className="w-4 h-4 text-gray-500" />
                        </a>
                      )}
                    </div>
                  </div>

                  {/* Cellules des jours */}
                  {days.map(day => {
                    const cellAffectations = getAffectationsForCell(user.id, day)
                    const hasAffectations = cellAffectations.length > 0
                    const cellKey = `${user.id}-${format(day, 'yyyy-MM-dd')}`
                    const isDragOver = dragOverCell === cellKey
                    const dateStr = format(day, 'yyyy-MM-dd')
                    // Vérifier si cette cellule est dans la preview du resize (même utilisateur)
                    const isUserMatch = resizeState && String(resizeState.affectation.utilisateur_id) === String(user.id)
                    const isAddPreview = isUserMatch && resizePreview.datesToAdd.includes(dateStr)
                    const isRemovePreview = isUserMatch && resizePreview.datesToRemove.includes(dateStr)
                    // Couleur de la preview = couleur du chantier (ajout) ou rouge (suppression)
                    const previewColor = isAddPreview
                      ? (resizeState?.affectation.chantier_couleur || '#3498DB')
                      : isRemovePreview
                        ? '#EF4444' // Rouge pour suppression
                        : undefined

                    return (
                      <div
                        key={day.toISOString()}
                        data-cell-day={dateStr}
                        tabIndex={0}
                        role="gridcell"
                        aria-label={`${user.prenom} ${user.nom}, ${format(day, 'EEEE d MMMM', { locale: fr })}`}
                        onClick={() => !hasAffectations && !resizeState && onCellClick(user.id, day)}
                        onDoubleClick={() => !resizeState && onCellClick(user.id, day)}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter' || e.key === ' ') {
                            e.preventDefault()
                            onCellClick(user.id, day)
                          }
                        }}
                        onDragOver={(e) => handleDragOver(e, cellKey)}
                        onDragLeave={handleDragLeave}
                        onDrop={(e) => handleDrop(e, user.id, day)}
                        className={`p-1 border-r last:border-r-0 min-h-[60px] overflow-hidden transition-colors focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary-500 ${
                          isToday(day) ? 'bg-primary-50/50' : ''
                        } ${
                          isDragOver ? 'bg-blue-100 ring-2 ring-inset ring-blue-400' : ''
                        } ${
                          !hasAffectations && !isAddPreview ? 'cursor-pointer hover:bg-gray-100' : ''
                        }`}
                        style={previewColor ? {
                          backgroundColor: `${previewColor}50`,
                        } : undefined}
                      >
                        <div className="space-y-1 w-full">
                          {cellAffectations.map(aff => (
                            <AffectationBlock
                              key={aff.id}
                              affectation={aff}
                              onClick={() => onAffectationClick(aff)}
                              onDelete={() => onAffectationDelete(aff)}
                              compact={cellAffectations.length > 1}
                              draggable={!!onAffectationMove}
                              onDragStart={(e) => handleDragStart(e, aff)}
                              onDragEnd={handleDragEnd}
                              resizable={!!onAffectationResize || !!onAffectationsDelete}
                              onResizeStart={(direction, e) => handleResizeStart(aff, direction, e)}
                              isResizing={resizeState?.affectation.id === aff.id}
                              proportionalHeight={true}
                              cellHeight={60}
                            />
                          ))}
                        </div>
                      </div>
                    )
                  })}
                </div>
              ))}
            </div>
          )
        })}
      </div>

      {/* Message si aucun utilisateur */}
      {utilisateurs.length === 0 && (
        <div className="p-8 text-center text-gray-500">
          Aucun utilisateur à afficher
        </div>
      )}
    </div>
  )
}
