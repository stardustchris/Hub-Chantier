/**
 * StatutPieChart - Camembert répartition statuts chantiers
 * Lazy-loadable component for Recharts (Performance 2.2.5)
 */

import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts'
import type { PieLabelRenderProps } from 'recharts'
import ChartTooltip from './ChartTooltip'

interface StatutPieChartProps {
  data: Array<{ name: string; value: number; color: string }>
  renderLabel: (props: PieLabelRenderProps) => string | null
}

export default function StatutPieChart({ data, renderLabel }: StatutPieChartProps) {
  return (
    <ResponsiveContainer width="100%" height={250}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          innerRadius={50}
          outerRadius={90}
          paddingAngle={3}
          dataKey="value"
          label={renderLabel}
          labelLine={false}
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.color} />
          ))}
        </Pie>
        <Tooltip
          content={({ active, payload }) => (
            <ChartTooltip
              active={active}
              payload={payload?.map((p) => ({
                name: String(p.name),
                value: Number(p.value),
                color: String(p.payload?.color || p.payload?.fill || '#374151'),
              }))}
            />
          )}
        />
      </PieChart>
    </ResponsiveContainer>
  )
}
