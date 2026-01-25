/**
 * Composant Feed - Liste des posts avec scroll infini
 * Selon CDC Section 2 - FEED-18 (scroll infini), FEED-09 (filtrage)
 */

import { useState, useEffect, useCallback } from 'react'
import PostCard from './PostCard'
import PostComposer from './PostComposer'
import CommentModal from './CommentModal'
import type { Post, Author, CreatePostData } from '../../types/dashboard'

interface FeedProps {
  currentUserId: number
  currentUserRole: string
  isCompagnon?: boolean
  // Données mockées pour démo (remplacées par API en prod)
  mockPosts?: Post[]
  mockAuthors?: Record<number, Author>
}

// Données mock pour la démo visuelle
const MOCK_AUTHORS: Record<number, Author> = {
  1: { id: 1, prenom: 'Jean', nom: 'Martin', role: 'admin', couleur: '#9B59B6', metier: 'Direction' },
  2: { id: 2, prenom: 'Pierre', nom: 'Dupont', role: 'conducteur', couleur: '#3498DB', metier: 'Conducteur de travaux' },
  3: { id: 3, prenom: 'Marc', nom: 'Bernard', role: 'chef_chantier', couleur: '#27AE60', metier: 'Chef de chantier' },
  4: { id: 4, prenom: 'Luc', nom: 'Moreau', role: 'compagnon', couleur: '#E67E22', metier: 'Maçon' },
}

const MOCK_POSTS: Post[] = [
  {
    id: 1,
    author_id: 1,
    content: "📢 Rappel important : réunion de chantier demain à 8h30 sur le site Villa Lyon. Présence obligatoire pour tous les chefs de chantier.\n\nOrdre du jour :\n- Point d'avancement\n- Planning semaine 5\n- Questions logistique",
    status: 'pinned',
    is_urgent: true,
    is_pinned: true,
    target_type: 'everyone',
    target_display: 'Tout le monde',
    created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
    likes_count: 12,
    comments_count: 3,
    medias_count: 0,
  },
  {
    id: 2,
    author_id: 3,
    content: "Coulage du plancher R+2 terminé avec succès ! 💪 Beau travail de l'équipe. On enchaîne demain avec le ferraillage des voiles.",
    status: 'published',
    is_urgent: false,
    is_pinned: false,
    target_type: 'specific_chantiers',
    target_display: 'Villa Lyon 3ème',
    created_at: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(),
    likes_count: 8,
    comments_count: 5,
    medias_count: 3,
  },
  {
    id: 3,
    author_id: 2,
    content: "Livraison de ferraille prévue demain matin entre 7h et 8h. Merci de prévoir la zone de déchargement. @Marc tu peux coordonner avec le grutier ?",
    status: 'published',
    is_urgent: false,
    is_pinned: false,
    target_type: 'specific_chantiers',
    target_display: 'Résidence Les Pins',
    created_at: new Date(Date.now() - 8 * 60 * 60 * 1000).toISOString(),
    likes_count: 3,
    comments_count: 2,
    medias_count: 0,
  },
  {
    id: 4,
    author_id: 4,
    content: "⚠️ Attention : problème détecté sur l'échafaudage zone B. J'ai sécurisé la zone en attendant vérification. Photos jointes.",
    status: 'published',
    is_urgent: false,
    is_pinned: false,
    target_type: 'specific_chantiers',
    target_display: 'Villa Lyon 3ème',
    created_at: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
    likes_count: 15,
    comments_count: 8,
    medias_count: 2,
  },
  {
    id: 5,
    author_id: 1,
    content: "🎉 Félicitations à toute l'équipe ! Le chantier Résidence Bellevue a été réceptionné avec 0 réserve. C'est le résultat d'un excellent travail collectif. Bravo !",
    status: 'published',
    is_urgent: false,
    is_pinned: false,
    target_type: 'everyone',
    target_display: 'Tout le monde',
    created_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
    likes_count: 28,
    comments_count: 12,
    medias_count: 1,
  },
]

export default function Feed({
  currentUserId,
  isCompagnon = false,
  mockPosts = MOCK_POSTS,
  mockAuthors = MOCK_AUTHORS,
}: FeedProps) {
  const [posts, setPosts] = useState<Post[]>(mockPosts)
  const [loading, setLoading] = useState(false)
  const [hasMore, setHasMore] = useState(true)
  const [likedPosts, setLikedPosts] = useState<Set<number>>(new Set([1, 5]))
  const [commentModalPostId, setCommentModalPostId] = useState<number | null>(null)

  // Trier les posts : épinglés en premier, puis par date
  const sortedPosts = [...posts].sort((a, b) => {
    if (a.is_pinned && !b.is_pinned) return -1
    if (!a.is_pinned && b.is_pinned) return 1
    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  })

  // Créer un post
  const handleCreatePost = async (data: CreatePostData) => {
    const newPost: Post = {
      id: Date.now(),
      author_id: currentUserId,
      content: data.content,
      status: data.is_urgent ? 'pinned' : 'published',
      is_urgent: data.is_urgent || false,
      is_pinned: data.is_urgent || false,
      target_type: data.target_type,
      target_display: data.target_type === 'everyone' ? 'Tout le monde' : 'Ciblé',
      created_at: new Date().toISOString(),
      likes_count: 0,
      comments_count: 0,
      medias_count: 0,
    }
    setPosts([newPost, ...posts])
  }

  // Like/Unlike
  const handleLike = (postId: number) => {
    setLikedPosts((prev) => new Set([...prev, postId]))
  }

  const handleUnlike = (postId: number) => {
    setLikedPosts((prev) => {
      const next = new Set(prev)
      next.delete(postId)
      return next
    })
  }

  // Commenter (ouvre modal)
  const handleComment = (postId: number) => {
    setCommentModalPostId(postId)
  }

  // Supprimer
  const handleDelete = (postId: number) => {
    if (window.confirm('Êtes-vous sûr de vouloir supprimer ce post ?')) {
      setPosts(posts.filter((p) => p.id !== postId))
    }
  }

  // Charger plus (scroll infini - FEED-18)
  const loadMore = useCallback(() => {
    if (loading || !hasMore) return
    setLoading(true)
    // Simuler chargement
    setTimeout(() => {
      setLoading(false)
      setHasMore(false) // Plus de posts dans la démo
    }, 1000)
  }, [loading, hasMore])

  // Détection scroll pour chargement infini
  useEffect(() => {
    const handleScroll = () => {
      if (
        window.innerHeight + document.documentElement.scrollTop >=
        document.documentElement.offsetHeight - 500
      ) {
        loadMore()
      }
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [loadMore])

  return (
    <div className="max-w-2xl mx-auto">
      {/* Zone de publication */}
      <PostComposer
        onSubmit={handleCreatePost}
        isCompagnon={isCompagnon}
      />

      {/* Liste des posts */}
      <div className="space-y-4">
        {sortedPosts.map((post) => (
          <PostCard
            key={post.id}
            post={post}
            author={mockAuthors[post.author_id]}
            currentUserId={currentUserId}
            onLike={handleLike}
            onUnlike={handleUnlike}
            onComment={handleComment}
            onDelete={handleDelete}
            isLiked={likedPosts.has(post.id)}
          />
        ))}
      </div>

      {/* Indicateur de chargement */}
      {loading && (
        <div className="text-center py-8">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-primary-500 border-t-transparent"></div>
          <p className="text-gray-500 mt-2">Chargement...</p>
        </div>
      )}

      {/* Fin du feed */}
      {!hasMore && !loading && (
        <div className="text-center py-8 text-gray-500">
          Vous avez atteint la fin du fil d'actualités
        </div>
      )}

      {/* Modal de commentaire avec mentions @ */}
      {commentModalPostId !== null && (
        <CommentModal
          isOpen={true}
          onClose={() => setCommentModalPostId(null)}
          postId={commentModalPostId}
          postAuthor={
            mockAuthors[
              sortedPosts.find((p) => p.id === commentModalPostId)?.author_id ?? 0
            ]?.prenom ?? 'Auteur'
          }
          onCommentAdded={() => {
            // Rafraichir le compteur de commentaires
            setPosts((prev) =>
              prev.map((p) =>
                p.id === commentModalPostId
                  ? { ...p, comments_count: p.comments_count + 1 }
                  : p
              )
            )
          }}
        />
      )}
    </div>
  )
}
