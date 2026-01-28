/**
 * Page Logistique - Gestion du materiel et reservations
 *
 * LOG-01 a LOG-18: Module complet de gestion logistique
 */

import React, { useState, useEffect } from 'react'
import { Truck, Calendar, Clock, AlertCircle } from 'lucide-react'
import { useLogistique } from '../hooks'
import { RessourceList, ReservationCalendar, ReservationModal } from '../components/logistique'
import Layout from '../components/Layout'
import { listRessources } from '../api/logistique'
import type { Ressource } from '../types/logistique'

const LogistiquePage: React.FC = () => {
  const {
    isAdmin,
    canValidate,
    activeTab,
    setActiveTab,
    chantiers,
    reservationsEnAttente,
    selectedRessource,
    setSelectedRessource,
    showModal,
    modalInitialData,
    selectedReservation,
    handleSelectRessource,
    handleCreateReservation,
    handleSelectReservation,
    handleSelectPendingReservation,
    handleModalClose,
    handleModalSuccess,
    tabs,
  } = useLogistique()

  // Liste des ressources pour le sélecteur
  const [allRessources, setAllRessources] = useState<Ressource[]>([])
  const [loadingRessources, setLoadingRessources] = useState(false)

  // Charger toutes les ressources
  useEffect(() => {
    const loadRessources = async () => {
      setLoadingRessources(true)
      try {
        const data = await listRessources({ limit: 1000 })
        setAllRessources(data?.items || [])
      } catch (error) {
        console.error('Erreur chargement ressources:', error)
      } finally {
        setLoadingRessources(false)
      }
    }
    if (activeTab === 'planning') {
      loadRessources()
    }
  }, [activeTab])

  return (
    <Layout>
    <div>
      {/* Header */}
      <div className="bg-white border-b border-gray-200 -mx-4 sm:-mx-6 lg:-mx-8 -mt-4 sm:-mt-6 lg:-mt-8 px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Truck className="text-blue-600" size={24} />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Logistique</h1>
                <p className="text-sm text-gray-500">
                  Gestion du materiel et reservations
                </p>
              </div>
            </div>
          </div>

          {/* Tabs */}
          <div className="flex gap-0.5 sm:gap-1 mt-4 -mb-px">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-1 sm:gap-2 px-2 sm:px-4 py-2 text-xs sm:text-sm font-medium rounded-t-lg transition-colors ${
                  activeTab === tab.id
                    ? 'bg-blue-50 text-blue-600 border-b-2 border-blue-600'
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                }`}
              >
                {tab.id === 'ressources' && <Truck size={16} className="sm:w-[18px] sm:h-[18px]" />}
                {tab.id === 'planning' && <Calendar size={16} className="sm:w-[18px] sm:h-[18px]" />}
                {tab.id === 'en-attente' && <Clock size={16} className="sm:w-[18px] sm:h-[18px]" />}
                <span>{tab.label}</span>
                {tab.badge !== undefined && tab.badge > 0 && (
                  <span className="px-2 py-0.5 text-xs bg-orange-500 text-white rounded-full">
                    {tab.badge}
                  </span>
                )}
              </button>
            ))}
          </div>
      </div>

      {/* Contenu */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Tab Ressources */}
        {activeTab === 'ressources' && (
          <RessourceList
            onSelectRessource={handleSelectRessource}
            selectedRessourceId={selectedRessource?.id}
            isAdmin={isAdmin}
          />
        )}

        {/* Tab Planning */}
        {activeTab === 'planning' && (
          <div className="space-y-4">
            {/* Sélecteur de ressource */}
            <div className="bg-white p-4 rounded-lg border border-gray-200">
              <label htmlFor="ressource-select" className="block text-sm font-medium text-gray-700 mb-2">
                Ressource à afficher
              </label>
              <select
                id="ressource-select"
                value={selectedRessource?.id || ''}
                onChange={(e) => {
                  const ressourceId = parseInt(e.target.value, 10)
                  const ressource = allRessources.find((r) => r.id === ressourceId)
                  setSelectedRessource(ressource || null)
                }}
                className="w-full sm:w-auto px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                disabled={loadingRessources}
              >
                <option value="">-- Sélectionner une ressource --</option>
                {allRessources.map((ressource) => (
                  <option key={ressource.id} value={ressource.id}>
                    [{ressource.code}] {ressource.nom}
                  </option>
                ))}
              </select>
              {allRessources.length === 0 && !loadingRessources && (
                <p className="text-sm text-gray-500 mt-2">
                  Aucune ressource disponible. {isAdmin && 'Créez-en une depuis l\'onglet Ressources.'}
                </p>
              )}
            </div>

            {/* Planning de la ressource sélectionnée */}
            {selectedRessource ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold text-gray-900">
                    Planning : {selectedRessource.nom}
                  </h2>
                  <button
                    onClick={() => setActiveTab('ressources')}
                    className="text-sm text-blue-600 hover:text-blue-700"
                  >
                    Voir toutes les ressources
                  </button>
                </div>
                <ReservationCalendar
                  ressource={selectedRessource}
                  onCreateReservation={handleCreateReservation}
                  onSelectReservation={handleSelectReservation}
                />
              </div>
            ) : (
              <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
                <Calendar size={48} className="mx-auto text-gray-400 mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Sélectionnez une ressource
                </h3>
                <p className="text-gray-500">
                  Utilisez le sélecteur ci-dessus pour afficher le planning d'une ressource
                </p>
              </div>
            )}
          </div>
        )}

        {/* Tab En attente */}
        {activeTab === 'en-attente' && canValidate && (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <AlertCircle className="text-orange-500" size={20} />
              Reservations en attente de validation
            </h2>

            {reservationsEnAttente.length === 0 ? (
              <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
                <Clock size={48} className="mx-auto text-gray-400 mb-4" />
                <p className="text-gray-500">
                  Aucune reservation en attente
                </p>
              </div>
            ) : (
              <div className="bg-white rounded-lg border border-gray-200 divide-y divide-gray-200">
                {reservationsEnAttente.map((reservation) => (
                  <div
                    key={reservation.id}
                    className="p-4 hover:bg-gray-50 cursor-pointer transition-colors"
                    onClick={() => handleSelectPendingReservation(reservation)}
                  >
                    <div className="flex items-start gap-3">
                      <div
                        className="w-3 h-12 rounded flex-shrink-0 mt-0.5"
                        style={{ backgroundColor: reservation.ressource_couleur || '#3B82F6' }}
                      />
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-gray-900 text-sm sm:text-base">
                          [{reservation.ressource_code}] {reservation.ressource_nom}
                        </p>
                        <p className="text-xs sm:text-sm text-gray-500">
                          {new Date(reservation.date_reservation).toLocaleDateString('fr-FR', {
                            weekday: 'short',
                            day: 'numeric',
                            month: 'short',
                          })}{' '}
                          • {reservation.heure_debut.substring(0, 5)} - {reservation.heure_fin.substring(0, 5)}
                        </p>
                        <div className="flex items-center gap-2 mt-1 text-xs text-gray-500">
                          <span>{reservation.demandeur_nom || `User #${reservation.demandeur_id}`}</span>
                          <span>•</span>
                          <span>{reservation.chantier_nom || `Chantier #${reservation.chantier_id}`}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Modal de reservation */}
      {selectedRessource && (
        <ReservationModal
          isOpen={showModal}
          onClose={handleModalClose}
          ressource={selectedRessource}
          reservation={selectedReservation}
          chantiers={chantiers}
          initialDate={modalInitialData.date}
          initialHeureDebut={modalInitialData.heureDebut}
          initialHeureFin={modalInitialData.heureFin}
          canValidate={canValidate}
          onSuccess={handleModalSuccess}
        />
      )}
    </div>
    </Layout>
  )
}

export default LogistiquePage
