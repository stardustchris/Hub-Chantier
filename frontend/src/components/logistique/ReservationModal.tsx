/**
 * Composant ReservationModal - Modal pour créer/voir une réservation
 *
 * LOG-07: Demande de réservation
 * LOG-08: Sélection chantier
 * LOG-09: Sélection créneau
 * LOG-16: Motif de refus
 */

import React, { useState, useEffect } from 'react'
import { X, Calendar, Clock, Building2, MessageSquare, Check, XCircle } from 'lucide-react'
import type { Ressource, Reservation, ReservationCreate } from '../../types/logistique'
import { STATUTS_RESERVATION } from '../../types/logistique'
import { createReservation, validerReservation, refuserReservation, annulerReservation } from '../../api/logistique'
import type { Chantier } from '../../types'

interface ReservationModalProps {
  isOpen: boolean
  onClose: () => void
  ressource: Ressource
  reservation?: Reservation | null
  chantiers: Chantier[]
  initialDate?: string
  initialHeureDebut?: string
  initialHeureFin?: string
  canValidate?: boolean
  onSuccess?: () => void
}

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
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [motifRefus, setMotifRefus] = useState('')
  const [showMotifRefus, setShowMotifRefus] = useState(false)

  const [formData, setFormData] = useState<Partial<ReservationCreate>>({
    ressource_id: ressource.id,
    chantier_id: 0,
    date_reservation: initialDate || new Date().toISOString().split('T')[0],
    heure_debut: initialHeureDebut || ressource.heure_debut_defaut.substring(0, 5),
    heure_fin: initialHeureFin || ressource.heure_fin_defaut.substring(0, 5),
    commentaire: '',
  })

  useEffect(() => {
    if (isOpen && !reservation) {
      setFormData({
        ressource_id: ressource.id,
        chantier_id: 0,
        date_reservation: initialDate || new Date().toISOString().split('T')[0],
        heure_debut: initialHeureDebut || ressource.heure_debut_defaut.substring(0, 5),
        heure_fin: initialHeureFin || ressource.heure_fin_defaut.substring(0, 5),
        commentaire: '',
      })
      setError(null)
      setShowMotifRefus(false)
      setMotifRefus('')
    }
  }, [isOpen, reservation, ressource, initialDate, initialHeureDebut, initialHeureFin])

  if (!isOpen) return null

  const isViewMode = !!reservation
  const statutInfo = reservation ? STATUTS_RESERVATION[reservation.statut] : null

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.chantier_id) {
      setError('Veuillez sélectionner un chantier')
      return
    }

    try {
      setLoading(true)
      setError(null)
      await createReservation(formData as ReservationCreate)
      onSuccess?.()
      onClose()
    } catch (err: any) {
      if (err.response?.status === 409) {
        setError('Conflit: ce créneau est déjà réservé')
      } else {
        setError(err.response?.data?.detail || 'Erreur lors de la création')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleValider = async () => {
    if (!reservation) return
    try {
      setLoading(true)
      await validerReservation(reservation.id)
      onSuccess?.()
      onClose()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erreur lors de la validation')
    } finally {
      setLoading(false)
    }
  }

  const handleRefuser = async () => {
    if (!reservation) return
    try {
      setLoading(true)
      await refuserReservation(reservation.id, motifRefus || undefined)
      onSuccess?.()
      onClose()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erreur lors du refus')
    } finally {
      setLoading(false)
    }
  }

  const handleAnnuler = async () => {
    if (!reservation) return
    try {
      setLoading(true)
      await annulerReservation(reservation.id)
      onSuccess?.()
      onClose()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erreur lors de l\'annulation')
    } finally {
      setLoading(false)
    }
  }

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
            {reservation.motif_refus && (
              <span className="text-sm text-gray-600 ml-2">
                - {reservation.motif_refus}
              </span>
            )}
          </div>
        )}

        {/* Formulaire */}
        <form onSubmit={handleSubmit} className="p-4 space-y-4">
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
                onChange={(e) => setFormData({ ...formData, chantier_id: parseInt(e.target.value) })}
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
                onChange={(e) => setFormData({ ...formData, date_reservation: e.target.value })}
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
                  onChange={(e) => setFormData({ ...formData, heure_debut: e.target.value })}
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
                  onChange={(e) => setFormData({ ...formData, heure_fin: e.target.value })}
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
                onChange={(e) => setFormData({ ...formData, commentaire: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                rows={2}
                placeholder="Commentaire optionnel..."
              />
            )}
          </div>

          {/* Demandeur (mode vue) */}
          {isViewMode && (
            <div className="text-sm text-gray-500 pt-2 border-t border-gray-200">
              <p>Demandé par: {reservation?.demandeur_nom || `User #${reservation?.demandeur_id}`}</p>
              {reservation?.validated_at && (
                <p>
                  Traité par: {reservation.valideur_nom || `User #${reservation.valideur_id}`}
                  {' le '}
                  {new Date(reservation.validated_at).toLocaleDateString('fr-FR')}
                </p>
              )}
            </div>
          )}

          {/* Motif refus */}
          {showMotifRefus && (
            <div>
              <label className="text-sm font-medium text-gray-700 mb-1 block">
                Motif du refus
              </label>
              <textarea
                value={motifRefus}
                onChange={(e) => setMotifRefus(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
                rows={2}
                placeholder="Motif optionnel..."
              />
            </div>
          )}

          {/* Erreur */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-2 rounded-lg text-sm">
              {error}
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-3 pt-2">
            {isViewMode ? (
              <>
                {canValidate && reservation?.statut === 'en_attente' && (
                  <>
                    {showMotifRefus ? (
                      <>
                        <button
                          type="button"
                          onClick={() => setShowMotifRefus(false)}
                          className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                        >
                          Annuler
                        </button>
                        <button
                          type="button"
                          onClick={handleRefuser}
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
                          onClick={handleValider}
                          disabled={loading}
                          className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
                        >
                          <Check size={18} />
                          Valider
                        </button>
                        <button
                          type="button"
                          onClick={() => setShowMotifRefus(true)}
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
                {reservation?.statut === 'validee' && (
                  <button
                    type="button"
                    onClick={handleAnnuler}
                    disabled={loading}
                    className="flex-1 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:opacity-50"
                  >
                    Annuler la réservation
                  </button>
                )}
                <button
                  type="button"
                  onClick={onClose}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                >
                  Fermer
                </button>
              </>
            ) : (
              <>
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
              </>
            )}
          </div>

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
