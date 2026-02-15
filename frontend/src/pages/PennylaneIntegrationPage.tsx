/**
 * PennylaneIntegrationPage - Page principale integration Pennylane
 * Module 18.12 - Import donnees comptables
 *
 * Onglets :
 * - Dashboard : Reconciliation des factures importees
 * - Mappings : Configuration codes analytiques -> chantiers
 * - Historique : Liste des synchronisations
 */

import { useState, useCallback } from 'react'
import Layout from '../components/Layout'
import PennylaneReconciliationDashboard from '../components/financier/PennylaneReconciliationDashboard'
import PennylaneMappingsManager from '../components/financier/PennylaneMappingsManager'
import { useDocumentTitle } from '../hooks/useDocumentTitle'
import PennylaneSyncHistory from '../components/financier/PennylaneSyncHistory'
import {
  FileText,
  Tag,
  History,
  Link2,
} from 'lucide-react'

type TabId = 'dashboard' | 'mappings' | 'history'

interface Tab {
  id: TabId
  label: string
  icon: typeof FileText
  description: string
}

const TABS: Tab[] = [
  {
    id: 'dashboard',
    label: 'Reconciliation',
    icon: FileText,
    description: 'Validez les factures importees depuis Pennylane',
  },
  {
    id: 'mappings',
    label: 'Mappings',
    icon: Tag,
    description: 'Configurez les codes analytiques',
  },
  {
    id: 'history',
    label: 'Historique',
    icon: History,
    description: 'Consultez les synchronisations passees',
  },
]

export default function PennylaneIntegrationPage() {
  useDocumentTitle('Intégration Pennylane')
  const [activeTab, setActiveTab] = useState<TabId>('dashboard')
  const [syncTrigger, setSyncTrigger] = useState(0)

  const handleSyncTriggered = useCallback(() => {
    // Incrementer le trigger pour forcer le refresh de l'historique
    setSyncTrigger((prev) => prev + 1)
  }, [])

  return (
    <Layout>
      <div className="space-y-6" role="main" aria-label="Integration Pennylane">
        {/* Header */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-blue-600 rounded-xl flex items-center justify-center">
              <Link2 className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">Integration Pennylane</h1>
              <p className="text-sm text-gray-500">
                Import et reconciliation des donnees comptables
              </p>
            </div>
          </div>
        </div>

        {/* Tabs navigation */}
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8" aria-label="Onglets">
            {TABS.map((tab) => {
              const Icon = tab.icon
              const isActive = activeTab === tab.id

              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`
                    group inline-flex items-center gap-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors
                    ${isActive
                      ? 'border-blue-600 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }
                  `}
                  aria-current={isActive ? 'page' : undefined}
                >
                  <Icon size={18} className={isActive ? 'text-blue-600' : 'text-gray-600 group-hover:text-gray-700'} />
                  {tab.label}
                </button>
              )
            })}
          </nav>
        </div>

        {/* Tab description */}
        <p className="text-sm text-gray-500">
          {TABS.find((t) => t.id === activeTab)?.description}
        </p>

        {/* Tab content */}
        <div className="min-h-[400px]">
          {activeTab === 'dashboard' && (
            <PennylaneReconciliationDashboard onSyncTriggered={handleSyncTriggered} />
          )}
          {activeTab === 'mappings' && (
            <PennylaneMappingsManager />
          )}
          {activeTab === 'history' && (
            <PennylaneSyncHistory refreshTrigger={syncTrigger} />
          )}
        </div>

        {/* Help section */}
        <div className="bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-xl p-6">
          <h3 className="font-semibold text-purple-900 mb-3">Comment fonctionne l'integration ?</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div className="bg-white/60 rounded-lg p-4">
              <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center mb-2">
                <span className="text-purple-600 font-bold">1</span>
              </div>
              <p className="font-medium text-gray-900 mb-1">Synchronisation automatique</p>
              <p className="text-gray-600">
                Toutes les 15 minutes, Hub Chantier recupere les factures payees depuis Pennylane.
              </p>
            </div>
            <div className="bg-white/60 rounded-lg p-4">
              <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center mb-2">
                <span className="text-purple-600 font-bold">2</span>
              </div>
              <p className="font-medium text-gray-900 mb-1">Matching intelligent</p>
              <p className="text-gray-600">
                Les factures sont automatiquement associees aux achats previsionnels via le fournisseur, montant et code analytique.
              </p>
            </div>
            <div className="bg-white/60 rounded-lg p-4">
              <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center mb-2">
                <span className="text-purple-600 font-bold">3</span>
              </div>
              <p className="font-medium text-gray-900 mb-1">Validation manuelle</p>
              <p className="text-gray-600">
                Les factures sans correspondance arrivent en reconciliation pour validation ou reaffectation manuelle.
              </p>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}
