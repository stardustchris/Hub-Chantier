import { ChevronLeft, ChevronRight, Download } from 'lucide-react'
import { format, startOfWeek, endOfWeek, getISOWeek, addWeeks, subWeeks } from 'date-fns'
import { fr } from 'date-fns/locale'

interface TimesheetWeekNavigationProps {
  currentDate: Date
  onDateChange: (date: Date) => void
  onExport?: () => void
  isExporting?: boolean
}

export default function TimesheetWeekNavigation({
  currentDate,
  onDateChange,
  onExport,
  isExporting,
}: TimesheetWeekNavigationProps) {
  const weekStart = startOfWeek(currentDate, { weekStartsOn: 1 })
  const weekEnd = endOfWeek(currentDate, { weekStartsOn: 1 })
  const weekNumber = getISOWeek(currentDate)
  const year = weekStart.getFullYear()

  const handlePrev = () => {
    onDateChange(subWeeks(currentDate, 1))
  }

  const handleNext = () => {
    onDateChange(addWeeks(currentDate, 1))
  }

  const handleToday = () => {
    onDateChange(new Date())
  }

  return (
    <div className="flex items-center justify-between bg-white rounded-lg shadow px-4 py-3">
      {/* Titre */}
      <div className="text-lg font-semibold text-gray-900">
        Feuilles d'heures
      </div>

      {/* Navigation temporelle */}
      <div className="flex items-center gap-3">
        <button
          onClick={handlePrev}
          className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
          title="Semaine precedente"
        >
          <ChevronLeft className="w-5 h-5 text-gray-600" />
        </button>

        <div className="text-center min-w-[220px]">
          <div className="text-sm text-gray-500">Semaine {weekNumber} - {year}</div>
          <div className="font-medium">
            {format(weekStart, 'd', { locale: fr })} -{' '}
            {format(weekEnd, 'd MMMM yyyy', { locale: fr })}
          </div>
        </div>

        <button
          onClick={handleNext}
          className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
          title="Semaine suivante"
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

      {/* Actions */}
      <div className="flex items-center gap-2">
        {onExport && (
          <button
            onClick={onExport}
            disabled={isExporting}
            className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors disabled:opacity-50"
          >
            <Download className="w-4 h-4" />
            {isExporting ? 'Export...' : 'Exporter'}
          </button>
        )}
      </div>
    </div>
  )
}
