import { useState, useEffect, useCallback } from 'react'
import { Clock, Loader2, AlertCircle } from 'lucide-react'
import { devisService } from '../../services/devis'
import type { JournalDevisEntry } from '../../types'

interface JournalDevisProps {
  devisId: number
}

export default function JournalDevis({ devisId }: JournalDevisProps) {
  const [entries, setEntries] = useState<JournalDevisEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadJournal = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const result = await devisService.listJournal(devisId, { limit: 50 })
      setEntries(result.items)
    } catch {
      setError('Erreur lors du chargement du journal')
    } finally {
      setLoading(false)
    }
  }, [devisId])

  useEffect(() => {
    loadJournal()
  }, [loadJournal])

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="w-6 h-6 animate-spin text-blue-600" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center gap-2">
        <AlertCircle className="w-4 h-4 flex-shrink-0" />
        <span className="text-sm">{error}</span>
      </div>
    )
  }

  if (entries.length === 0) {
    return (
      <div className="text-center py-8 text-gray-400">
        <Clock className="w-8 h-8 mx-auto mb-2" />
        <p className="text-sm">Aucune modification enregistree</p>
      </div>
    )
  }

  return (
    <div className="space-y-0">
      {entries.map((entry, index) => (
        <div key={entry.id} className="relative flex gap-4 pb-6">
          {/* Timeline line */}
          {index < entries.length - 1 && (
            <div className="absolute left-[15px] top-8 bottom-0 w-px bg-gray-200" />
          )}

          {/* Timeline dot */}
          <div className="relative z-10 flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
            <Clock className="w-4 h-4 text-blue-600" />
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-sm font-medium text-gray-900">{entry.action}</span>
              <span className="text-xs text-gray-400">
                {entry.created_at ? new Date(entry.created_at).toLocaleString('fr-FR', {
                  day: '2-digit',
                  month: '2-digit',
                  year: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit',
                }) : ''}
              </span>
            </div>

            {entry.details && (
              <p className="text-xs text-gray-500">
                {entry.details}
              </p>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}
