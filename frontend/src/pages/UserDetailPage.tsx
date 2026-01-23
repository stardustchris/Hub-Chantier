import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { usersService, NavigationIds } from '../services/users'
import { useAuth } from '../contexts/AuthContext'
import Layout from '../components/Layout'
import NavigationPrevNext from '../components/NavigationPrevNext'
import ImageUpload from '../components/ImageUpload'
import {
  ArrowLeft,
  Phone,
  Mail,
  Edit,
  Loader2,
  X,
  UserCheck,
  UserX,
  AlertCircle,
  Calendar,
  Briefcase,
  Hash,
} from 'lucide-react'
import { format } from 'date-fns'
import { fr } from 'date-fns/locale'
import type { User, UserUpdate, UserRole, Metier } from '../types'
import { ROLES, METIERS, USER_COLORS } from '../types'

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
      console.error('Error loading user:', error)
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
      console.error('Error updating photo:', error)
    }
  }

  const handleUpdateUser = async (data: UserUpdate) => {
    try {
      const updated = await usersService.update(id!, data)
      setUser(updated)
      setShowEditModal(false)
    } catch (error) {
      console.error('Error updating user:', error)
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
      console.error('Error toggling user status:', error)
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
  const metierInfo = user.metier ? METIERS[user.metier as Metier] : null

  return (
    <Layout>
      <div className="max-w-4xl mx-auto">
        {/* Back button + Navigation (USR-09) */}
        <div className="flex items-center justify-between mb-4">
          <Link
            to="/utilisateurs"
            className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900"
          >
            <ArrowLeft className="w-4 h-4" />
            Retour aux utilisateurs
          </Link>
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
                    {metierInfo && (
                      <span
                        className="text-sm px-3 py-1 rounded-full"
                        style={{ backgroundColor: metierInfo.color + '20', color: metierInfo.color }}
                      >
                        {metierInfo.label}
                      </span>
                    )}
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
                      {user.type_utilisateur === 'employe' ? 'Employe' : 'Sous-traitant'}
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
                    {user.type_utilisateur === 'employe' ? 'Employe' : 'Sous-traitant'}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Calendar className="w-5 h-5 text-gray-400" />
                <div>
                  <p className="text-sm text-gray-500">Membre depuis</p>
                  <p className="font-medium">
                    {format(new Date(user.created_at), 'dd MMMM yyyy', { locale: fr })}
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

interface EditUserModalProps {
  user: User
  onClose: () => void
  onSubmit: (data: UserUpdate) => void
}

function EditUserModal({ user, onClose, onSubmit }: EditUserModalProps) {
  const [formData, setFormData] = useState<UserUpdate>({
    nom: user.nom,
    prenom: user.prenom,
    role: user.role,
    type_utilisateur: user.type_utilisateur,
    telephone: user.telephone,
    metier: user.metier,
    code_utilisateur: user.code_utilisateur,
    couleur: user.couleur,
    contact_urgence_nom: user.contact_urgence_nom,
    contact_urgence_telephone: user.contact_urgence_telephone,
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
          <h2 className="text-lg font-semibold">Modifier l'utilisateur</h2>
          <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-lg">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Prenom
              </label>
              <input
                type="text"
                value={formData.prenom || ''}
                onChange={(e) => setFormData({ ...formData, prenom: e.target.value })}
                className="input"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nom
              </label>
              <input
                type="text"
                value={formData.nom || ''}
                onChange={(e) => setFormData({ ...formData, nom: e.target.value })}
                className="input"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Role
              </label>
              <select
                value={formData.role}
                onChange={(e) => setFormData({ ...formData, role: e.target.value as UserRole })}
                className="input"
              >
                {(Object.entries(ROLES) as [UserRole, typeof ROLES[UserRole]][]).map(
                  ([role, info]) => (
                    <option key={role} value={role}>
                      {info.label}
                    </option>
                  )
                )}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Type
              </label>
              <select
                value={formData.type_utilisateur}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    type_utilisateur: e.target.value as 'employe' | 'sous_traitant',
                  })
                }
                className="input"
              >
                <option value="employe">Employe</option>
                <option value="sous_traitant">Sous-traitant</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Metier
            </label>
            <select
              value={formData.metier || ''}
              onChange={(e) =>
                setFormData({ ...formData, metier: (e.target.value as Metier) || undefined })
              }
              className="input"
            >
              <option value="">Non specifie</option>
              {(Object.entries(METIERS) as [Metier, typeof METIERS[Metier]][]).map(
                ([metier, info]) => (
                  <option key={metier} value={metier}>
                    {info.label}
                  </option>
                )
              )}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Telephone
              </label>
              <input
                type="tel"
                value={formData.telephone || ''}
                onChange={(e) => setFormData({ ...formData, telephone: e.target.value })}
                className="input"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Code utilisateur
              </label>
              <input
                type="text"
                value={formData.code_utilisateur || ''}
                onChange={(e) => setFormData({ ...formData, code_utilisateur: e.target.value })}
                className="input"
                placeholder="Ex: EMP001"
              />
            </div>
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

          <div className="border-t pt-4">
            <h3 className="font-medium text-gray-900 mb-3">Contact d'urgence</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nom
                </label>
                <input
                  type="text"
                  value={formData.contact_urgence_nom || ''}
                  onChange={(e) =>
                    setFormData({ ...formData, contact_urgence_nom: e.target.value })
                  }
                  className="input"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Telephone
                </label>
                <input
                  type="tel"
                  value={formData.contact_urgence_telephone || ''}
                  onChange={(e) =>
                    setFormData({ ...formData, contact_urgence_telephone: e.target.value })
                  }
                  className="input"
                />
              </div>
            </div>
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
