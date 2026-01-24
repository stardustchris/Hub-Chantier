import { useState, useEffect } from 'react'
import { X, Clock, Check, Send, XCircle, Trash2, PenTool } from 'lucide-react'
import { format } from 'date-fns'
import { fr } from 'date-fns/locale'
import { logger } from '../../services/logger'
import type { Pointage, PointageCreate, PointageUpdate, Chantier, StatutPointage } from '../../types'
import { STATUTS_POINTAGE } from '../../types'

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
  const [chantierId, setChantierId] = useState<number | ''>('')
  const [heuresNormales, setHeuresNormales] = useState('07:00')
  const [heuresSupplementaires, setHeuresSupplementaires] = useState('00:00')
  const [commentaire, setCommentaire] = useState('')
  const [signature, setSignature] = useState('')
  const [motifRejet, setMotifRejet] = useState('')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [showRejectForm, setShowRejectForm] = useState(false)

  const isEditing = !!pointage
  const isEditable = !pointage || pointage.statut === 'brouillon' || pointage.statut === 'rejete'

  useEffect(() => {
    if (isOpen) {
      if (pointage) {
        setChantierId(pointage.chantier_id)
        setHeuresNormales(pointage.heures_normales || '07:00')
        setHeuresSupplementaires(pointage.heures_supplementaires || '00:00')
        setCommentaire(pointage.commentaire || '')
        setSignature('')
        setMotifRejet('')
      } else {
        setChantierId(selectedChantierId || '')
        setHeuresNormales('07:00')
        setHeuresSupplementaires('00:00')
        setCommentaire('')
        setSignature('')
        setMotifRejet('')
      }
      setError('')
      setShowRejectForm(false)
    }
  }, [isOpen, pointage, selectedChantierId])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!chantierId) {
      setError('Veuillez selectionner un chantier')
      return
    }

    setSaving(true)
    setError('')

    try {
      if (isEditing) {
        await onSave({
          heures_normales: heuresNormales,
          heures_supplementaires: heuresSupplementaires,
          commentaire: commentaire || undefined,
        } as PointageUpdate)
      } else {
        if (!selectedUserId || !selectedDate) {
          setError('Utilisateur et date requis')
          return
        }
        await onSave({
          utilisateur_id: selectedUserId,
          chantier_id: Number(chantierId),
          date_pointage: format(selectedDate, 'yyyy-MM-dd'),
          heures_normales: heuresNormales,
          heures_supplementaires: heuresSupplementaires,
          commentaire: commentaire || undefined,
        } as PointageCreate)
      }
      onClose()
    } catch (err) {
      setError('Erreur lors de l\'enregistrement')
      logger.error('Erreur pointage', err, { context: 'PointageModal' })
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async () => {
    if (!onDelete) return
    if (!confirm('Supprimer ce pointage ?')) return

    setSaving(true)
    try {
      await onDelete()
      onClose()
    } catch (err) {
      setError('Erreur lors de la suppression')
      logger.error('Erreur pointage', err, { context: 'PointageModal' })
    } finally {
      setSaving(false)
    }
  }

  const handleSign = async () => {
    if (!onSign || !signature.trim()) {
      setError('Veuillez saisir votre signature')
      return
    }

    setSaving(true)
    try {
      await onSign(signature.trim())
      onClose()
    } catch (err) {
      setError('Erreur lors de la signature')
      logger.error('Erreur pointage', err, { context: 'PointageModal' })
    } finally {
      setSaving(false)
    }
  }

  const handleSubmitForValidation = async () => {
    if (!onSubmit) return

    setSaving(true)
    try {
      await onSubmit()
      onClose()
    } catch (err) {
      setError('Erreur lors de la soumission')
      logger.error('Erreur pointage', err, { context: 'PointageModal' })
    } finally {
      setSaving(false)
    }
  }

  const handleValidate = async () => {
    if (!onValidate) return

    setSaving(true)
    try {
      await onValidate()
      onClose()
    } catch (err) {
      setError('Erreur lors de la validation')
      logger.error('Erreur pointage', err, { context: 'PointageModal' })
    } finally {
      setSaving(false)
    }
  }

  const handleReject = async () => {
    if (!onReject || !motifRejet.trim()) {
      setError('Veuillez saisir un motif de rejet')
      return
    }

    setSaving(true)
    try {
      await onReject(motifRejet.trim())
      onClose()
    } catch (err) {
      setError('Erreur lors du rejet')
      logger.error('Erreur pointage', err, { context: 'PointageModal' })
    } finally {
      setSaving(false)
    }
  }

  const renderStatutBadge = (statut: StatutPointage) => {
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
                {isEditing ? 'Modifier le pointage' : 'Nouveau pointage'}
              </h2>
              {selectedDate && (
                <p className="text-sm text-gray-500">
                  {format(selectedDate, 'EEEE d MMMM yyyy', { locale: fr })}
                </p>
              )}
              {pointage && (
                <p className="text-sm text-gray-500">
                  {format(new Date(pointage.date_pointage), 'EEEE d MMMM yyyy', { locale: fr })}
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
          <form onSubmit={handleSubmit} className="p-6 space-y-4">
            {error && (
              <div className="bg-red-50 text-red-700 p-3 rounded-lg text-sm">
                {error}
              </div>
            )}

            {/* Motif de rejet affiché */}
            {pointage?.motif_rejet && (
              <div className="bg-red-50 border border-red-200 p-3 rounded-lg">
                <p className="text-sm font-medium text-red-800">Motif de rejet :</p>
                <p className="text-sm text-red-700">{pointage.motif_rejet}</p>
              </div>
            )}

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

            {/* Signature (FDH-12) */}
            {pointage && pointage.statut === 'brouillon' && onSign && (
              <div className="border-t pt-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Signature electronique
                </label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={signature}
                    onChange={(e) => setSignature(e.target.value)}
                    className="flex-1 px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    placeholder="Saisir votre nom pour signer"
                  />
                  <button
                    type="button"
                    onClick={handleSign}
                    disabled={saving || !signature.trim()}
                    className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                  >
                    <PenTool className="w-4 h-4" />
                    Signer
                  </button>
                </div>
                {pointage.signature_utilisateur && (
                  <p className="mt-2 text-sm text-green-600">
                    Signe par {pointage.signature_utilisateur} le{' '}
                    {pointage.signature_date &&
                      format(new Date(pointage.signature_date), 'dd/MM/yyyy HH:mm')}
                  </p>
                )}
              </div>
            )}

            {/* Actions validateur (FDH-12) */}
            {isValidateur && pointage?.statut === 'soumis' && (
              <div className="border-t pt-4 space-y-3">
                <p className="text-sm font-medium text-gray-700">Actions de validation</p>

                {showRejectForm ? (
                  <div className="space-y-2">
                    <textarea
                      value={motifRejet}
                      onChange={(e) => setMotifRejet(e.target.value)}
                      rows={2}
                      className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
                      placeholder="Motif du rejet..."
                    />
                    <div className="flex gap-2">
                      <button
                        type="button"
                        onClick={handleReject}
                        disabled={saving || !motifRejet.trim()}
                        className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
                      >
                        <XCircle className="w-4 h-4" />
                        Confirmer le rejet
                      </button>
                      <button
                        type="button"
                        onClick={() => setShowRejectForm(false)}
                        className="px-4 py-2 border rounded-lg hover:bg-gray-50"
                      >
                        Annuler
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="flex gap-2">
                    <button
                      type="button"
                      onClick={handleValidate}
                      disabled={saving}
                      className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
                    >
                      <Check className="w-4 h-4" />
                      Valider
                    </button>
                    <button
                      type="button"
                      onClick={() => setShowRejectForm(true)}
                      disabled={saving}
                      className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 disabled:opacity-50"
                    >
                      <XCircle className="w-4 h-4" />
                      Rejeter
                    </button>
                  </div>
                )}
              </div>
            )}
          </form>

          {/* Footer */}
          <div className="flex items-center justify-between px-6 py-4 border-t bg-gray-50">
            <div>
              {isEditing && isEditable && onDelete && (
                <button
                  type="button"
                  onClick={handleDelete}
                  disabled={saving}
                  className="flex items-center gap-2 px-3 py-2 text-red-600 hover:bg-red-50 rounded-lg disabled:opacity-50"
                >
                  <Trash2 className="w-4 h-4" />
                  Supprimer
                </button>
              )}
            </div>

            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
              >
                Annuler
              </button>

              {/* Soumettre pour validation */}
              {pointage && pointage.statut === 'brouillon' && onSubmit && (
                <button
                  type="button"
                  onClick={handleSubmitForValidation}
                  disabled={saving}
                  className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  <Send className="w-4 h-4" />
                  Soumettre
                </button>
              )}

              {/* Enregistrer */}
              {isEditable && (
                <button
                  type="submit"
                  onClick={handleSubmit}
                  disabled={saving}
                  className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
                >
                  <Check className="w-4 h-4" />
                  {saving ? 'Enregistrement...' : 'Enregistrer'}
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
