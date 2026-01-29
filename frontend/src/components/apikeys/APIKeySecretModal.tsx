/**
 * Modal d'affichage du secret de cle API (UNE FOIS)
 */

import {
  AlertTriangle,
  CheckCircle2,
  Copy,
  Info,
} from 'lucide-react'

interface APIKeySecretModalProps {
  secret: string
  keyInfo: { key_prefix: string; nom: string; expires_at: string | null }
  copied: boolean
  onCopy: () => void
  onClose: () => void
}

export default function APIKeySecretModal({
  secret,
  keyInfo,
  copied,
  onCopy,
  onClose,
}: APIKeySecretModalProps) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-2xl w-full p-6">
        {/* Alerte */}
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-4">
          <div className="flex items-start">
            <AlertTriangle className="w-5 h-5 text-yellow-600 mt-0.5 mr-3" />
            <div>
              <h3 className="text-sm font-medium text-yellow-800 mb-1">
                Secret affiché une seule fois
              </h3>
              <p className="text-sm text-yellow-700">
                Copiez ce secret maintenant. Il ne sera plus jamais accessible
                après la fermeture de cette fenêtre.
              </p>
            </div>
          </div>
        </div>

        {/* Infos */}
        <div className="mb-4">
          <h2 className="text-xl font-bold mb-1">Clé API créée</h2>
          <p className="text-sm text-gray-600">
            Nom: <span className="font-medium">{keyInfo.nom}</span>
          </p>
        </div>

        {/* Secret */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Clé API Secret
          </label>
          <div className="flex gap-2">
            <div className="flex-1 font-mono text-sm bg-gray-100 px-3 py-2 rounded-lg border border-gray-300 overflow-x-auto">
              {secret}
            </div>
            <button
              onClick={onCopy}
              className={`px-4 py-2 rounded-lg transition-colors flex items-center gap-2 ${
                copied
                  ? 'bg-green-600 text-white'
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              }`}
            >
              {copied ? (
                <>
                  <CheckCircle2 className="w-4 h-4" />
                  Copié
                </>
              ) : (
                <>
                  <Copy className="w-4 h-4" />
                  Copier
                </>
              )}
            </button>
          </div>
        </div>

        {/* Instructions */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
          <div className="flex items-start">
            <Info className="w-5 h-5 text-blue-600 mt-0.5 mr-3" />
            <div className="text-sm text-blue-800">
              <p className="font-medium mb-1">Comment utiliser cette clé :</p>
              <code className="block bg-white px-2 py-1 rounded text-xs mt-2">
                curl -H "Authorization: Bearer {secret}" https://api.hub-chantier.fr/api/v1/...
              </code>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors"
          >
            Fermer
          </button>
        </div>
      </div>
    </div>
  )
}
