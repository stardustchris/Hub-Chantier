/**
 * TodayPlanningCard - Carte planning du jour
 * CDC Section 2.3.2 - Planning de la journee
 */

import { Calendar, MapPin, CheckCircle, Navigation, Phone } from 'lucide-react'

interface Task {
  id: string
  name: string
  priority: 'urgent' | 'high' | 'medium' | 'low'
}

interface PlanningSlot {
  id: string
  startTime: string
  endTime: string
  period: 'morning' | 'afternoon' | 'break'
  siteName?: string
  siteAddress?: string
  status?: 'in_progress' | 'planned' | 'completed'
  tasks?: Task[]
}

interface TodayPlanningCardProps {
  slots?: PlanningSlot[]
  onNavigate?: (slotId: string) => void
  onCall?: (slotId: string) => void
}

const defaultSlots: PlanningSlot[] = [
  {
    id: '1',
    startTime: '08:00',
    endTime: '12:00',
    period: 'morning',
    siteName: 'Villa Moderne - Lyon 3eme',
    siteAddress: '45 rue de la Republique, Lyon 3eme',
    status: 'in_progress',
    tasks: [{ id: '1', name: 'Coulage dalle beton - Zone A', priority: 'urgent' }],
  },
  {
    id: '2',
    startTime: '12:00',
    endTime: '13:30',
    period: 'break',
  },
  {
    id: '3',
    startTime: '13:30',
    endTime: '17:00',
    period: 'afternoon',
    siteName: 'Villa Moderne - Lyon 3eme',
    siteAddress: 'Meme adresse',
    status: 'planned',
    tasks: [{ id: '2', name: 'Montage murs porteurs', priority: 'medium' }],
  },
]

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

export default function TodayPlanningCard({
  slots = defaultSlots,
  onNavigate,
  onCall,
}: TodayPlanningCardProps) {
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

      <div className="space-y-4">
        {slots.map((slot) => {
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
            <div key={slot.id} className={`border-l-4 ${period.border} rounded-xl ${period.bg} p-4`}>
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

              <h3 className="font-semibold text-gray-900 text-lg">{slot.siteName}</h3>
              <p className="text-sm text-gray-600 flex items-center gap-1 mt-1">
                <MapPin className="w-4 h-4 text-red-500" />
                {slot.siteAddress}
              </p>

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
                  onClick={() => onNavigate?.(slot.id)}
                  className="bg-green-600 text-white py-2 px-4 rounded-xl flex items-center justify-center gap-2 hover:bg-green-700 font-medium"
                >
                  <Navigation className="w-4 h-4" />
                  Itineraire
                </button>
                <button
                  onClick={() => onCall?.(slot.id)}
                  className="border-2 border-gray-200 py-2 px-4 rounded-xl flex items-center justify-center gap-2 hover:bg-gray-50 font-medium"
                >
                  <Phone className="w-4 h-4" />
                  Appeler
                </button>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
