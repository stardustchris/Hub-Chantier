/**
 * EvolutionChart - Courbes d'evolution financiere cumulative (FIN-17)
 *
 * LineChart Recharts avec 3 courbes :
 * - Prévu cumulé (bleu)
 * - Engagé cumulé (ambre)
 * - Déboursé cumulé (vert)
 */

import { useState, useEffect, useCallback } from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import { Loader2 } from 'lucide-react'
import { financierService } from '../../services/financier'
import { logger } from '../../services/logger'
import ChartTooltip from './ChartTooltip'
import type { EvolutionMensuelle } from '../../types'

interface EvolutionChartProps {
  chantierId: number
}

const formatYAxis = (value: number): string =>
  `${(value / 1000).toFixed(0)}k`

export default function EvolutionChart({ chantierId }: EvolutionChartProps) {
  const [data, setData] = useState<EvolutionMensuelle[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadData = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const result = await financierService.getEvolutionFinanciere(chantierId)
      setData(result.points)
    } catch (err) {
      setError('Erreur lors du chargement de l\'evolution financiere')
      logger.error('Erreur chargement evolution financiere', err, { context: 'EvolutionChart' })
    } finally {
      setLoading(false)
    }
  }, [chantierId])

  useEffect(() => {
    loadData()
  }, [loadData])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[300px]">
        <Loader2 className="w-6 h-6 animate-spin text-primary-600" aria-label="Chargement du graphique d'evolution" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-[300px] text-sm text-red-600">
        {error}
      </div>
    )
  }

  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center h-[300px] text-sm text-gray-500">
        Aucune donnee d'evolution disponible
      </div>
    )
  }

  return (
    <div role="img" aria-label="Graphique d'evolution financiere du chantier avec courbes prevu, engage et debourse">
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="mois"
            tick={{ fontSize: 12 }}
            stroke="#6b7280"
          />
          <YAxis
            tickFormatter={formatYAxis}
            tick={{ fontSize: 12 }}
            stroke="#6b7280"
          />
          <Tooltip content={<ChartTooltip />} />
          <Legend />
          <Line
            type="monotone"
            dataKey="prevu_cumule"
            name="Prévu"
            stroke="#3b82f6"
            strokeWidth={2}
            dot={{ r: 3 }}
            activeDot={{ r: 5 }}
          />
          <Line
            type="monotone"
            dataKey="engage_cumule"
            name="Engagé"
            stroke="#f59e0b"
            strokeWidth={2}
            dot={{ r: 3 }}
            activeDot={{ r: 5 }}
          />
          <Line
            type="monotone"
            dataKey="realise_cumule"
            name="Déboursé"
            stroke="#10b981"
            strokeWidth={2}
            dot={{ r: 3 }}
            activeDot={{ r: 5 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
