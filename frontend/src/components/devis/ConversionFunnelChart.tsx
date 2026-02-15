/**
 * ConversionFunnelChart - Graphique funnel de conversion des devis
 * Lazy-loadable component for Recharts (Performance 2.2.5)
 */

import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'

interface ConversionFunnelChartProps {
  funnelData: Array<{ name: string; value: number; color: string }>
}

export default function ConversionFunnelChart({ funnelData }: ConversionFunnelChartProps) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={funnelData} layout="vertical" margin={{ left: 80 }}>
        <XAxis type="number" hide />
        <YAxis type="category" dataKey="name" tick={{ fontSize: 12, fill: '#6B7280' }} />
        <Tooltip
          formatter={(value) => [`${value} devis`]}
          contentStyle={{ borderRadius: 8, border: '1px solid #E5E7EB' }}
        />
        <Bar dataKey="value" radius={[0, 4, 4, 0]} maxBarSize={32}>
          {funnelData.map((entry) => (
            <Cell key={entry.name} fill={entry.color} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
