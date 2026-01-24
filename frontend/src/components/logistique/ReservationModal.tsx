/**
 * Composant ReservationModal - Modal pour créer/voir une réservation.
 *
 * M13: Refactoré pour extraire la logique dans useReservationModal
 * et les sous-composants ReservationFormFields et ReservationActions.
 *
 * Fonctionnalités:
 * - LOG-07: Demande de réservation - Création depuis mobile ou web
 * - LOG-08: Sélection chantier - Association obligatoire au projet
 * - LOG-09: Sélection créneau - Date + heure début / heure fin
 * - LOG-11: Workflow validation - Valider ou refuser une demande
 * - LOG-16: Motif de refus - Champ texte optionnel
 *
 * @module components/logistique/ReservationModal
 */

import React from 'react'
import { X } from 'lucide-react'
import type { Ressource, Reservation } from '../../types/logistique'
import { STATUTS_RESERVATION } from '../../types/logistique'
import type { Chantier } from '../../types'
import { useReservationModal } from '../../hooks/useReservationModal'
import ReservationFormFields from './ReservationFormFields'
import ReservationActions from './ReservationActions'

/**
 * Props du composant ReservationModal.
 */
export interface ReservationModalProps {
  /** Indique si le modal est ouvert */
  isOpen: boolean
  /** Callback pour fermer le modal */
  onClose: () => void
  /** Ressource concernée par la réservation */
  ressource: Ressource
  /** Réservation existante (mode vue) ou null/undefined (mode création) */
  reservation?: Reservation | null
  /** Liste des chantiers disponibles */
  chantiers: Chantier[]
  /** Date initiale pour le formulaire (format YYYY-MM-DD) */
  initialDate?: string
  /** Heure de début initiale (format HH:MM) */
  initialHeureDebut?: string
  /** Heure de fin initiale (format HH:MM) */
  initialHeureFin?: string
  /** Indique si l'utilisateur peut valider/refuser les demandes */
  canValidate?: boolean
  /** Callback appelé après une action réussie */
  onSuccess?: () => void
}

/**
 * Modal pour créer une nouvelle réservation ou visualiser une réservation existante.
 *
 * Deux modes d'utilisation:
 * 1. **Mode création**: Sans `reservation` prop, affiche un formulaire éditable
 * 2. **Mode vue**: Avec `reservation` prop, affiche les détails en lecture seule
 *    avec possibilité de valider/refuser/annuler selon les permissions
 *
 * @example
 * ```tsx
 * // Mode création
 * <ReservationModal
 *   isOpen={isOpen}
 *   onClose={() => setIsOpen(false)}
 *   ressource={selectedRessource}
 *   chantiers={chantiersList}
 *   initialDate="2026-01-25"
 *   onSuccess={() => refetchReservations()}
 * />
 *
 * // Mode vue avec validation
 * <ReservationModal
 *   isOpen={isOpen}
 *   onClose={() => setIsOpen(false)}
 *   ressource={selectedRessource}
 *   reservation={selectedReservation}
 *   chantiers={chantiersList}
 *   canValidate={userCanValidate}
 *   onSuccess={() => refetchReservations()}
 * />
 * ```
 *
 * @param props - Props du composant
 */
const ReservationModal: React.FC<ReservationModalProps> = ({
  isOpen,
  onClose,
  ressource,
  reservation,
  chantiers,
  initialDate,
  initialHeureDebut,
  initialHeureFin,
  canValidate = false,
  onSuccess,
}) => {
  const {
    loading,
    error,
    formData,
    motifRefus,
    showMotifRefus,
    setFormData,
    setMotifRefus,
    setShowMotifRefus,
    handleSubmit,
    handleValider,
    handleRefuser,
    handleAnnuler,
    isViewMode,
  } = useReservationModal({
    isOpen,
    ressource,
    reservation,
    initialDate,
    initialHeureDebut,
    initialHeureFin,
    onSuccess,
    onClose,
  })

  if (!isOpen) return null

  const statutInfo = reservation ? STATUTS_RESERVATION[reservation.statut] : null

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-md">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <div
              className="w-3 h-10 rounded"
              style={{ backgroundColor: ressource.couleur }}
            />
            <div>
              <h2 className="font-semibold text-gray-900">
                {isViewMode ? 'Détails réservation' : 'Nouvelle réservation'}
              </h2>
              <p className="text-sm text-gray-500">
                [{ressource.code}] {ressource.nom}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            aria-label="Fermer"
          >
            <X size={20} className="text-gray-500" />
          </button>
        </div>

        {/* Statut (mode vue) */}
        {isViewMode && statutInfo && (
          <div
            className="mx-4 mt-4 px-4 py-2 rounded-lg flex items-center gap-2"
            style={{ backgroundColor: statutInfo.bgColor }}
          >
            <span>{statutInfo.emoji}</span>
            <span style={{ color: statutInfo.color }} className="font-medium">
              {statutInfo.label}
            </span>
            {reservation?.motif_refus && (
              <span className="text-sm text-gray-600 ml-2">
                - {reservation.motif_refus}
              </span>
            )}
          </div>
        )}

        {/* Formulaire */}
        <form onSubmit={handleSubmit} className="p-4 space-y-4">
          <ReservationFormFields
            isViewMode={isViewMode}
            reservation={reservation}
            formData={formData}
            chantiers={chantiers}
            onFormDataChange={setFormData}
          />

          {/* Erreur */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-2 rounded-lg text-sm">
              {error}
            </div>
          )}

          {/* Actions */}
          <ReservationActions
            isViewMode={isViewMode}
            reservation={reservation}
            canValidate={canValidate}
            loading={loading}
            motifRefus={motifRefus}
            showMotifRefus={showMotifRefus}
            onValider={handleValider}
            onRefuser={handleRefuser}
            onAnnuler={handleAnnuler}
            onClose={onClose}
            onShowMotifRefus={setShowMotifRefus}
            onMotifRefusChange={setMotifRefus}
          />

          {/* Info validation */}
          {!isViewMode && ressource.validation_requise && (
            <p className="text-xs text-orange-600 text-center">
              Cette ressource nécessite une validation par un responsable
            </p>
          )}
        </form>
      </div>
    </div>
  )
}

export default ReservationModal
