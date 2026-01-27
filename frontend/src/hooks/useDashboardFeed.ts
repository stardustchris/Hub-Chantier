/**
 * Hook pour gérer le feed du dashboard (posts, likes, etc.)
 * Extrait de DashboardPage pour améliorer la maintenabilité
 */
import { useState, useEffect, useCallback, useMemo } from 'react'
import { dashboardService } from '../services/dashboard'
import { chantiersService } from '../services/chantiers'
import { logger } from '../services/logger'
import { useAuth } from '../contexts/AuthContext'
import type { Post, Chantier, TargetType } from '../types'

export interface UseDashboardFeedReturn {
  // Data
  posts: Post[]
  sortedPosts: Post[]
  chantiers: Chantier[]

  // State
  isLoading: boolean
  hasMore: boolean
  page: number

  // Post composer state
  newPostContent: string
  setNewPostContent: (content: string) => void
  targetType: TargetType
  setTargetType: (type: TargetType) => void
  selectedChantiers: string[]
  setSelectedChantiers: (chantiers: string[]) => void
  isUrgent: boolean
  setIsUrgent: (urgent: boolean) => void
  isPosting: boolean

  // Actions
  loadFeed: (pageNum?: number) => Promise<void>
  handleCreatePost: () => Promise<void>
  handleLike: (postId: string | number, isLiked: boolean) => Promise<void>
  handlePin: (postId: string | number, isPinned: boolean) => Promise<void>
  handleDelete: (postId: string | number) => Promise<void>
}

/**
 * Hook pour gérer le feed du dashboard
 */
export function useDashboardFeed(): UseDashboardFeedReturn {
  const { user } = useAuth()

  // Data state
  const [posts, setPosts] = useState<Post[]>([])
  const [chantiers, setChantiers] = useState<Chantier[]>([])

  // Loading state
  const [isLoading, setIsLoading] = useState(false)
  const [page, setPage] = useState(1)
  const [hasMore, setHasMore] = useState(false)

  // Post composer state
  const [newPostContent, setNewPostContent] = useState('')
  const [isPosting, setIsPosting] = useState(false)
  const [targetType, setTargetType] = useState<TargetType>('tous')
  const [selectedChantiers, setSelectedChantiers] = useState<string[]>([])
  const [isUrgent, setIsUrgent] = useState(false)

  // Load data on mount
  useEffect(() => {
    loadFeed()
    loadChantiers()
  }, [])

  /**
   * Charge le feed depuis l'API
   */
  const loadFeed = useCallback(async (pageNum = 1) => {
    try {
      setIsLoading(true)
      const response = await dashboardService.getFeed({ page: pageNum, size: 20 })
      const items = response?.items || []

      if (pageNum === 1) {
        setPosts(items)
      } else {
        setPosts(prev => [...prev, ...items])
      }

      setHasMore((response?.page || 1) < (response?.pages || 1))
      setPage(pageNum)
    } catch (error) {
      logger.error('Error loading feed', error, { context: 'DashboardFeed' })
    } finally {
      setIsLoading(false)
    }
  }, [])

  /**
   * Charge la liste des chantiers
   */
  const loadChantiers = async () => {
    try {
      const response = await chantiersService.list({ size: 100, statut: 'en_cours' })
      setChantiers(response?.items || [])
    } catch (error) {
      logger.error('Error loading chantiers', error, { context: 'DashboardFeed' })
    }
  }

  /**
   * Crée un nouveau post
   */
  const handleCreatePost = useCallback(async () => {
    if (!newPostContent.trim()) return

    try {
      setIsPosting(true)
      await dashboardService.createPost({
        contenu: newPostContent,
        target_type: targetType,
        target_chantier_ids: targetType === 'chantiers' ? selectedChantiers : undefined,
        is_urgent: isUrgent,
      })

      // Reset form
      setNewPostContent('')
      setTargetType('tous')
      setSelectedChantiers([])
      setIsUrgent(false)

      // Reload feed
      loadFeed(1)
    } catch (error) {
      logger.error('Erreur lors de la publication', error, { context: 'DashboardFeed', showToast: true })
    } finally {
      setIsPosting(false)
    }
  }, [newPostContent, targetType, selectedChantiers, isUrgent, loadFeed])

  /**
   * Like/Unlike un post
   */
  const handleLike = useCallback(async (postId: string | number, isLiked: boolean) => {
    try {
      if (isLiked) {
        await dashboardService.unlikePost(String(postId))
      } else {
        await dashboardService.likePost(String(postId))
      }
      const updatedPost = await dashboardService.getPost(String(postId))
      setPosts(prev => prev.map(p => (p.id === postId ? updatedPost : p)))
    } catch (error) {
      logger.error('Erreur lors du like', error, { context: 'DashboardFeed', showToast: true })
    }
  }, [user?.id])

  /**
   * Pin/Unpin un post
   */
  const handlePin = useCallback(async (postId: string | number, isPinned: boolean) => {
    try {
      if (isPinned) {
        await dashboardService.unpinPost(String(postId))
      } else {
        await dashboardService.pinPost(String(postId))
      }
      loadFeed(1)
    } catch (error) {
      logger.error('Erreur lors de l\'epinglage', error, { context: 'DashboardFeed', showToast: true })
    }
  }, [loadFeed])

  /**
   * Supprime un post
   */
  const handleDelete = useCallback(async (postId: string | number) => {
    if (!confirm('Supprimer cette publication ?')) return

    try {
      await dashboardService.deletePost(String(postId))
      setPosts(prev => prev.filter(p => p.id !== postId))
    } catch (error) {
      logger.error('Erreur lors de la suppression', error, { context: 'DashboardFeed', showToast: true })
    }
  }, [])

  /**
   * Posts triés (pinnés en premier, puis par date)
   */
  const sortedPosts = useMemo(() => [...posts].sort((a, b) => {
    if (a.is_pinned && !b.is_pinned) return -1
    if (!a.is_pinned && b.is_pinned) return 1
    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  }), [posts])

  return {
    posts,
    sortedPosts,
    chantiers,
    isLoading,
    hasMore,
    page,
    newPostContent,
    setNewPostContent,
    targetType,
    setTargetType,
    selectedChantiers,
    setSelectedChantiers,
    isUrgent,
    setIsUrgent,
    isPosting,
    loadFeed,
    handleCreatePost,
    handleLike,
    handlePin,
    handleDelete,
  }
}

export default useDashboardFeed
