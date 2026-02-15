import { useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { format, addDays, startOfWeek, isToday } from 'date-fns'
import { fr } from 'date-fns/locale'
import { Plus, Check, Clock, AlertCircle } from 'lucide-react'
import type { VueCompagnon, Pointage, StatutPointage } from '../../types'
import { STATUTS_POINTAGE, JOURS_SEMAINE_ARRAY } from '../../types'

interface TimesheetGridProps {
  currentDate: Date
  vueCompagnons: VueCompagnon[]
  onCellClick: (utilisateurId: number, chantierId: number | null, date: Date) => void
  onPointageClick: (pointage: Pointage) => void
  showWeekend?: boolean
  canEdit?: boolean
  // Batch selection
  enableBatchSelect?: boolean
  selectedPointageIds?: Set<number>
  onTogglePointage?: (id: number) => void
  onSelectAll?: () => void
  onDeselectAll?: () => void
  selectablePointageIds?: number[]
}

export default function TimesheetGrid({
  currentDate,
  vueCompagnons,
  onCellClick,
  onPointageClick,
  showWeekend = false,
  canEdit = false,
  enableBatchSelect = false,
  selectedPointageIds = new Set(),
  onTogglePointage,
  onSelectAll,
  onDeselectAll,
  selectablePointageIds = [],
}: TimesheetGridProps) {
  const navigate = useNavigate()

  // Vérifier si tous les pointages sélectionnables sont sélectionnés
  const allSelected = useMemo(() => {
    return selectablePointageIds.length > 0 &&
      selectablePointageIds.every((id) => selectedPointageIds.has(id))
  }, [selectablePointageIds, selectedPointageIds])

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
        {config.label}
      </span>
    )
  }

  // Rendu d'une cellule de pointage
  const renderPointageCell = (
    utilisateurId: number,
    chantierId: number,
    _chantierNom: string,
    _chantierCouleur: string | undefined,
    pointagesParJour: Record<string, Pointage[]>,
    jour: typeof jours[0]
  ) => {
    const pointagesJour = pointagesParJour[jour.jourNom] || []
    const pointage = pointagesJour[0] // On prend le premier pointage pour ce chantier/jour

    if (pointage) {
      const isEditable = pointage.is_editable !== false && canEdit
      const isSelectable = enableBatchSelect && pointage.statut === 'soumis'
      const isSelected = selectedPointageIds.has(pointage.id)

      return (
        <td
          key={jour.dateStr}
          className={`border px-2 py-1 text-center relative ${
            jour.isToday ? 'bg-primary-50' : ''
          } ${isSelected ? 'bg-primary-100' : ''} ${isEditable ? 'cursor-pointer hover:bg-gray-50' : ''}`}
          onClick={() => isEditable && onPointageClick(pointage)}
        >
          <div className="flex flex-col items-center gap-1">
            {/* Checkbox pour sélection */}
            {isSelectable && onTogglePointage && (
              <input
                type="checkbox"
                checked={isSelected}
                onChange={(e) => {
                  e.stopPropagation()
                  onTogglePointage(pointage.id)
                }}
                onClick={(e) => e.stopPropagation()}
                className="absolute top-1 left-1 w-5 h-5 min-w-[20px] min-h-[20px] rounded border-gray-300 text-primary-600 focus:ring-primary-500 cursor-pointer"
                aria-label={`Sélectionner le pointage du ${jour.label}`}
              />
            )}
            <span className="font-medium text-gray-900">
              {pointage.total_heures || '00:00'}
            </span>
            {pointage.heures_supplementaires && pointage.heures_supplementaires !== '00:00' && (
              <span className="text-xs text-orange-600">
                +{pointage.heures_supplementaires}
              </span>
            )}
            {renderStatutBadge(pointage.statut)}
          </div>
        </td>
      )
    }

    // Cellule vide - permettre l'ajout
    return (
      <td
        key={jour.dateStr}
        className={`border px-2 py-1 text-center ${
          jour.isToday ? 'bg-primary-50' : 'bg-gray-50'
        } ${canEdit ? 'cursor-pointer hover:bg-gray-100 group' : ''}`}
        onClick={() => canEdit && onCellClick(utilisateurId, chantierId, jour.date)}
      >
        {canEdit && (
          <Plus className="w-4 h-4 text-gray-600 mx-auto opacity-0 group-hover:opacity-100 transition-opacity" />
        )}
      </td>
    )
  }

  // Rendu d'une ligne vide pour ajouter un nouveau chantier
  const renderAddChantierRow = (utilisateurId: number) => {
    if (!canEdit) return null

    return (
      <tr className="bg-gray-50/50">
        {enableBatchSelect && selectablePointageIds.length > 0 && (
          <td className="border" />
        )}
        <td className="border px-3 py-2 text-sm text-gray-500 italic">
          <button
            onClick={() => onCellClick(utilisateurId, null, jours[0].date)}
            className="flex items-center gap-1 text-primary-600 hover:text-primary-700"
          >
            <Plus className="w-4 h-4" />
            Ajouter un chantier
          </button>
        </td>
        {jours.map((jour) => (
          <td
            key={jour.dateStr}
            className={`border px-2 py-1 ${jour.isToday ? 'bg-primary-50' : ''}`}
          />
        ))}
        <td className="border px-3 py-2" />
      </tr>
    )
  }

  if (vueCompagnons.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-8 text-center">
        <Clock className="w-12 h-12 text-gray-600 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Aucune donnee</h3>
        <p className="text-gray-600">
          Aucun pointage pour cette semaine. Selectionnez des utilisateurs ou ajoutez des pointages.
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
              {enableBatchSelect && selectablePointageIds.length > 0 && (
                <th className="border px-3 py-2 text-center w-12">
                  <input
                    type="checkbox"
                    checked={allSelected}
                    onChange={() => {
                      if (allSelected && onDeselectAll) {
                        onDeselectAll()
                      } else if (onSelectAll) {
                        onSelectAll()
                      }
                    }}
                    className="w-5 h-5 min-w-[20px] min-h-[20px] rounded border-gray-300 text-primary-600 focus:ring-primary-500 cursor-pointer"
                    aria-label="Tout sélectionner"
                    title={allSelected ? 'Tout désélectionner' : 'Tout sélectionner'}
                  />
                </th>
              )}
              <th className="border px-3 py-2 text-left text-sm font-medium text-gray-700 w-48">
                Chantier
              </th>
              {jours.map((jour) => (
                <th
                  key={jour.dateStr}
                  className={`border px-3 py-2 text-center text-sm font-medium min-w-[100px] ${
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
            {vueCompagnons.map((compagnon) => (
              <>
                {/* Ligne d'en-tete utilisateur */}
                <tr key={`user-${compagnon.utilisateur_id}`} className="bg-gray-50">
                  {enableBatchSelect && selectablePointageIds.length > 0 && (
                    <td className="border" />
                  )}
                  <td
                    colSpan={jours.length + 2}
                    className="border px-3 py-2 font-medium text-gray-900"
                  >
                    <div className="flex items-center justify-between">
                      <span
                        className="cursor-pointer text-primary-600 hover:text-primary-800"
                        onClick={() => navigate(`/utilisateurs/${compagnon.utilisateur_id}`)}
                      >
                        {compagnon.utilisateur_nom}
                      </span>
                      <span className="text-sm font-normal text-gray-600">
                        Total: {compagnon.total_heures} ({compagnon.total_heures_decimal}h)
                      </span>
                    </div>
                  </td>
                </tr>

                {/* Lignes par chantier */}
                {compagnon.chantiers.map((chantier) => (
                  <tr key={`${compagnon.utilisateur_id}-${chantier.chantier_id}`}>
                    {enableBatchSelect && selectablePointageIds.length > 0 && (
                      <td className="border" />
                    )}
                    <td
                      className="border px-3 py-2 cursor-pointer hover:bg-gray-50 transition-colors"
                      onClick={() => navigate(`/chantiers/${chantier.chantier_id}`)}
                    >
                      <div className="flex items-center gap-2">
                        <span
                          className="w-3 h-3 rounded-full flex-shrink-0"
                          style={{ backgroundColor: chantier.chantier_couleur || '#9E9E9E' }}
                        />
                        <span className="text-sm font-medium text-primary-600 hover:text-primary-800 truncate">
                          {chantier.chantier_nom}
                        </span>
                      </div>
                    </td>
                    {jours.map((jour) =>
                      renderPointageCell(
                        compagnon.utilisateur_id,
                        chantier.chantier_id,
                        chantier.chantier_nom,
                        chantier.chantier_couleur,
                        chantier.pointages_par_jour,
                        jour
                      )
                    )}
                    <td className="border px-3 py-2 text-center font-medium text-gray-900">
                      {chantier.total_heures}
                    </td>
                  </tr>
                ))}

                {/* Ligne pour ajouter un chantier */}
                {renderAddChantierRow(compagnon.utilisateur_id)}

                {/* Ligne totaux par jour pour l'utilisateur */}
                <tr className="bg-gray-100">
                  {enableBatchSelect && selectablePointageIds.length > 0 && (
                    <td className="border" />
                  )}
                  <td className="border px-3 py-2 text-sm font-medium text-gray-700">
                    Total journalier
                  </td>
                  {jours.map((jour) => (
                    <td
                      key={`total-${jour.dateStr}`}
                      className={`border px-3 py-2 text-center text-sm font-medium ${
                        jour.isToday ? 'bg-primary-100' : ''
                      }`}
                    >
                      {compagnon.totaux_par_jour[jour.jourNom] || '00:00'}
                    </td>
                  ))}
                  <td className="border px-3 py-2 text-center font-bold text-gray-900">
                    {compagnon.total_heures}
                  </td>
                </tr>
              </>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
