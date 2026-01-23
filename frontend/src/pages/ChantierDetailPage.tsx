import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { chantiersService, NavigationIds } from '../services/chantiers'
import { usersService } from '../services/users'
import { useAuth } from '../contexts/AuthContext'
import { useToast } from '../contexts/ToastContext'
import Layout from '../components/Layout'
import NavigationPrevNext from '../components/NavigationPrevNext'
import MiniMap from '../components/MiniMap'
import { TaskList } from '../components/taches'
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
  Plus,
  X,
  Navigation,
  ExternalLink,
  ListTodo,
  Info,
  Users,
} from 'lucide-react'
import { format } from 'date-fns'
import { fr } from 'date-fns/locale'
import type { Chantier, ChantierUpdate, User } from '../types'
import { CHANTIER_STATUTS, ROLES, USER_COLORS } from '../types'
import type { UserRole } from '../types'

type TabType = 'infos' | 'taches' | 'equipe'

export default function ChantierDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { user: currentUser } = useAuth()
  const { showUndoToast, addToast } = useToast()
  const [chantier, setChantier] = useState<Chantier | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [showEditModal, setShowEditModal] = useState(false)
  const [showAddUserModal, setShowAddUserModal] = useState<'conducteur' | 'chef' | null>(null)
  const [availableUsers, setAvailableUsers] = useState<User[]>([])
  const [navIds, setNavIds] = useState<NavigationIds>({ prevId: null, nextId: null })
  const [activeTab, setActiveTab] = useState<TabType>('infos')

  const isAdmin = currentUser?.role === 'admin'
  const isConducteur = currentUser?.role === 'conducteur'
  const canEdit = isAdmin || isConducteur

  useEffect(() => {
    if (id) {
      loadChantier()
      loadNavigation()
    }
  }, [id])

  const loadNavigation = async () => {
    const ids = await chantiersService.getNavigationIds(id!)
    setNavIds(ids)
  }

  const loadChantier = async () => {
    try {
      setIsLoading(true)
      const data = await chantiersService.getById(id!)
      setChantier(data)
    } catch (error) {
      console.error('Error loading chantier:', error)
      navigate('/chantiers')
    } finally {
      setIsLoading(false)
    }
  }

  const loadAvailableUsers = async (role: 'conducteur' | 'chef') => {
    try {
      const response = await usersService.list({
        size: 100,
        role: role === 'conducteur' ? 'conducteur' : 'chef_chantier',
        is_active: true,
      })
      const existingIds = role === 'conducteur'
        ? chantier?.conducteurs.map((u) => u.id) || []
        : chantier?.chefs.map((u) => u.id) || []
      setAvailableUsers(response.items.filter((u) => !existingIds.includes(u.id)))
    } catch (error) {
      console.error('Error loading users:', error)
    }
  }

  const handleUpdateChantier = async (data: ChantierUpdate) => {
    try {
      const updated = await chantiersService.update(id!, data)
      setChantier(updated)
      setShowEditModal(false)
    } catch (error) {
      console.error('Error updating chantier:', error)
    }
  }

  const handleDeleteChantier = () => {
    if (!chantier) return

    const chantierName = chantier.nom
    // Navigate immediately for better UX
    navigate('/chantiers')

    // Show undo toast - delete only happens after timeout
    showUndoToast(
      `Chantier "${chantierName}" supprime`,
      // onUndo - user clicked "Annuler"
      () => {
        navigate(`/chantiers/${id}`)
        addToast({ message: 'Suppression annulee', type: 'success', duration: 3000 })
      },
      // onConfirm - timeout elapsed, actually delete
      async () => {
        try {
          await chantiersService.delete(id!)
        } catch (error) {
          console.error('Error deleting chantier:', error)
          addToast({ message: 'Erreur lors de la suppression', type: 'error', duration: 5000 })
        }
      },
      5000 // 5 seconds to undo
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
    } catch (error) {
      console.error('Error changing statut:', error)
    }
  }

  const handleAddUser = async (userId: string) => {
    if (!showAddUserModal) return

    try {
      let updated: Chantier
      if (showAddUserModal === 'conducteur') {
        updated = await chantiersService.addConducteur(id!, userId)
      } else {
        updated = await chantiersService.addChef(id!, userId)
      }
      setChantier(updated)
      setShowAddUserModal(null)
    } catch (error) {
      console.error('Error adding user:', error)
    }
  }

  const handleRemoveUser = (userId: string, type: 'conducteur' | 'chef') => {
    if (!chantier) return

    // Find the user being removed
    const userList = type === 'conducteur' ? chantier.conducteurs : chantier.chefs
    const removedUser = userList.find((u) => u.id === userId)
    if (!removedUser) return

    // Optimistic update - remove immediately from UI
    const updatedChantier = {
      ...chantier,
      conducteurs: type === 'conducteur'
        ? chantier.conducteurs.filter((u) => u.id !== userId)
        : chantier.conducteurs,
      chefs: type === 'chef'
        ? chantier.chefs.filter((u) => u.id !== userId)
        : chantier.chefs,
    }
    setChantier(updatedChantier)

    const roleLabel = type === 'conducteur' ? 'conducteur' : 'chef de chantier'

    // Show undo toast
    showUndoToast(
      `${removedUser.prenom} ${removedUser.nom} retire`,
      // onUndo - restore user
      () => {
        setChantier(chantier) // Restore original state
        addToast({ message: 'Retrait annule', type: 'success', duration: 3000 })
      },
      // onConfirm - actually call API
      async () => {
        try {
          if (type === 'conducteur') {
            await chantiersService.removeConducteur(id!, userId)
          } else {
            await chantiersService.removeChef(id!, userId)
          }
        } catch (error) {
          console.error('Error removing user:', error)
          setChantier(chantier) // Restore on error
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
        {/* Back button + Navigation (CHT-14) */}
        <div className="flex items-center justify-between mb-4">
          <Link
            to="/chantiers"
            className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900"
          >
            <ArrowLeft className="w-4 h-4" />
            Retour aux chantiers
          </Link>
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

        {/* Onglets (TAC-01) */}
        <div className="flex border-b mb-6 overflow-x-auto">
          <button
            onClick={() => setActiveTab('infos')}
            className={`flex items-center gap-2 px-4 py-3 border-b-2 font-medium text-sm whitespace-nowrap transition-colors ${
              activeTab === 'infos'
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
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
          >
            <Users className="w-4 h-4" />
            Equipe
          </button>
        </div>

        {/* Contenu selon l'onglet actif */}
        {activeTab === 'taches' ? (
          /* Onglet Taches (TAC-01 à TAC-20) */
          <TaskList chantierId={parseInt(id!)} chantierNom={chantier.nom} />
        ) : activeTab === 'equipe' ? (
          /* Onglet Equipe */
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-semibold text-gray-900">Equipe</h2>
            </div>

            {/* Conducteurs */}
            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-medium text-gray-700">Conducteurs de travaux</h3>
                {canEdit && (
                  <button
                    onClick={() => {
                      loadAvailableUsers('conducteur')
                      setShowAddUserModal('conducteur')
                    }}
                    className="text-sm text-primary-600 hover:text-primary-700 flex items-center gap-1"
                  >
                    <Plus className="w-4 h-4" />
                    Ajouter
                  </button>
                )}
              </div>
              {chantier.conducteurs.length === 0 ? (
                <p className="text-sm text-gray-500">Aucun conducteur assigne</p>
              ) : (
                <div className="space-y-2">
                  {chantier.conducteurs.map((user) => (
                    <UserRow
                      key={user.id}
                      user={user}
                      canRemove={canEdit}
                      onRemove={() => handleRemoveUser(user.id, 'conducteur')}
                    />
                  ))}
                </div>
              )}
            </div>

            {/* Chefs */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-medium text-gray-700">Chefs de chantier</h3>
                {canEdit && (
                  <button
                    onClick={() => {
                      loadAvailableUsers('chef')
                      setShowAddUserModal('chef')
                    }}
                    className="text-sm text-primary-600 hover:text-primary-700 flex items-center gap-1"
                  >
                    <Plus className="w-4 h-4" />
                    Ajouter
                  </button>
                )}
              </div>
              {chantier.chefs.length === 0 ? (
                <p className="text-sm text-gray-500">Aucun chef assigne</p>
              ) : (
                <div className="space-y-2">
                  {chantier.chefs.map((user) => (
                    <UserRow
                      key={user.id}
                      user={user}
                      canRemove={canEdit}
                      onRemove={() => handleRemoveUser(user.id, 'chef')}
                    />
                  ))}
                </div>
              )}
            </div>
          </div>
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
                <h2 className="font-semibold text-gray-900 mb-4">Planning</h2>
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
                          {format(new Date(chantier.date_debut_prevue), 'dd MMMM yyyy', { locale: fr })}
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
                          {format(new Date(chantier.date_fin_prevue), 'dd MMMM yyyy', { locale: fr })}
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
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

              {/* Map / Navigation (CHT-08, CHT-09) */}
              {chantier.latitude && chantier.longitude && (
                <div className="card">
                  <h2 className="font-semibold text-gray-900 mb-4">Localisation</h2>
                  {/* Mini carte interactive (CHT-09) */}
                  <MiniMap
                    latitude={chantier.latitude}
                    longitude={chantier.longitude}
                    height="h-40"
                    locationName={chantier.nom}
                  />
                  {/* Boutons navigation GPS (CHT-08) */}
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

interface UserRowProps {
  user: User
  canRemove: boolean
  onRemove: () => void
}

function UserRow({ user, canRemove, onRemove }: UserRowProps) {
  const roleInfo = ROLES[user.role as UserRole]

  return (
    <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
      <div className="flex items-center gap-3">
        <div
          className="w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-semibold"
          style={{ backgroundColor: user.couleur || '#3498DB' }}
        >
          {user.prenom?.[0]}
          {user.nom?.[0]}
        </div>
        <div>
          <p className="font-medium text-sm">
            {user.prenom} {user.nom}
          </p>
          {roleInfo && (
            <span
              className="text-xs px-2 py-0.5 rounded-full"
              style={{ backgroundColor: roleInfo.color + '20', color: roleInfo.color }}
            >
              {roleInfo.label}
            </span>
          )}
        </div>
      </div>
      {canRemove && (
        <button
          onClick={onRemove}
          className="p-1 text-gray-400 hover:text-red-500"
        >
          <X className="w-4 h-4" />
        </button>
      )}
    </div>
  )
}

interface EditChantierModalProps {
  chantier: Chantier
  onClose: () => void
  onSubmit: (data: ChantierUpdate) => void
}

function EditChantierModal({ chantier, onClose, onSubmit }: EditChantierModalProps) {
  const [formData, setFormData] = useState<ChantierUpdate>({
    nom: chantier.nom,
    adresse: chantier.adresse,
    couleur: chantier.couleur,
    statut: chantier.statut,
    contact_nom: chantier.contact_nom,
    contact_telephone: chantier.contact_telephone,
    heures_estimees: chantier.heures_estimees,
    date_debut_prevue: chantier.date_debut_prevue,
    date_fin_prevue: chantier.date_fin_prevue,
    description: chantier.description,
  })
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    try {
      await onSubmit(formData)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="fixed inset-0 bg-black/50" onClick={onClose} />
      <div className="relative bg-white rounded-xl shadow-xl w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b px-6 py-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold">Modifier le chantier</h2>
          <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-lg">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nom du chantier
            </label>
            <input
              type="text"
              value={formData.nom || ''}
              onChange={(e) => setFormData({ ...formData, nom: e.target.value })}
              className="input"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Adresse
            </label>
            <textarea
              value={formData.adresse || ''}
              onChange={(e) => setFormData({ ...formData, adresse: e.target.value })}
              className="input"
              rows={2}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Couleur
            </label>
            <div className="flex flex-wrap gap-2">
              {USER_COLORS.map((color) => (
                <button
                  key={color.code}
                  type="button"
                  onClick={() => setFormData({ ...formData, couleur: color.code })}
                  className={`w-8 h-8 rounded-full border-2 transition-all ${
                    formData.couleur === color.code
                      ? 'border-gray-900 scale-110'
                      : 'border-transparent'
                  }`}
                  style={{ backgroundColor: color.code }}
                  title={color.name}
                />
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Statut
            </label>
            <select
              value={formData.statut || chantier.statut}
              onChange={(e) => setFormData({ ...formData, statut: e.target.value as any })}
              className="input"
            >
              {Object.entries(CHANTIER_STATUTS).map(([key, info]) => (
                <option key={key} value={key}>
                  {info.label}
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Contact nom
              </label>
              <input
                type="text"
                value={formData.contact_nom || ''}
                onChange={(e) => setFormData({ ...formData, contact_nom: e.target.value })}
                className="input"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Contact telephone
              </label>
              <input
                type="tel"
                value={formData.contact_telephone || ''}
                onChange={(e) => setFormData({ ...formData, contact_telephone: e.target.value })}
                className="input"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Date debut prevue
              </label>
              <input
                type="date"
                value={formData.date_debut_prevue || ''}
                onChange={(e) => setFormData({ ...formData, date_debut_prevue: e.target.value })}
                className="input"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Date fin prevue
              </label>
              <input
                type="date"
                value={formData.date_fin_prevue || ''}
                onChange={(e) => setFormData({ ...formData, date_fin_prevue: e.target.value })}
                className="input"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Heures estimees
            </label>
            <input
              type="number"
              value={formData.heures_estimees || ''}
              onChange={(e) =>
                setFormData({ ...formData, heures_estimees: parseInt(e.target.value) || undefined })
              }
              className="input"
              min={0}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              value={formData.description || ''}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="input"
              rows={3}
            />
          </div>

          <div className="flex gap-3 pt-4">
            <button type="button" onClick={onClose} className="flex-1 btn btn-outline">
              Annuler
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="flex-1 btn btn-primary flex items-center justify-center gap-2"
            >
              {isSubmitting && <Loader2 className="w-4 h-4 animate-spin" />}
              Enregistrer
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

interface AddUserModalProps {
  type: 'conducteur' | 'chef'
  users: User[]
  onClose: () => void
  onSelect: (userId: string) => void
}

function AddUserModal({ type, users, onClose, onSelect }: AddUserModalProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="fixed inset-0 bg-black/50" onClick={onClose} />
      <div className="relative bg-white rounded-xl shadow-xl w-full max-w-md mx-4 max-h-[80vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b px-6 py-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold">
            Ajouter un {type === 'conducteur' ? 'conducteur' : 'chef de chantier'}
          </h2>
          <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-lg">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-4">
          {users.length === 0 ? (
            <p className="text-center text-gray-500 py-8">
              Aucun utilisateur disponible
            </p>
          ) : (
            <div className="space-y-2">
              {users.map((user) => (
                <button
                  key={user.id}
                  onClick={() => onSelect(user.id)}
                  className="w-full flex items-center gap-3 p-3 rounded-lg hover:bg-gray-50 text-left"
                >
                  <div
                    className="w-10 h-10 rounded-full flex items-center justify-center text-white font-semibold"
                    style={{ backgroundColor: user.couleur || '#3498DB' }}
                  >
                    {user.prenom?.[0]}
                    {user.nom?.[0]}
                  </div>
                  <div>
                    <p className="font-medium">
                      {user.prenom} {user.nom}
                    </p>
                    <p className="text-sm text-gray-500">{user.email}</p>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
