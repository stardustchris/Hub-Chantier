/**
 * JournalFinancier - Timeline chronologique des modifications (FIN-15)
 *
 * Affiche l'historique des actions financieres avec :
 * - Date, auteur, action, champ modifie, ancienne/nouvelle valeur
 */

import { useState, useEffect } from 'react'
import { Clock, Loader2, ChevronDown } from 'lucide-react'
import { financierService } from '../../services/financier'
import { logger } from '../../services/logger'
import type { JournalFinancierEntry } from '../../types'

interface JournalFinancierProps {
  entiteType?: string
  entiteId?: number
}

const formatDateTime = (dateStr: string): string => {
  const date = new Date(dateStr)
  return date.toLocaleString('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export default function JournalFinancier({ entiteType, entiteId }: JournalFinancierProps) {
  const [entries, setEntries] = useState<JournalFinancierEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [limit, setLimit] = useState(20)

  useEffect(() => {
    loadJournal()
  }, [entiteType, entiteId, limit])

  const loadJournal = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await financierService.listJournal({
        entite_type: entiteType,
        entite_id: entiteId,
        limit,
      })
      setEntries(data.items || [])
    } catch (err) {
      setError('Erreur lors du chargement du journal')
      logger.error('Erreur chargement journal financier', err, { context: 'JournalFinancier' })
    } finally {
      setLoading(false)
    }
  }

  if (loading && entries.length === 0) {
    return (
      <div className="flex items-center justify-center py-6">
        <Loader2 className="w-5 h-5 animate-spin text-primary-600" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
        {error}
      </div>
    )
  }

  if (entries.length === 0) {
    return (
      <div className="text-center py-6 text-gray-500 text-sm">
        Aucune modification enregistree
      </div>
    )
  }

  return (
    <div className="bg-white border rounded-xl">
      <div className="p-4 border-b">
        <h3 className="font-semibold text-gray-900 flex items-center gap-2">
          <Clock size={16} />
          Journal financier
        </h3>
      </div>

      <div className="p-4">
        <div className="relative">
          {/* Ligne verticale */}
          <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200" />

          <div className="space-y-4">
            {entries.map((entry) => (
              <div key={entry.id} className="relative flex gap-4 pl-10">
                {/* Point */}
                <div className="absolute left-2.5 top-1.5 w-3 h-3 rounded-full bg-white border-2 border-blue-500" />

                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-xs text-gray-400">
                      {formatDateTime(entry.created_at)}
                    </span>
                    {entry.auteur_nom && (
                      <span className="text-xs font-medium text-gray-600">
                        {entry.auteur_nom}
                      </span>
                    )}
                  </div>

                  <p className="text-sm text-gray-900 mt-0.5">
                    <span className="font-medium">{entry.action}</span>
                    {entry.entite_type && (
                      <span className="text-gray-500">
                        {' '}sur {entry.entite_type} #{entry.entite_id}
                      </span>
                    )}
                  </p>

                  {entry.champ_modifie && (
                    <div className="mt-1 text-xs text-gray-500">
                      <span className="font-medium">{entry.champ_modifie}</span>
                      {entry.ancienne_valeur && (
                        <>
                          {' : '}
                          <span className="line-through text-red-400">{entry.ancienne_valeur}</span>
                        </>
                      )}
                      {entry.nouvelle_valeur && (
                        <>
                          {' -> '}
                          <span className="text-green-600">{entry.nouvelle_valeur}</span>
                        </>
                      )}
                    </div>
                  )}

                  {entry.motif && (
                    <p className="mt-1 text-xs text-gray-400 italic">
                      Motif: {entry.motif}
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {entries.length >= limit && (
          <div className="mt-4 text-center">
            <button
              onClick={() => setLimit(prev => prev + 20)}
              className="flex items-center gap-1 mx-auto px-3 py-1.5 text-sm text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
            >
              <ChevronDown size={14} />
              Voir plus
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
