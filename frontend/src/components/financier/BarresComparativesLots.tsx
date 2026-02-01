/**
 * BarresComparativesLots - Comparaison prevu/engage/realise par lot (FIN-17)
 *
 * BarChart Recharts avec 3 barres par lot :
 * - Prevu (bleu)
 * - Engage (ambre)
 * - Realise (vert)
 */

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import type { RepartitionLot } from '../../types'
import ChartTooltip from './ChartTooltip'

interface BarresComparativesLotsProps {
  lots: RepartitionLot[]
}

const formatYAxis = (value: number): string =>
  `${(value / 1000).toFixed(0)}k EUR`

export default function BarresComparativesLots({ lots }: BarresComparativesLotsProps) {
  if (lots.length === 0) {
    return (
      <div className="flex items-center justify-center h-[400px] text-sm text-gray-500">
        Aucun lot budgetaire
      </div>
    )
  }

  const chartData = lots.map((lot) => ({
    code_lot: lot.code_lot,
    Prevu: lot.total_prevu_ht,
    Engage: lot.engage,
    Realise: lot.realise,
  }))

  return (
    <div role="img" aria-label="Barres comparatives prevu, engage et realise par lot budgetaire">
      <ResponsiveContainer width="100%" height={400}>
        <BarChart data={chartData} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="code_lot"
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
          <Bar dataKey="Prevu" fill="#3b82f6" radius={[4, 4, 0, 0]} />
          <Bar dataKey="Engage" fill="#f59e0b" radius={[4, 4, 0, 0]} />
          <Bar dataKey="Realise" fill="#10b981" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
