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

export default function BudgetBarChart({ data, chartColors }: BudgetBarChartProps) {
  return (
    <ResponsiveContainer width="100%" height={250}>
      <BarChart data={data} margin={{ top: 5, right: 10, left: 10, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
        <XAxis dataKey="name" tick={{ fontSize: 11 }} angle={-20} textAnchor="end" height={60} />
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
