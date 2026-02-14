/**
 * Modal d'affichage du secret webhook (UNE FOIS)
 */

import type { Webhook } from '../../api/webhooks'
import { Copy, CheckCircle2, AlertTriangle, Info } from 'lucide-react'
import { useFocusTrap } from '../../hooks/useFocusTrap'

interface SecretModalProps {
  secret: string
  webhook: Webhook
  copied: boolean
  onCopy: () => void
  onClose: () => void
}

export default function SecretModal({ secret, webhook, copied, onCopy, onClose }: SecretModalProps) {
  const focusTrapRef = useFocusTrap({ enabled: true, onClose })
  return (
    <div ref={focusTrapRef} className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-2xl w-full p-6">
        {/* Succes */}
        <div className="bg-green-50 border-l-4 border-green-400 p-4 mb-4">
          <div className="flex items-start">
            <CheckCircle2 className="w-5 h-5 text-green-600 mt-0.5 mr-3" />
            <div>
              <h3 className="text-sm font-medium text-green-800 mb-1">
                Webhook créé avec succès!
              </h3>
              <p className="text-sm text-green-700">
                Votre webhook est maintenant actif et prêt à recevoir des événements.
              </p>
            </div>
          </div>
        </div>

        {/* Alerte Secret */}
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-4">
          <div className="flex items-start">
            <AlertTriangle className="w-5 h-5 text-yellow-600 mt-0.5 mr-3" />
            <div>
              <h3 className="text-sm font-medium text-yellow-800 mb-1">
                Votre secret (copiez-le maintenant, il ne sera plus affiché)
              </h3>
              <p className="text-sm text-yellow-700">
                Stockez ce secret de manière sécurisée. Vous en aurez besoin pour vérifier les signatures HMAC des événements.
              </p>
            </div>
          </div>
        </div>

        {/* Secret */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Secret Webhook
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

        {/* Infos Webhook */}
        <div className="bg-gray-50 rounded-lg p-4 mb-4">
          <h4 className="text-sm font-medium text-gray-900 mb-2">Détails du webhook</h4>
          <dl className="space-y-1 text-sm">
            <div className="flex">
              <dt className="text-gray-500 w-24">URL:</dt>
              <dd className="text-gray-900 font-mono break-all">{webhook.url}</dd>
            </div>
            <div className="flex">
              <dt className="text-gray-500 w-24">Événements:</dt>
              <dd className="text-gray-900">{webhook.events.join(', ')}</dd>
            </div>
          </dl>
        </div>

        {/* Documentation */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
          <div className="flex items-start">
            <Info className="w-5 h-5 text-blue-600 mt-0.5 mr-3" />
            <div className="text-sm text-blue-800">
              <p className="font-medium mb-1">Vérification de signature HMAC-SHA256</p>
              <code className="block bg-white px-2 py-1 rounded text-xs mt-2 overflow-x-auto">
                const signature = req.headers['x-webhook-signature']<br/>
                const computed = crypto.createHmac('sha256', secret).update(body).digest('hex')<br/>
                const valid = signature === computed
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
