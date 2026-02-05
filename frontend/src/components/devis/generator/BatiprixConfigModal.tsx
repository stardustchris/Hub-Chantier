import { useState } from 'react'
import { X, Save } from 'lucide-react'

interface Props {
  onClose: () => void
}

export default function BatiprixConfigModal({ onClose }: Props) {
  const [apiKey, setApiKey] = useState(localStorage.getItem('batiprix_api_key') || '')
  const [env, setEnv] = useState(localStorage.getItem('batiprix_env') || 'production')

  const handleSave = () => {
    if (apiKey.trim()) {
      localStorage.setItem('batiprix_api_key', apiKey.trim())
    } else {
      localStorage.removeItem('batiprix_api_key')
    }
    localStorage.setItem('batiprix_env', env)
    onClose()
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-lg">
        <div className="flex items-center justify-between p-6 border-b border-gray-100">
          <h2 className="text-lg font-semibold text-gray-900">Configuration Batiprix</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Cle API</label>
            <input
              type="password"
              value={apiKey}
              onChange={e => setApiKey(e.target.value)}
              className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none text-sm"
              placeholder="Votre cle API Batiprix"
            />
            <p className="text-xs text-gray-500 mt-1">Stockee localement dans votre navigateur</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Environnement</label>
            <select
              value={env}
              onChange={e => setEnv(e.target.value)}
              className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none text-sm"
            >
              <option value="production">Production</option>
              <option value="sandbox">Sandbox (test)</option>
            </select>
          </div>
        </div>

        <div className="flex justify-end gap-3 p-6 border-t border-gray-100">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg"
          >
            Annuler
          </button>
          <button
            onClick={handleSave}
            className="flex items-center gap-2 px-4 py-2 text-sm text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg"
          >
            <Save className="w-4 h-4" /> Enregistrer
          </button>
        </div>
      </div>
    </div>
  )
}
