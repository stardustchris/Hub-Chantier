/**
 * CoutsMainOeuvrePanel - Couts main-d'oeuvre d'un chantier (FIN-09)
 *
 * Affiche :
 * - Total heures et cout en en-tete
 * - Table: nom employe, heures validees, taux horaire, cout total
 * - Filtre par plage de dates
 */

import { useState, useEffect, useCallback } from 'react'
import { Loader2, Search } from 'lucide-react'
import { financierService } from '../../services/financier'
import { logger } from '../../services/logger'
import type { CoutMainOeuvreSummary } from '../../types'
import { formatEUR } from '../../utils/format'

interface CoutsMainOeuvrePanelProps {
  chantierId: number
}

export default function CoutsMainOeuvrePanel({ chantierId }: CoutsMainOeuvrePanelProps) {
  const [data, setData] = useState<CoutMainOeuvreSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [dateDebut, setDateDebut] = useState('')
  const [dateFin, setDateFin] = useState('')

  const loadData = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const params: { date_debut?: string; date_fin?: string } = {}
      if (dateDebut) params.date_debut = dateDebut
      if (dateFin) params.date_fin = dateFin
      const result = await financierService.getCoutsMainOeuvre(chantierId, params)
      setData(result)
    } catch (err) {
      setError('Erreur lors du chargement des couts main-d\'oeuvre')
      logger.error('Erreur chargement couts MO', err, { context: 'CoutsMainOeuvrePanel' })
    } finally {
      setLoading(false)
    }
  }, [chantierId, dateDebut, dateFin])

  useEffect(() => {
    loadData()
  }, [loadData])

  const handleFilter = () => {
    loadData()
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="w-6 h-6 animate-spin text-primary-600" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
        {error}
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Summary */}
      {data && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="bg-white border border-blue-200 rounded-xl p-4">
            <p className="text-sm text-gray-500 mb-1">Total heures</p>
            <p className="text-2xl font-bold text-blue-700">
              {data.total_heures.toLocaleString('fr-FR', { minimumFractionDigits: 1 })} h
            </p>
          </div>
          <div className="bg-white border border-green-200 rounded-xl p-4">
            <p className="text-sm text-gray-500 mb-1">Cout total</p>
            <p className="text-2xl font-bold text-green-700">{formatEUR(data.cout_total)}</p>
          </div>
        </div>
      )}

      {/* Date filter */}
      <div className="bg-white border rounded-xl p-4">
        <div className="flex flex-wrap items-end gap-3">
          <div>
            <label className="block text-xs text-gray-500 mb-1">Date debut</label>
            <input
              type="date"
              value={dateDebut}
              onChange={(e) => setDateDebut(e.target.value)}
              className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">Date fin</label>
            <input
              type="date"
              value={dateFin}
              onChange={(e) => setDateFin(e.target.value)}
              className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <button
            onClick={handleFilter}
            className="flex items-center gap-1 px-3 py-1.5 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 text-sm transition-colors"
          >
            <Search size={14} />
            Filtrer
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white border rounded-xl">
        <div className="p-4 border-b">
          <h3 className="font-semibold text-gray-900">Detail par employe</h3>
        </div>
        {data && data.details.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            Aucune donnee de main-d'oeuvre
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="text-left px-4 py-3 font-medium text-gray-500">Employe</th>
                  <th className="text-right px-4 py-3 font-medium text-gray-500">Heures validees</th>
                  <th className="text-right px-4 py-3 font-medium text-gray-500">Taux horaire</th>
                  <th className="text-right px-4 py-3 font-medium text-gray-500">Cout total</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {data?.details.map((employe) => (
                  <tr key={employe.user_id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium text-gray-900">
                      {employe.prenom} {employe.nom}
                    </td>
                    <td className="px-4 py-3 text-right text-gray-700">
                      {employe.heures_validees.toLocaleString('fr-FR', { minimumFractionDigits: 1 })} h
                    </td>
                    <td className="px-4 py-3 text-right text-gray-500">
                      {formatEUR(employe.taux_horaire)}/h
                    </td>
                    <td className="px-4 py-3 text-right font-medium whitespace-nowrap">
                      {formatEUR(employe.cout_total)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
