/**
 * Composant ReservationFormFields - Champs du formulaire de réservation.
 *
 * M13: Extraction des champs de formulaire depuis ReservationModal.
 *
 * Ce composant affiche les champs du formulaire en mode édition (création)
 * ou en mode lecture seule (vue d'une réservation existante).
 *
 * @module components/logistique/ReservationFormFields
 */

import React from 'react'
import { Calendar, Clock, Building2, MessageSquare } from 'lucide-react'
import type { Reservation, ReservationCreate } from '../../types/logistique'
import type { Chantier } from '../../types'

/**
 * Props du composant ReservationFormFields.
 */
export interface ReservationFormFieldsProps {
  /** Indique si le formulaire est en mode lecture seule */
  isViewMode: boolean
  /** Réservation existante (mode vue) */
  reservation?: Reservation | null
  /** Données du formulaire (mode création) */
  formData: Partial<ReservationCreate>
  /** Liste des chantiers disponibles */
  chantiers: Chantier[]
  /** Callback pour mettre à jour les données du formulaire */
  onFormDataChange: (data: Partial<ReservationCreate>) => void
}

/**
 * Affiche les champs du formulaire de réservation.
 *
 * Gère deux modes:
 * - Mode création: champs éditables avec select/input
 * - Mode vue: affichage en lecture seule des données
 *
 * @example
 * ```tsx
 * <ReservationFormFields
 *   isViewMode={false}
 *   formData={formData}
 *   chantiers={chantiersList}
 *   onFormDataChange={setFormData}
 * />
 * ```
 *
 * @param props - Props du composant
 */
const ReservationFormFields: React.FC<ReservationFormFieldsProps> = ({
  isViewMode,
  reservation,
  formData,
  chantiers,
  onFormDataChange,
}) => {
  return (
    <>
      {/* Chantier */}
      <div>
        <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-1">
          <Building2 size={16} />
          Chantier *
        </label>
        {isViewMode ? (
          <p className="px-3 py-2 bg-gray-50 rounded-lg">
            {reservation?.chantier_nom || `Chantier #${reservation?.chantier_id}`}
          </p>
        ) : (
          <select
            value={formData.chantier_id}
            onChange={(e) =>
              onFormDataChange({ ...formData, chantier_id: parseInt(e.target.value) })
            }
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            required
          >
            <option value={0}>Sélectionner un chantier</option>
            {chantiers.map((c) => (
              <option key={c.id} value={c.id}>
                [{c.code}] {c.nom}
              </option>
            ))}
          </select>
        )}
      </div>

      {/* Date */}
      <div>
        <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-1">
          <Calendar size={16} />
          Date *
        </label>
        {isViewMode ? (
          <p className="px-3 py-2 bg-gray-50 rounded-lg">
            {new Date(reservation!.date_reservation).toLocaleDateString('fr-FR', {
              weekday: 'long',
              day: 'numeric',
              month: 'long',
              year: 'numeric',
            })}
          </p>
        ) : (
          <input
            type="date"
            value={formData.date_reservation}
            onChange={(e) =>
              onFormDataChange({ ...formData, date_reservation: e.target.value })
            }
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            required
          />
        )}
      </div>

      {/* Horaires */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-1">
            <Clock size={16} />
            Début *
          </label>
          {isViewMode ? (
            <p className="px-3 py-2 bg-gray-50 rounded-lg">
              {reservation!.heure_debut.substring(0, 5)}
            </p>
          ) : (
            <input
              type="time"
              value={formData.heure_debut}
              onChange={(e) =>
                onFormDataChange({ ...formData, heure_debut: e.target.value })
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
            />
          )}
        </div>
        <div>
          <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-1">
            <Clock size={16} />
            Fin *
          </label>
          {isViewMode ? (
            <p className="px-3 py-2 bg-gray-50 rounded-lg">
              {reservation!.heure_fin.substring(0, 5)}
            </p>
          ) : (
            <input
              type="time"
              value={formData.heure_fin}
              onChange={(e) =>
                onFormDataChange({ ...formData, heure_fin: e.target.value })
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
            />
          )}
        </div>
      </div>

      {/* Commentaire */}
      <div>
        <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-1">
          <MessageSquare size={16} />
          Commentaire
        </label>
        {isViewMode ? (
          <p className="px-3 py-2 bg-gray-50 rounded-lg min-h-[60px]">
            {reservation!.commentaire || '-'}
          </p>
        ) : (
          <textarea
            value={formData.commentaire}
            onChange={(e) =>
              onFormDataChange({ ...formData, commentaire: e.target.value })
            }
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            rows={2}
            placeholder="Commentaire optionnel..."
          />
        )}
      </div>

      {/* Demandeur (mode vue) */}
      {isViewMode && reservation && (
        <div className="text-sm text-gray-500 pt-2 border-t border-gray-200">
          <p>Demandé par: {reservation.demandeur_nom || `User #${reservation.demandeur_id}`}</p>
          {reservation.validated_at && (
            <p>
              Traité par: {reservation.valideur_nom || `User #${reservation.valideur_id}`}
              {' le '}
              {new Date(reservation.validated_at).toLocaleDateString('fr-FR')}
            </p>
          )}
        </div>
      )}
    </>
  )
}

export default ReservationFormFields
