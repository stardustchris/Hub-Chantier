/**
 * ValidatorActions - Actions de validation pour le validateur (FDH-12)
 */

import { Check, XCircle } from 'lucide-react'

interface ValidatorActionsProps {
  showRejectForm: boolean
  setShowRejectForm: (show: boolean) => void
  motifRejet: string
  setMotifRejet: (value: string) => void
  onValidate: () => Promise<void>
  onReject: () => Promise<void>
  saving: boolean
}

export function ValidatorActions({
  showRejectForm,
  setShowRejectForm,
  motifRejet,
  setMotifRejet,
  onValidate,
  onReject,
  saving,
}: ValidatorActionsProps) {
  return (
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
              onClick={onReject}
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
            onClick={onValidate}
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
  )
}
