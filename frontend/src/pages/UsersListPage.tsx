import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { usersService } from '../services/users'
import { useAuth } from '../contexts/AuthContext'
import Layout from '../components/Layout'
import {
  Users,
  Plus,
  Search,
  Phone,
  Mail,
  ChevronRight,
  Loader2,
  X,
  UserCheck,
  UserX,
} from 'lucide-react'
import type { User, UserRole, UserCreate } from '../types'
import { ROLES, METIERS, USER_COLORS } from '../types'
import type { Metier } from '../types'

export default function UsersListPage() {
  const { user: currentUser } = useAuth()
  const [users, setUsers] = useState<User[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [roleFilter, setRoleFilter] = useState<UserRole | ''>('')
  const [activeFilter, setActiveFilter] = useState<boolean | null>(null)
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [showCreateModal, setShowCreateModal] = useState(false)

  const isAdmin = currentUser?.role === 'administrateur'

  useEffect(() => {
    loadUsers()
  }, [page, search, roleFilter, activeFilter])

  const loadUsers = async () => {
    try {
      setIsLoading(true)
      const response = await usersService.list({
        page,
        size: 12,
        search: search || undefined,
        role: roleFilter || undefined,
        is_active: activeFilter ?? undefined,
      })
      setUsers(response.items)
      setTotalPages(response.pages)
    } catch (error) {
      console.error('Error loading users:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleCreateUser = async (data: UserCreate) => {
    try {
      await usersService.create(data)
      setShowCreateModal(false)
      loadUsers()
    } catch (error) {
      console.error('Error creating user:', error)
      throw error
    }
  }

  const handleToggleActive = async (user: User) => {
    try {
      if (user.is_active) {
        await usersService.deactivate(user.id)
      } else {
        await usersService.activate(user.id)
      }
      loadUsers()
    } catch (error) {
      console.error('Error toggling user status:', error)
    }
  }

  const getRoleCount = (role: UserRole) => {
    return users.filter((u) => u.role === role).length
  }

  return (
    <Layout>
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Utilisateurs</h1>
            <p className="text-gray-600">Gerez les membres de votre equipe</p>
          </div>
          {isAdmin && (
            <button
              onClick={() => setShowCreateModal(true)}
              className="btn btn-primary flex items-center gap-2"
            >
              <Plus className="w-5 h-5" />
              Nouvel utilisateur
            </button>
          )}
        </div>

        {/* Stats cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          {(Object.entries(ROLES) as [UserRole, typeof ROLES[UserRole]][]).map(([role, info]) => (
            <button
              key={role}
              onClick={() => setRoleFilter(roleFilter === role ? '' : role)}
              className={`card text-left transition-all ${
                roleFilter === role ? 'ring-2 ring-primary-500' : ''
              }`}
            >
              <div className="flex items-center gap-3">
                <div
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: info.color }}
                />
                <div>
                  <p className="text-2xl font-bold text-gray-900">{getRoleCount(role)}</p>
                  <p className="text-xs text-gray-500">{info.label}</p>
                </div>
              </div>
            </button>
          ))}
        </div>

        {/* Search and filters */}
        <div className="card mb-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={search}
                onChange={(e) => {
                  setSearch(e.target.value)
                  setPage(1)
                }}
                placeholder="Rechercher un utilisateur..."
                className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div className="flex gap-2">
              <select
                value={roleFilter}
                onChange={(e) => {
                  setRoleFilter(e.target.value as UserRole | '')
                  setPage(1)
                }}
                className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500"
              >
                <option value="">Tous les roles</option>
                {(Object.entries(ROLES) as [UserRole, typeof ROLES[UserRole]][]).map(
                  ([role, info]) => (
                    <option key={role} value={role}>
                      {info.label}
                    </option>
                  )
                )}
              </select>
              <select
                value={activeFilter === null ? '' : activeFilter ? 'active' : 'inactive'}
                onChange={(e) => {
                  const value = e.target.value
                  setActiveFilter(value === '' ? null : value === 'active')
                  setPage(1)
                }}
                className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500"
              >
                <option value="">Tous</option>
                <option value="active">Actifs</option>
                <option value="inactive">Desactives</option>
              </select>
              {(search || roleFilter || activeFilter !== null) && (
                <button
                  onClick={() => {
                    setSearch('')
                    setRoleFilter('')
                    setActiveFilter(null)
                    setPage(1)
                  }}
                  className="px-3 py-2 text-gray-500 hover:text-gray-700"
                >
                  <X className="w-5 h-5" />
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Users grid */}
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
          </div>
        ) : users.length === 0 ? (
          <div className="card text-center py-12">
            <Users className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">Aucun utilisateur trouve</p>
            {(search || roleFilter || activeFilter !== null) && (
              <button
                onClick={() => {
                  setSearch('')
                  setRoleFilter('')
                  setActiveFilter(null)
                }}
                className="mt-4 text-primary-600 hover:text-primary-700"
              >
                Effacer les filtres
              </button>
            )}
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
              {users.map((user) => (
                <UserCard
                  key={user.id}
                  user={user}
                  canEdit={isAdmin}
                  onToggleActive={() => handleToggleActive(user)}
                />
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-center gap-2">
                <button
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="px-4 py-2 border rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                >
                  Precedent
                </button>
                <span className="px-4 py-2 text-gray-600">
                  Page {page} sur {totalPages}
                </span>
                <button
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                  className="px-4 py-2 border rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                >
                  Suivant
                </button>
              </div>
            )}
          </>
        )}

        {/* Create Modal */}
        {showCreateModal && (
          <CreateUserModal
            onClose={() => setShowCreateModal(false)}
            onSubmit={handleCreateUser}
          />
        )}
      </div>
    </Layout>
  )
}

interface UserCardProps {
  user: User
  canEdit: boolean
  onToggleActive: () => void
}

function UserCard({ user, canEdit, onToggleActive }: UserCardProps) {
  const roleInfo = ROLES[user.role as UserRole]
  const metierInfo = user.metier ? METIERS[user.metier as Metier] : null

  return (
    <div className={`card relative ${!user.is_active ? 'opacity-60' : ''}`}>
      <Link to={`/utilisateurs/${user.id}`} className="block">
        {/* Header */}
        <div className="flex items-start gap-4 mb-4">
          <div
            className="w-12 h-12 rounded-full flex items-center justify-center text-white font-semibold text-lg"
            style={{ backgroundColor: user.couleur || '#3498DB' }}
          >
            {user.prenom?.[0]}
            {user.nom?.[0]}
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-gray-900 truncate">
              {user.prenom} {user.nom}
            </h3>
            <div className="flex flex-wrap items-center gap-2 mt-1">
              {roleInfo && (
                <span
                  className="text-xs px-2 py-0.5 rounded-full"
                  style={{ backgroundColor: roleInfo.color + '20', color: roleInfo.color }}
                >
                  {roleInfo.label}
                </span>
              )}
              {metierInfo && (
                <span
                  className="text-xs px-2 py-0.5 rounded-full"
                  style={{ backgroundColor: metierInfo.color + '20', color: metierInfo.color }}
                >
                  {metierInfo.label}
                </span>
              )}
              {!user.is_active && (
                <span className="text-xs px-2 py-0.5 rounded-full bg-red-100 text-red-700">
                  Desactive
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Contact info */}
        <div className="space-y-2 text-sm">
          <div className="flex items-center gap-2 text-gray-600">
            <Mail className="w-4 h-4 text-gray-400" />
            <span className="truncate">{user.email}</span>
          </div>
          {user.telephone && (
            <div className="flex items-center gap-2 text-gray-600">
              <Phone className="w-4 h-4 text-gray-400" />
              <span>{user.telephone}</span>
            </div>
          )}
        </div>

        {/* Arrow */}
        <ChevronRight className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-300" />
      </Link>

      {/* Toggle active button */}
      {canEdit && (
        <button
          onClick={(e) => {
            e.preventDefault()
            onToggleActive()
          }}
          className={`absolute top-4 right-10 p-1 rounded ${
            user.is_active
              ? 'text-green-600 hover:bg-green-50'
              : 'text-red-600 hover:bg-red-50'
          }`}
          title={user.is_active ? 'Desactiver' : 'Activer'}
        >
          {user.is_active ? <UserCheck className="w-5 h-5" /> : <UserX className="w-5 h-5" />}
        </button>
      )}
    </div>
  )
}

interface CreateUserModalProps {
  onClose: () => void
  onSubmit: (data: UserCreate) => Promise<void>
}

function CreateUserModal({ onClose, onSubmit }: CreateUserModalProps) {
  const [formData, setFormData] = useState<UserCreate>({
    email: '',
    password: '',
    nom: '',
    prenom: '',
    role: 'compagnon',
    type_utilisateur: 'employe',
    couleur: USER_COLORS[0].code,
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsSubmitting(true)
    try {
      await onSubmit(formData)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erreur lors de la creation')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="fixed inset-0 bg-black/50" onClick={onClose} />
      <div className="relative bg-white rounded-xl shadow-xl w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b px-6 py-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold">Nouvel utilisateur</h2>
          <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-lg">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="bg-red-50 text-red-600 p-3 rounded-lg text-sm">{error}</div>
          )}

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Prenom *
              </label>
              <input
                type="text"
                required
                value={formData.prenom}
                onChange={(e) => setFormData({ ...formData, prenom: e.target.value })}
                className="input"
                placeholder="Jean"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nom *
              </label>
              <input
                type="text"
                required
                value={formData.nom}
                onChange={(e) => setFormData({ ...formData, nom: e.target.value })}
                className="input"
                placeholder="Dupont"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email *
            </label>
            <input
              type="email"
              required
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              className="input"
              placeholder="jean.dupont@email.com"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Mot de passe *
            </label>
            <input
              type="password"
              required
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              className="input"
              placeholder="********"
              minLength={6}
            />
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
                  setFormData({ ...formData, type_utilisateur: e.target.value as 'employe' | 'sous_traitant' })
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

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Telephone
            </label>
            <input
              type="tel"
              value={formData.telephone || ''}
              onChange={(e) => setFormData({ ...formData, telephone: e.target.value })}
              className="input"
              placeholder="06 12 34 56 78"
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

          <div className="flex gap-3 pt-4">
            <button type="button" onClick={onClose} className="flex-1 btn btn-outline">
              Annuler
            </button>
            <button
              type="submit"
              disabled={isSubmitting || !formData.email || !formData.password || !formData.nom || !formData.prenom}
              className="flex-1 btn btn-primary flex items-center justify-center gap-2"
            >
              {isSubmitting && <Loader2 className="w-4 h-4 animate-spin" />}
              Creer
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
