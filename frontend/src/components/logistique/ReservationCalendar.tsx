/**
 * Composant ReservationCalendar - Calendrier des réservations d'une ressource
 *
 * LOG-03: Planning par ressource - Vue calendrier hebdomadaire 7 jours
 * LOG-04: Navigation semaine
 * LOG-05: Axe horaire vertical 08:00 → 18:00
 * LOG-06: Blocs réservation colorés
 */

import React, { useState, useEffect } from 'react'
import { ChevronLeft, ChevronRight, Calendar, Plus } from 'lucide-react'
import type { Ressource, Reservation, PlanningRessource } from '../../types/logistique'
import { STATUTS_RESERVATION } from '../../types/logistique'
import { getPlanningRessource, getLundiSemaine, formatDateISO } from '../../api/logistique'

interface ReservationCalendarProps {
  ressource: Ressource
  onCreateReservation?: (date: string, heureDebut: string, heureFin: string) => void
  onSelectReservation?: (reservation: Reservation) => void
}

const HEURES = Array.from({ length: 11 }, (_, i) => `${String(8 + i).padStart(2, '0')}:00`)
const JOURS_SEMAINE = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']

const ReservationCalendar: React.FC<ReservationCalendarProps> = ({
  ressource,
  onCreateReservation,
  onSelectReservation,
}) => {
  const [currentDate, setCurrentDate] = useState(getLundiSemaine(new Date()))
  const [planning, setPlanning] = useState<PlanningRessource | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadPlanning()
  }, [ressource.id, currentDate])

  const loadPlanning = async () => {
    try {
      setLoading(true)
      const dateFin = new Date(currentDate)
      dateFin.setDate(dateFin.getDate() + 6)
      const data = await getPlanningRessource(
        ressource.id,
        formatDateISO(currentDate),
        formatDateISO(dateFin)
      )
      setPlanning(data)
    } catch (err) {
      console.error('Erreur chargement planning:', err)
    } finally {
      setLoading(false)
    }
  }

  const goToPreviousWeek = () => {
    const newDate = new Date(currentDate)
    newDate.setDate(newDate.getDate() - 7)
    setCurrentDate(newDate)
  }

  const goToNextWeek = () => {
    const newDate = new Date(currentDate)
    newDate.setDate(newDate.getDate() + 7)
    setCurrentDate(newDate)
  }

  const goToToday = () => {
    setCurrentDate(getLundiSemaine(new Date()))
  }

  const getWeekNumber = (date: Date): number => {
    const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()))
    const dayNum = d.getUTCDay() || 7
    d.setUTCDate(d.getUTCDate() + 4 - dayNum)
    const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1))
    return Math.ceil((((d.getTime() - yearStart.getTime()) / 86400000) + 1) / 7)
  }

  const getReservationsForDayAndHour = (dayIndex: number, heure: string): Reservation[] => {
    if (!planning) return []
    const dateStr = planning.jours[dayIndex]
    return planning.reservations.filter((r) => {
      if (r.date_reservation !== dateStr) return false
      const heureNum = parseInt(heure.split(':')[0])
      const debutNum = parseInt(r.heure_debut.split(':')[0])
      const finNum = parseInt(r.heure_fin.split(':')[0])
      return heureNum >= debutNum && heureNum < finNum
    })
  }

  const handleCellClick = (dayIndex: number, heure: string) => {
    if (!planning || !onCreateReservation) return
    const dateStr = planning.jours[dayIndex]
    const heureDebut = heure
    const heureFin = `${String(parseInt(heure.split(':')[0]) + 1).padStart(2, '0')}:00`
    onCreateReservation(dateStr, heureDebut, heureFin)
  }

  const formatDayHeader = (dayIndex: number): { day: string; date: string } => {
    if (!planning) return { day: JOURS_SEMAINE[dayIndex], date: '' }
    const dateStr = planning.jours[dayIndex]
    const date = new Date(dateStr)
    return {
      day: JOURS_SEMAINE[dayIndex],
      date: `${date.getDate()}/${date.getMonth() + 1}`,
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      {/* Header avec navigation */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <div className="flex items-center gap-2">
          <div
            className="w-4 h-4 rounded"
            style={{ backgroundColor: ressource.couleur }}
          />
          <h3 className="font-semibold text-gray-900">
            [{ressource.code}] {ressource.nom}
          </h3>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={goToPreviousWeek}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ChevronLeft size={20} />
          </button>

          <button
            onClick={goToToday}
            className="flex items-center gap-1 px-3 py-1.5 text-sm text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
          >
            <Calendar size={16} />
            <span>Aujourd'hui</span>
          </button>

          <span className="px-3 py-1.5 bg-gray-100 rounded-lg font-medium">
            Semaine {getWeekNumber(currentDate)}
          </span>

          <button
            onClick={goToNextWeek}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ChevronRight size={20} />
          </button>
        </div>
      </div>

      {/* Calendrier */}
      {loading ? (
        <div className="flex justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr>
                <th className="w-16 p-2 text-sm text-gray-500 bg-gray-50 border-b border-r border-gray-200">
                  Heure
                </th>
                {JOURS_SEMAINE.map((_, dayIndex) => {
                  const { day, date } = formatDayHeader(dayIndex)
                  return (
                    <th
                      key={dayIndex}
                      className="p-2 text-sm bg-gray-50 border-b border-r border-gray-200 last:border-r-0"
                    >
                      <div className="font-semibold text-gray-900">{day}</div>
                      <div className="text-gray-500">{date}</div>
                    </th>
                  )
                })}
              </tr>
            </thead>
            <tbody>
              {HEURES.map((heure) => (
                <tr key={heure}>
                  <td className="p-2 text-sm text-gray-500 text-center border-r border-b border-gray-200 bg-gray-50">
                    {heure}
                  </td>
                  {JOURS_SEMAINE.map((_, dayIndex) => {
                    const reservations = getReservationsForDayAndHour(dayIndex, heure)
                    const hasReservation = reservations.length > 0

                    return (
                      <td
                        key={dayIndex}
                        className={`relative h-12 border-r border-b border-gray-200 last:border-r-0 ${
                          !hasReservation && onCreateReservation
                            ? 'hover:bg-blue-50 cursor-pointer'
                            : ''
                        }`}
                        onClick={() => !hasReservation && handleCellClick(dayIndex, heure)}
                      >
                        {reservations.map((reservation) => (
                          <div
                            key={reservation.id}
                            onClick={(e) => {
                              e.stopPropagation()
                              onSelectReservation?.(reservation)
                            }}
                            className="absolute inset-1 rounded px-2 py-1 text-xs text-white cursor-pointer hover:opacity-90 transition-opacity flex items-center justify-between"
                            style={{ backgroundColor: reservation.ressource_couleur || ressource.couleur }}
                          >
                            <span className="truncate">
                              {reservation.demandeur_nom || `User #${reservation.demandeur_id}`}
                            </span>
                            <span
                              className="w-2 h-2 rounded-full flex-shrink-0"
                              style={{ backgroundColor: STATUTS_RESERVATION[reservation.statut].color }}
                              title={STATUTS_RESERVATION[reservation.statut].label}
                            />
                          </div>
                        ))}
                        {!hasReservation && onCreateReservation && (
                          <div className="absolute inset-0 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity">
                            <Plus size={16} className="text-blue-500" />
                          </div>
                        )}
                      </td>
                    )
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Légende */}
      <div className="flex items-center gap-4 p-3 bg-gray-50 border-t border-gray-200 text-xs">
        {Object.entries(STATUTS_RESERVATION).map(([key, info]) => (
          <div key={key} className="flex items-center gap-1">
            <span
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: info.color }}
            />
            <span className="text-gray-600">{info.label}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

export default ReservationCalendar
