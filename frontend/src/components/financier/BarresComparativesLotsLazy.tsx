/**
 * Lazy wrapper for BarresComparativesLots with Recharts lazy-loading
 * Performance optimization: 2.2.5
 */

import { lazy, Suspense } from 'react'
import type { RepartitionLot } from '../../types'

const BarresComparativesLots = lazy(() => import('./BarresComparativesLots'))

interface BarresComparativesLotsProps {
  lots: RepartitionLot[]
}

function BarresComparativesLotsSkeleton() {
  return (
    <div className="h-[400px] bg-gray-50 rounded-lg animate-pulse flex items-center justify-center">
      <div className="text-sm text-gray-500">Chargement du graphique...</div>
    </div>
  )
}

export default function BarresComparativesLotsLazy(props: BarresComparativesLotsProps) {
  return (
    <Suspense fallback={<BarresComparativesLotsSkeleton />}>
      <BarresComparativesLots {...props} />
    </Suspense>
  )
}
