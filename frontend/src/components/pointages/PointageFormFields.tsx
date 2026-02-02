/**
 * PointageFormFields - Champs de saisie du formulaire de pointage
 */

import type { Chantier } from '../../types'
import MobileTimePicker from '../MobileTimePicker'

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
          value={String(chantierId)}
          onChange={(e) => setChantierId(e.target.value ? Number(e.target.value) : '')}
          disabled={isEditing || !isEditable}
          className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 disabled:bg-gray-100"
        >
          <option value="">Selectionner un chantier</option>
          {chantiers.map((chantier) => (
            <option key={chantier.id} value={String(chantier.id)}>
              {chantier.nom}
            </option>
          ))}
        </select>
      </div>

      {/* Heures */}
      <div className="grid grid-cols-2 gap-4">
        <MobileTimePicker
          value={heuresNormales}
          onChange={setHeuresNormales}
          label="Heures normales *"
          disabled={!isEditable}
          step={15}
        />
        <MobileTimePicker
          value={heuresSupplementaires}
          onChange={setHeuresSupplementaires}
          label="Heures sup."
          disabled={!isEditable}
          step={15}
        />
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
