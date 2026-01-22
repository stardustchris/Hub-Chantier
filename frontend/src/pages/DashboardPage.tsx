import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { dashboardService } from '../services/dashboard'
import { chantiersService } from '../services/chantiers'
import Layout from '../components/Layout'
import {
  Send,
  Image,
  Heart,
  MessageCircle,
  Pin,
  MoreHorizontal,
  Trash2,
  Building2,
  Users,
  AlertTriangle,
  Clock,
  MapPin,
  Calendar,
  Loader2,
} from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import { fr } from 'date-fns/locale'
import type { Post, Chantier, TargetType } from '../types'
import { ROLES, METIERS } from '../types'
import type { UserRole, Metier } from '../types'

export default function DashboardPage() {
  const { user } = useAuth()
  const [posts, setPosts] = useState<Post[]>([])
  const [chantiers, setChantiers] = useState<Chantier[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [newPostContent, setNewPostContent] = useState('')
  const [isPosting, setIsPosting] = useState(false)
  const [targetType, setTargetType] = useState<TargetType>('tous')
  const [selectedChantiers, setSelectedChantiers] = useState<string[]>([])
  const [isUrgent, setIsUrgent] = useState(false)
  const [page, setPage] = useState(1)
  const [hasMore, setHasMore] = useState(true)

  const isDirectionOrConducteur = user?.role === 'administrateur' || user?.role === 'conducteur'

  useEffect(() => {
    loadFeed()
    loadChantiers()
  }, [])

  const loadFeed = async (pageNum = 1) => {
    try {
      setIsLoading(true)
      const response = await dashboardService.getFeed({ page: pageNum, size: 20 })
      if (pageNum === 1) {
        setPosts(response.items)
      } else {
        setPosts((prev) => [...prev, ...response.items])
      }
      setHasMore(response.page < response.pages)
      setPage(pageNum)
    } catch (error) {
      console.error('Error loading feed:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const loadChantiers = async () => {
    try {
      const response = await chantiersService.list({ size: 100, statut: 'en_cours' })
      setChantiers(response.items)
    } catch (error) {
      console.error('Error loading chantiers:', error)
    }
  }

  const handleCreatePost = async () => {
    if (!newPostContent.trim()) return

    try {
      setIsPosting(true)
      await dashboardService.createPost({
        contenu: newPostContent,
        target_type: targetType,
        target_chantier_ids: targetType === 'chantiers' ? selectedChantiers : undefined,
        is_urgent: isUrgent,
      })
      setNewPostContent('')
      setTargetType('tous')
      setSelectedChantiers([])
      setIsUrgent(false)
      loadFeed(1)
    } catch (error) {
      console.error('Error creating post:', error)
    } finally {
      setIsPosting(false)
    }
  }

  const handleLike = async (postId: string, isLiked: boolean) => {
    try {
      if (isLiked) {
        await dashboardService.unlikePost(postId)
      } else {
        await dashboardService.likePost(postId)
      }
      // Refresh post
      const updatedPost = await dashboardService.getPost(postId)
      setPosts((prev) => prev.map((p) => (p.id === postId ? updatedPost : p)))
    } catch (error) {
      console.error('Error toggling like:', error)
    }
  }

  const handlePin = async (postId: string, isPinned: boolean) => {
    try {
      if (isPinned) {
        await dashboardService.unpinPost(postId)
      } else {
        await dashboardService.pinPost(postId)
      }
      loadFeed(1)
    } catch (error) {
      console.error('Error toggling pin:', error)
    }
  }

  const handleDelete = async (postId: string) => {
    if (!confirm('Supprimer cette publication ?')) return

    try {
      await dashboardService.deletePost(postId)
      setPosts((prev) => prev.filter((p) => p.id !== postId))
    } catch (error) {
      console.error('Error deleting post:', error)
    }
  }

  // Sort posts: pinned first, then by date
  const sortedPosts = [...posts].sort((a, b) => {
    if (a.is_pinned && !b.is_pinned) return -1
    if (!a.is_pinned && b.is_pinned) return 1
    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  })

  return (
    <Layout>
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Tableau de bord</h1>
          <p className="text-gray-600">
            Bienvenue, {user?.prenom} ! Voici les dernieres actualites.
          </p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="card">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-primary-100 rounded-lg">
                <Building2 className="w-5 h-5 text-primary-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">{chantiers.length}</p>
                <p className="text-xs text-gray-500">Chantiers actifs</p>
              </div>
            </div>
          </div>
          <div className="card">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 rounded-lg">
                <Clock className="w-5 h-5 text-green-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">32h</p>
                <p className="text-xs text-gray-500">Cette semaine</p>
              </div>
            </div>
          </div>
          <div className="card">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-secondary-100 rounded-lg">
                <Calendar className="w-5 h-5 text-secondary-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">5</p>
                <p className="text-xs text-gray-500">Taches</p>
              </div>
            </div>
          </div>
          <div className="card">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <MessageCircle className="w-5 h-5 text-purple-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">{posts.length}</p>
                <p className="text-xs text-gray-500">Publications</p>
              </div>
            </div>
          </div>
        </div>

        {/* Create Post (Direction/Conducteur only) */}
        {isDirectionOrConducteur && (
          <div className="card mb-6">
            <div className="flex gap-4">
              <div
                className="w-10 h-10 rounded-full flex items-center justify-center text-white font-semibold shrink-0"
                style={{ backgroundColor: user?.couleur || '#3498DB' }}
              >
                {user?.prenom?.[0]}
                {user?.nom?.[0]}
              </div>
              <div className="flex-1">
                <textarea
                  value={newPostContent}
                  onChange={(e) => setNewPostContent(e.target.value)}
                  placeholder="Partagez une actualite avec votre equipe..."
                  className="w-full p-3 border rounded-lg resize-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  rows={3}
                />

                {/* Targeting options */}
                <div className="flex flex-wrap items-center gap-3 mt-3">
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-gray-500">Destinataires:</span>
                    <select
                      value={targetType}
                      onChange={(e) => setTargetType(e.target.value as TargetType)}
                      className="text-sm border rounded-lg px-2 py-1"
                    >
                      <option value="tous">Tout le monde</option>
                      <option value="chantiers">Chantiers specifiques</option>
                    </select>
                  </div>

                  {targetType === 'chantiers' && (
                    <select
                      multiple
                      value={selectedChantiers}
                      onChange={(e) =>
                        setSelectedChantiers(
                          Array.from(e.target.selectedOptions, (opt) => opt.value)
                        )
                      }
                      className="text-sm border rounded-lg px-2 py-1 max-w-xs"
                    >
                      {chantiers.map((c) => (
                        <option key={c.id} value={c.id}>
                          {c.code} - {c.nom}
                        </option>
                      ))}
                    </select>
                  )}

                  <label className="flex items-center gap-2 text-sm">
                    <input
                      type="checkbox"
                      checked={isUrgent}
                      onChange={(e) => setIsUrgent(e.target.checked)}
                      className="rounded text-red-500"
                    />
                    <AlertTriangle className="w-4 h-4 text-red-500" />
                    Urgent
                  </label>
                </div>

                {/* Actions */}
                <div className="flex items-center justify-between mt-4">
                  <div className="flex gap-2">
                    <button className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700">
                      <Image className="w-4 h-4" />
                      Photo
                    </button>
                  </div>
                  <button
                    onClick={handleCreatePost}
                    disabled={!newPostContent.trim() || isPosting}
                    className="btn btn-primary flex items-center gap-2"
                  >
                    {isPosting ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Send className="w-4 h-4" />
                    )}
                    Publier
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Feed */}
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
            Fil d'actualites
            {isLoading && <Loader2 className="w-4 h-4 animate-spin" />}
          </h2>

          {sortedPosts.length === 0 && !isLoading ? (
            <div className="card text-center py-12">
              <MessageCircle className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">Aucune publication pour le moment</p>
            </div>
          ) : (
            sortedPosts.map((post) => (
              <PostCard
                key={post.id}
                post={post}
                currentUserId={user?.id || ''}
                isAdmin={user?.role === 'administrateur'}
                onLike={handleLike}
                onPin={handlePin}
                onDelete={handleDelete}
              />
            ))
          )}

          {/* Load more */}
          {hasMore && !isLoading && (
            <button
              onClick={() => loadFeed(page + 1)}
              className="w-full py-3 text-primary-600 hover:text-primary-700 font-medium"
            >
              Charger plus
            </button>
          )}
        </div>
      </div>
    </Layout>
  )
}

interface PostCardProps {
  post: Post
  currentUserId: string
  isAdmin: boolean
  onLike: (postId: string, isLiked: boolean) => void
  onPin: (postId: string, isPinned: boolean) => void
  onDelete: (postId: string) => void
}

function PostCard({ post, currentUserId, isAdmin, onLike, onPin, onDelete }: PostCardProps) {
  const [showComments, setShowComments] = useState(false)
  const [showMenu, setShowMenu] = useState(false)
  const [newComment, setNewComment] = useState('')
  const [isCommenting, setIsCommenting] = useState(false)
  const [comments, setComments] = useState(post.commentaires || [])

  const isLiked = post.likes?.some((l) => l.user_id === currentUserId)
  const canDelete = isAdmin || post.auteur?.id === currentUserId
  const canPin = isAdmin

  const roleInfo = post.auteur?.role ? ROLES[post.auteur.role as UserRole] : null
  const metierInfo = post.auteur?.metier ? METIERS[post.auteur.metier as Metier] : null

  const handleAddComment = async () => {
    if (!newComment.trim()) return
    try {
      setIsCommenting(true)
      const updatedPost = await dashboardService.addComment(post.id, { contenu: newComment })
      setComments(updatedPost.commentaires || [])
      setNewComment('')
    } catch (error) {
      console.error('Error adding comment:', error)
    } finally {
      setIsCommenting(false)
    }
  }

  return (
    <div className={`card ${post.is_pinned ? 'border-l-4 border-l-primary-500' : ''} ${post.is_urgent ? 'border-l-4 border-l-red-500 bg-red-50' : ''}`}>
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div
            className="w-10 h-10 rounded-full flex items-center justify-center text-white font-semibold"
            style={{ backgroundColor: post.auteur?.couleur || '#3498DB' }}
          >
            {post.auteur?.prenom?.[0]}
            {post.auteur?.nom?.[0]}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-medium text-gray-900">
                {post.auteur?.prenom} {post.auteur?.nom}
              </span>
              {roleInfo && (
                <span
                  className="text-xs px-2 py-0.5 rounded-full"
                  style={{ backgroundColor: roleInfo.color + '20', color: roleInfo.color }}
                >
                  {roleInfo.label}
                </span>
              )}
              {metierInfo && (
                <span
                  className="text-xs px-2 py-0.5 rounded-full"
                  style={{ backgroundColor: metierInfo.color + '20', color: metierInfo.color }}
                >
                  {metierInfo.label}
                </span>
              )}
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <span>
                {formatDistanceToNow(new Date(post.created_at), { addSuffix: true, locale: fr })}
              </span>
              {post.target_type === 'chantiers' && post.target_chantiers?.length && (
                <span className="flex items-center gap-1">
                  <MapPin className="w-3 h-3" />
                  {post.target_chantiers.map((c) => c.nom).join(', ')}
                </span>
              )}
              {post.target_type === 'tous' && (
                <span className="flex items-center gap-1">
                  <Users className="w-3 h-3" />
                  Tout le monde
                </span>
              )}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {post.is_pinned && (
            <span className="text-xs bg-primary-100 text-primary-700 px-2 py-1 rounded-full flex items-center gap-1">
              <Pin className="w-3 h-3" />
              Epingle
            </span>
          )}
          {post.is_urgent && (
            <span className="text-xs bg-red-100 text-red-700 px-2 py-1 rounded-full flex items-center gap-1">
              <AlertTriangle className="w-3 h-3" />
              Urgent
            </span>
          )}

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
      </div>

      {/* Content */}
      <p className="text-gray-800 whitespace-pre-wrap mb-4">{post.contenu}</p>

      {/* Media */}
      {post.medias && post.medias.length > 0 && (
        <div className="grid grid-cols-2 gap-2 mb-4">
          {post.medias.map((media) => (
            <img
              key={media.id}
              src={media.url}
              alt=""
              className="rounded-lg w-full h-48 object-cover"
            />
          ))}
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center gap-4 pt-4 border-t">
        <button
          onClick={() => onLike(post.id, isLiked)}
          className={`flex items-center gap-1 text-sm ${
            isLiked ? 'text-red-500' : 'text-gray-500 hover:text-red-500'
          }`}
        >
          <Heart className={`w-5 h-5 ${isLiked ? 'fill-current' : ''}`} />
          <span>{post.likes_count || 0}</span>
        </button>
        <button
          onClick={() => setShowComments(!showComments)}
          className="flex items-center gap-1 text-sm text-gray-500 hover:text-primary-500"
        >
          <MessageCircle className="w-5 h-5" />
          <span>{post.commentaires_count || comments.length || 0}</span>
        </button>
      </div>

      {/* Comments */}
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
                  <span className="font-medium text-sm">
                    {comment.auteur?.prenom} {comment.auteur?.nom}
                  </span>
                  <p className="text-sm text-gray-700">{comment.contenu}</p>
                </div>
                <span className="text-xs text-gray-500 ml-2">
                  {formatDistanceToNow(new Date(comment.created_at), { addSuffix: true, locale: fr })}
                </span>
              </div>
            </div>
          ))}

          {/* Add comment */}
          <div className="flex gap-3 mt-3">
            <div className="w-8 h-8 rounded-full bg-gray-300 shrink-0" />
            <div className="flex-1 flex gap-2">
              <input
                type="text"
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
                placeholder="Ajouter un commentaire..."
                className="flex-1 px-3 py-2 text-sm border rounded-lg focus:ring-2 focus:ring-primary-500"
                onKeyDown={(e) => e.key === 'Enter' && handleAddComment()}
              />
              <button
                onClick={handleAddComment}
                disabled={!newComment.trim() || isCommenting}
                className="btn btn-primary text-sm px-3"
              >
                {isCommenting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
