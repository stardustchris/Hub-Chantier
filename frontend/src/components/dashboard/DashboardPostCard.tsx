/**
 * DashboardPostCard - Carte de publication pour le fil d'actualités (API réelle)
 * Extrait de DashboardPage pour réduction de taille
 * P1-6: Utilise useAuth() directement au lieu de props drilling
 */

import { useState, memo } from 'react'
import { Link } from 'react-router-dom'
import {
  Heart,
  MessageCircle,
  Pin,
  MoreHorizontal,
  Trash2,
  Send,
  Loader2,
} from 'lucide-react'
import MentionInput from '../common/MentionInput'
import { useAuth } from '../../contexts/AuthContext'
import { dashboardService } from '../../services/dashboard'
import { logger } from '../../services/logger'
import { formatRelative } from '../../utils/dates'
import { renderContentWithMentions } from '../../utils/mentionRenderer'
import type { Post, User, UserRole } from '../../types'
import { ROLES } from '../../types'

interface DashboardPostCardProps {
  post: Post
  allAuthors?: User[]
  onLike: (postId: string | number, isLiked: boolean) => void
  onPin: (postId: string | number, isPinned: boolean) => void
  onDelete: (postId: string | number) => void
}

// P1-7: Memoize le composant pour éviter re-renders inutiles
export const DashboardPostCard = memo(function DashboardPostCard({
  post,
  allAuthors = [],
  onLike,
  onPin,
  onDelete,
}: DashboardPostCardProps) {
  // P1-6: Consommer le context directement au lieu de recevoir en props
  const { user } = useAuth()
  const currentUserId = user?.id || ''
  const isAdmin = user?.role === 'admin'
  const [showComments, setShowComments] = useState(false)
  const [showMenu, setShowMenu] = useState(false)
  const [newComment, setNewComment] = useState('')
  const [isCommenting, setIsCommenting] = useState(false)
  const [comments, setComments] = useState(post.commentaires || [])

  const isLiked = post.likes?.some((l) => l.user_id === currentUserId)
  const canDelete = isAdmin || post.auteur?.id === currentUserId
  const canPin = isAdmin

  const roleInfo = post.auteur?.role ? ROLES[post.auteur.role as UserRole] : null

  const handleAddComment = async () => {
    if (!newComment.trim()) return
    try {
      setIsCommenting(true)

      // Appeler l'API
      const updatedPost = await dashboardService.addComment(String(post.id), { contenu: newComment })
      setComments(updatedPost.commentaires || [])
      setNewComment('')
    } catch (error) {
      logger.error('Erreur lors de l\'ajout du commentaire', error, { context: 'DashboardPostCard', showToast: true })
    } finally {
      setIsCommenting(false)
    }
  }

  return (
    <div className={`border-b border-gray-100 pb-4 ${post.is_pinned ? 'border-l-4 border-l-green-500 pl-4' : ''} ${post.is_urgent ? 'border-l-4 border-l-red-500 pl-4 bg-red-50 rounded-lg p-4' : ''}`}>
      <div className="flex gap-3">
        <div
          className="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold text-sm shrink-0"
          style={{ backgroundColor: post.auteur?.couleur || '#3498DB' }}
        >
          {post.auteur?.prenom?.[0]}
          {post.auteur?.nom?.[0]}
        </div>
        <div className="flex-1">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-2 flex-wrap">
                {post.auteur?.id ? (
                  <Link to={`/utilisateurs/${post.auteur.id}`} className="font-semibold text-gray-900 hover:underline">
                    {post.auteur.prenom} {post.auteur.nom}
                  </Link>
                ) : (
                  <span className="font-semibold text-gray-900">
                    {post.auteur?.prenom} {post.auteur?.nom}
                  </span>
                )}
                {roleInfo && (
                  <span
                    className="text-xs px-2 py-0.5 rounded-full"
                    style={{ backgroundColor: roleInfo.color + '20', color: roleInfo.color }}
                  >
                    {roleInfo.label}
                  </span>
                )}
                {post.target_type === 'tous' && (
                  <span className="text-sm text-gray-500">→ Tout le monde</span>
                )}
                {post.target_type === 'chantiers' && post.target_chantiers?.length && (
                  <span className="text-sm text-gray-500">
                    → {post.target_chantiers.map((c) => c.nom).join(', ')}
                  </span>
                )}
              </div>
              <p className="text-xs text-gray-400">
                {formatRelative(post.created_at)}
              </p>
            </div>

            {(canDelete || canPin) && (
              <div className="relative">
                <button
                  onClick={() => setShowMenu(!showMenu)}
                  className="p-1 rounded hover:bg-gray-100"
                >
                  <MoreHorizontal className="w-5 h-5 text-gray-400" />
                </button>
                {showMenu && (
                  <>
                    <div className="fixed inset-0 z-10" onClick={() => setShowMenu(false)} />
                    <div className="absolute right-0 mt-1 w-40 bg-white rounded-lg shadow-lg border z-20">
                      {canPin && (
                        <button
                          onClick={() => {
                            onPin(post.id, post.is_pinned)
                            setShowMenu(false)
                          }}
                          className="flex items-center gap-2 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                        >
                          <Pin className="w-4 h-4" />
                          {post.is_pinned ? 'Desepingler' : 'Epingler'}
                        </button>
                      )}
                      {canDelete && (
                        <button
                          onClick={() => {
                            onDelete(post.id)
                            setShowMenu(false)
                          }}
                          className="flex items-center gap-2 w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                        >
                          <Trash2 className="w-4 h-4" />
                          Supprimer
                        </button>
                      )}
                    </div>
                  </>
                )}
              </div>
            )}
          </div>

          <p className="text-gray-700 mt-2 mb-3 whitespace-pre-wrap">
            {renderContentWithMentions(post.contenu, allAuthors)}
          </p>

          {post.medias && post.medias.length > 0 && (
            <div className="grid grid-cols-2 gap-2 mb-3">
              {post.medias.map((media) => (
                <img
                  key={media.id}
                  src={media.url}
                  alt=""
                  className="rounded-xl w-full h-48 object-cover"
                />
              ))}
            </div>
          )}

          <div className="flex items-center gap-4 text-sm text-gray-500">
            <button
              onClick={() => onLike(post.id, isLiked ?? false)}
              className={`flex items-center gap-1 hover:text-red-500 ${isLiked ? 'text-red-500' : ''}`}
            >
              <Heart className={`w-4 h-4 ${isLiked ? 'fill-current' : ''}`} />
              {post.likes_count || 0}
            </button>
            <button
              onClick={() => setShowComments(!showComments)}
              className="flex items-center gap-1 hover:text-blue-500"
            >
              <MessageCircle className="w-4 h-4" />
              {post.commentaires_count || comments.length || 0}
            </button>
          </div>

          {showComments && (
            <div className="mt-4 pt-4 border-t">
              {comments.map((comment) => (
                <div key={comment.id} className="flex gap-3 mb-3">
                  <div
                    className="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-semibold shrink-0"
                    style={{ backgroundColor: comment.auteur?.couleur || '#3498DB' }}
                  >
                    {comment.auteur?.prenom?.[0]}
                    {comment.auteur?.nom?.[0]}
                  </div>
                  <div className="flex-1">
                    <div className="bg-gray-100 rounded-lg p-3">
                      {comment.auteur?.id ? (
                        <Link to={`/utilisateurs/${comment.auteur.id}`} className="font-medium text-sm text-gray-900 hover:underline">
                          {comment.auteur.prenom} {comment.auteur.nom}
                        </Link>
                      ) : (
                        <span className="font-medium text-sm">
                          {comment.auteur?.prenom} {comment.auteur?.nom}
                        </span>
                      )}
                      <p className="text-sm text-gray-700 whitespace-pre-wrap">
                        {renderContentWithMentions(comment.contenu, allAuthors)}
                      </p>
                    </div>
                    <span className="text-xs text-gray-500 ml-2">
                      {formatRelative(comment.created_at)}
                    </span>
                  </div>
                </div>
              ))}

              <div className="flex gap-3 mt-3">
                <div className="w-8 h-8 rounded-full bg-gray-300 shrink-0" />
                <div className="flex-1 flex gap-2">
                  <div className="flex-1">
                    <MentionInput
                      value={newComment}
                      onChange={setNewComment}
                      placeholder="Ajouter un commentaire... @ pour mentionner"
                      rows={1}
                      className="text-sm"
                    />
                  </div>
                  <button
                    onClick={handleAddComment}
                    disabled={!newComment.trim() || isCommenting}
                    className="bg-green-600 text-white px-3 rounded-lg hover:bg-green-700 disabled:opacity-50 self-start mt-1"
                  >
                    {isCommenting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
})
