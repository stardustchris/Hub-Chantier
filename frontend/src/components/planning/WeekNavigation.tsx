import { ChevronLeft, ChevronRight } from 'lucide-react'
import { format, startOfWeek, endOfWeek, getWeek } from 'date-fns'
import { fr } from 'date-fns/locale'

interface WeekNavigationProps {
  currentDate: Date
  onPrevWeek: () => void
  onNextWeek: () => void
  onToday: () => void
}

/**
 * Navigation temporelle pour le planning (PLN-09, PLN-10).
 */
export function WeekNavigation({ currentDate, onPrevWeek, onNextWeek, onToday }: WeekNavigationProps) {
  const weekStart = startOfWeek(currentDate, { weekStartsOn: 1 })
  const weekEnd = endOfWeek(currentDate, { weekStartsOn: 1 })
  const weekNumber = getWeek(currentDate, { weekStartsOn: 1 })

  const formatDate = (date: Date) => format(date, 'd MMM', { locale: fr })

  return (
    <div className="flex items-center gap-4">
      {/* Indicateur semaine (PLN-10) */}
      <span className="text-sm text-gray-500 font-medium">Semaine {weekNumber}</span>

      {/* Navigation temporelle (PLN-09) */}
      <div className="flex items-center gap-2">
        <button
          onClick={onPrevWeek}
          className="p-1 hover:bg-gray-100 rounded-md transition-colors"
          title="Semaine précédente"
        >
          <ChevronLeft className="w-5 h-5" />
        </button>

        <span className="text-sm font-medium min-w-[140px] text-center">
          {formatDate(weekStart)} - {formatDate(weekEnd)}
        </span>

        <button
          onClick={onNextWeek}
          className="p-1 hover:bg-gray-100 rounded-md transition-colors"
          title="Semaine suivante"
        >
          <ChevronRight className="w-5 h-5" />
        </button>
      </div>

      <button onClick={onToday} className="btn btn-outline text-sm py-1 px-3">
        Aujourd'hui
      </button>
    </div>
  )
}
