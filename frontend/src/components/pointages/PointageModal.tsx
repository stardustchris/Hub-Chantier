/**
 * PointageModal - Modal de création/édition de pointage
 * Refactorisé pour utiliser des sous-composants (P1-5)
 */

import { X, Check, Send, Trash2 } from 'lucide-react'
import { format } from 'date-fns'
import { fr } from 'date-fns/locale'
import type { Pointage, PointageCreate, PointageUpdate, Chantier, StatutPointage } from '../../types'
import { STATUTS_POINTAGE } from '../../types'
import { usePointageForm } from './usePointageForm'
import { PointageFormFields } from './PointageFormFields'
import { SignatureSection } from './SignatureSection'
import { ValidatorActions } from './ValidatorActions'

interface PointageModalProps {
  isOpen: boolean
  onClose: () => void
  onSave: (data: PointageCreate | PointageUpdate) => Promise<void>
  onDelete?: () => Promise<void>
  onSign?: (signature: string) => Promise<void>
  onSubmit?: () => Promise<void>
  onValidate?: () => Promise<void>
  onReject?: (motif: string) => Promise<void>
  pointage: Pointage | null
  chantiers: Chantier[]
  selectedDate?: Date
  selectedUserId?: number
  selectedChantierId?: number
  isValidateur?: boolean
}

function renderStatutBadge(statut: StatutPointage) {
  const config = STATUTS_POINTAGE[statut]
  return (
    <span
      className="inline-flex items-center gap-1 px-2 py-1 rounded text-sm font-medium"
      style={{ backgroundColor: config.bgColor, color: config.color }}
    >
      {config.label}
    </span>
  )
}

export default function PointageModal({
  isOpen,
  onClose,
  onSave,
  onDelete,
  onSign,
  onSubmit,
  onValidate,
  onReject,
  pointage,
  chantiers,
  selectedDate,
  selectedUserId,
  selectedChantierId,
  isValidateur = false,
}: PointageModalProps) {
  const form = usePointageForm({
    isOpen,
    pointage,
    selectedDate,
    selectedUserId,
    selectedChantierId,
    onSave,
    onDelete,
    onSign,
    onSubmit,
    onValidate,
    onReject,
    onClose,
  })

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-screen items-center justify-center p-4">
        {/* Overlay */}
        <div
          className="fixed inset-0 bg-black/50 transition-opacity"
          onClick={onClose}
        />

        {/* Modal */}
        <div className="relative bg-white rounded-lg shadow-xl w-full max-w-lg">
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-4 border-b">
            <div>
              <h2 className="text-lg font-semibold text-gray-900">
                {form.isEditing ? 'Modifier le pointage' : 'Nouveau pointage'}
              </h2>
              {selectedDate && (
                <p className="text-sm text-gray-500">
                  {format(selectedDate, 'EEEE d MMMM yyyy', { locale: fr })}
                </p>
              )}
              {pointage && pointage.date_pointage && (
                <p className="text-sm text-gray-500">
                  {format(new Date(pointage.date_pointage + 'T00:00:00'), 'EEEE d MMMM yyyy', { locale: fr })}
                </p>
              )}
            </div>
            <div className="flex items-center gap-2">
              {pointage && renderStatutBadge(pointage.statut)}
              <button
                onClick={onClose}
                className="p-1 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>
          </div>

          {/* Content */}
          <form onSubmit={form.handleSubmit} className="p-6 space-y-4">
            {form.error && (
              <div className="bg-red-50 text-red-700 p-3 rounded-lg text-sm">
                {form.error}
              </div>
            )}

            {/* Motif de rejet affiché */}
            {pointage?.motif_rejet && (
              <div className="bg-red-50 border border-red-200 p-3 rounded-lg">
                <p className="text-sm font-medium text-red-800">Motif de rejet :</p>
                <p className="text-sm text-red-700">{pointage.motif_rejet}</p>
              </div>
            )}

            {/* Champs de formulaire */}
            <PointageFormFields
              chantierId={form.chantierId}
              setChantierId={form.setChantierId}
              heuresNormales={form.heuresNormales}
              setHeuresNormales={form.setHeuresNormales}
              heuresSupplementaires={form.heuresSupplementaires}
              setHeuresSupplementaires={form.setHeuresSupplementaires}
              commentaire={form.commentaire}
              setCommentaire={form.setCommentaire}
              chantiers={chantiers}
              isEditing={form.isEditing}
              isEditable={form.isEditable}
            />

            {/* Signature (FDH-12) */}
            {pointage && pointage.statut === 'brouillon' && onSign && (
              <SignatureSection
                pointage={pointage}
                signature={form.signature}
                setSignature={form.setSignature}
                onSign={form.handleSign}
                saving={form.saving}
              />
            )}

            {/* Actions validateur (FDH-12) */}
            {isValidateur && pointage?.statut === 'soumis' && (
              <ValidatorActions
                showRejectForm={form.showRejectForm}
                setShowRejectForm={form.setShowRejectForm}
                motifRejet={form.motifRejet}
                setMotifRejet={form.setMotifRejet}
                onValidate={form.handleValidate}
                onReject={form.handleReject}
                saving={form.saving}
              />
            )}
          </form>

          {/* Footer */}
          <div className="flex items-center justify-between px-4 py-3 border-t bg-gray-50 gap-2">
            <div className="shrink-0">
              {form.isEditing && form.isEditable && onDelete && (
                <button
                  type="button"
                  onClick={form.handleDelete}
                  disabled={form.saving}
                  className="flex items-center gap-1.5 px-2.5 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg disabled:opacity-50"
                >
                  <Trash2 className="w-4 h-4" />
                  <span className="hidden sm:inline">Supprimer</span>
                </button>
              )}
            </div>

            <div className="flex items-center gap-2 flex-wrap justify-end">
              <button
                type="button"
                onClick={onClose}
                className="px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg"
              >
                Annuler
              </button>

              {/* Soumettre pour validation */}
              {pointage && pointage.statut === 'brouillon' && onSubmit && (
                <button
                  type="button"
                  onClick={form.handleSubmitForValidation}
                  disabled={form.saving}
                  className="flex items-center gap-1.5 px-3 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  <Send className="w-3.5 h-3.5" />
                  Soumettre
                </button>
              )}

              {/* Enregistrer */}
              {form.isEditable && (
                <button
                  type="submit"
                  onClick={form.handleSubmit}
                  disabled={form.saving}
                  className="flex items-center gap-1.5 px-3 py-2 text-sm bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
                >
                  <Check className="w-3.5 h-3.5" />
                  {form.saving ? 'En cours...' : 'Enregistrer'}
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
