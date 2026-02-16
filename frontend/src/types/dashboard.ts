/**
 * Types pour le module Dashboard (Feed d'actualités)
 * Selon CDC Section 2 - FEED-01 à FEED-20
 */

export type TargetType = 'everyone' | 'specific_chantiers' | 'specific_people'
export type PostStatus = 'published' | 'pinned' | 'archived' | 'deleted'

export interface Post {
  id: number
  author_id: number
  content: string
  status: PostStatus
  is_urgent: boolean
  is_pinned: boolean
  target_type: TargetType
  target_display: string
  chantier_ids?: number[]
  user_ids?: number[]
  created_at: string
  likes_count: number
  comments_count: number
  medias_count: number
}

export interface PostDetail extends Post {
  medias: PostMedia[]
  comments: Comment[]
  liked_by_user_ids: number[]
}

export interface PostMedia {
  id: number
  post_id: number
  media_type: 'image'
  file_url: string
  thumbnail_url?: string
  original_filename?: string
  position: number
  webp_thumbnail_url?: string
  webp_medium_url?: string
  webp_large_url?: string
}

export interface Comment {
  id: number
  post_id: number
  author_id: number
  content: string
  created_at: string
}

export interface Like {
  id: number
  post_id: number
  user_id: number
  created_at: string
}

export interface CreatePostData {
  content: string
  target_type: TargetType
  chantier_ids?: number[]
  user_ids?: number[]
  is_urgent?: boolean
}

export interface CreateCommentData {
  content: string
}

export interface FeedResponse {
  posts: Post[]
  total: number
  page: number
  page_size: number
  has_next: boolean
  has_previous: boolean
}

// Auteur enrichi pour l'affichage
export interface Author {
  id: number
  prenom: string
  nom: string
  role: string
  metier?: string
  couleur?: string
  photo_url?: string
}
