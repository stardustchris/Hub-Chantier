/**
 * TodayPlanningCard - Carte planning du jour
 * CDC Section 2.3.2 - Planning de la journee
 * Affiche les affectations réelles de l'utilisateur connecté depuis le planning
 */

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Calendar, MapPin, CheckCircle, Navigation, Phone, CalendarX, Loader2, Users, ChevronDown } from 'lucide-react'

interface Task {
  id: string
  name: string
  priority: 'urgent' | 'high' | 'medium' | 'low'
}

interface PlanningSlot {
  id: string
  chantierId?: string
  startTime: string
  endTime: string
  period: 'morning' | 'afternoon' | 'break'
  siteName?: string
  siteAddress?: string
  status?: 'in_progress' | 'planned' | 'completed'
  tasks?: Task[]
  isPersonalAffectation?: boolean // true si l'utilisateur est personnellement affecté
}

interface TodayPlanningCardProps {
  slots?: PlanningSlot[]
  isLoading?: boolean
  onNavigate?: (slotId: string) => void
  onCall?: (slotId: string) => void
  onChantierClick?: (chantierId: string) => void
}

const priorityStyles = {
  urgent: { bg: 'bg-red-100', text: 'text-red-700', dot: 'bg-red-500', label: 'Urgent' },
  high: { bg: 'bg-orange-100', text: 'text-orange-700', dot: 'bg-orange-500', label: 'Haute' },
  medium: { bg: 'bg-orange-100', text: 'text-orange-700', dot: 'bg-orange-500', label: 'Moyenne' },
  low: { bg: 'bg-blue-100', text: 'text-blue-700', dot: 'bg-blue-500', label: 'Basse' },
}

const statusStyles = {
  in_progress: { bg: 'bg-green-100', text: 'text-green-700', label: 'En cours' },
  planned: { bg: 'bg-blue-100', text: 'text-blue-700', label: 'Planifie' },
  completed: { bg: 'bg-gray-100', text: 'text-gray-700', label: 'Termine' },
}

const periodStyles = {
  morning: { border: 'border-orange-500', bg: 'bg-orange-50', badge: 'bg-orange-500' },
  afternoon: { border: 'border-blue-500', bg: 'bg-blue-50', badge: 'bg-blue-500' },
  break: { border: 'border-gray-400', bg: 'bg-gray-50', badge: 'bg-gray-400' },
}

/** Nombre de chantiers affichés initialement */
const INITIAL_DISPLAY_COUNT = 3

export default function TodayPlanningCard({
  slots = [],
  isLoading = false,
  onNavigate,
  onCall,
  onChantierClick,
}: TodayPlanningCardProps) {
  const navigate = useNavigate()
  const [showAll, setShowAll] = useState(false)

  // Filtrer les slots de chantiers (exclure les pauses)
  const chantierSlots = slots.filter(s => s.period !== 'break')
  const breakSlots = slots.filter(s => s.period === 'break')

  // Slots à afficher (limités si showAll est false)
  const displayedChantierSlots = showAll ? chantierSlots : chantierSlots.slice(0, INITIAL_DISPLAY_COUNT)
  const hasMore = chantierSlots.length > INITIAL_DISPLAY_COUNT && !showAll

  // Reconstruire les slots avec les pauses au bon endroit
  const displayedSlots = [...displayedChantierSlots]
  // Ajouter les pauses seulement si on affiche des slots matin ET après-midi
  const hasMorning = displayedChantierSlots.some(s => s.period === 'morning')
  const hasAfternoon = displayedChantierSlots.some(s => s.period === 'afternoon')
  if (hasMorning && hasAfternoon && breakSlots.length > 0) {
    // Insérer la pause entre matin et après-midi
    const morningSlots = displayedChantierSlots.filter(s => s.period === 'morning')
    const afternoonSlots = displayedChantierSlots.filter(s => s.period === 'afternoon')
    displayedSlots.length = 0
    displayedSlots.push(...morningSlots, ...breakSlots, ...afternoonSlots)
  }

  const handleChantierClick = (slot: PlanningSlot) => {
    if (onChantierClick && slot.chantierId) {
      onChantierClick(slot.chantierId)
    } else if (slot.chantierId) {
      navigate(`/chantiers/${slot.chantierId}`)
    }
  }

  return (
    <div className="bg-white rounded-2xl p-5 shadow-lg">
      <div className="flex items-center justify-between mb-4">
        <h2 className="font-semibold text-gray-800 flex items-center gap-2">
          <Calendar className="w-5 h-5 text-green-600" />
          Mon planning aujourd'hui
        </h2>
        <a href="/planning" className="text-sm text-green-600 hover:text-green-700 font-medium">
          Voir semaine →
        </a>
      </div>

      {/* État de chargement */}
      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-green-600" />
        </div>
      )}

      {/* Aucune affectation */}
      {!isLoading && slots.length === 0 && (
        <div className="text-center py-12">
          <CalendarX className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500 font-medium">Aucune affectation aujourd'hui</p>
          <p className="text-sm text-gray-400 mt-1">
            Consultez le planning pour voir vos prochaines affectations
          </p>
          <a
            href="/planning"
            className="inline-block mt-4 text-green-600 hover:text-green-700 font-medium text-sm"
          >
            Voir le planning →
          </a>
        </div>
      )}

      {/* Liste des slots */}
      {!isLoading && slots.length > 0 && (
        <div className="space-y-4">
          {displayedSlots.map((slot) => {
          const period = periodStyles[slot.period]

          if (slot.period === 'break') {
            return (
              <div key={slot.id} className="flex items-center gap-3 py-3 px-4 bg-gray-50 rounded-xl">
                <span className={`text-xs px-2 py-1 rounded-md font-semibold ${period.badge} text-white`}>
                  {slot.startTime} - {slot.endTime}
                </span>
                <span className="text-sm text-gray-600">Pause dejeuner</span>
              </div>
            )
          }

          const status = slot.status ? statusStyles[slot.status] : null

          return (
            <div
              key={slot.id}
              onClick={() => handleChantierClick(slot)}
              className={`border-l-4 ${period.border} rounded-xl ${period.bg} p-4 cursor-pointer hover:shadow-md transition-shadow`}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => e.key === 'Enter' && handleChantierClick(slot)}
            >
              <div className="flex items-start justify-between mb-2">
                <div>
                  <span className={`text-xs px-2 py-1 rounded-md font-semibold ${period.badge} text-white`}>
                    {slot.startTime} - {slot.endTime}
                  </span>
                  <span className="ml-2 text-sm text-gray-600">
                    {slot.period === 'morning' ? 'Matin' : 'Apres-midi'}
                  </span>
                </div>
                {status && (
                  <span className={`text-xs px-3 py-1 rounded-full font-medium ${status.bg} ${status.text}`}>
                    {status.label}
                  </span>
                )}
              </div>

              <div className="flex items-center gap-2">
                <h3 className="font-semibold text-gray-900 text-lg">
                  {slot.siteName}
                </h3>
                {slot.isPersonalAffectation === false && (
                  <span className="inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full bg-purple-100 text-purple-700">
                    <Users className="w-3 h-3" />
                    Equipe
                  </span>
                )}
              </div>
              {slot.siteAddress && (
                <p className="text-sm text-gray-600 flex items-center gap-1 mt-1">
                  <MapPin className="w-4 h-4 text-red-500" />
                  {slot.siteAddress}
                </p>
              )}

              {slot.tasks && slot.tasks.length > 0 && (
                <div className="mt-3">
                  <p className="text-sm text-gray-600 flex items-center gap-1 mb-2">
                    <CheckCircle className="w-4 h-4" />
                    Taches assignees :
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {slot.tasks.map((task) => {
                      const priority = priorityStyles[task.priority]
                      return (
                        <span key={task.id} className="inline-flex items-center gap-1 text-sm">
                          <span className={`w-2 h-2 rounded-full ${priority.dot}`} />
                          {task.name}
                          <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${priority.bg} ${priority.text}`}>
                            {priority.label}
                          </span>
                        </span>
                      )
                    })}
                  </div>
                </div>
              )}

              <div className="grid grid-cols-2 gap-3 mt-4">
                <button
                  onClick={(e) => { e.stopPropagation(); onNavigate?.(slot.id) }}
                  className="bg-green-600 text-white py-2 px-4 rounded-xl flex items-center justify-center gap-2 hover:bg-green-700 font-medium"
                >
                  <Navigation className="w-4 h-4" />
                  Itineraire
                </button>
                <button
                  onClick={(e) => { e.stopPropagation(); onCall?.(slot.id) }}
                  className="border-2 border-gray-200 py-2 px-4 rounded-xl flex items-center justify-center gap-2 hover:bg-gray-50 font-medium"
                >
                  <Phone className="w-4 h-4" />
                  Appeler chef
                </button>
              </div>
            </div>
          )
        })}

          {/* Bouton Voir plus */}
          {hasMore && (
            <button
              onClick={() => setShowAll(true)}
              className="w-full flex items-center justify-center gap-1 py-2 text-sm text-green-600 hover:text-green-700 font-medium hover:bg-green-50 rounded-lg transition-colors"
            >
              <ChevronDown className="w-4 h-4" />
              Voir plus ({chantierSlots.length - INITIAL_DISPLAY_COUNT} autres)
            </button>
          )}
        </div>
      )}
    </div>
  )
}
