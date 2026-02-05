import { useNavigate } from 'react-router-dom'
import { ArrowLeft, Eye, Send } from 'lucide-react'
import DevisStatusBadge from '../DevisStatusBadge'
import DevisWorkflowActions from '../DevisWorkflowActions'
import type { DevisDetail } from '../../../types'

interface Props {
  devis: DevisDetail
  onSoumettre: () => Promise<void>
  onValider: () => Promise<void>
  onRetournerBrouillon: () => Promise<void>
  onAccepter: () => Promise<void>
  onRefuser: (motif?: string) => Promise<void>
  onPerdu: (motif?: string) => Promise<void>
}

export default function GeneratorHeader({
  devis, onSoumettre, onValider, onRetournerBrouillon,
  onAccepter, onRefuser, onPerdu,
}: Props) {
  const navigate = useNavigate()

  return (
    <header className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-6 py-4 shadow-lg">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/devis')}
            className="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center hover:bg-white/30 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-xl font-bold">{devis.objet || 'Nouveau Devis'}</h1>
            <p className="text-indigo-200 text-sm">{devis.numero} &bull; {devis.client_nom}</p>
          </div>
          <DevisStatusBadge statut={devis.statut} size="md" />
        </div>

        <div className="flex items-center gap-3">
          <DevisWorkflowActions
            statut={devis.statut}
            onSoumettre={onSoumettre}
            onValider={onValider}
            onRetournerBrouillon={onRetournerBrouillon}
            onAccepter={onAccepter}
            onRefuser={onRefuser}
            onPerdu={onPerdu}
          />
          <button className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg text-sm font-medium transition-colors">
            <Eye className="w-4 h-4" />
            Apercu PDF
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-white text-indigo-600 hover:bg-indigo-50 rounded-lg text-sm font-medium transition-colors">
            <Send className="w-4 h-4" />
            Envoyer au client
          </button>
        </div>
      </div>
    </header>
  )
}
