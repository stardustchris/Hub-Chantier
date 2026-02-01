/**
 * CamembertLots - Repartition budgetaire par lot en camembert (FIN-17)
 *
 * PieChart Recharts avec couleurs distinctes par lot.
 * Labels avec nom du lot + pourcentage.
 */

import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import type { RepartitionLot } from '../../types'

interface CamembertLotsProps {
  lots: RepartitionLot[]
}

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#f97316']

const formatEUR = (value: number): string =>
  new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(value)

import type { PieLabelRenderProps } from 'recharts'

const RADIAN = Math.PI / 180

function renderLabel(props: PieLabelRenderProps) {
  const cx = Number(props.cx ?? 0)
  const cy = Number(props.cy ?? 0)
  const midAngle = Number(props.midAngle ?? 0)
  const innerRadius = Number(props.innerRadius ?? 0)
  const outerRadius = Number(props.outerRadius ?? 0)
  const percent = Number(props.percent ?? 0)
  const name = String(props.name ?? '')

  const radius = innerRadius + (outerRadius - innerRadius) * 1.4
  const x = cx + radius * Math.cos(-midAngle * RADIAN)
  const y = cy + radius * Math.sin(-midAngle * RADIAN)

  if (percent < 0.05) return null

  return (
    <text
      x={x}
      y={y}
      fill="#374151"
      textAnchor={x > cx ? 'start' : 'end'}
      dominantBaseline="central"
      fontSize={11}
    >
      {name} ({(percent * 100).toFixed(0)}%)
    </text>
  )
}

interface CustomTooltipProps {
  active?: boolean
  payload?: ReadonlyArray<{
    name: string
    value: number
    payload: { fill: string }
  }>
}

function ChartTooltip({ active, payload }: CustomTooltipProps) {
  if (!active || !payload || payload.length === 0) return null

  const entry = payload[0]
  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-3">
      <p className="text-sm font-medium text-gray-900">{entry.name}</p>
      <p className="text-sm" style={{ color: entry.payload.fill }}>
        {formatEUR(entry.value)}
      </p>
    </div>
  )
}

export default function CamembertLots({ lots }: CamembertLotsProps) {
  if (lots.length === 0) {
    return (
      <div className="flex items-center justify-center h-[300px] text-sm text-gray-500">
        Aucun lot budgetaire
      </div>
    )
  }

  const chartData = lots.map((lot) => ({
    name: lot.code_lot,
    value: lot.total_prevu_ht,
    libelle: lot.libelle,
  }))

  return (
    <div role="img" aria-label="Camembert de repartition budgetaire par lot">
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            outerRadius={90}
            dataKey="value"
            label={renderLabel}
            labelLine={false}
          >
            {chartData.map((_, index) => (
              <Cell
                key={`cell-${chartData[index].name}`}
                fill={COLORS[index % COLORS.length]}
              />
            ))}
          </Pie>
          <Tooltip content={<ChartTooltip />} />
          <Legend
            formatter={(value: string) => {
              const lot = lots.find((l) => l.code_lot === value)
              return lot ? `${value} - ${lot.libelle}` : value
            }}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}
