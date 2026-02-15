/**
 * Modal de creation de cle API
 */

import { useState } from 'react'
import { apiKeysService } from '../../services/apiKeys'
import type { CreateAPIKeyRequest } from '../../services/apiKeys'
import { Loader2, Plus } from 'lucide-react'
import { logger } from '../../services/logger'
import { useFocusTrap } from '../../hooks/useFocusTrap'

interface CreateAPIKeyModalProps {
  onClose: () => void
  onCreated: (
    secret: string,
    keyInfo: { key_prefix: string; nom: string; expires_at: string | null }
  ) => void
}

export default function CreateAPIKeyModal({ onClose, onCreated }: CreateAPIKeyModalProps) {
  const focusTrapRef = useFocusTrap({ enabled: true, onClose })
  const [nom, setNom] = useState('')
  const [description, setDescription] = useState('')
  const [scopes, setScopes] = useState<string[]>(['read'])
  const [expiresDays, setExpiresDays] = useState(90)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const availableScopes = [
    'read',
    'write',
    'chantiers:read',
    'chantiers:write',
    'planning:read',
    'planning:write',
    'documents:read',
    'documents:write',
  ]

  const toggleScope = (scope: string) => {
    setScopes((prev) =>
      prev.includes(scope) ? prev.filter((s) => s !== scope) : [...prev, scope]
    )
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!nom.trim()) {
      alert('Le nom est requis')
      return
    }

    if (scopes.length === 0) {
      alert('Au moins un scope est requis')
      return
    }

    try {
      setIsSubmitting(true)
      const data: CreateAPIKeyRequest = {
        nom: nom.trim(),
        description: description.trim() || undefined,
        scopes,
        expires_days: expiresDays,
      }
      const result = await apiKeysService.create(data)
      onCreated(result.api_key, {
        key_prefix: result.key_prefix,
        nom: result.nom,
        expires_at: result.expires_at,
      })
    } catch (error) {
      logger.error('Erreur creation cle API', error, {
        context: 'CreateAPIKeyModal',
        showToast: true,
      })
      setIsSubmitting(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div
        ref={focusTrapRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
        className="bg-white rounded-lg max-w-lg w-full p-6"
      >
        <h2 id="modal-title" className="text-xl font-bold mb-4">Créer une clé API</h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          <p className="text-sm text-gray-500">Les champs marques <span className="text-red-500">*</span> sont obligatoires</p>
          {/* Nom */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nom <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={nom}
              onChange={(e) => setNom(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Clé de production"
              maxLength={255}
              required
              aria-required="true"
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Utilisée pour le système de synchronisation..."
              rows={2}
            />
          </div>

          {/* Scopes */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Permissions (Scopes) <span className="text-red-500">*</span>
            </label>
            <div className="grid grid-cols-2 gap-2">
              {availableScopes.map((scope) => (
                <label
                  key={scope}
                  className="flex items-center gap-2 p-2 border rounded cursor-pointer hover:bg-gray-50"
                >
                  <input
                    type="checkbox"
                    checked={scopes.includes(scope)}
                    onChange={() => toggleScope(scope)}
                    className="w-4 h-4 text-blue-600"
                  />
                  <span className="text-sm">{scope}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Expiration */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Expiration (jours)
            </label>
            <input
              type="number"
              value={expiresDays}
              onChange={(e) => setExpiresDays(parseInt(e.target.value) || 90)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              min={1}
              max={3650}
            />
            <p className="text-xs text-gray-500 mt-1">
              La clé expirera automatiquement après {expiresDays} jours
            </p>
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              disabled={isSubmitting}
            >
              Annuler
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2 disabled:opacity-50"
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Création...
                </>
              ) : (
                <>
                  <Plus className="w-4 h-4" />
                  Créer
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
