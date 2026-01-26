import { useMemo } from 'react'
import { format, addDays, startOfWeek, isToday } from 'date-fns'
import { fr } from 'date-fns/locale'
import { Plus, Check, Clock, AlertCircle } from 'lucide-react'
import type { VueChantier, Pointage, StatutPointage } from '../../types'
import { STATUTS_POINTAGE, JOURS_SEMAINE_ARRAY } from '../../types'

interface TimesheetChantierGridProps {
  currentDate: Date
  vueChantiers: VueChantier[]
  onCellClick: (chantierId: number, date: Date) => void
  onPointageClick: (pointage: Pointage) => void
  showWeekend?: boolean
  canEdit?: boolean
}

export default function TimesheetChantierGrid({
  currentDate,
  vueChantiers,
  onCellClick,
  onPointageClick,
  showWeekend = false,
  canEdit = false,
}: TimesheetChantierGridProps) {
  // Calculer les jours de la semaine
  const jours = useMemo(() => {
    const weekStart = startOfWeek(currentDate, { weekStartsOn: 1 })
    const nbJours = showWeekend ? 7 : 5
    return Array.from({ length: nbJours }, (_, i) => {
      const date = addDays(weekStart, i)
      return {
        date,
        dateStr: format(date, 'yyyy-MM-dd'),
        jourNom: JOURS_SEMAINE_ARRAY[i],
        label: format(date, 'EEE d', { locale: fr }),
        isToday: isToday(date),
      }
    })
  }, [currentDate, showWeekend])

  // Rendu du statut
  const renderStatutBadge = (statut: StatutPointage) => {
    const config = STATUTS_POINTAGE[statut] || STATUTS_POINTAGE.brouillon
    return (
      <span
        className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-xs font-medium"
        style={{ backgroundColor: config.bgColor, color: config.color }}
      >
        {statut === 'valide' && <Check className="w-3 h-3" />}
        {statut === 'soumis' && <Clock className="w-3 h-3" />}
        {statut === 'rejete' && <AlertCircle className="w-3 h-3" />}
      </span>
    )
  }

  // Rendu des pointages d'une cellule (peut contenir plusieurs utilisateurs)
  const renderPointagesCell = (
    chantierId: number,
    pointagesParJour: Record<string, Pointage[]>,
    jour: typeof jours[0]
  ) => {
    const pointagesJour = pointagesParJour[jour.jourNom] || []

    if (pointagesJour.length === 0) {
      return (
        <td
          key={jour.dateStr}
          className={`border px-2 py-1 text-center ${
            jour.isToday ? 'bg-primary-50' : 'bg-gray-50'
          } ${canEdit ? 'cursor-pointer hover:bg-gray-100 group' : ''}`}
          onClick={() => canEdit && onCellClick(chantierId, jour.date)}
        >
          {canEdit && (
            <Plus className="w-4 h-4 text-gray-400 mx-auto opacity-0 group-hover:opacity-100 transition-opacity" />
          )}
        </td>
      )
    }

    return (
      <td
        key={jour.dateStr}
        className={`border px-2 py-1 ${jour.isToday ? 'bg-primary-50' : ''}`}
      >
        <div className="space-y-1">
          {pointagesJour.map((pointage) => (
            <div
              key={pointage.id}
              className={`flex items-center justify-between gap-1 p-1 rounded text-xs ${
                pointage.is_editable !== false && canEdit
                  ? 'cursor-pointer hover:bg-gray-100'
                  : ''
              }`}
              onClick={() =>
                pointage.is_editable !== false && canEdit && onPointageClick(pointage)
              }
            >
              <span className="truncate text-gray-700" title={pointage.utilisateur_nom}>
                {pointage.utilisateur_nom?.split(' ')[0] || 'Utilisateur'}
              </span>
              <div className="flex items-center gap-1">
                <span className="font-medium text-gray-900">{pointage.total_heures}</span>
                {renderStatutBadge(pointage.statut)}
              </div>
            </div>
          ))}
        </div>
      </td>
    )
  }

  if (vueChantiers.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-8 text-center">
        <Clock className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Aucune donnee</h3>
        <p className="text-gray-600">
          Aucun pointage pour cette semaine sur les chantiers selectionnes.
        </p>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          <thead>
            <tr className="bg-gray-100">
              <th className="border px-3 py-2 text-left text-sm font-medium text-gray-700 w-56">
                Chantier
              </th>
              {jours.map((jour) => (
                <th
                  key={jour.dateStr}
                  className={`border px-3 py-2 text-center text-sm font-medium min-w-[140px] ${
                    jour.isToday ? 'bg-primary-100 text-primary-800' : 'text-gray-700'
                  }`}
                >
                  <div className="capitalize">{jour.label}</div>
                </th>
              ))}
              <th className="border px-3 py-2 text-center text-sm font-medium text-gray-700 w-24">
                Total
              </th>
            </tr>
          </thead>
          <tbody>
            {vueChantiers.map((chantier) => (
              <tr key={chantier.chantier_id}>
                <td className="border px-3 py-2">
                  <div className="flex items-center gap-2">
                    <span
                      className="w-3 h-3 rounded-full flex-shrink-0"
                      style={{ backgroundColor: chantier.chantier_couleur || '#9E9E9E' }}
                    />
                    <span className="text-sm font-medium text-gray-900 truncate">
                      {chantier.chantier_nom}
                    </span>
                  </div>
                </td>
                {jours.map((jour) =>
                  renderPointagesCell(chantier.chantier_id, chantier.pointages_par_jour, jour)
                )}
                <td className="border px-3 py-2 text-center">
                  <div className="font-medium text-gray-900">{chantier.total_heures}</div>
                  <div className="text-xs text-gray-500">
                    {chantier.total_heures_decimal}h
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
