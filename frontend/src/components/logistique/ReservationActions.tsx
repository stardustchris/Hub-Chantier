/**
 * Composant ReservationActions - Boutons d'action pour une réservation.
 *
 * M13: Extraction des actions depuis ReservationModal.
 *
 * Ce composant gère les boutons d'action selon le mode et le statut:
 * - Mode création: Annuler / Réserver
 * - Mode vue (en_attente + canValidate): Valider / Refuser
 * - Mode vue (validée): Annuler la réservation
 *
 * @module components/logistique/ReservationActions
 */

import React from 'react'
import { Check, XCircle } from 'lucide-react'
import type { Reservation } from '../../types/logistique'

/**
 * Props du composant ReservationActions.
 */
export interface ReservationActionsProps {
  /** Indique si le formulaire est en mode lecture seule */
  isViewMode: boolean
  /** Réservation existante (mode vue) */
  reservation?: Reservation | null
  /** Indique si l'utilisateur peut valider/refuser */
  canValidate: boolean
  /** Indicateur de chargement */
  loading: boolean
  /** Motif de refus saisi */
  motifRefus: string
  /** Indique si le champ motif de refus est visible */
  showMotifRefus: boolean
  /** Callback pour valider la réservation */
  onValider: () => void
  /** Callback pour refuser la réservation */
  onRefuser: () => void
  /** Callback pour annuler la réservation */
  onAnnuler: () => void
  /** Callback pour fermer le modal */
  onClose: () => void
  /** Callback pour afficher le champ motif de refus */
  onShowMotifRefus: (show: boolean) => void
  /** Callback pour modifier le motif de refus */
  onMotifRefusChange: (motif: string) => void
}

/**
 * Affiche les boutons d'action appropriés selon le contexte.
 *
 * @example
 * ```tsx
 * <ReservationActions
 *   isViewMode={true}
 *   reservation={reservation}
 *   canValidate={true}
 *   loading={loading}
 *   motifRefus={motifRefus}
 *   showMotifRefus={showMotifRefus}
 *   onValider={handleValider}
 *   onRefuser={handleRefuser}
 *   onAnnuler={handleAnnuler}
 *   onClose={onClose}
 *   onShowMotifRefus={setShowMotifRefus}
 *   onMotifRefusChange={setMotifRefus}
 * />
 * ```
 *
 * @param props - Props du composant
 */
const ReservationActions: React.FC<ReservationActionsProps> = ({
  isViewMode,
  reservation,
  canValidate,
  loading,
  motifRefus,
  showMotifRefus,
  onValider,
  onRefuser,
  onAnnuler,
  onClose,
  onShowMotifRefus,
  onMotifRefusChange,
}) => {
  // Mode création: boutons Annuler / Réserver
  if (!isViewMode) {
    return (
      <div className="flex gap-3 pt-2">
        <button
          type="button"
          onClick={onClose}
          className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
        >
          Annuler
        </button>
        <button
          type="submit"
          disabled={loading}
          className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'Création...' : 'Réserver'}
        </button>
      </div>
    )
  }

  // Mode vue
  return (
    <>
      {/* Champ motif de refus (si visible) */}
      {showMotifRefus && (
        <div>
          <label className="text-sm font-medium text-gray-700 mb-1 block">
            Motif du refus
          </label>
          <textarea
            value={motifRefus}
            onChange={(e) => onMotifRefusChange(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
            rows={2}
            placeholder="Motif optionnel..."
          />
        </div>
      )}

      <div className="flex gap-3 pt-2">
        {/* Actions pour réservation en attente */}
        {canValidate && reservation?.statut === 'en_attente' && (
          <>
            {showMotifRefus ? (
              <>
                <button
                  type="button"
                  onClick={() => onShowMotifRefus(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                >
                  Annuler
                </button>
                <button
                  type="button"
                  onClick={onRefuser}
                  disabled={loading}
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
                >
                  <XCircle size={18} />
                  Confirmer refus
                </button>
              </>
            ) : (
              <>
                <button
                  type="button"
                  onClick={onValider}
                  disabled={loading}
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
                >
                  <Check size={18} />
                  Valider
                </button>
                <button
                  type="button"
                  onClick={() => onShowMotifRefus(true)}
                  disabled={loading}
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
                >
                  <XCircle size={18} />
                  Refuser
                </button>
              </>
            )}
          </>
        )}

        {/* Action pour réservation validée */}
        {reservation?.statut === 'validee' && (
          <button
            type="button"
            onClick={onAnnuler}
            disabled={loading}
            className="flex-1 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:opacity-50"
          >
            Annuler la réservation
          </button>
        )}

        {/* Bouton Fermer (toujours présent en mode vue) */}
        <button
          type="button"
          onClick={onClose}
          className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
        >
          Fermer
        </button>
      </div>
    </>
  )
}

export default ReservationActions
