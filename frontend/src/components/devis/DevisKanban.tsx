import { useNavigate } from 'react-router-dom'
import { User, Euro } from 'lucide-react'
import type { DevisRecent, StatutDevis } from '../../types'
import { STATUT_DEVIS_CONFIG } from '../../types'

const formatEUR = (value: number) =>
  new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(value)

const KANBAN_COLUMNS: StatutDevis[] = [
  'brouillon',
  'en_validation',
  'envoye',
  'vu',
  'en_negociation',
  'accepte',
  'refuse',
]

interface DevisKanbanProps {
  devis: DevisRecent[]
  devisParStatut: Record<string, number>
}

export default function DevisKanban({ devis, devisParStatut }: DevisKanbanProps) {
  const navigate = useNavigate()

  const getDevisByStatut = (statut: StatutDevis): DevisRecent[] => {
    return devis.filter((d) => d.statut === statut)
  }

  return (
    <div className="overflow-x-auto pb-4">
      <div className="flex gap-4 min-w-max">
        {KANBAN_COLUMNS.map((statut) => {
          const config = STATUT_DEVIS_CONFIG[statut]
          const items = getDevisByStatut(statut)
          const count = devisParStatut[statut] || 0

          return (
            <div
              key={statut}
              className="w-72 flex-shrink-0 bg-gray-50 rounded-xl"
            >
              {/* Column header */}
              <div
                className="px-4 py-3 rounded-t-xl border-b-2"
                style={{ borderBottomColor: config.couleur }}
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-semibold text-gray-700">{config.label}</span>
                  <span
                    className="px-2 py-0.5 rounded-full text-xs font-bold"
                    style={{
                      backgroundColor: config.couleur + '20',
                      color: config.couleur,
                    }}
                  >
                    {count}
                  </span>
                </div>
              </div>

              {/* Cards */}
              <div className="p-2 space-y-2 max-h-[500px] overflow-y-auto">
                {items.map((d) => (
                  <div
                    key={d.id}
                    onClick={() => navigate(`/devis/${d.id}`)}
                    className="bg-white rounded-lg p-3 border border-gray-200 hover:shadow-md transition-shadow cursor-pointer"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <span className="text-xs font-mono text-gray-400">{d.numero}</span>
                    </div>
                    <p className="text-sm font-medium text-gray-900 line-clamp-2 mb-2">
                      {d.objet}
                    </p>
                    <div className="space-y-1.5 text-xs text-gray-500">
                      <div className="flex items-center gap-1.5">
                        <User className="w-3.5 h-3.5" />
                        <span className="truncate">{d.client_nom}</span>
                      </div>
                      <div className="flex items-center gap-1.5">
                        <Euro className="w-3.5 h-3.5" />
                        <span className="font-medium text-gray-700">{formatEUR(Number(d.montant_total_ht))}</span>
                      </div>
                    </div>
                  </div>
                ))}

                {items.length === 0 && (
                  <div className="text-center py-4 text-gray-400 text-xs">
                    Aucun devis
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
