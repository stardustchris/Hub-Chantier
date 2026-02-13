/**
 * PostSkeleton - Squelette pour un post du feed
 * Imite la structure d'un post : avatar + nom/date + contenu + actions
 */

import { Skeleton } from '../ui'

export default function PostSkeleton() {
  return (
    <div className="bg-white border border-gray-200 rounded-xl p-4">
      <div className="flex gap-3">
        {/* Avatar circulaire */}
        <Skeleton variant="circular" width={40} height={40} className="shrink-0" />

        {/* Contenu principal */}
        <div className="flex-1 space-y-3">
          {/* En-tête : nom auteur + date */}
          <div className="space-y-1">
            <Skeleton variant="text" width="8rem" />
            <Skeleton variant="text" width="6rem" />
          </div>

          {/* Contenu du post (3 lignes) */}
          <Skeleton variant="text" lines={3} />

          {/* Barre d'actions en bas */}
          <div className="flex gap-2 pt-2">
            <Skeleton variant="rectangular" width={60} height={32} />
            <Skeleton variant="rectangular" width={60} height={32} />
          </div>
        </div>
      </div>
    </div>
  )
}
