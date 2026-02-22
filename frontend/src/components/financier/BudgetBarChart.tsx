/**
 * BudgetBarChart - Barres Budget/Engagé/Déboursé par chantier
 * Lazy-loadable component for Recharts (Performance 2.2.5)
 */

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { formatEUR } from '../../utils/format'

interface BudgetBarChartProps {
  data: Array<{
    name: string
    Budget: number
    Engagé: number
    Déboursé: number
  }>
  chartColors: {
    budget: string
    engage: string
    realise: string
  }
}

const MAX_LABEL = 12

// Tronque un nom trop long pour éviter le débordement sur le graphique
function truncate(name: string) {
  return name.length > MAX_LABEL ? name.slice(0, MAX_LABEL) + '…' : name
}

// Tick personnalisé avec label vertical pour éviter le clipping SVG
function CustomTick({ x, y, payload }: { x?: number; y?: number; payload?: { value: string } }) {
  return (
    <g transform={`translate(${x},${y})`}>
      <text
        x={0}
        y={0}
        dy={4}
        textAnchor="end"
        fill="#6b7280"
        fontSize={10}
        transform="rotate(-45)"
      >
        {payload?.value}
      </text>
    </g>
  )
}

export default function BudgetBarChart({ data, chartColors }: BudgetBarChartProps) {
  const truncatedData = data.map(d => ({ ...d, name: truncate(d.name) }))

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={truncatedData} margin={{ top: 5, right: 20, left: 10, bottom: 80 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
        <XAxis
          dataKey="name"
          tick={<CustomTick />}
          interval={0}
          height={90}
        />
        <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`} />
        <Tooltip
          formatter={(value) => [formatEUR(Number(value))]}
          contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb' }}
        />
        <Legend wrapperStyle={{ fontSize: '12px' }} />
        <Bar dataKey="Budget" fill={chartColors.budget} radius={[4, 4, 0, 0]} />
        <Bar dataKey="Engagé" fill={chartColors.engage} radius={[4, 4, 0, 0]} />
        <Bar dataKey="Déboursé" fill={chartColors.realise} radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}

