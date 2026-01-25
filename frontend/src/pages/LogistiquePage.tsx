/**
 * Page Logistique - Gestion du matériel et réservations
 *
 * LOG-01 à LOG-18: Module complet de gestion logistique
 */

import React, { useState, useEffect } from 'react'
import { Truck, Calendar, Clock, AlertCircle } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import { RessourceList, ReservationCalendar, ReservationModal } from '../components/logistique'
import type { Ressource, Reservation } from '../types/logistique'
import type { Chantier } from '../types'
import { listRessources, listReservationsEnAttente } from '../api/logistique'
import { chantiersService } from '../services/chantiers'

type TabType = 'ressources' | 'planning' | 'en-attente'

const LogistiquePage: React.FC = () => {
  const { user } = useAuth()
  const [activeTab, setActiveTab] = useState<TabType>('ressources')
  const [selectedRessource, setSelectedRessource] = useState<Ressource | null>(null)
  const [selectedReservation, setSelectedReservation] = useState<Reservation | null>(null)
  const [chantiers, setChantiers] = useState<Chantier[]>([])
  const [reservationsEnAttente, setReservationsEnAttente] = useState<Reservation[]>([])
  const [showModal, setShowModal] = useState(false)
  const [modalInitialData, setModalInitialData] = useState<{
    date?: string
    heureDebut?: string
    heureFin?: string
  }>({})

  const isAdmin = user?.role === 'admin'
  const canValidate = user?.role === 'admin' || user?.role === 'conducteur' || user?.role === 'chef_chantier'

  useEffect(() => {
    loadChantiers()
    if (canValidate) {
      loadReservationsEnAttente()
    }
  }, [canValidate])

  const loadChantiers = async () => {
    try {
      const data = await chantiersService.list({ size: 500 })
      setChantiers(data?.items || [])
    } catch (err) {
      console.error('Erreur chargement chantiers:', err)
    }
  }

  const loadReservationsEnAttente = async () => {
    try {
      const data = await listReservationsEnAttente()
      setReservationsEnAttente(data?.items || [])
    } catch (err) {
      console.error('Erreur chargement réservations en attente:', err)
    }
  }

  const handleSelectRessource = (ressource: Ressource) => {
    setSelectedRessource(ressource)
    setActiveTab('planning')
  }

  const handleCreateReservation = (date: string, heureDebut: string, heureFin: string) => {
    setModalInitialData({ date, heureDebut, heureFin })
    setSelectedReservation(null)
    setShowModal(true)
  }

  const handleSelectReservation = (reservation: Reservation) => {
    setSelectedReservation(reservation)
    setShowModal(true)
  }

  const handleModalSuccess = () => {
    // Recharger les données
    if (selectedRessource) {
      // Le calendrier se rechargera automatiquement
    }
    if (canValidate) {
      loadReservationsEnAttente()
    }
  }

  const tabs: { id: TabType; label: string; icon: React.ReactNode; badge?: number }[] = [
    { id: 'ressources', label: 'Ressources', icon: <Truck size={18} /> },
    { id: 'planning', label: 'Planning', icon: <Calendar size={18} /> },
  ]

  if (canValidate) {
    tabs.push({
      id: 'en-attente',
      label: 'En attente',
      icon: <Clock size={18} />,
      badge: reservationsEnAttente.length,
    })
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Truck className="text-blue-600" size={24} />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Logistique</h1>
                <p className="text-sm text-gray-500">
                  Gestion du matériel et réservations
                </p>
              </div>
            </div>
          </div>

          {/* Tabs */}
          <div className="flex gap-1 mt-4 -mb-px">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-t-lg transition-colors ${
                  activeTab === tab.id
                    ? 'bg-blue-50 text-blue-600 border-b-2 border-blue-600'
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                }`}
              >
                {tab.icon}
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
          <>
            {selectedRessource ? (
              <div className="space-y-4">
                <button
                  onClick={() => setSelectedRessource(null)}
                  className="text-sm text-blue-600 hover:text-blue-700"
                >
                  ← Retour aux ressources
                </button>
                <ReservationCalendar
                  ressource={selectedRessource}
                  onCreateReservation={handleCreateReservation}
                  onSelectReservation={handleSelectReservation}
                />
              </div>
            ) : (
              <div className="text-center py-12">
                <Calendar size={48} className="mx-auto text-gray-400 mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Sélectionnez une ressource
                </h3>
                <p className="text-gray-500 mb-4">
                  Choisissez une ressource pour voir son planning de réservations
                </p>
                <button
                  onClick={() => setActiveTab('ressources')}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Voir les ressources
                </button>
              </div>
            )}
          </>
        )}

        {/* Tab En attente */}
        {activeTab === 'en-attente' && canValidate && (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <AlertCircle className="text-orange-500" size={20} />
              Réservations en attente de validation
            </h2>

            {reservationsEnAttente.length === 0 ? (
              <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
                <Clock size={48} className="mx-auto text-gray-400 mb-4" />
                <p className="text-gray-500">
                  Aucune réservation en attente
                </p>
              </div>
            ) : (
              <div className="bg-white rounded-lg border border-gray-200 divide-y divide-gray-200">
                {reservationsEnAttente.map((reservation) => (
                  <div
                    key={reservation.id}
                    className="p-4 hover:bg-gray-50 cursor-pointer transition-colors"
                    onClick={() => {
                      // Charger la ressource puis afficher le modal
                      listRessources({ limit: 1000 }).then((data) => {
                        const ressource = (data?.items || []).find((r) => r.id === reservation.ressource_id)
                        if (ressource) {
                          setSelectedRessource(ressource)
                          setSelectedReservation(reservation)
                          setShowModal(true)
                        }
                      })
                    }}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div
                          className="w-3 h-12 rounded"
                          style={{ backgroundColor: reservation.ressource_couleur || '#3B82F6' }}
                        />
                        <div>
                          <p className="font-medium text-gray-900">
                            [{reservation.ressource_code}] {reservation.ressource_nom}
                          </p>
                          <p className="text-sm text-gray-500">
                            {new Date(reservation.date_reservation).toLocaleDateString('fr-FR', {
                              weekday: 'short',
                              day: 'numeric',
                              month: 'short',
                            })}{' '}
                            • {reservation.heure_debut.substring(0, 5)} - {reservation.heure_fin.substring(0, 5)}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-sm text-gray-900">
                          {reservation.demandeur_nom || `User #${reservation.demandeur_id}`}
                        </p>
                        <p className="text-xs text-gray-500">
                          {reservation.chantier_nom || `Chantier #${reservation.chantier_id}`}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Modal de réservation */}
      {selectedRessource && (
        <ReservationModal
          isOpen={showModal}
          onClose={() => {
            setShowModal(false)
            setSelectedReservation(null)
            setModalInitialData({})
          }}
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
  )
}

export default LogistiquePage
