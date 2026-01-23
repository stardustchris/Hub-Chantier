import { ChevronLeft, ChevronRight } from 'lucide-react'
import { format, startOfWeek, endOfWeek, getISOWeek, addWeeks, subWeeks, addMonths, subMonths } from 'date-fns'
import { fr } from 'date-fns/locale'

interface WeekNavigationProps {
  currentDate: Date
  onDateChange: (date: Date) => void
  viewMode: 'semaine' | 'mois'
  onViewModeChange: (mode: 'semaine' | 'mois') => void
}

export default function WeekNavigation({
  currentDate,
  onDateChange,
  viewMode,
  onViewModeChange,
}: WeekNavigationProps) {
  const weekStart = startOfWeek(currentDate, { weekStartsOn: 1 })
  const weekEnd = endOfWeek(currentDate, { weekStartsOn: 1 })
  const weekNumber = getISOWeek(currentDate)

  const handlePrev = () => {
    if (viewMode === 'mois') {
      onDateChange(subMonths(currentDate, 1))
    } else {
      onDateChange(subWeeks(currentDate, 1))
    }
  }

  const handleNext = () => {
    if (viewMode === 'mois') {
      onDateChange(addMonths(currentDate, 1))
    } else {
      onDateChange(addWeeks(currentDate, 1))
    }
  }

  const handleToday = () => {
    onDateChange(new Date())
  }

  return (
    <div className="flex items-center justify-between bg-white rounded-lg shadow px-4 py-3">
      {/* Sélecteur de période */}
      <div className="flex items-center gap-2">
        <button
          onClick={() => onViewModeChange('semaine')}
          className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
            viewMode === 'semaine'
              ? 'bg-primary-100 text-primary-700'
              : 'text-gray-600 hover:bg-gray-100'
          }`}
        >
          Semaine
        </button>
        <button
          onClick={() => onViewModeChange('mois')}
          className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
            viewMode === 'mois'
              ? 'bg-primary-100 text-primary-700'
              : 'text-gray-600 hover:bg-gray-100'
          }`}
        >
          Mois
        </button>
      </div>

      {/* Navigation temporelle */}
      <div className="flex items-center gap-3">
        <button
          onClick={handlePrev}
          className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
        >
          <ChevronLeft className="w-5 h-5 text-gray-600" />
        </button>

        <div className="text-center min-w-[200px]">
          {viewMode === 'mois' ? (
            <>
              <div className="text-sm text-gray-500">Mois</div>
              <div className="font-medium capitalize">
                {format(currentDate, 'MMMM yyyy', { locale: fr })}
              </div>
            </>
          ) : (
            <>
              <div className="text-sm text-gray-500">Semaine {weekNumber}</div>
              <div className="font-medium">
                {format(weekStart, 'd', { locale: fr })} -{' '}
                {format(weekEnd, 'd MMMM yyyy', { locale: fr })}
              </div>
            </>
          )}
        </div>

        <button
          onClick={handleNext}
          className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
        >
          <ChevronRight className="w-5 h-5 text-gray-600" />
        </button>

        <button
          onClick={handleToday}
          className="px-3 py-1.5 text-sm font-medium text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
        >
          Aujourd'hui
        </button>
      </div>

      {/* Espace réservé pour équilibrer */}
      <div className="w-[140px]" />
    </div>
  )
}
