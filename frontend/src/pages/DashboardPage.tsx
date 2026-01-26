/**
 * DashboardPage - Page d'accueil avec tableau de bord et fil d'actualites
 * CDC Section 2 - Tableau de Bord & Feed d'Actualites
 *
 * Refactoré pour utiliser les hooks custom:
 * - useClockCard: gestion du pointage
 * - useDashboardFeed: gestion du feed
 */

import { useCallback, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { useToast } from '../contexts/ToastContext'
import { useClockCard, useDashboardFeed, useTodayPlanning, useWeeklyStats } from '../hooks'
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
import MentionInput from '../components/common/MentionInput'
import {
  MessageCircle,
  AlertTriangle,
  Loader2,
  ImagePlus,
  X,
} from 'lucide-react'
import type { TargetType } from '../types'

export default function DashboardPage() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const { addToast } = useToast()

  // Hook pour le pointage (clock-in/out)
  const clock = useClockCard()

  // Hook pour le feed (posts, likes, etc.)
  const feed = useDashboardFeed()

  // Hook pour le planning du jour (affectations réelles de l'utilisateur)
  const todayPlanning = useTodayPlanning()

  // Hook pour les statistiques hebdomadaires (heures, tâches)
  const weeklyStats = useWeeklyStats()

  const isDirectionOrConducteur = user?.role === 'admin' || user?.role === 'conducteur'
  const canEditTime = user?.role === 'admin' || user?.role === 'conducteur' || user?.role === 'chef_chantier'

  // Ref pour l'input file (ajout de photos)
  const fileInputRef = useRef<HTMLInputElement>(null)

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
    const encodedAddress = encodeURIComponent(address)

    // Detecter la plateforme
    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent)
    const isAndroid = /Android/.test(navigator.userAgent)

    // Priorite: Waze > Google Maps > Apple Maps (iOS) > Google Maps web
    if (isIOS) {
      const wazeUrl = `waze://?q=${encodedAddress}&navigate=yes`
      const appleMapsUrl = `maps://maps.apple.com/?q=${encodedAddress}`
      const googleMapsWeb = `https://maps.google.com/?q=${encodedAddress}`

      window.location.href = wazeUrl
      setTimeout(() => {
        window.location.href = appleMapsUrl
        setTimeout(() => {
          window.open(googleMapsWeb, '_blank')
        }, 500)
      }, 500)
    } else if (isAndroid) {
      const wazeUrl = `waze://?q=${encodedAddress}&navigate=yes`
      const googleMapsUrl = `google.navigation:q=${encodedAddress}`
      const googleMapsWeb = `https://maps.google.com/?q=${encodedAddress}`

      window.location.href = wazeUrl
      setTimeout(() => {
        window.location.href = googleMapsUrl
        setTimeout(() => {
          window.open(googleMapsWeb, '_blank')
        }, 500)
      }, 500)
    } else {
      window.open(`https://maps.google.com/?q=${encodedAddress}`, '_blank')
    }
  }, [])

  const handleCall = useCallback((_slotId: string) => {
    addToast({ message: 'Appel du chef de chantier...', type: 'info' })
    // En prod: window.location.href = 'tel:+33612345678'
  }, [addToast])

  const handleDocumentClick = useCallback((docId: string) => {
    addToast({ message: `Ouverture du document ${docId}...`, type: 'info' })
    // En prod: navigate(`/documents/${docId}`)
  }, [addToast])

  const handleViewAllDocuments = useCallback(() => {
    navigate('/documents')
  }, [navigate])

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
              tasksCompleted={weeklyStats.tasksCompleted}
              tasksTotal={weeklyStats.tasksTotal}
            />
          </div>

          {/* Quick Actions */}
          <QuickActions onActionClick={handleQuickAction} />

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
                        rows={2}
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

                  <div className="flex gap-3 mt-3">
                    <button
                      onClick={feed.handleCreatePost}
                      disabled={!feed.newPostContent.trim() || feed.isPosting}
                      className="flex-1 bg-green-600 text-white py-2.5 px-4 rounded-xl flex items-center justify-center gap-2 hover:bg-green-700 font-medium disabled:opacity-50"
                    >
                      {feed.isPosting ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Publier'}
                    </button>
                    <button
                      onClick={() => fileInputRef.current?.click()}
                      className="bg-orange-500 text-white py-2.5 px-4 rounded-xl flex items-center justify-center gap-2 hover:bg-orange-600 font-medium"
                    >
                      <ImagePlus className="w-5 h-5" />
                      Ajouter une photo
                    </button>
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept="image/*"
                      multiple
                      onChange={handlePhotoSelect}
                      className="hidden"
                    />
                  </div>
                </div>

                {/* Posts */}
                <div className="space-y-4 max-h-[500px] overflow-y-scroll pr-2 scrollbar-thin" style={{ scrollbarWidth: 'thin' }}>
                  {feed.sortedPosts.length === 0 && !feed.isLoading ? (
                    <div className="text-center py-12">
                      <MessageCircle className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                      <p className="text-gray-500">Aucune publication pour le moment</p>
                    </div>
                  ) : (
                    feed.sortedPosts.map((post) => (
                      <DashboardPostCard
                        key={post.id}
                        post={post}
                        onLike={feed.handleLike}
                        onPin={feed.handlePin}
                        onDelete={feed.handleDelete}
                      />
                    ))
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
              <DocumentsCard
                onDocumentClick={handleDocumentClick}
                onViewAll={handleViewAllDocuments}
              />
              <TeamCard />
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
