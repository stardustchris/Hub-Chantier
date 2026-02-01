import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { usersService, NavigationIds } from '../services/users'
import { useAuth } from '../contexts/AuthContext'
import { logger } from '../services/logger'
import Layout from '../components/Layout'
import NavigationPrevNext from '../components/NavigationPrevNext'
import ImageUpload from '../components/ImageUpload'
import { EditUserModal } from '../components/users'
import {
  ArrowLeft,
  Phone,
  Mail,
  Edit,
  Loader2,
  UserCheck,
  UserX,
  AlertCircle,
  Calendar,
  Briefcase,
  Hash,
} from 'lucide-react'
import { formatDateFull } from '../utils/dates'
import type { User, UserUpdate, UserRole, Metier } from '../types'
import { ROLES, METIERS } from '../types'

export default function UserDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { user: currentUser } = useAuth()
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [showEditModal, setShowEditModal] = useState(false)
  const [navIds, setNavIds] = useState<NavigationIds>({ prevId: null, nextId: null })

  const isAdmin = currentUser?.role === 'admin'
  const isSelf = currentUser?.id === id

  useEffect(() => {
    if (id) {
      loadUser()
      loadNavigation()
    }
  }, [id])

  const loadUser = async () => {
    try {
      setIsLoading(true)
      const data = await usersService.getById(id!)
      setUser(data)
    } catch (error) {
      logger.error('Error loading user', error, { context: 'UserDetailPage' })
      navigate('/utilisateurs')
    } finally {
      setIsLoading(false)
    }
  }

  const loadNavigation = async () => {
    const ids = await usersService.getNavigationIds(id!)
    setNavIds(ids)
  }

  const handlePhotoUpload = async (url: string) => {
    try {
      const updated = await usersService.update(id!, { photo_profil: url } as UserUpdate)
      setUser(updated)
    } catch (error) {
      logger.error('Erreur lors de la mise a jour de la photo', error, { context: 'UserDetailPage', showToast: true })
    }
  }

  const handleUpdateUser = async (data: UserUpdate) => {
    try {
      const updated = await usersService.update(id!, data)
      setUser(updated)
      setShowEditModal(false)
    } catch (error) {
      logger.error('Erreur lors de la mise a jour', error, { context: 'UserDetailPage', showToast: true })
    }
  }

  const handleToggleActive = async () => {
    if (!user) return

    try {
      let updated: User
      if (user.is_active) {
        updated = await usersService.deactivate(id!)
      } else {
        updated = await usersService.activate(id!)
      }
      setUser(updated)
    } catch (error) {
      logger.error('Erreur lors du changement de statut', error, { context: 'UserDetailPage', showToast: true })
    }
  }

  if (isLoading || !user) {
    return (
      <Layout>
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
        </div>
      </Layout>
    )
  }

  const roleInfo = ROLES[user.role as UserRole]
  const metierInfos = (user.metiers || []).map(m => METIERS[m as Metier]).filter(Boolean)

  return (
    <Layout>
      <div className="max-w-4xl mx-auto">
        {/* Back button + Navigation (USR-09) */}
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
            baseUrl="/utilisateurs"
            entityLabel="utilisateur"
          />
        </div>

        {/* Header card */}
        <div className="card mb-6">
          <div className="flex flex-col md:flex-row md:items-start gap-6">
            {/* Avatar with upload (USR-02) */}
            {(isAdmin || isSelf) ? (
              <ImageUpload
                currentImage={user.photo_profil}
                onUpload={handlePhotoUpload}
                type="profile"
                entityId={id!}
                size="large"
                placeholder={
                  <div
                    className="w-full h-full rounded-full flex items-center justify-center text-white font-bold text-3xl"
                    style={{ backgroundColor: user.couleur || '#3498DB' }}
                  >
                    {user.prenom?.[0]}
                    {user.nom?.[0]}
                  </div>
                }
              />
            ) : (
              <div
                className="w-24 h-24 rounded-full flex items-center justify-center text-white font-bold text-3xl shrink-0 overflow-hidden"
                style={{ backgroundColor: user.couleur || '#3498DB' }}
              >
                {user.photo_profil ? (
                  <img src={user.photo_profil} alt={`${user.prenom} ${user.nom}`} className="w-full h-full object-cover" />
                ) : (
                  <>
                    {user.prenom?.[0]}
                    {user.nom?.[0]}
                  </>
                )}
              </div>
            )}

            {/* Info */}
            <div className="flex-1">
              <div className="flex items-start justify-between">
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">
                    {user.prenom} {user.nom}
                  </h1>
                  <div className="flex flex-wrap items-center gap-2 mt-2">
                    {roleInfo && (
                      <span
                        className="text-sm px-3 py-1 rounded-full"
                        style={{ backgroundColor: roleInfo.color + '20', color: roleInfo.color }}
                      >
                        {roleInfo.label}
                      </span>
                    )}
                    {metierInfos.map((metierInfo, idx) => (
                      <span
                        key={idx}
                        className="text-sm px-3 py-1 rounded-full"
                        style={{ backgroundColor: metierInfo.color + '20', color: metierInfo.color }}
                      >
                        {metierInfo.label}
                      </span>
                    ))}
                    <span
                      className={`text-sm px-3 py-1 rounded-full ${
                        user.is_active
                          ? 'bg-green-100 text-green-700'
                          : 'bg-red-100 text-red-700'
                      }`}
                    >
                      {user.is_active ? 'Actif' : 'Desactive'}
                    </span>
                    <span className="text-sm px-3 py-1 rounded-full bg-gray-100 text-gray-700">
                      {user.type_utilisateur === 'employe' && 'Employe'}
                      {user.type_utilisateur === 'cadre' && 'Cadre'}
                      {user.type_utilisateur === 'interimaire' && 'Interimaire'}
                      {user.type_utilisateur === 'sous_traitant' && 'Sous-traitant'}
                    </span>
                  </div>
                </div>

                {/* Actions */}
                {(isAdmin || isSelf) && (
                  <div className="flex gap-2">
                    <button
                      onClick={() => setShowEditModal(true)}
                      className="btn btn-outline flex items-center gap-2"
                    >
                      <Edit className="w-4 h-4" />
                      Modifier
                    </button>
                    {isAdmin && !isSelf && (
                      <button
                        onClick={handleToggleActive}
                        className={`btn flex items-center gap-2 ${
                          user.is_active
                            ? 'border-red-200 text-red-600 hover:bg-red-50'
                            : 'border-green-200 text-green-600 hover:bg-green-50'
                        }`}
                      >
                        {user.is_active ? (
                          <>
                            <UserX className="w-4 h-4" />
                            Desactiver
                          </>
                        ) : (
                          <>
                            <UserCheck className="w-4 h-4" />
                            Activer
                          </>
                        )}
                      </button>
                    )}
                  </div>
                )}
              </div>

              {/* Contact info */}
              <div className="flex flex-wrap gap-4 mt-4">
                <a
                  href={`mailto:${user.email}`}
                  className="flex items-center gap-2 text-primary-600 hover:text-primary-700"
                >
                  <Mail className="w-4 h-4" />
                  {user.email}
                </a>
                {user.telephone && (
                  <a
                    href={`tel:${user.telephone}`}
                    className="flex items-center gap-2 text-primary-600 hover:text-primary-700"
                  >
                    <Phone className="w-4 h-4" />
                    {user.telephone}
                  </a>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Details grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Info card */}
          <div className="card">
            <h2 className="font-semibold text-gray-900 mb-4">Informations</h2>
            <div className="space-y-4">
              {user.code_utilisateur && (
                <div className="flex items-center gap-3">
                  <Hash className="w-5 h-5 text-gray-400" />
                  <div>
                    <p className="text-sm text-gray-500">Code utilisateur</p>
                    <p className="font-medium">{user.code_utilisateur}</p>
                  </div>
                </div>
              )}
              <div className="flex items-center gap-3">
                <Briefcase className="w-5 h-5 text-gray-400" />
                <div>
                  <p className="text-sm text-gray-500">Type</p>
                  <p className="font-medium">
                    {user.type_utilisateur === 'employe' && 'Employe'}
                    {user.type_utilisateur === 'cadre' && 'Cadre'}
                    {user.type_utilisateur === 'interimaire' && 'Interimaire'}
                    {user.type_utilisateur === 'sous_traitant' && 'Sous-traitant'}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Calendar className="w-5 h-5 text-gray-400" />
                <div>
                  <p className="text-sm text-gray-500">Membre depuis</p>
                  <p className="font-medium">
                    {formatDateFull(user.created_at)}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Emergency contact */}
          <div className="card">
            <h2 className="font-semibold text-gray-900 mb-4">Contact d'urgence</h2>
            {user.contact_urgence_nom || user.contact_urgence_telephone ? (
              <div className="space-y-3">
                {user.contact_urgence_nom && (
                  <p className="font-medium text-gray-900">{user.contact_urgence_nom}</p>
                )}
                {user.contact_urgence_telephone && (
                  <a
                    href={`tel:${user.contact_urgence_telephone}`}
                    className="flex items-center gap-2 text-primary-600 hover:text-primary-700"
                  >
                    <Phone className="w-4 h-4" />
                    {user.contact_urgence_telephone}
                  </a>
                )}
              </div>
            ) : (
              <div className="flex items-center gap-2 text-gray-500">
                <AlertCircle className="w-5 h-5" />
                <span>Non renseigne</span>
              </div>
            )}
          </div>
        </div>

        {/* Edit Modal */}
        {showEditModal && (
          <EditUserModal
            user={user}
            onClose={() => setShowEditModal(false)}
            onSubmit={handleUpdateUser}
          />
        )}
      </div>
    </Layout>
  )
}
