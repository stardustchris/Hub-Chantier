/**
 * DashboardPage - Page d'accueil avec tableau de bord et fil d'actualites
 * CDC Section 2 - Tableau de Bord & Feed d'Actualites
 *
 * Refactoré pour utiliser les hooks custom:
 * - useClockCard: gestion du pointage
 * - useDashboardFeed: gestion du feed
 */

import { useCallback, useRef, useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { useToast } from '../contexts/ToastContext'
import { useClockCard, useDashboardFeed, useTodayPlanning, useWeeklyStats, useTodayTeam, useWeather, useDocumentTitle } from '../hooks'
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
  WeatherBulletinPost,
  DevisPipelineCard,
  AlertesFinancieresCard,
  PostSkeleton,
  WeeklyProgressCard,
  TeamLeaderboardCard,
} from '../components/dashboard'
import PhotoCaptureModal from '../components/dashboard/PhotoCaptureModal'
import { weatherNotificationService } from '../services/weatherNotifications'
import { consentService } from '../services/consent'
import { openNavigationApp } from '../utils/navigation'
import MentionInput from '../components/common/MentionInput'
import ProgressiveHintBanner from '../components/common/ProgressiveHintBanner'
import {
  MessageCircle,
  AlertTriangle,
  Loader2,
  ImagePlus,
  Camera,
  X,
  ChevronDown,
  ChevronUp,
} from 'lucide-react'
import type { TargetType, User } from '../types'
import { usersService } from '../services/users'

export default function DashboardPage() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const { addToast } = useToast()

  // Document title
  useDocumentTitle('Tableau de bord')

  // Hook pour le pointage (clock-in/out)
  const clock = useClockCard()

  // Hook pour le feed (posts, likes, etc.)
  const feed = useDashboardFeed()

  // Charger tous les utilisateurs pour le matching des mentions @
  const [allUsers, setAllUsers] = useState<User[]>([])
  useEffect(() => {
    usersService.list({ size: 100 }).then((res) => setAllUsers(res.items)).catch(() => {})
  }, [])

  // Progressive disclosure pour mobile (5.2.3)
  // État pour savoir si les cartes secondaires sont dépliées sur mobile
  const [isSecondaryCardsExpanded, setIsSecondaryCardsExpanded] = useState(() => {
    const saved = localStorage.getItem('hub_dashboard_secondary_cards_expanded')
    return saved === 'true'
  })

  // Persister l'état dans localStorage
  useEffect(() => {
    localStorage.setItem('hub_dashboard_secondary_cards_expanded', String(isSecondaryCardsExpanded))
  }, [isSecondaryCardsExpanded])

  // Hook pour le planning du jour (affectations réelles de l'utilisateur)
  const todayPlanning = useTodayPlanning()

  // Associer le premier chantier du planning au pointage
  useEffect(() => {
    const firstSlot = todayPlanning.slots.find(s => s.chantierId)
    if (firstSlot?.chantierId && clock.setChantierId) {
      clock.setChantierId(firstSlot.chantierId)
    }
  }, [todayPlanning.slots, clock])

  // Hook pour les statistiques hebdomadaires (heures, tâches)
  const weeklyStats = useWeeklyStats()

  // Hook pour l'équipe du jour (depuis les affectations du planning)
  const todayTeam = useTodayTeam()

  // Hook pour la météo réelle avec alertes
  const { weather, alert: weatherAlert } = useWeather()

  // Demander la permission pour les notifications (uniquement si consentement donné)
  useEffect(() => {
    const requestNotifications = async () => {
      // Vérifier le consentement utilisateur RGPD avant de demander la permission
      const hasConsent = await consentService.hasConsent('notifications')

      if (hasConsent && weatherNotificationService.areNotificationsSupported()) {
        weatherNotificationService.requestNotificationPermission()
      }
    }

    requestNotifications()
  }, [])

  // Envoyer une notification si alerte météo (uniquement si consentement donné)
  useEffect(() => {
    const sendAlert = async () => {
      // Vérifier le consentement avant d'envoyer une notification
      const hasConsent = await consentService.hasConsent('notifications')

      if (weatherAlert && hasConsent) {
        weatherNotificationService.sendWeatherAlertNotification(weatherAlert)
      }
    }

    sendAlert()
  }, [weatherAlert])

  // Déterminer le slot en cours ou le prochain (synchro équipe avec planning)
  const currentSlot = useMemo(() => {
    const realSlots = todayPlanning.slots.filter(s => s.period !== 'break')
    // Priorité : slot en cours > prochain slot planifié > premier slot
    return realSlots.find(s => s.status === 'in_progress')
      || realSlots.find(s => s.status === 'planned')
      || realSlots[0]
      || null
  }, [todayPlanning.slots])

  // Équipe filtrée pour le chantier du slot en cours
  const currentTeamMembers = useMemo(() => {
    if (!currentSlot?.chantierId) return todayTeam.members
    return todayTeam.getTeamForChantier(currentSlot.chantierId)
  }, [currentSlot, todayTeam])

  const isDirectionOrConducteur = user?.role === 'admin' || user?.role === 'conducteur'
  const canEditTime = user?.role === 'admin' || user?.role === 'conducteur' || user?.role === 'chef_chantier'
  const canViewDevisPipeline = user?.role === 'admin' || user?.role === 'conducteur'

  // Keyboard shortcut: Space to clock in/out (4.4.4)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Only handle Space key
      if (e.key !== ' ') return

      // Skip if user is typing in an input field or focused on a button
      const target = e.target as HTMLElement
      const tagName = target?.tagName?.toLowerCase()
      if (tagName === 'input' || tagName === 'textarea' || tagName === 'select' || tagName === 'button') {
        return
      }

      // Prevent default space behavior (page scroll)
      e.preventDefault()

      // Trigger appropriate clock action based on state
      if (clock.isClockedIn && !clock.hasClockedOut) {
        clock.handleClockOut()
      } else if (!clock.isClockedIn || clock.hasClockedOut) {
        clock.handleClockIn()
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [clock.isClockedIn, clock.hasClockedOut, clock.handleClockIn, clock.handleClockOut])

  // Verifier si la gamification est activee
  const [gamificationEnabled, setGamificationEnabled] = useState(true)
  useEffect(() => {
    const enabled = localStorage.getItem('hub_gamification_enabled')
    setGamificationEnabled(enabled !== 'false')
  }, [])

  // Fusionner les posts avec le bulletin météo pour un tri unifié
  const feedItemsWithWeather = useMemo(() => {
    // Trier les posts par date (déjà trié normalement)
    const sortedPosts = [...feed.sortedPosts]

    // Si pas de météo, retourner juste les posts
    if (!weather) {
      return sortedPosts.map(post => ({ type: 'post' as const, data: post, sortDate: new Date(post.created_at) }))
    }

    // Trouver le premier post créé il y a plus de 6 heures
    // Le bulletin météo apparaîtra après les posts récents (< 6h) et avant les posts plus anciens
    const sixHoursAgo = new Date()
    sixHoursAgo.setHours(sixHoursAgo.getHours() - 6)

    const firstOldPostIndex = sortedPosts.findIndex(post => {
      const postDate = new Date(post.created_at)
      return postDate.getTime() < sixHoursAgo.getTime()
    })

    const result: Array<{ type: 'post' | 'weather'; data: any; sortDate: Date }> = []

    // Si tous les posts sont récents (< 6h), mettre le bulletin après tous les posts
    if (firstOldPostIndex === -1) {
      sortedPosts.forEach(post => {
        result.push({ type: 'post', data: post, sortDate: new Date(post.created_at) })
      })
      result.push({ type: 'weather', data: { weather, alert: weatherAlert }, sortDate: sixHoursAgo })
    } else {
      // Insérer le bulletin météo juste après les posts récents (< 6h)
      sortedPosts.slice(0, firstOldPostIndex).forEach(post => {
        result.push({ type: 'post', data: post, sortDate: new Date(post.created_at) })
      })
      result.push({ type: 'weather', data: { weather, alert: weatherAlert }, sortDate: sixHoursAgo })
      sortedPosts.slice(firstOldPostIndex).forEach(post => {
        result.push({ type: 'post', data: post, sortDate: new Date(post.created_at) })
      })
    }

    return result
  }, [feed.sortedPosts, weather, weatherAlert])

  // State pour le modal de capture photo
  const [isPhotoCaptureModalOpen, setIsPhotoCaptureModalOpen] = useState(false)

  // Refs pour les inputs file (ajout de photos)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const cameraInputRef = useRef<HTMLInputElement>(null)
  const [showComposer, setShowComposer] = useState(false)

  // Handler pour la sélection de photos
  const handlePhotoSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files.length > 0) {
      // TODO: Implémenter l'upload des photos
      const fileNames = Array.from(files).map(f => f.name).join(', ')
      addToast({ message: `Photo(s) sélectionnée(s): ${fileNames}`, type: 'info' })
      // Reset input pour permettre de sélectionner le même fichier
      e.target.value = ''
    }
  }, [addToast])

  // Handlers pour les actions rapides
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
        setIsPhotoCaptureModalOpen(true)
        break
    }
  }, [navigate, addToast])

  const handleNavigate = useCallback((_slotId: string) => {
    // Adresse demo - en prod, recuperer depuis le slot
    const address = '45 rue de la Republique, Lyon 3eme, France'
    openNavigationApp(address)
  }, [])

  const handleCall = useCallback((_slotId: string) => {
    addToast({ message: 'Appel du chef de chantier...', type: 'info' })
    // En prod: window.location.href = 'tel:+33612345678'
  }, [addToast])

  // Handler pour soumettre une photo depuis le modal
  const handlePhotoSubmit = useCallback(async (_photoBase64: string, description: string) => {
    try {
      // Créer le contenu du post (description + indication qu'il y a une photo)
      const content = description || '📷 Photo ajoutée'

      // TODO: Implémenter l'upload de la photo vers le backend
      // Pour l'instant, on crée juste le post avec la description
      // On met temporairement le contenu dans le state du feed puis on créer le post
      feed.setNewPostContent(content)

      // Attendre un peu pour que le state soit mis à jour
      await new Promise(resolve => setTimeout(resolve, 50))

      await feed.handleCreatePost()

      addToast({ message: 'Photo publiée avec succès !', type: 'success' })
    } catch (error) {
      addToast({ message: 'Erreur lors de la publication de la photo', type: 'error' })
      throw error
    }
  }, [feed, addToast])

  return (
    <Layout>
      <div className="min-h-screen bg-gray-100">
        <div className="p-4 space-y-4">
          {/* Progressive hint banner */}
          <ProgressiveHintBanner
            pageId="/"
            message="Astuce : Consultez la carte météo pour planifier vos chantiers. Le fil d'actualités vous permet de partager des infos rapidement avec l'équipe."
          />

          {/* Top Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div data-tour="clock-card">
              <ClockCard
                isClockedIn={clock.isClockedIn}
                hasClockedOut={clock.hasClockedOut}
                clockInTime={clock.clockState?.clockInTime}
                clockOutTime={clock.clockState?.clockOutTime}
                lastClockIn={clock.lastPointageLabel}
                canEdit={canEditTime}
                canReclockIn={isDirectionOrConducteur}
                onClockIn={clock.handleClockIn}
                onClockOut={clock.handleClockOut}
                onEditTime={clock.handleEditTime}
              />
            </div>
            <WeatherCard />
            <div data-tour="dashboard-stats">
              <StatsCard
                hoursWorked={weeklyStats.hoursWorked}
                hoursProgress={weeklyStats.hoursProgress}
                joursTravailesMois={weeklyStats.joursTravailesMois}
                joursTotalMois={weeklyStats.joursTotalMois}
                congesPris={weeklyStats.congesPris}
                congesTotal={weeklyStats.congesTotal}
              />
            </div>
          </div>

          {/* Quick Actions */}
          <QuickActions
            onActionClick={handleQuickAction}
            tasksBadge={weeklyStats.tasksTotal > 0 ? `${weeklyStats.tasksCompleted}/${weeklyStats.tasksTotal}` : undefined}
          />

          {/* Main Content Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {/* Left Column - Planning & Feed */}
            <div className="lg:col-span-2 space-y-4">
              <TodayPlanningCard
                slots={todayPlanning.slots}
                isLoading={todayPlanning.isLoading}
                onNavigate={handleNavigate}
                onCall={handleCall}
              />

              {/* Actualites Section - replié par défaut sur mobile */}
              <div
                className={`
                  bg-white rounded-2xl p-5 shadow-lg border-2 border-gray-200
                  transition-all duration-300 ease-in-out
                  lg:block
                  ${isSecondaryCardsExpanded ? 'block' : 'hidden'}
                `}
                data-tour="dashboard-feed"
              >
                <h2 className="font-semibold text-gray-800 flex items-center gap-2 mb-4">
                  <MessageCircle className="w-5 h-5 text-blue-600" />
                  Actualites
                  {feed.isLoading && <Loader2 className="w-4 h-4 animate-spin" />}
                </h2>

                {/* Post Composer */}
                <div className="mb-6">
                  {!showComposer ? (
                    /* Collapsed: bouton "Rediger un message" */
                    <button
                      onClick={() => setShowComposer(true)}
                      className="w-full flex items-center gap-3 p-4 bg-white border border-gray-200 rounded-xl hover:bg-gray-50 transition-colors"
                    >
                      <div
                        className="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold text-sm shrink-0"
                        style={{ backgroundColor: user?.couleur || '#f97316' }}
                      >
                        {user?.prenom?.[0]}{user?.nom?.[0]}
                      </div>
                      <span className="text-gray-500 text-left flex-1">
                        Rediger un message, partager une photo...
                      </span>
                      <MessageCircle className="w-5 h-5 text-gray-500" />
                    </button>
                  ) : (
                    /* Expanded: composeur complet */
                    <div className="bg-white border border-gray-200 rounded-xl p-4">
                      <div className="flex gap-3">
                        <div
                          className="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold text-sm shrink-0"
                          style={{ backgroundColor: user?.couleur || '#f97316' }}
                        >
                          {user?.prenom?.[0]}{user?.nom?.[0]}
                        </div>
                        <div className="flex-1">
                          <MentionInput
                            value={feed.newPostContent}
                            onChange={feed.setNewPostContent}
                            placeholder="Partager une photo, signaler un probleme... Utilisez @ pour mentionner"
                            rows={3}
                            className="border-gray-200 rounded-xl focus:ring-green-500"
                          />
                        </div>
                      </div>

                      {isDirectionOrConducteur && feed.newPostContent && (
                        <div className="flex flex-wrap items-center gap-3 mt-3 ml-13">
                          <select
                            value={feed.targetType}
                            onChange={(e) => feed.setTargetType(e.target.value as TargetType)}
                            className="text-sm border rounded-lg px-2 py-1"
                          >
                            <option value="tous">Tout le monde</option>
                            <option value="chantiers">Chantiers specifiques</option>
                          </select>
                          {feed.targetType === 'chantiers' && (
                            <select
                              multiple
                              value={feed.selectedChantiers}
                              onChange={(e) =>
                                feed.setSelectedChantiers(
                                  Array.from(e.target.selectedOptions, (opt) => opt.value)
                                )
                              }
                              className="text-sm border rounded-lg px-2 py-1 max-w-xs"
                            >
                              {feed.chantiers.map((c) => (
                                <option key={c.id} value={c.id}>
                                  {c.code} - {c.nom}
                                </option>
                              ))}
                            </select>
                          )}
                          <label className="flex items-center gap-2 text-sm">
                            <input
                              type="checkbox"
                              checked={feed.isUrgent}
                              onChange={(e) => feed.setIsUrgent(e.target.checked)}
                              className="rounded text-red-500"
                            />
                            <AlertTriangle className="w-4 h-4 text-red-500" />
                            Urgent
                          </label>
                        </div>
                      )}

                      {/* Actions: Publier + Photo (camera ou galerie) */}
                      <div className="flex gap-3 mt-3">
                        <button
                          onClick={() => {
                            feed.handleCreatePost()
                            setShowComposer(false)
                          }}
                          disabled={!feed.newPostContent.trim() || feed.isPosting}
                          className="flex-1 bg-green-600 text-white py-2.5 px-4 rounded-xl flex items-center justify-center gap-2 hover:bg-green-700 font-medium disabled:opacity-50"
                        >
                          {feed.isPosting ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Publier'}
                        </button>
                        <button
                          onClick={() => cameraInputRef.current?.click()}
                          className="bg-orange-500 text-white py-2.5 px-4 rounded-xl flex items-center justify-center gap-2 hover:bg-orange-600 font-medium"
                          title="Prendre une photo"
                        >
                          <Camera className="w-5 h-5" />
                          <span className="hidden sm:inline">Camera</span>
                        </button>
                        <button
                          onClick={() => fileInputRef.current?.click()}
                          className="bg-blue-500 text-white py-2.5 px-4 rounded-xl flex items-center justify-center gap-2 hover:bg-blue-600 font-medium"
                          title="Choisir une photo"
                        >
                          <ImagePlus className="w-5 h-5" />
                          <span className="hidden sm:inline">Galerie</span>
                        </button>
                        <button
                          onClick={() => {
                            feed.setNewPostContent('')
                            setShowComposer(false)
                          }}
                          className="text-gray-600 hover:text-gray-800 py-2.5 px-3 rounded-xl"
                          title="Annuler"
                        >
                          <X className="w-5 h-5" />
                        </button>
                      </div>

                      {/* Hidden file inputs */}
                      <input
                        ref={cameraInputRef}
                        type="file"
                        accept="image/*"
                        capture="environment"
                        onChange={handlePhotoSelect}
                        className="hidden"
                      />
                      <input
                        ref={fileInputRef}
                        type="file"
                        accept="image/*"
                        multiple
                        onChange={handlePhotoSelect}
                        className="hidden"
                      />
                    </div>
                  )}
                </div>

                {/* Posts */}
                <div className="space-y-4 max-h-[500px] overflow-y-scroll pr-2 scrollbar-thin" style={{ scrollbarWidth: 'thin' }}>
                  {feed.isLoading && feedItemsWithWeather.length === 0 ? (
                    /* Afficher 3 skeletons lors du chargement initial */
                    <>
                      <PostSkeleton />
                      <PostSkeleton />
                      <PostSkeleton />
                    </>
                  ) : feedItemsWithWeather.length === 0 ? (
                    <div className="text-center py-12">
                      <MessageCircle className="w-12 h-12 text-gray-500 mx-auto mb-4" />
                      <p className="text-gray-600">Aucune publication pour le moment</p>
                      <p className="text-gray-500 text-sm mt-1">Partagez une info avec votre equipe ci-dessus</p>
                    </div>
                  ) : (
                    <>
                      {feedItemsWithWeather.map((item) => (
                        item.type === 'post' ? (
                          <DashboardPostCard
                            key={item.data.id}
                            post={item.data}
                            allAuthors={allUsers}
                            onLike={feed.handleLike}
                            onPin={feed.handlePin}
                            onDelete={feed.handleDelete}
                          />
                        ) : (
                          <WeatherBulletinPost
                            key="weather-bulletin"
                            weather={item.data.weather}
                            alert={item.data.alert}
                            chantierName={currentSlot?.siteName}
                            chantierAddress={currentSlot?.siteAddress}
                            chantierLatitude={currentSlot?.siteLatitude}
                            chantierLongitude={currentSlot?.siteLongitude}
                          />
                        )
                      ))}
                    </>
                  )}

                  {feed.hasMore && !feed.isLoading && (
                    <button
                      onClick={() => feed.loadFeed(feed.page + 1)}
                      className="w-full py-3 text-green-600 hover:text-green-700 font-medium"
                    >
                      Charger plus
                    </button>
                  )}
                </div>
              </div>
            </div>

            {/* Right Column */}
            <div className="space-y-4">
              {gamificationEnabled && (
                <WeeklyProgressCard
                  hoursWorked={weeklyStats.hoursWorkedDecimal}
                  weeklyGoal={35}
                />
              )}
              {gamificationEnabled && (user?.role === 'chef_chantier' || user?.role === 'conducteur' || user?.role === 'admin') && (
                <TeamLeaderboardCard
                  members={[
                    { id: '1', name: 'Jean Martin', hoursLogged: 38.5, hoursPlanned: 35 },
                    { id: '2', name: 'Sophie Dubois', hoursLogged: 34.2, hoursPlanned: 35 },
                    { id: '3', name: 'Marc Lefebvre', hoursLogged: 32.8, hoursPlanned: 35 },
                    { id: '4', name: 'Claire Bernard', hoursLogged: 28.5, hoursPlanned: 35 },
                    { id: '5', name: 'Luc Petit', hoursLogged: 24.0, hoursPlanned: 35 },
                    { id: '6', name: 'Emma Robert', hoursLogged: 22.5, hoursPlanned: 35 },
                  ]}
                />
              )}
              {canViewDevisPipeline && <DevisPipelineCard />}
              {canViewDevisPipeline && <AlertesFinancieresCard />}
              <DocumentsCard />
              <TeamCard members={currentTeamMembers} chantierName={currentSlot?.siteName} />
            </div>
          </div>
        </div>
      </div>

      {/* Modal pour modifier l'heure de pointage */}
      {clock.showEditModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl p-6 w-full max-w-sm">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-lg">
                Modifier l'heure {clock.editTimeType === 'arrival' ? "d'arrivee" : 'de depart'}
              </h3>
              <button
                onClick={clock.closeEditModal}
                className="p-2 hover:bg-gray-100 rounded-full"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="mb-4">
              <label className="block text-sm text-gray-600 mb-1">Heure</label>
              <input
                type="time"
                value={clock.editTimeValue}
                onChange={(e) => clock.setEditTimeValue(e.target.value)}
                className="w-full border border-gray-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>
            <div className="flex gap-3">
              <button
                onClick={clock.closeEditModal}
                className="flex-1 py-3 border border-gray-300 rounded-xl font-medium hover:bg-gray-50"
              >
                Annuler
              </button>
              <button
                onClick={clock.handleSaveEditedTime}
                disabled={!clock.editTimeValue}
                className="flex-1 py-3 bg-green-600 text-white rounded-xl font-medium hover:bg-green-700 disabled:opacity-50"
              >
                Enregistrer
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal pour capture photo */}
      <PhotoCaptureModal
        isOpen={isPhotoCaptureModalOpen}
        onClose={() => setIsPhotoCaptureModalOpen(false)}
        onSubmit={handlePhotoSubmit}
      />
    </Layout>
  )
}
