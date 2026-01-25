/**
 * SignatureSection - Section de signature électronique (FDH-12)
 */

import { PenTool } from 'lucide-react'
import { format } from 'date-fns'
import type { Pointage } from '../../types'

interface SignatureSectionProps {
  pointage: Pointage
  signature: string
  setSignature: (value: string) => void
  onSign: () => Promise<void>
  saving: boolean
}

export function SignatureSection({
  pointage,
  signature,
  setSignature,
  onSign,
  saving,
}: SignatureSectionProps) {
  return (
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
          onClick={onSign}
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
  )
}
