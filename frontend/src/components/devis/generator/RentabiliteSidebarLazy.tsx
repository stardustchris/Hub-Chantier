/**
 * Lazy wrapper for RentabiliteSidebar with Recharts lazy-loading
 * Performance optimization: 2.2.5
 */

import { lazy, Suspense } from 'react'
import type { DevisDetail } from '../../../types'

const RentabiliteSidebar = lazy(() => import('./RentabiliteSidebar'))

interface Props {
  devis: DevisDetail
  onSaved?: () => void
}

function RentabiliteSidebarSkeleton() {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 animate-pulse">
      <div className="flex items-center justify-between mb-4">
        <div className="h-5 w-24 bg-gray-200 rounded"></div>
        <div className="h-4 w-16 bg-gray-200 rounded"></div>
      </div>
      <div className="mx-auto w-40 h-40 bg-gray-200 rounded-full mb-4"></div>
      <div className="space-y-2">
        <div className="h-4 w-full bg-gray-200 rounded"></div>
        <div className="h-4 w-full bg-gray-200 rounded"></div>
        <div className="h-4 w-full bg-gray-200 rounded"></div>
      </div>
    </div>
  )
}

export default function RentabiliteSidebarLazy(props: Props) {
  return (
    <Suspense fallback={<RentabiliteSidebarSkeleton />}>
      <RentabiliteSidebar {...props} />
    </Suspense>
  )
}
