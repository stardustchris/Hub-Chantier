/**
 * PointageFormFields - Champs de saisie du formulaire de pointage
 */

import { Clock } from 'lucide-react'
import type { Chantier } from '../../types'

interface PointageFormFieldsProps {
  chantierId: number | ''
  setChantierId: (id: number | '') => void
  heuresNormales: string
  setHeuresNormales: (value: string) => void
  heuresSupplementaires: string
  setHeuresSupplementaires: (value: string) => void
  commentaire: string
  setCommentaire: (value: string) => void
  chantiers: Chantier[]
  isEditing: boolean
  isEditable: boolean
}

export function PointageFormFields({
  chantierId,
  setChantierId,
  heuresNormales,
  setHeuresNormales,
  heuresSupplementaires,
  setHeuresSupplementaires,
  commentaire,
  setCommentaire,
  chantiers,
  isEditing,
  isEditable,
}: PointageFormFieldsProps) {
  return (
    <>
      {/* Chantier */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Chantier *
        </label>
        <select
          value={chantierId}
          onChange={(e) => setChantierId(e.target.value ? Number(e.target.value) : '')}
          disabled={isEditing || !isEditable}
          className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 disabled:bg-gray-100"
        >
          <option value="">Selectionner un chantier</option>
          {chantiers.map((chantier) => (
            <option key={chantier.id} value={chantier.id}>
              {chantier.nom}
            </option>
          ))}
        </select>
      </div>

      {/* Heures */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Heures normales *
          </label>
          <div className="relative">
            <Clock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="time"
              value={heuresNormales}
              onChange={(e) => setHeuresNormales(e.target.value)}
              disabled={!isEditable}
              className="w-full pl-10 pr-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 disabled:bg-gray-100"
            />
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Heures sup.
          </label>
          <div className="relative">
            <Clock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-orange-400" />
            <input
              type="time"
              value={heuresSupplementaires}
              onChange={(e) => setHeuresSupplementaires(e.target.value)}
              disabled={!isEditable}
              className="w-full pl-10 pr-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 disabled:bg-gray-100"
            />
          </div>
        </div>
      </div>

      {/* Commentaire */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Commentaire
        </label>
        <textarea
          value={commentaire}
          onChange={(e) => setCommentaire(e.target.value)}
          disabled={!isEditable}
          rows={2}
          className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 disabled:bg-gray-100"
          placeholder="Optionnel..."
        />
      </div>
    </>
  )
}
