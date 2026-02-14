/**
 * Composant PostCard - Affichage d'un post dans le feed
 * Selon CDC Section 2.2 - Types de posts affichés
 *
 * Optimisé avec React.memo pour éviter les re-renders inutiles
 */

import { useState, useCallback, memo } from 'react'
import { Link } from 'react-router-dom'
import type { Post, Author } from '../../types/dashboard'
import { formatRelativeShort } from '../../utils/dates'
import { renderContentWithMentions } from '../../utils/mentionRenderer'

interface PostCardProps {
  post: Post
  author?: Author
  allAuthors?: Author[]
  currentUserId: number
  onLike: (postId: number) => void
  onUnlike: (postId: number) => void
  onComment: (postId: number) => void
  onDelete?: (postId: number) => void
  isLiked?: boolean
}

// Badge couleur selon le rôle (FEED-06)
const roleBadgeColors: Record<string, string> = {
  admin: 'bg-purple-100 text-purple-800',
  conducteur: 'bg-blue-100 text-blue-800',
  chef_chantier: 'bg-green-100 text-green-800',
  compagnon: 'bg-gray-100 text-gray-800',
}

const PostCard = memo(function PostCard({
  post,
  author,
  allAuthors = [],
  currentUserId,
  onLike,
  onUnlike,
  onComment,
  onDelete,
  isLiked = false,
}: PostCardProps) {
  const [liked, setLiked] = useState(isLiked)
  const [likesCount, setLikesCount] = useState(post.likes_count)

  const handleLikeClick = useCallback(() => {
    if (liked) {
      onUnlike(post.id)
      setLiked(false)
      setLikesCount((c) => c - 1)
    } else {
      onLike(post.id)
      setLiked(true)
      setLikesCount((c) => c + 1)
    }
  }, [liked, onUnlike, onLike, post.id])

  const handleDeleteClick = useCallback(() => {
    onDelete?.(post.id)
  }, [onDelete, post.id])

  const handleCommentClick = useCallback(() => {
    onComment(post.id)
  }, [onComment, post.id])

  const isAuthor = post.author_id === currentUserId
  const canDelete = isAuthor || author?.role === 'admin'

  return (
    <article className={`bg-white rounded-lg shadow p-4 ${post.is_pinned ? 'border-l-4 border-orange-500' : ''}`}>
      {/* Header avec épingle si urgent (FEED-08) */}
      {post.is_pinned && (
        <div className="flex items-center gap-1 text-orange-600 text-sm mb-2">
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path d="M10 2a.75.75 0 01.75.75v.5h2.5a.75.75 0 010 1.5h-.75v2.604c0 .995.403 1.948 1.116 2.64l.54.524a.75.75 0 01-.54 1.282H6.384a.75.75 0 01-.54-1.282l.54-.524c.713-.692 1.116-1.645 1.116-2.64V4.75h-.75a.75.75 0 010-1.5h2.5v-.5A.75.75 0 0110 2z"/>
            <path d="M9.25 14.75v2.5a.75.75 0 001.5 0v-2.5h-1.5z"/>
          </svg>
          <span className="font-medium">Post épinglé</span>
        </div>
      )}

      {/* Auteur et badge (FEED-06) */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          {/* Avatar */}
          <div
            className="w-10 h-10 rounded-full flex items-center justify-center text-white font-semibold"
            style={{ backgroundColor: author?.couleur || '#6B7280' }}
          >
            {author ? `${author.prenom[0]}${author.nom[0]}` : '??'}
          </div>

          <div>
            <div className="flex items-center gap-2">
              {author ? (
                <Link to={`/utilisateurs/${author.id}`} className="font-semibold text-gray-900 hover:underline">
                  {author.prenom} {author.nom}
                </Link>
              ) : (
                <span className="font-semibold text-gray-900">Utilisateur</span>
              )}
              {/* Badge rôle */}
              {author?.role && (
                <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${roleBadgeColors[author.role] || 'bg-gray-100 text-gray-800'}`}>
                  {author.role === 'admin' && 'Direction'}
                  {author.role === 'conducteur' && 'Conducteur de travaux'}
                  {author.role === 'chef_chantier' && 'Chef de chantier'}
                  {author.role === 'compagnon' && 'Compagnon'}
                </span>
              )}
            </div>
            {/* Ciblage (FEED-07) */}
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <span>{formatRelativeShort(post.created_at)}</span>
              <span>•</span>
              <span className="flex items-center gap-1">
                {post.target_type === 'everyone' && '📢'}
                {post.target_type === 'specific_chantiers' && '🏗️'}
                {post.target_type === 'specific_people' && '👥'}
                {post.target_display}
              </span>
            </div>
          </div>
        </div>

        {/* Menu actions */}
        {canDelete && onDelete && (
          <button
            onClick={handleDeleteClick}
            className="text-gray-600 hover:text-red-500 p-1"
            title="Supprimer"
            aria-label="Supprimer le post"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        )}
      </div>

      {/* Contenu (FEED-01, FEED-10 emojis, FEED-14 mentions @) */}
      <div className="text-gray-800 mb-4 whitespace-pre-wrap">
        {renderContentWithMentions(post.content, allAuthors)}
      </div>

      {/* Médias (FEED-02) */}
      {post.medias_count > 0 && (
        <div className="mb-4 bg-gray-100 rounded-lg p-4 text-center text-gray-500">
          📷 {post.medias_count} photo{post.medias_count > 1 ? 's' : ''}
        </div>
      )}

      {/* Compteurs */}
      <div className="flex items-center gap-4 text-sm text-gray-500 mb-3 pb-3 border-b">
        {likesCount > 0 && (
          <span>{likesCount} j'aime{likesCount > 1 ? '' : ''}</span>
        )}
        {post.comments_count > 0 && (
          <span>{post.comments_count} commentaire{post.comments_count > 1 ? 's' : ''}</span>
        )}
      </div>

      {/* Actions (FEED-04, FEED-05) */}
      <div className="flex items-center gap-2">
        <button
          onClick={handleLikeClick}
          aria-label={liked ? "Retirer j'aime" : "J'aime"}
          aria-pressed={liked}
          className={`flex-1 flex items-center justify-center gap-2 py-2 rounded-lg transition-colors ${
            liked
              ? 'text-red-500 bg-red-50 hover:bg-red-100'
              : 'text-gray-600 hover:bg-gray-100'
          }`}
        >
          <svg className="w-5 h-5" fill={liked ? 'currentColor' : 'none'} stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
          </svg>
          <span>J'aime</span>
        </button>

        <button
          onClick={handleCommentClick}
          aria-label="Commenter le post"
          className="flex-1 flex items-center justify-center gap-2 py-2 rounded-lg text-gray-600 hover:bg-gray-100 transition-colors"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
          <span>Commenter</span>
        </button>
      </div>
    </article>
  )
})

export default PostCard
