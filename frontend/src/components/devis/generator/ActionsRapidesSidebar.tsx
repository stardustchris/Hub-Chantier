import { useState } from 'react'
import { Copy, RefreshCw, FileText, Clock } from 'lucide-react'
import { devisService } from '../../../services/devis'
import VersionsPanel from '../VersionsPanel'
import AttestationTVAPanel from '../AttestationTVAPanel'
import JournalDevis from '../JournalDevis'
import type { DevisDetail } from '../../../types'

interface Props {
  devis: DevisDetail
  onReload: () => void
}

export default function ActionsRapidesSidebar({ devis, onReload }: Props) {
  const [showVersions, setShowVersions] = useState(false)
  const [showAttestation, setShowAttestation] = useState(false)
  const [showJournal, setShowJournal] = useState(false)

  const handleDuplicate = async () => {
    await devisService.creerRevision(devis.id)
    onReload()
  }

  const handleVariante = async () => {
    await devisService.creerVariante(devis.id, 'ALT')
    onReload()
  }

  return (
    <>
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h3 className="font-semibold text-gray-900 mb-4">Actions</h3>
        <div className="space-y-2">
          <button
            onClick={handleDuplicate}
            className="w-full flex items-center gap-3 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg text-sm font-medium transition-colors text-left"
          >
            <Copy className="w-5 h-5 text-gray-500" /> Dupliquer
          </button>
          <button
            onClick={handleVariante}
            className="w-full flex items-center gap-3 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg text-sm font-medium transition-colors text-left"
          >
            <RefreshCw className="w-5 h-5 text-gray-500" /> Creer variante
          </button>
          <button
            onClick={() => setShowAttestation(true)}
            className="w-full flex items-center gap-3 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg text-sm font-medium transition-colors text-left"
          >
            <FileText className="w-5 h-5 text-gray-500" /> Generer CERFA TVA
          </button>
          <button
            onClick={() => setShowJournal(!showJournal)}
            className="w-full flex items-center gap-3 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg text-sm font-medium transition-colors text-left"
          >
            <Clock className="w-5 h-5 text-gray-500" /> Historique
          </button>
        </div>
      </div>

      {showVersions && (
        <VersionsPanel
          devisId={devis.id}
          isEditable={devis.statut === 'brouillon'}
          onVersionCreated={() => { setShowVersions(false); onReload() }}
        />
      )}
      {showAttestation && (
        <AttestationTVAPanel devisId={devis.id} devis={devis} />
      )}
      {showJournal && (
        <JournalDevis devisId={devis.id} />
      )}
    </>
  )
}
