import { useState, useEffect, useMemo } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { chantiersService, NavigationIds } from '../services/chantiers'
import { usersService } from '../services/users'
import { planningService } from '../services/planning'
import { useAuth } from '../contexts/AuthContext'
import { useToast } from '../contexts/ToastContext'
import { logger } from '../services/logger'
import Layout from '../components/Layout'
import NavigationPrevNext from '../components/NavigationPrevNext'
import MiniMap from '../components/MiniMap'
import { TaskList } from '../components/taches'
import { EditChantierModal, AddUserModal, ChantierEquipeTab, MesInterventions, ChantierLogistiqueSection } from '../components/chantiers'
import {
  ArrowLeft,
  MapPin,
  Phone,
  Clock,
  Calendar,
  Edit,
  Trash2,
  Play,
  CheckCircle,
  Lock,
  Loader2,
  Navigation,
  ExternalLink,
  ListTodo,
  Info,
  Users,
} from 'lucide-react'
import { formatDateFull } from '../utils/dates'
import type { Chantier, ChantierUpdate, User, Affectation } from '../types'
import { CHANTIER_STATUTS } from '../types'

type TabType = 'infos' | 'taches' | 'equipe'

export default function ChantierDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { user: currentUser } = useAuth()
  const { showUndoToast, addToast } = useToast()
  const [chantier, setChantier] = useState<Chantier | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [showEditModal, setShowEditModal] = useState(false)
  const [showAddUserModal, setShowAddUserModal] = useState<'conducteur' | 'chef' | 'ouvrier' | null>(null)
  const [availableUsers, setAvailableUsers] = useState<User[]>([])
  const [navIds, setNavIds] = useState<NavigationIds>({ prevId: null, nextId: null })
  // Tab state - lire depuis l'URL au démarrage
  const getInitialTab = (): TabType => {
    const params = new URLSearchParams(window.location.search)
    const tab = params.get('tab') as TabType | null
    return (tab && ['infos', 'documents', 'taches', 'planning'].includes(tab)) ? tab : 'infos'
  }
  const [activeTab, setActiveTab] = useState<TabType>(getInitialTab())
  const [planningAffectations, setPlanningAffectations] = useState<Affectation[]>([])

  const isAdmin = currentUser?.role === 'admin'
  const isConducteur = currentUser?.role === 'conducteur'
  const canEdit = isAdmin || isConducteur

  // Fusionner les ouvriers directement assignés avec ceux des affectations planning
  const allOuvriers = useMemo(() => {
    if (!chantier) return []

    const directOuvriers = chantier.ouvriers || []
    const directIds = new Set(directOuvriers.map(u => u.id))

    // Extraire les utilisateurs uniques des affectations (seulement compagnons/ouvriers)
    const planningUsersMap = new Map<string, Partial<User>>()

    planningAffectations.forEach(aff => {
      // Ignorer si déjà dans les ouvriers directs ou déjà ajouté
      if (directIds.has(aff.utilisateur_id) || planningUsersMap.has(aff.utilisateur_id)) {
        return
      }
      // Ignorer les conducteurs et chefs de chantier (ils sont dans leurs propres listes)
      const role = aff.utilisateur_role || 'compagnon'
      if (role === 'conducteur' || role === 'admin') {
        return
      }

      // Créer un objet User à partir des données de l'affectation
      planningUsersMap.set(aff.utilisateur_id, {
        id: aff.utilisateur_id,
        nom: aff.utilisateur_nom?.split(' ').slice(1).join(' ') || '',
        prenom: aff.utilisateur_nom?.split(' ')[0] || '',
        couleur: aff.utilisateur_couleur,
        metier: aff.utilisateur_metier as User['metier'],
        email: '',
        role: (role as User['role']) || 'compagnon',
        type_utilisateur: (aff.utilisateur_type as User['type_utilisateur']) || 'employe',
        is_active: true,
        created_at: '',
      })
    })

    // Combiner les deux listes
    return [
      ...directOuvriers,
      ...Array.from(planningUsersMap.values()) as User[],
    ]
  }, [chantier, planningAffectations])

  useEffect(() => {
    if (id) {
      loadChantier()
      loadNavigation()
      loadPlanningUsers()
    }
  }, [id])

  // Synchroniser l'onglet actif avec l'URL
  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    params.set('tab', activeTab)
    const newUrl = `${window.location.pathname}?${params.toString()}`
    window.history.replaceState({}, '', newUrl)
  }, [activeTab])

  const loadNavigation = async () => {
    try {
      const ids = await chantiersService.getNavigationIds(id!)
      setNavIds(ids)
    } catch (error) {
      logger.error('Error loading navigation', error, { context: 'ChantierDetailPage' })
    }
  }

  const loadPlanningUsers = async () => {
    try {
      // Charger les affectations des 30 derniers jours + 30 prochains jours
      const today = new Date()
      const startDate = new Date()
      startDate.setDate(today.getDate() - 30)
      const endDate = new Date()
      endDate.setDate(today.getDate() + 30)

      const dateDebut = startDate.toISOString().split('T')[0]
      const dateFin = endDate.toISOString().split('T')[0]

      const affectations = await planningService.getByChantier(id!, dateDebut, dateFin)
      setPlanningAffectations(affectations)
    } catch (error) {
      logger.error('Error loading planning users', error, { context: 'ChantierDetailPage' })
    }
  }

  const loadChantier = async () => {
    try {
      setIsLoading(true)
      const data = await chantiersService.getById(id!)
      setChantier(data)
    } catch (error) {
      logger.error('Error loading chantier', error, { context: 'ChantierDetailPage' })
      addToast({ message: 'Erreur lors du chargement du chantier', type: 'error' })
      navigate('/chantiers')
    } finally {
      setIsLoading(false)
    }
  }

  const loadAvailableUsers = async (role: 'conducteur' | 'chef' | 'ouvrier') => {
    try {
      // Pour les ouvriers, on charge tous les utilisateurs actifs (intérimaires, sous-traitants, ouvriers)
      const roleFilter = role === 'conducteur' ? 'conducteur' : role === 'chef' ? 'chef_chantier' : 'ouvrier'
      const response = await usersService.list({
        size: 100,
        role: roleFilter,
        is_active: true,
      })
      let existingIds: string[] = []
      if (role === 'conducteur') {
        existingIds = chantier?.conducteurs.map((u) => u.id) || []
      } else if (role === 'chef') {
        existingIds = chantier?.chefs.map((u) => u.id) || []
      } else {
        existingIds = chantier?.ouvriers?.map((u) => u.id) || []
      }
      setAvailableUsers(response.items.filter((u) => !existingIds.includes(u.id)))
    } catch (error) {
      logger.error('Error loading users', error, { context: 'ChantierDetailPage' })
      addToast({ message: 'Erreur lors du chargement des utilisateurs', type: 'error' })
    }
  }

  const handleUpdateChantier = async (data: ChantierUpdate) => {
    try {
      const updated = await chantiersService.update(id!, data)
      setChantier(updated)
      setShowEditModal(false)
      addToast({ message: 'Chantier mis a jour', type: 'success' })
    } catch (error) {
      logger.error('Error updating chantier', error, { context: 'ChantierDetailPage' })
      addToast({ message: 'Erreur lors de la mise a jour', type: 'error' })
    }
  }

  const handleDeleteChantier = () => {
    if (!chantier) return

    const chantierName = chantier.nom
    navigate('/chantiers')

    showUndoToast(
      `Chantier "${chantierName}" supprime`,
      () => {
        navigate(`/chantiers/${id}`)
        addToast({ message: 'Suppression annulee', type: 'success', duration: 3000 })
      },
      async () => {
        try {
          await chantiersService.delete(id!)
        } catch (error) {
          logger.error('Error deleting chantier', error, { context: 'ChantierDetailPage' })
          addToast({ message: 'Erreur lors de la suppression', type: 'error', duration: 5000 })
        }
      },
      5000
    )
  }

  const handleChangeStatut = async (action: 'demarrer' | 'receptionner' | 'fermer') => {
    try {
      let updated: Chantier
      switch (action) {
        case 'demarrer':
          updated = await chantiersService.demarrer(id!)
          break
        case 'receptionner':
          updated = await chantiersService.receptionner(id!)
          break
        case 'fermer':
          updated = await chantiersService.fermer(id!)
          break
      }
      setChantier(updated)
      addToast({ message: 'Statut mis a jour', type: 'success' })
    } catch (error) {
      logger.error('Error changing statut', error, { context: 'ChantierDetailPage' })
      addToast({ message: 'Erreur lors du changement de statut', type: 'error' })
    }
  }

  const handleAddUser = async (userId: string) => {
    if (!showAddUserModal) return

    try {
      let updated: Chantier
      if (showAddUserModal === 'conducteur') {
        updated = await chantiersService.addConducteur(id!, userId)
      } else if (showAddUserModal === 'chef') {
        updated = await chantiersService.addChef(id!, userId)
      } else {
        updated = await chantiersService.addOuvrier(id!, userId)
      }
      setChantier(updated)
      setShowAddUserModal(null)
      addToast({ message: 'Utilisateur ajoute', type: 'success' })
    } catch (error) {
      logger.error('Error adding user', error, { context: 'ChantierDetailPage' })
      addToast({ message: "Erreur lors de l'ajout", type: 'error' })
    }
  }

  const handleRemoveUser = (userId: string, type: 'conducteur' | 'chef' | 'ouvrier') => {
    if (!chantier) return

    let userList: User[]
    if (type === 'conducteur') {
      userList = chantier.conducteurs
    } else if (type === 'chef') {
      userList = chantier.chefs
    } else {
      userList = chantier.ouvriers || []
    }
    const removedUser = userList.find((u) => u.id === userId)
    if (!removedUser) return

    const updatedChantier = {
      ...chantier,
      conducteurs: type === 'conducteur'
        ? chantier.conducteurs.filter((u) => u.id !== userId)
        : chantier.conducteurs,
      chefs: type === 'chef'
        ? chantier.chefs.filter((u) => u.id !== userId)
        : chantier.chefs,
      ouvriers: type === 'ouvrier'
        ? (chantier.ouvriers || []).filter((u) => u.id !== userId)
        : chantier.ouvriers,
    }
    setChantier(updatedChantier)

    showUndoToast(
      `${removedUser.prenom} ${removedUser.nom} retire`,
      () => {
        setChantier(chantier)
        addToast({ message: 'Retrait annule', type: 'success', duration: 3000 })
      },
      async () => {
        try {
          if (type === 'conducteur') {
            await chantiersService.removeConducteur(id!, userId)
          } else if (type === 'chef') {
            await chantiersService.removeChef(id!, userId)
          } else {
            await chantiersService.removeOuvrier(id!, userId)
          }
        } catch (error) {
          logger.error('Error removing user', error, { context: 'ChantierDetailPage' })
          setChantier(chantier)
          addToast({ message: 'Erreur lors du retrait', type: 'error', duration: 5000 })
        }
      },
      5000
    )
  }

  if (isLoading || !chantier) {
    return (
      <Layout>
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
        </div>
      </Layout>
    )
  }

  const statutInfo = CHANTIER_STATUTS[chantier.statut]

  return (
    <Layout>
      <div className="max-w-5xl mx-auto">
        {/* Back button + Navigation */}
        <div className="flex items-center justify-between mb-4">
          <button
            onClick={() => navigate(-1)}
            className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900"
          >
            <ArrowLeft className="w-4 h-4" />
            Retour
          </button>
          <NavigationPrevNext
            prevId={navIds.prevId}
            nextId={navIds.nextId}
            baseUrl="/chantiers"
            entityLabel="chantier"
          />
        </div>

        {/* Header */}
        <div className="card mb-6">
          <div
            className="h-3 -mx-6 -mt-6 mb-4 rounded-t-xl"
            style={{ backgroundColor: chantier.couleur || '#3498DB' }}
          />

          <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <span className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">
                  {chantier.code}
                </span>
                <span
                  className="text-sm px-3 py-1 rounded-full flex items-center gap-1"
                  style={{ backgroundColor: statutInfo.color + '20', color: statutInfo.color }}
                >
                  <span
                    className="w-2 h-2 rounded-full"
                    style={{ backgroundColor: statutInfo.color }}
                  />
                  {statutInfo.label}
                </span>
              </div>
              <h1 className="text-2xl font-bold text-gray-900 mb-2">{chantier.nom}</h1>
              <div className="flex items-start gap-2 text-gray-600">
                <MapPin className="w-5 h-5 shrink-0 mt-0.5" />
                <span>{chantier.adresse}</span>
              </div>
            </div>

            {canEdit && (
              <div className="flex gap-2">
                <button
                  onClick={() => setShowEditModal(true)}
                  className="btn btn-outline flex items-center gap-2"
                >
                  <Edit className="w-4 h-4" />
                  Modifier
                </button>
                {isAdmin && (
                  <button
                    onClick={handleDeleteChantier}
                    className="btn border-red-200 text-red-600 hover:bg-red-50 flex items-center gap-2"
                  >
                    <Trash2 className="w-4 h-4" />
                    Supprimer
                  </button>
                )}
              </div>
            )}
          </div>

          {/* Status actions */}
          {canEdit && (
            <div className="flex flex-wrap gap-2 mt-4 pt-4 border-t">
              {chantier.statut === 'ouvert' && (
                <button
                  onClick={() => handleChangeStatut('demarrer')}
                  className="btn bg-green-600 text-white hover:bg-green-700 flex items-center gap-2"
                >
                  <Play className="w-4 h-4" />
                  Demarrer le chantier
                </button>
              )}
              {chantier.statut === 'en_cours' && (
                <button
                  onClick={() => handleChangeStatut('receptionner')}
                  className="btn bg-yellow-500 text-white hover:bg-yellow-600 flex items-center gap-2"
                >
                  <CheckCircle className="w-4 h-4" />
                  Marquer comme receptionne
                </button>
              )}
              {chantier.statut === 'receptionne' && (
                <button
                  onClick={() => handleChangeStatut('fermer')}
                  className="btn bg-red-600 text-white hover:bg-red-700 flex items-center gap-2"
                >
                  <Lock className="w-4 h-4" />
                  Fermer le chantier
                </button>
              )}
            </div>
          )}
        </div>

        {/* Onglets */}
        <div className="flex border-b mb-6 overflow-x-auto" role="tablist">
          <button
            onClick={() => setActiveTab('infos')}
            className={`flex items-center gap-2 px-4 py-3 border-b-2 font-medium text-sm whitespace-nowrap transition-colors ${
              activeTab === 'infos'
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
            role="tab"
            aria-selected={activeTab === 'infos'}
          >
            <Info className="w-4 h-4" />
            Informations
          </button>
          <button
            onClick={() => setActiveTab('taches')}
            className={`flex items-center gap-2 px-4 py-3 border-b-2 font-medium text-sm whitespace-nowrap transition-colors ${
              activeTab === 'taches'
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
            role="tab"
            aria-selected={activeTab === 'taches'}
          >
            <ListTodo className="w-4 h-4" />
            Taches
          </button>
          <button
            onClick={() => setActiveTab('equipe')}
            className={`flex items-center gap-2 px-4 py-3 border-b-2 font-medium text-sm whitespace-nowrap transition-colors ${
              activeTab === 'equipe'
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
            role="tab"
            aria-selected={activeTab === 'equipe'}
          >
            <Users className="w-4 h-4" />
            Equipe
          </button>
        </div>

        {/* Contenu selon l'onglet actif */}
        {activeTab === 'taches' ? (
          <TaskList chantierId={parseInt(id!)} chantierNom={chantier.nom} />
        ) : activeTab === 'equipe' ? (
          <ChantierEquipeTab
            conducteurs={chantier.conducteurs}
            chefs={chantier.chefs}
            ouvriers={allOuvriers}
            canEdit={canEdit}
            onAddUser={(type) => {
              loadAvailableUsers(type)
              setShowAddUserModal(type)
            }}
            onRemoveUser={handleRemoveUser}
          />
        ) : (
          /* Onglet Informations */
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Colonne principale */}
            <div className="lg:col-span-2 space-y-6">
              {/* Description */}
              {chantier.description && (
                <div className="card">
                  <h2 className="font-semibold text-gray-900 mb-3">Description</h2>
                  <p className="text-gray-600 whitespace-pre-wrap">{chantier.description}</p>
                </div>
              )}

              {/* Dates et heures */}
              <div className="card">
                <h2 className="font-semibold text-gray-900 mb-4">Planning du chantier</h2>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  {chantier.heures_estimees && (
                    <div className="flex items-center gap-3 text-sm">
                      <Clock className="w-5 h-5 text-gray-400" />
                      <div>
                        <p className="text-gray-500">Heures estimees</p>
                        <p className="font-medium">{chantier.heures_estimees}h</p>
                      </div>
                    </div>
                  )}
                  {chantier.date_debut_prevue && (
                    <div className="flex items-center gap-3 text-sm">
                      <Calendar className="w-5 h-5 text-gray-400" />
                      <div>
                        <p className="text-gray-500">Date de debut</p>
                        <p className="font-medium">
                          {formatDateFull(chantier.date_debut_prevue)}
                        </p>
                      </div>
                    </div>
                  )}
                  {chantier.date_fin_prevue && (
                    <div className="flex items-center gap-3 text-sm">
                      <Calendar className="w-5 h-5 text-gray-400" />
                      <div>
                        <p className="text-gray-500">Date de fin prevue</p>
                        <p className="font-medium">
                          {formatDateFull(chantier.date_fin_prevue)}
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Mes interventions planifiees - visible pour tous les utilisateurs */}
              <MesInterventions chantierId={id!} />

              {/* Section Logistique */}
              <ChantierLogistiqueSection chantierId={id!} />
            </div>

            {/* Sidebar */}
            <div className="space-y-6">

              {/* Contact */}
              {(chantier.contact_nom || chantier.contact_telephone) && (
                <div className="card">
                  <h2 className="font-semibold text-gray-900 mb-4">Contact sur place</h2>
                  {chantier.contact_nom && (
                    <p className="font-medium text-gray-900">{chantier.contact_nom}</p>
                  )}
                  {chantier.contact_telephone && (
                    <a
                      href={`tel:${chantier.contact_telephone}`}
                      className="flex items-center gap-2 text-primary-600 hover:text-primary-700 mt-2"
                    >
                      <Phone className="w-4 h-4" />
                      {chantier.contact_telephone}
                    </a>
                  )}
                </div>
              )}

              {/* Map / Navigation */}
              {chantier.latitude && chantier.longitude && (
                <div className="card">
                  <h2 className="font-semibold text-gray-900 mb-4">Localisation</h2>
                  <MiniMap
                    latitude={chantier.latitude}
                    longitude={chantier.longitude}
                    height="h-40"
                    locationName={chantier.nom}
                  />
                  <div className="flex gap-2 mt-3">
                    <a
                      href={chantiersService.getGoogleMapsUrl(chantier.latitude, chantier.longitude)}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex-1 btn btn-primary flex items-center justify-center gap-2 text-sm"
                    >
                      <Navigation className="w-4 h-4" />
                      Google Maps
                    </a>
                    <a
                      href={chantiersService.getWazeUrl(chantier.latitude, chantier.longitude)}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex-1 btn btn-outline flex items-center justify-center gap-2 text-sm"
                    >
                      <ExternalLink className="w-4 h-4" />
                      Waze
                    </a>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Edit Modal */}
        {showEditModal && (
          <EditChantierModal
            chantier={chantier}
            onClose={() => setShowEditModal(false)}
            onSubmit={handleUpdateChantier}
          />
        )}

        {/* Add User Modal */}
        {showAddUserModal && (
          <AddUserModal
            type={showAddUserModal}
            users={availableUsers}
            onClose={() => setShowAddUserModal(null)}
            onSelect={handleAddUser}
          />
        )}
      </div>
    </Layout>
  )
}
