/**
 * MargesBarChart - Barres marges par chantier (horizontal)
 * Lazy-loadable component for Recharts (Performance 2.2.5)
 */

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'

interface MargesBarChartProps {
  data: Array<{
    name: string
    marge: number
    fill: string
  }>
}

export default function MargesBarChart({ data }: MargesBarChartProps) {
  return (
    <ResponsiveContainer width="100%" height={250}>
      <BarChart data={data} layout="vertical" margin={{ top: 5, right: 30, left: 80, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
        <XAxis type="number" tick={{ fontSize: 11 }} tickFormatter={(v) => `${v}%`} />
        <YAxis type="category" dataKey="name" tick={{ fontSize: 11 }} width={80} />
        <Tooltip
          formatter={(value) => [`${Number(value).toFixed(1)}%`, 'Marge']}
          contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb' }}
        />
        <Bar dataKey="marge" radius={[0, 4, 4, 0]}>
          {data.map((entry, index) => (
            <Cell key={`marge-${index}`} fill={entry.fill} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
