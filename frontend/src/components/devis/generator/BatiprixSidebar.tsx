import { useState } from 'react'
import { Settings, Layers } from 'lucide-react'
import BatiprixConfigModal from './BatiprixConfigModal'

export default function BatiprixSidebar() {
  const [showConfig, setShowConfig] = useState(false)

  // Batiprix status from localStorage
  const apiKey = localStorage.getItem('batiprix_api_key')
  const connected = !!apiKey
  const usageCount = Number(localStorage.getItem('batiprix_usage_count') || '0')
  const usageLimit = 500

  return (
    <>
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
              <Layers className="w-5 h-5 text-green-600" />
            </div>
            <h3 className="font-semibold text-gray-900">Batiprix</h3>
          </div>
          <span className={`px-2 py-1 text-xs rounded-full font-medium ${
            connected ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'
          }`}>
            {connected ? 'Connecte' : 'Non connecte'}
          </span>
        </div>

        <p className="text-sm text-gray-500 mb-4">
          Accedez a plus de 50 000 prix d&apos;ouvrages BTP actualises.
        </p>

        {connected && (
          <div className="space-y-2 mb-4">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">Ouvrages utilises ce mois</span>
              <span className="font-medium">{usageCount} / {usageLimit}</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-green-500 h-2 rounded-full transition-all"
                style={{ width: `${Math.min(100, (usageCount / usageLimit) * 100)}%` }}
              />
            </div>
          </div>
        )}

        <button
          onClick={() => setShowConfig(true)}
          className="w-full flex items-center justify-center gap-2 px-3 py-2 border border-gray-200 rounded-lg text-sm text-gray-700 hover:bg-gray-50"
        >
          <Settings className="w-4 h-4" /> Parametres API
        </button>
      </div>

      {showConfig && <BatiprixConfigModal onClose={() => setShowConfig(false)} />}
    </>
  )
}
