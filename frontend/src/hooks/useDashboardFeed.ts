/**
 * Hook pour gérer le feed du dashboard (posts, likes, etc.)
 * Extrait de DashboardPage pour améliorer la maintenabilité
 * Phase 2: Migration vers TanStack Query pour optimisation cache/performance
 */
import { useState, useCallback, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { dashboardService } from '../services/dashboard'
import { chantiersService } from '../services/chantiers'
import { logger } from '../services/logger'
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
  const queryClient = useQueryClient()

  // Local state (non-query related)
  const [page, setPage] = useState(1)

  // Post composer state
  const [newPostContent, setNewPostContent] = useState('')
  const [targetType, setTargetType] = useState<TargetType>('tous')
  const [selectedChantiers, setSelectedChantiers] = useState<string[]>([])
  const [isUrgent, setIsUrgent] = useState(false)

  // TanStack Query: Feed data (staleTime: 1 minute car le feed change souvent)
  const {
    data: feedData,
    isLoading: isFeedLoading,
    refetch: refetchFeed,
  } = useQuery({
    queryKey: ['dashboard-feed', page],
    queryFn: async () => {
      const response = await dashboardService.getFeed({ page, size: 20 })
      return response
    },
    staleTime: 1 * 60 * 1000, // 1 minute (feed dynamique)
  })

  // TanStack Query: Chantiers list
  const { data: chantiersData } = useQuery({
    queryKey: ['chantiers-list'],
    queryFn: async () => {
      const response = await chantiersService.list({ size: 100, statut: 'en_cours' })
      return response?.items || []
    },
    staleTime: 5 * 60 * 1000, // 5 minutes (moins dynamique)
  })

  // Extract data from query results
  const posts = feedData?.items || []
  const chantiers = chantiersData || []
  const hasMore = (feedData?.page || 1) < (feedData?.pages || 1)
  const isLoading = isFeedLoading

  /**
   * Charge le feed depuis l'API (garde l'interface publique pour compatibilité)
   */
  const loadFeed = useCallback(async (pageNum = 1) => {
    setPage(pageNum)
    await refetchFeed()
  }, [refetchFeed])

  // TanStack Query Mutation: Create post
  const createPostMutation = useMutation({
    mutationFn: async (data: { contenu: string; target_type: TargetType; target_chantier_ids?: string[]; is_urgent: boolean }) => {
      return dashboardService.createPost(data)
    },
    onSuccess: () => {
      // Invalidate feed query to refetch
      queryClient.invalidateQueries({ queryKey: ['dashboard-feed'] })
      // Reset form
      setNewPostContent('')
      setTargetType('tous')
      setSelectedChantiers([])
      setIsUrgent(false)
    },
    onError: (error) => {
      logger.error('Erreur lors de la publication', error, { context: 'DashboardFeed', showToast: true })
    },
  })

  /**
   * Crée un nouveau post
   */
  const handleCreatePost = useCallback(async () => {
    if (!newPostContent.trim()) return

    createPostMutation.mutate({
      contenu: newPostContent,
      target_type: targetType,
      target_chantier_ids: targetType === 'chantiers' ? selectedChantiers : undefined,
      is_urgent: isUrgent,
    })
  }, [newPostContent, targetType, selectedChantiers, isUrgent, createPostMutation])

  // TanStack Query Mutation: Like/Unlike post
  const likeMutation = useMutation({
    mutationFn: async ({ postId, isLiked }: { postId: string; isLiked: boolean }) => {
      if (isLiked) {
        await dashboardService.unlikePost(postId)
      } else {
        await dashboardService.likePost(postId)
      }
      return dashboardService.getPost(postId)
    },
    onSuccess: () => {
      // Invalidate to refetch with updated data
      queryClient.invalidateQueries({ queryKey: ['dashboard-feed'] })
    },
    onError: (error) => {
      logger.error('Erreur lors du like', error, { context: 'DashboardFeed', showToast: true })
    },
  })

  /**
   * Like/Unlike un post
   */
  const handleLike = useCallback(async (postId: string | number, isLiked: boolean) => {
    likeMutation.mutate({ postId: String(postId), isLiked })
  }, [likeMutation])

  // TanStack Query Mutation: Pin/Unpin post
  const pinMutation = useMutation({
    mutationFn: async ({ postId, isPinned }: { postId: string; isPinned: boolean }) => {
      if (isPinned) {
        return dashboardService.unpinPost(postId)
      } else {
        return dashboardService.pinPost(postId)
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dashboard-feed'] })
    },
    onError: (error) => {
      logger.error('Erreur lors de l\'epinglage', error, { context: 'DashboardFeed', showToast: true })
    },
  })

  /**
   * Pin/Unpin un post
   */
  const handlePin = useCallback(async (postId: string | number, isPinned: boolean) => {
    pinMutation.mutate({ postId: String(postId), isPinned })
  }, [pinMutation])

  // TanStack Query Mutation: Delete post
  const deleteMutation = useMutation({
    mutationFn: async (postId: string) => {
      return dashboardService.deletePost(postId)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dashboard-feed'] })
    },
    onError: (error) => {
      logger.error('Erreur lors de la suppression', error, { context: 'DashboardFeed', showToast: true })
    },
  })

  /**
   * Supprime un post
   */
  const handleDelete = useCallback(async (postId: string | number) => {
    if (!confirm('Supprimer cette publication ?')) return
    deleteMutation.mutate(String(postId))
  }, [deleteMutation])

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
    isPosting: createPostMutation.isPending,
    loadFeed,
    handleCreatePost,
    handleLike,
    handlePin,
    handleDelete,
  }
}

export default useDashboardFeed
