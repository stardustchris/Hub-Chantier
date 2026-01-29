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
import { useClockCard, useDashboardFeed, useTodayPlanning, useWeeklyStats, useTodayTeam, useWeather } from '../hooks'
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
} from '../components/dashboard'
import { weatherNotificationService } from '../services/weatherNotifications'
import { consentService } from '../services/consent'
import { openNavigationApp } from '../utils/navigation'
import MentionInput from '../components/common/MentionInput'
import {
  MessageCircle,
  AlertTriangle,
  Loader2,
  ImagePlus,
  Camera,
  X,
} from 'lucide-react'
import type { TargetType, User } from '../types'
import { usersService } from '../services/users'

export default function DashboardPage() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const { addToast } = useToast()

  // Hook pour le pointage (clock-in/out)
  const clock = useClockCard()

  // Hook pour le feed (posts, likes, etc.)
  const feed = useDashboardFeed()

  // Charger tous les utilisateurs pour le matching des mentions @
  const [allUsers, setAllUsers] = useState<User[]>([])
  useEffect(() => {
    usersService.list({ size: 100 }).then((res) => setAllUsers(res.items)).catch(() => {})
  }, [])

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
        addToast({ message: 'Ouverture de la camera...', type: 'info' })
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

  return (
    <Layout>
      <div className="min-h-screen bg-gray-100">
        <div className="p-4 space-y-4">
          {/* Top Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <ClockCard
              isClockedIn={clock.isClockedIn}
              clockInTime={clock.clockState?.clockInTime}
              lastClockIn={clock.clockState?.clockOutTime ? `Aujourd'hui ${clock.clockState.clockOutTime}` : 'Hier 17:32'}
              canEdit={canEditTime}
              onClockIn={clock.handleClockIn}
              onClockOut={clock.handleClockOut}
              onEditTime={clock.handleEditTime}
            />
            <WeatherCard />
            <StatsCard
              hoursWorked={weeklyStats.hoursWorked}
              hoursProgress={weeklyStats.hoursProgress}
              joursTravailesMois={weeklyStats.joursTravailesMois}
              joursTotalMois={weeklyStats.joursTotalMois}
              congesPris={weeklyStats.congesPris}
              congesTotal={weeklyStats.congesTotal}
            />
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

              {/* Actualites Section */}
              <div className="bg-white rounded-2xl p-5 shadow-lg">
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
                      <span className="text-gray-400 text-left flex-1">
                        Rediger un message, partager une photo...
                      </span>
                      <MessageCircle className="w-5 h-5 text-gray-400" />
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
                          className="text-gray-400 hover:text-gray-600 py-2.5 px-3 rounded-xl"
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
                  {feed.sortedPosts.length === 0 && !feed.isLoading && !weather ? (
                    <div className="text-center py-12">
                      <MessageCircle className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                      <p className="text-gray-500">Aucune publication pour le moment</p>
                      <p className="text-gray-400 text-sm mt-1">Partagez une info avec votre equipe ci-dessus</p>
                    </div>
                  ) : (
                    <>
                      {feed.sortedPosts.map((post) => (
                        <DashboardPostCard
                          key={post.id}
                          post={post}
                          allAuthors={allUsers}
                          onLike={feed.handleLike}
                          onPin={feed.handlePin}
                          onDelete={feed.handleDelete}
                        />
                      ))}

                      {/* Bulletin météo du jour - lié au 1er chantier du planning */}
                      {weather && (
                        <WeatherBulletinPost
                          weather={weather}
                          alert={weatherAlert}
                          chantierName={currentSlot?.siteName}
                          chantierAddress={currentSlot?.siteAddress}
                          chantierLatitude={currentSlot?.siteLatitude}
                          chantierLongitude={currentSlot?.siteLongitude}
                        />
                      )}
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
    </Layout>
  )
}
