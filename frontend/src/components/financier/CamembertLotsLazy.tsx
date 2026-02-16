/**
 * Lazy wrapper for CamembertLots with Recharts lazy-loading
 * Performance optimization: 2.2.5
 */

import { lazy, Suspense } from 'react'
import type { RepartitionLot } from '../../types'

const CamembertLots = lazy(() => import('./CamembertLots'))

interface CamembertLotsProps {
  lots: RepartitionLot[]
}

function CamembertLotsSkeleton() {
  return (
    <div className="h-[300px] bg-gray-50 rounded-lg animate-pulse flex items-center justify-center">
      <div className="text-sm text-gray-500">Chargement du graphique...</div>
    </div>
  )
}

export default function CamembertLotsLazy(props: CamembertLotsProps) {
  return (
    <Suspense fallback={<CamembertLotsSkeleton />}>
      <CamembertLots {...props} />
    </Suspense>
  )
}
