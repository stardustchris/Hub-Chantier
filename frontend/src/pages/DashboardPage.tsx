/**
 * DashboardPage - Page d'accueil avec tableau de bord et fil d'actualites
 * CDC Section 2 - Tableau de Bord & Feed d'Actualites
 */

import { useState, useEffect, useCallback, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { dashboardService } from '../services/dashboard'
import { chantiersService } from '../services/chantiers'
import { logger } from '../services/logger'
import Layout from '../components/Layout'
import {
  ClockCard,
  WeatherCard,
  StatsCard,
  QuickActions,
  TodayPlanningCard,
  TeamCard,
  DocumentsCard,
  DashboardPostCard,
} from '../components/dashboard'
import {
  MessageCircle,
  AlertTriangle,
  Loader2,
  Camera,
} from 'lucide-react'
import type { Post, Chantier, TargetType } from '../types'

// Mock posts pour démonstration
const MOCK_POSTS: Post[] = [
  {
    id: 'mock-1',
    contenu: 'Dalle coulée avec succès sur le chantier Villa Moderne ! Beau travail de toute l\'équipe malgré la météo difficile ce matin.',
    type: 'message',
    auteur: { id: '1', prenom: 'Pierre', nom: 'Martin', couleur: '#3498DB', role: 'chef_chantier' } as Post['auteur'],
    target_type: 'tous',
    is_pinned: true,
    is_urgent: false,
    likes_count: 12,
    commentaires_count: 3,
    likes: [],
    medias: [],
    commentaires: [
      { id: 'c1', contenu: 'Bravo à tous !', auteur: { id: '2', prenom: 'Marie', nom: 'Dupont', couleur: '#E74C3C' } as Post['auteur'], created_at: new Date(Date.now() - 3600000).toISOString() },
    ],
    created_at: new Date(Date.now() - 7200000).toISOString(),
  },
  {
    id: 'mock-2',
    contenu: '⚠️ URGENT: Livraison de béton décalée à 14h au lieu de 10h sur Résidence Les Pins. Merci de réorganiser les équipes.',
    type: 'urgent',
    auteur: { id: '3', prenom: 'Jean', nom: 'Conducteur', couleur: '#9B59B6', role: 'conducteur' } as Post['auteur'],
    target_type: 'chantiers',
    target_chantiers: [{ id: 'ch1', nom: 'Résidence Les Pins' }] as Post['target_chantiers'],
    is_pinned: false,
    is_urgent: true,
    likes_count: 5,
    commentaires_count: 8,
    likes: [],
    medias: [],
    commentaires: [],
    created_at: new Date(Date.now() - 1800000).toISOString(),
  },
  {
    id: 'mock-3',
    contenu: 'Formation sécurité effectuée ce matin. Rappel: port du casque OBLIGATOIRE sur tous les chantiers. Bonne journée à tous !',
    type: 'message',
    auteur: { id: '4', prenom: 'Admin', nom: 'Greg', couleur: '#27AE60', role: 'admin' } as Post['auteur'],
    target_type: 'tous',
    is_pinned: false,
    is_urgent: false,
    likes_count: 24,
    commentaires_count: 2,
    likes: [],
    medias: [],
    commentaires: [],
    created_at: new Date(Date.now() - 86400000).toISOString(),
  },
  {
    id: 'mock-4',
    contenu: 'Nouvelle machine arrivée sur le chantier École Pasteur. Formation d\'utilisation demain à 8h pour les volontaires.',
    type: 'message',
    auteur: { id: '5', prenom: 'Sophie', nom: 'Technique', couleur: '#F39C12', role: 'chef_chantier' } as Post['auteur'],
    target_type: 'tous',
    is_pinned: false,
    is_urgent: false,
    likes_count: 8,
    commentaires_count: 5,
    likes: [],
    medias: [],
    commentaires: [],
    created_at: new Date(Date.now() - 172800000).toISOString(),
  },
  {
    id: 'mock-5',
    contenu: 'Félicitations à l\'équipe du chantier Maison Durand pour la livraison en avance ! Client très satisfait.',
    type: 'message',
    auteur: { id: '4', prenom: 'Admin', nom: 'Greg', couleur: '#27AE60', role: 'admin' } as Post['auteur'],
    target_type: 'tous',
    is_pinned: false,
    is_urgent: false,
    likes_count: 45,
    commentaires_count: 12,
    likes: [],
    medias: [],
    commentaires: [],
    created_at: new Date(Date.now() - 259200000).toISOString(),
  },
]

export default function DashboardPage() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [posts, setPosts] = useState<Post[]>(MOCK_POSTS)
  const [chantiers, setChantiers] = useState<Chantier[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [newPostContent, setNewPostContent] = useState('')
  const [isPosting, setIsPosting] = useState(false)
  const [targetType, setTargetType] = useState<TargetType>('tous')
  const [selectedChantiers, setSelectedChantiers] = useState<string[]>([])
  const [isUrgent, setIsUrgent] = useState(false)
  const [page, setPage] = useState(1)
  const [hasMore, setHasMore] = useState(false)

  const isDirectionOrConducteur = user?.role === 'admin' || user?.role === 'conducteur'

  useEffect(() => {
    loadFeed()
    loadChantiers()
  }, [])

  // Handlers pour les actions
  const handleClockIn = useCallback(() => {
    alert('Pointage enregistré ! Bonne journée de travail.')
  }, [])

  const handleQuickAction = useCallback((actionId: string) => {
    switch (actionId) {
      case 'hours':
        navigate('/feuilles-heures')
        break
      case 'tasks':
        navigate('/chantiers')
        break
      case 'docs':
        navigate('/documents')
        break
      case 'photo':
        alert('Ouverture de la caméra...')
        break
    }
  }, [navigate])

  const handleNavigate = useCallback((_slotId: string) => {
    alert('Ouverture de l\'itinéraire dans Google Maps...')
    // En prod: window.open(`https://maps.google.com/?q=45+rue+de+la+Republique+Lyon`)
  }, [])

  const handleCall = useCallback((_slotId: string) => {
    alert('Appel du chef de chantier...')
    // En prod: window.location.href = 'tel:+33612345678'
  }, [])

  const loadFeed = async (pageNum = 1) => {
    try {
      setIsLoading(true)
      const response = await dashboardService.getFeed({ page: pageNum, size: 20 })
      const items = response?.items || []
      if (pageNum === 1) {
        // Utilise les mocks si l'API retourne vide
        setPosts(items.length > 0 ? items : MOCK_POSTS)
      } else {
        setPosts((prev) => [...prev, ...items])
      }
      setHasMore((response?.page || 1) < (response?.pages || 1))
      setPage(pageNum)
    } catch (error) {
      logger.error('Error loading feed', error, { context: 'DashboardPage' })
      // En cas d'erreur, affiche les mocks
      setPosts(MOCK_POSTS)
    } finally {
      setIsLoading(false)
    }
  }

  const loadChantiers = async () => {
    try {
      const response = await chantiersService.list({ size: 100, statut: 'en_cours' })
      setChantiers(response?.items || [])
    } catch (error) {
      logger.error('Error loading chantiers', error, { context: 'DashboardPage' })
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
      logger.error('Erreur lors de la publication', error, { context: 'DashboardPage', showToast: true })
    } finally {
      setIsPosting(false)
    }
  }

  // P1-7: Memoize handlers pour éviter re-renders des PostCards
  const handleLike = useCallback(async (postId: string, isLiked: boolean) => {
    try {
      if (isLiked) {
        await dashboardService.unlikePost(postId)
      } else {
        await dashboardService.likePost(postId)
      }
      const updatedPost = await dashboardService.getPost(postId)
      setPosts((prev) => prev.map((p) => (p.id === postId ? updatedPost : p)))
    } catch (error) {
      logger.error('Erreur lors du like', error, { context: 'DashboardPage', showToast: true })
    }
  }, [])

  const handlePin = useCallback(async (postId: string, isPinned: boolean) => {
    try {
      if (isPinned) {
        await dashboardService.unpinPost(postId)
      } else {
        await dashboardService.pinPost(postId)
      }
      loadFeed(1)
    } catch (error) {
      logger.error('Erreur lors de l\'epinglage', error, { context: 'DashboardPage', showToast: true })
    }
  }, [])

  const handleDelete = useCallback(async (postId: string) => {
    if (!confirm('Supprimer cette publication ?')) return

    try {
      await dashboardService.deletePost(postId)
      setPosts((prev) => prev.filter((p) => p.id !== postId))
    } catch (error) {
      logger.error('Erreur lors de la suppression', error, { context: 'DashboardPage', showToast: true })
    }
  }, [])

  // P1-7: Memoize sortedPosts pour éviter recalcul à chaque render
  const sortedPosts = useMemo(() => [...posts].sort((a, b) => {
    if (a.is_pinned && !b.is_pinned) return -1
    if (!a.is_pinned && b.is_pinned) return 1
    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  }), [posts])

  return (
    <Layout>
      <div className="min-h-screen bg-gray-100">
        <div className="p-4 space-y-4">
          {/* Top Cards - Extracted Components */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <ClockCard onClockIn={handleClockIn} />
            <WeatherCard />
            <StatsCard />
          </div>

          {/* Quick Actions - Extracted Component */}
          <QuickActions onActionClick={handleQuickAction} />

          {/* Main Content Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {/* Left Column - Planning & Feed */}
            <div className="lg:col-span-2 space-y-4">
              {/* Today's Planning - Extracted Component */}
              <TodayPlanningCard onNavigate={handleNavigate} onCall={handleCall} />

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

                {/* Posts - Fixed height with scroll */}
                <div className="space-y-4 max-h-[500px] overflow-y-auto pr-2">
                  {sortedPosts.length === 0 && !isLoading ? (
                    <div className="text-center py-12">
                      <MessageCircle className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                      <p className="text-gray-500">Aucune publication pour le moment</p>
                    </div>
                  ) : (
                    sortedPosts.map((post) => (
                      <DashboardPostCard
                        key={post.id}
                        post={post}
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
