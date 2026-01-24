/**
 * DashboardPage - Page d'accueil avec tableau de bord et fil d'actualites
 * CDC Section 2 - Tableau de Bord & Feed d'Actualites
 */

import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { dashboardService } from '../services/dashboard'
import { chantiersService } from '../services/chantiers'
import Layout from '../components/Layout'
import {
  ClockCard,
  WeatherCard,
  StatsCard,
  QuickActions,
  TodayPlanningCard,
  TeamCard,
  DocumentsCard,
} from '../components/dashboard'
import {
  Send,
  Heart,
  MessageCircle,
  Pin,
  MoreHorizontal,
  Trash2,
  AlertTriangle,
  Loader2,
  Camera,
} from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import { fr } from 'date-fns/locale'
import type { Post, Chantier, TargetType } from '../types'
import { ROLES } from '../types'
import type { UserRole } from '../types'

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

  const isDirectionOrConducteur = user?.role === 'admin' || user?.role === 'conducteur'

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

  const sortedPosts = [...posts].sort((a, b) => {
    if (a.is_pinned && !b.is_pinned) return -1
    if (!a.is_pinned && b.is_pinned) return 1
    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  })

  return (
    <Layout>
      <div className="min-h-screen bg-gray-100">
        <div className="p-4 space-y-4">
          {/* Top Cards - Extracted Components */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <ClockCard />
            <WeatherCard />
            <StatsCard />
          </div>

          {/* Quick Actions - Extracted Component */}
          <QuickActions />

          {/* Main Content Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {/* Left Column - Planning & Feed */}
            <div className="lg:col-span-2 space-y-4">
              {/* Today's Planning - Extracted Component */}
              <TodayPlanningCard />

              {/* Actualites Section */}
              <div className="bg-white rounded-2xl p-5 shadow-lg">
                <h2 className="font-semibold text-gray-800 flex items-center gap-2 mb-4">
                  <MessageCircle className="w-5 h-5 text-blue-600" />
                  Actualites
                  {isLoading && <Loader2 className="w-4 h-4 animate-spin" />}
                </h2>

                {/* Post Composer */}
                <div className="mb-6">
                  <div className="flex gap-3">
                    <div
                      className="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold text-sm shrink-0"
                      style={{ backgroundColor: user?.couleur || '#f97316' }}
                    >
                      {user?.prenom?.[0]}{user?.nom?.[0]}
                    </div>
                    <div className="flex-1">
                      <input
                        type="text"
                        value={newPostContent}
                        onChange={(e) => setNewPostContent(e.target.value)}
                        placeholder="Partager une photo, signaler un probleme..."
                        className="w-full border border-gray-200 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                      />
                    </div>
                  </div>

                  {isDirectionOrConducteur && newPostContent && (
                    <div className="flex flex-wrap items-center gap-3 mt-3 ml-13">
                      <select
                        value={targetType}
                        onChange={(e) => setTargetType(e.target.value as TargetType)}
                        className="text-sm border rounded-lg px-2 py-1"
                      >
                        <option value="tous">Tout le monde</option>
                        <option value="chantiers">Chantiers specifiques</option>
                      </select>
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
                  )}

                  <div className="flex gap-3 mt-3">
                    <button className="flex-1 bg-orange-500 text-white py-2.5 px-4 rounded-xl flex items-center justify-center gap-2 hover:bg-orange-600 font-medium">
                      <Camera className="w-5 h-5" />
                      Prendre une photo
                    </button>
                    <button
                      onClick={handleCreatePost}
                      disabled={!newPostContent.trim() || isPosting}
                      className="bg-gray-200 text-gray-700 py-2.5 px-6 rounded-xl hover:bg-gray-300 font-medium disabled:opacity-50"
                    >
                      {isPosting ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Publier'}
                    </button>
                  </div>
                </div>

                {/* Posts */}
                <div className="space-y-4">
                  {sortedPosts.length === 0 && !isLoading ? (
                    <div className="text-center py-12">
                      <MessageCircle className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                      <p className="text-gray-500">Aucune publication pour le moment</p>
                    </div>
                  ) : (
                    sortedPosts.map((post) => (
                      <PostCard
                        key={post.id}
                        post={post}
                        currentUserId={user?.id || ''}
                        isAdmin={user?.role === 'admin'}
                        onLike={handleLike}
                        onPin={handlePin}
                        onDelete={handleDelete}
                      />
                    ))
                  )}

                  {hasMore && !isLoading && (
                    <button
                      onClick={() => loadFeed(page + 1)}
                      className="w-full py-3 text-green-600 hover:text-green-700 font-medium"
                    >
                      Charger plus
                    </button>
                  )}
                </div>
              </div>
            </div>

            {/* Right Column - Documents & Team - Extracted Components */}
            <div className="space-y-4">
              <DocumentsCard />
              <TeamCard />
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}

// PostCard component - inline pour garder la cohesion avec le state parent
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
                <span className="font-semibold text-gray-900">
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
                {formatDistanceToNow(new Date(post.created_at), { addSuffix: true, locale: fr })}
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

          <p className="text-gray-700 mt-2 mb-3">{post.contenu}</p>

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
              onClick={() => onLike(post.id, isLiked)}
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

              <div className="flex gap-3 mt-3">
                <div className="w-8 h-8 rounded-full bg-gray-300 shrink-0" />
                <div className="flex-1 flex gap-2">
                  <input
                    type="text"
                    value={newComment}
                    onChange={(e) => setNewComment(e.target.value)}
                    placeholder="Ajouter un commentaire..."
                    className="flex-1 px-3 py-2 text-sm border rounded-lg focus:ring-2 focus:ring-green-500"
                    onKeyDown={(e) => e.key === 'Enter' && handleAddComment()}
                  />
                  <button
                    onClick={handleAddComment}
                    disabled={!newComment.trim() || isCommenting}
                    className="bg-green-600 text-white px-3 rounded-lg hover:bg-green-700 disabled:opacity-50"
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
}
