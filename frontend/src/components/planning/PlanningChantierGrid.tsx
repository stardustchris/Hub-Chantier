import { useMemo, useState, useCallback } from 'react'
import { format, eachDayOfInterval, startOfWeek, endOfWeek, startOfMonth, endOfMonth, isToday, isWeekend } from 'date-fns'
import { fr } from 'date-fns/locale'
import { MapPin, Copy, Users } from 'lucide-react'
import type { Affectation, Chantier } from '../../types'
import { CHANTIER_STATUTS } from '../../types'

interface PlanningChantierGridProps {
  currentDate: Date
  affectations: Affectation[]
  chantiers: Chantier[]
  onAffectationClick: (affectation: Affectation) => void
  onCellClick: (chantierId: string, date: Date) => void
  onDuplicateChantier: (chantierId: string) => void
  showWeekend?: boolean
  onAffectationMove?: (affectationId: string, newDate: string, newChantierId?: string) => void
  viewMode?: 'semaine' | 'mois' // PLN-05: Vue semaine ou mois
}

export default function PlanningChantierGrid({
  currentDate,
  affectations,
  chantiers,
  onAffectationClick,
  onCellClick,
  onDuplicateChantier,
  showWeekend = true,
  onAffectationMove,
  viewMode = 'semaine',
}: PlanningChantierGridProps) {
  // PLN-27: Drag state
  const [draggedAffectation, setDraggedAffectation] = useState<Affectation | null>(null)
  const [dragOverCell, setDragOverCell] = useState<string | null>(null)

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

  const handleDrop = useCallback((e: React.DragEvent, chantierId: string, date: Date) => {
    e.preventDefault()
    setDragOverCell(null)

    if (draggedAffectation && onAffectationMove) {
      const newDate = format(date, 'yyyy-MM-dd')
      // Only move if date or chantier changed
      if (draggedAffectation.date !== newDate || String(draggedAffectation.chantier_id) !== chantierId) {
        onAffectationMove(draggedAffectation.id, newDate, chantierId)
      }
    }
    setDraggedAffectation(null)
  }, [draggedAffectation, onAffectationMove])

  const handleDragEnd = useCallback(() => {
    setDraggedAffectation(null)
    setDragOverCell(null)
  }, [])

  // Indexer les affectations par chantier et date
  const affectationsByChantierAndDate = useMemo(() => {
    const index: Record<string, Record<string, Affectation[]>> = {}

    affectations.forEach(aff => {
      const chantierId = String(aff.chantier_id)
      if (!index[chantierId]) {
        index[chantierId] = {}
      }
      const dateKey = aff.date
      if (!index[chantierId][dateKey]) {
        index[chantierId][dateKey] = []
      }
      index[chantierId][dateKey].push(aff)
    })

    return index
  }, [affectations])

  const getAffectationsForCell = (chantierId: string, date: Date): Affectation[] => {
    const dateKey = format(date, 'yyyy-MM-dd')
    return affectationsByChantierAndDate[chantierId]?.[dateKey] || []
  }

  // Calculer le nombre d'utilisateurs uniques affectes par chantier
  const getUserCountByChantier = useMemo(() => {
    const counts: Record<string, number> = {}
    chantiers.forEach(c => {
      const uniqueUsers = new Set(
        affectations
          .filter(a => String(a.chantier_id) === String(c.id))
          .map(a => a.utilisateur_id)
      )
      counts[c.id] = uniqueUsers.size
    })
    return counts
  }, [affectations, chantiers])

  // PLN-05/PLN-06: Dynamic grid columns based on view mode and weekend visibility
  const gridCols = useMemo(() => {
    const numDays = days.length
    if (viewMode === 'mois') {
      // Pour le mois, colonne fixe pour chantiers + colonnes dynamiques pour les jours
      return `grid-cols-[220px_repeat(${numDays},minmax(40px,1fr))]`
    }
    return showWeekend ? 'grid-cols-[280px_repeat(7,1fr)]' : 'grid-cols-[280px_repeat(5,1fr)]'
  }, [days.length, viewMode, showWeekend])

  // Trier les chantiers par statut puis par nom
  const sortedChantiers = useMemo(() => {
    const statusOrder = ['en_cours', 'ouvert', 'receptionne', 'ferme']
    return [...chantiers].sort((a, b) => {
      const statusDiff = statusOrder.indexOf(a.statut) - statusOrder.indexOf(b.statut)
      if (statusDiff !== 0) return statusDiff
      return a.nom.localeCompare(b.nom)
    })
  }, [chantiers])

  // Mode mois = affichage compact
  const isMonthView = viewMode === 'mois'

  return (
    <div className={`bg-white rounded-lg shadow overflow-hidden ${isMonthView ? 'overflow-x-auto' : ''}`}>
      {/* Header - Jours */}
      <div className={`grid ${gridCols} border-b bg-gray-50 ${isMonthView ? 'min-w-max' : ''}`}>
        <div className={`${isMonthView ? 'px-2' : 'px-4'} py-3 font-medium text-gray-700 border-r`}>
          Chantiers
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

      {/* Corps - Lignes par chantier */}
      <div className="divide-y">
        {sortedChantiers.map(chantier => {
          const statutInfo = CHANTIER_STATUTS[chantier.statut] || { label: chantier.statut, color: '#607D8B' }
          const userCount = getUserCountByChantier[chantier.id] || 0

          return (
            <div
              key={chantier.id}
              className={`group grid ${gridCols} hover:bg-gray-50 transition-colors`}
            >
              {/* Colonne chantier */}
              <div className="px-4 py-3 flex items-center gap-3 border-r">
                {/* Indicateur couleur chantier */}
                <div
                  className="w-3 h-12 rounded-full flex-shrink-0"
                  style={{ backgroundColor: chantier.couleur || '#3498DB' }}
                />

                {/* Info chantier */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-gray-900 truncate">
                      {chantier.code} - {chantier.nom}
                    </span>
                  </div>
                  <div className="flex items-center gap-2 mt-1">
                    <span
                      className="text-xs px-1.5 py-0.5 rounded"
                      style={{
                        backgroundColor: statutInfo.color + '20',
                        color: statutInfo.color
                      }}
                    >
                      {statutInfo.label}
                    </span>
                    {userCount > 0 && (
                      <span className="flex items-center gap-1 text-xs text-gray-500">
                        <Users className="w-3 h-3" />
                        {userCount}
                      </span>
                    )}
                  </div>
                  {chantier.adresse && (
                    <div className="flex items-center gap-1 text-xs text-gray-400 mt-1 truncate">
                      <MapPin className="w-3 h-3 flex-shrink-0" />
                      <span className="truncate">{chantier.adresse}</span>
                    </div>
                  )}
                </div>

                {/* Actions */}
                <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      onDuplicateChantier(chantier.id)
                    }}
                    className="p-1 rounded hover:bg-gray-200"
                    title="Dupliquer les affectations vers la semaine suivante"
                  >
                    <Copy className="w-4 h-4 text-gray-500" />
                  </button>
                </div>
              </div>

              {/* Cellules des jours */}
              {days.map(day => {
                const cellAffectations = getAffectationsForCell(chantier.id, day)
                const hasAffectations = cellAffectations.length > 0
                const cellKey = `${chantier.id}-${format(day, 'yyyy-MM-dd')}`
                const isDragOver = dragOverCell === cellKey

                return (
                  <div
                    key={day.toISOString()}
                    tabIndex={0}
                    role="gridcell"
                    aria-label={`${chantier.nom}, ${format(day, 'EEEE d MMMM', { locale: fr })}`}
                    onClick={() => !hasAffectations && onCellClick(chantier.id, day)}
                    onDoubleClick={() => onCellClick(chantier.id, day)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault()
                        onCellClick(chantier.id, day)
                      }
                    }}
                    onDragOver={(e) => handleDragOver(e, cellKey)}
                    onDragLeave={handleDragLeave}
                    onDrop={(e) => handleDrop(e, chantier.id, day)}
                    className={`p-1 border-r last:border-r-0 min-h-[80px] transition-colors focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary-500 ${
                      isToday(day) ? 'bg-primary-50/50' : ''
                    } ${
                      isDragOver ? 'bg-blue-100 ring-2 ring-inset ring-blue-400' : ''
                    } ${
                      !hasAffectations ? 'cursor-pointer hover:bg-gray-100' : ''
                    }`}
                  >
                    <div className="space-y-1">
                      {cellAffectations.map(aff => (
                        <div
                          key={aff.id}
                          className={`rounded-lg px-2 py-1.5 text-xs cursor-pointer hover:opacity-90 transition-opacity ${!!onAffectationMove ? 'cursor-grab active:cursor-grabbing' : ''}`}
                          style={{ backgroundColor: aff.utilisateur_couleur || '#607D8B' }}
                          onClick={(e) => {
                            e.stopPropagation()
                            onAffectationClick(aff)
                          }}
                          draggable={!!onAffectationMove}
                          onDragStart={(e) => handleDragStart(e, aff)}
                          onDragEnd={handleDragEnd}
                        >
                          <div className="flex items-center gap-1 text-white">
                            {/* Avatar initiales */}
                            <div className="w-5 h-5 rounded-full bg-white/20 flex items-center justify-center text-[10px] font-semibold flex-shrink-0">
                              {aff.utilisateur_nom?.split(' ').map(n => n[0]).join('').slice(0, 2) || '?'}
                            </div>
                            <span className="font-medium truncate">
                              {aff.utilisateur_nom || 'Utilisateur'}
                            </span>
                          </div>
                          {aff.heure_debut && aff.heure_fin && (
                            <div className="text-white/80 text-[10px] ml-6">
                              {aff.heure_debut} - {aff.heure_fin}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )
              })}
            </div>
          )
        })}
      </div>

      {/* Message si aucun chantier */}
      {chantiers.length === 0 && (
        <div className="p-8 text-center text-gray-500">
          Aucun chantier a afficher
        </div>
      )}
    </div>
  )
}
