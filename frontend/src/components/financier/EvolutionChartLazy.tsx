/**
 * Lazy wrapper for EvolutionChart with Recharts lazy-loading
 * Performance optimization: 2.2.5
 */

import { lazy, Suspense } from 'react'

const EvolutionChart = lazy(() => import('./EvolutionChart'))

interface EvolutionChartProps {
  chantierId: number
}

function EvolutionChartSkeleton() {
  return (
    <div className="h-[300px] bg-gray-50 rounded-lg animate-pulse flex items-center justify-center">
      <div className="text-sm text-gray-500">Chargement du graphique...</div>
    </div>
  )
}

export default function EvolutionChartLazy(props: EvolutionChartProps) {
  return (
    <Suspense fallback={<EvolutionChartSkeleton />}>
      <EvolutionChart {...props} />
    </Suspense>
  )
}
