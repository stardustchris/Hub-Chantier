/**
 * DashboardSkeleton - Squelette pour l'ensemble du dashboard
 * Imite la structure : barre supérieure (2 cartes) + stats + feed
 */

import { Skeleton } from '../ui'
import PostSkeleton from './PostSkeleton'

export default function DashboardSkeleton() {
  return (
    <div className="min-h-screen bg-gray-100">
      <div className="p-4 space-y-4">
        {/* Barre supérieure : ClockCard + WeatherCard skeleton */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-4">
            <Skeleton variant="text" width="50%" className="mb-3" />
            <Skeleton variant="rectangular" height={80} />
            <div className="mt-3 flex gap-2">
              <Skeleton variant="rectangular" height={40} className="flex-1" />
              <Skeleton variant="rectangular" height={40} className="flex-1" />
            </div>
          </div>
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-4">
            <Skeleton variant="text" width="50%" className="mb-3" />
            <Skeleton variant="rectangular" height={120} />
          </div>
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-4">
            <Skeleton variant="text" width="50%" className="mb-3" />
            <Skeleton variant="rectangular" height={120} />
          </div>
        </div>

        {/* Ligne de stats (3 blocs rectangulaires) */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="bg-white rounded-2xl shadow-sm border border-gray-200 p-4">
              <Skeleton variant="text" width="60%" className="mb-2" />
              <Skeleton variant="rectangular" height={60} />
            </div>
          ))}
        </div>

        {/* Section feed (3 posts skeleton) */}
        <div className="space-y-4">
          <PostSkeleton />
          <PostSkeleton />
          <PostSkeleton />
        </div>
      </div>
    </div>
  )
}
