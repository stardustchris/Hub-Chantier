/**
 * ChartTooltip - Tooltip partage pour les graphiques Recharts financiers.
 *
 * Utilise par EvolutionChart, CamembertLots, BarresComparativesLots.
 */

import { formatEUR } from '../../utils/format'

export interface ChartTooltipEntry {
  name: string
  value: number
  color?: string
  payload?: { fill?: string }
}

interface ChartTooltipProps {
  active?: boolean
  payload?: ReadonlyArray<ChartTooltipEntry>
  label?: string
}

export default function ChartTooltip({ active, payload, label }: ChartTooltipProps) {
  if (!active || !payload || payload.length === 0) return null

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-3">
      {label && <p className="text-sm font-medium text-gray-900 mb-1">{label}</p>}
      {payload.map((entry) => (
        <p
          key={entry.name}
          className="text-sm"
          style={{ color: entry.color ?? entry.payload?.fill ?? '#374151' }}
        >
          {entry.name} : {formatEUR(entry.value)}
        </p>
      ))}
    </div>
  )
}
