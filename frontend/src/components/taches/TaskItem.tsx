/**
 * Composant TaskItem - Element de tache avec chevrons repliables (TAC-03)
 * Affiche une tache avec sa structure hierarchique et code couleur (TAC-20)
 */

import { useState } from 'react'
import {
  ChevronDown,
  ChevronRight,
  CheckCircle,
  Circle,
  Clock,
  Calendar,
  MoreVertical,
  Edit,
  Trash2,
  Plus,
  GripVertical,
} from 'lucide-react'
import { formatDateDayMonthShort } from '../../utils/dates'
import type { Tache, UniteMesure } from '../../types'
import { UNITES_MESURE, COULEURS_PROGRESSION } from '../../types'

interface TaskItemProps {
  tache: Tache
  level?: number
  onToggleComplete: (tacheId: number, terminer: boolean) => void
  onEdit: (tache: Tache) => void
  onDelete: (tacheId: number) => void
  onAddSubtask: (parentId: number) => void
  isDragging?: boolean
  dragHandleProps?: object
}

export default function TaskItem({
  tache,
  level = 0,
  onToggleComplete,
  onEdit,
  onDelete,
  onAddSubtask,
  isDragging = false,
  dragHandleProps,
}: TaskItemProps) {
  // TAC-03: Chevrons repliables pour les sous-taches
  const [isExpanded, setIsExpanded] = useState(true)
  const [showMenu, setShowMenu] = useState(false)

  const hasSousTaches = tache.sous_taches && tache.sous_taches.length > 0
  const couleurInfo = COULEURS_PROGRESSION[tache.couleur_progression]
  const paddingLeft = level * 24

  // Calcul de la progression
  const progressionHeures = tache.heures_estimees
    ? Math.min((tache.heures_realisees / tache.heures_estimees) * 100, 100)
    : 0
  const progressionQuantite = tache.quantite_estimee
    ? Math.min((tache.quantite_realisee / tache.quantite_estimee) * 100, 100)
    : 0

  return (
    <div className={`${isDragging ? 'opacity-50' : ''}`}>
      {/* Ligne principale de la tache */}
      <div
        className={`group flex items-center gap-2 py-2 px-3 rounded-lg hover:bg-gray-50 transition-colors ${
          tache.est_terminee ? 'opacity-60' : ''
        }`}
        style={{
          paddingLeft: `${paddingLeft + 12}px`,
          borderLeft: level > 0 ? '2px solid #E5E7EB' : 'none',
          marginLeft: level > 0 ? '12px' : '0',
        }}
      >
        {/* Drag handle (TAC-15) */}
        {dragHandleProps && (
          <div
            {...dragHandleProps}
            className="cursor-grab text-gray-400 hover:text-gray-600 opacity-0 group-hover:opacity-100 transition-opacity"
          >
            <GripVertical className="w-4 h-4" />
          </div>
        )}

        {/* Chevron repliable (TAC-03) */}
        {hasSousTaches ? (
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-1 text-gray-400 hover:text-gray-600 rounded"
            title={isExpanded ? 'Replier' : 'Derouler'}
          >
            {isExpanded ? (
              <ChevronDown className="w-4 h-4" />
            ) : (
              <ChevronRight className="w-4 h-4" />
            )}
          </button>
        ) : (
          <div className="w-6" />
        )}

        {/* Checkbox statut (TAC-13) */}
        <button
          onClick={() => onToggleComplete(tache.id, !tache.est_terminee)}
          className={`p-1 rounded transition-colors ${
            tache.est_terminee
              ? 'text-green-500 hover:text-green-600'
              : 'text-gray-400 hover:text-gray-600'
          }`}
          title={tache.est_terminee ? 'Marquer a faire' : 'Marquer termine'}
        >
          {tache.est_terminee ? (
            <CheckCircle className="w-5 h-5" />
          ) : (
            <Circle className="w-5 h-5" />
          )}
        </button>

        {/* Indicateur couleur progression (TAC-20) */}
        <div
          className="w-2 h-2 rounded-full shrink-0"
          style={{ backgroundColor: couleurInfo.color }}
          title={couleurInfo.label}
        />

        {/* Titre et infos */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span
              className={`font-medium truncate ${
                tache.est_terminee ? 'line-through text-gray-500' : 'text-gray-900'
              }`}
            >
              {tache.titre}
            </span>
            {/* Badge sous-taches */}
            {hasSousTaches && (
              <span className="text-xs bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded">
                {tache.nombre_sous_taches_terminees}/{tache.nombre_sous_taches}
              </span>
            )}
          </div>

          {/* Infos secondaires - responsive (TAC-17) */}
          <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-gray-500 mt-0.5">
            {/* Date echeance (TAC-08) */}
            {tache.date_echeance && (
              <span
                className={`flex items-center gap-1 ${
                  tache.est_en_retard ? 'text-red-500' : ''
                }`}
              >
                <Calendar className="w-3 h-3" />
                {formatDateDayMonthShort(tache.date_echeance)}
              </span>
            )}

            {/* Heures (TAC-11, TAC-12) */}
            {tache.heures_estimees && (
              <span className="flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {tache.heures_realisees.toFixed(1)}/{tache.heures_estimees}h
              </span>
            )}

            {/* Quantite (TAC-09, TAC-10) */}
            {tache.quantite_estimee && tache.unite_mesure && (
              <span>
                {tache.quantite_realisee.toFixed(1)}/{tache.quantite_estimee}{' '}
                {UNITES_MESURE[tache.unite_mesure as UniteMesure]?.symbol || tache.unite_mesure}
              </span>
            )}
          </div>
        </div>

        {/* Barre de progression */}
        {(tache.heures_estimees || tache.quantite_estimee) && (
          <div className="hidden sm:block w-20 h-1.5 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full rounded-full transition-all"
              style={{
                width: `${progressionHeures || progressionQuantite}%`,
                backgroundColor: couleurInfo.color,
              }}
            />
          </div>
        )}

        {/* Actions */}
        <div className="relative">
          <button
            onClick={() => setShowMenu(!showMenu)}
            className="p-1 text-gray-400 hover:text-gray-600 rounded opacity-0 group-hover:opacity-100 transition-opacity"
          >
            <MoreVertical className="w-4 h-4" />
          </button>

          {showMenu && (
            <>
              <div
                className="fixed inset-0 z-10"
                onClick={() => setShowMenu(false)}
              />
              <div className="absolute right-0 top-full mt-1 bg-white rounded-lg shadow-lg border py-1 z-20 min-w-[160px]">
                <button
                  onClick={() => {
                    onAddSubtask(tache.id)
                    setShowMenu(false)
                  }}
                  className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-700 hover:bg-gray-50"
                >
                  <Plus className="w-4 h-4" />
                  Ajouter sous-tache
                </button>
                <button
                  onClick={() => {
                    onEdit(tache)
                    setShowMenu(false)
                  }}
                  className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-700 hover:bg-gray-50"
                >
                  <Edit className="w-4 h-4" />
                  Modifier
                </button>
                <button
                  onClick={() => {
                    onDelete(tache.id)
                    setShowMenu(false)
                  }}
                  className="w-full flex items-center gap-2 px-3 py-2 text-sm text-red-600 hover:bg-red-50"
                >
                  <Trash2 className="w-4 h-4" />
                  Supprimer
                </button>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Sous-taches (TAC-02) - affichees si deroulees */}
      {hasSousTaches && isExpanded && (
        <div className="ml-2">
          {tache.sous_taches.map((sousTache) => (
            <TaskItem
              key={sousTache.id}
              tache={sousTache}
              level={level + 1}
              onToggleComplete={onToggleComplete}
              onEdit={onEdit}
              onDelete={onDelete}
              onAddSubtask={onAddSubtask}
            />
          ))}
        </div>
      )}
    </div>
  )
}
