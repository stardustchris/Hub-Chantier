import { useState, useCallback } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { useListPage } from '../hooks/useListPage'
import { useUsersList } from '../hooks/useUsersList'
import { logger } from '../services/logger'
import { useToast } from '../contexts/ToastContext'
import Layout from '../components/Layout'
import { UserCard, CreateUserModal, InviteUserModal } from '../components/users'
import { useDocumentTitle } from '../hooks/useDocumentTitle'
import {
  Users,
  Plus,
  Search,
  Loader2,
  X,
  Mail,
} from 'lucide-react'
import type { User, UserRole, UserCreate } from '../types'
import { ROLES } from '../types'

export default function UsersListPage() {
  const { user: currentUser } = useAuth()
  const { addToast } = useToast()
  const isAdmin = currentUser?.role === 'admin'

  // Document title
  useDocumentTitle('Utilisateurs')

  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showInviteModal, setShowInviteModal] = useState(false)

  const {
    roleStats,
    fetchUsers,
    handleCreateUser,
    handleInviteUser,
    handleToggleActive,
  } = useUsersList({ addToast })

  // Use the reusable list hook for pagination, search, and loading
  const {
    items: users,
    isLoading,
    page,
    setPage,
    totalPages,
    totalItems,
    search,
    setSearch,
    filters,
    setFilter,
    clearFilters,
    reload,
  } = useListPage<User>({
    fetchItems: fetchUsers,
    pageSize: 12,
  })

  const roleFilter = (filters.role as UserRole | undefined) || ''
  const activeFilter = filters.is_active as boolean | null ?? null

  const handleCreateUserWrapper = useCallback(async (data: UserCreate) => {
    try {
      await handleCreateUser(data)
      setShowCreateModal(false)
      reload()
    } catch (error) {
      logger.error('Error creating user', error, { context: 'UsersListPage' })
      throw error
    }
  }, [handleCreateUser, reload])

  const handleInviteUserWrapper = useCallback(async (data: { email: string; nom: string; prenom: string; role: string }) => {
    try {
      await handleInviteUser(data)
      setShowInviteModal(false)
      reload()
    } catch (error) {
      logger.error('Error inviting user', error, { context: 'UsersListPage' })
      throw error
    }
  }, [handleInviteUser, reload])

  const handleToggleActiveWrapper = useCallback(async (user: User) => {
    await handleToggleActive(user)
    reload()
  }, [handleToggleActive, reload])

  const handleSetRoleFilter = useCallback((role: UserRole | '') => {
    setFilter('role', role || undefined)
  }, [setFilter])

  const handleSetActiveFilter = useCallback((value: string) => {
    setFilter('is_active', value === '' ? undefined : value === 'active')
  }, [setFilter])

  const handleClearFilters = useCallback(() => {
    clearFilters()
  }, [clearFilters])

  const getRoleCount = useCallback((role: UserRole) => {
    return roleStats[role]
  }, [roleStats])

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
            <div className="flex gap-3">
              <button
                onClick={() => setShowInviteModal(true)}
                className="btn btn-outline flex items-center gap-2"
              >
                <Mail className="w-5 h-5" />
                Inviter
              </button>
              <button
                onClick={() => setShowCreateModal(true)}
                className="btn btn-primary flex items-center gap-2"
              >
                <Plus className="w-5 h-5" />
                Créer
              </button>
            </div>
          )}
        </div>

        {/* Stats cards */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
          {/* Bouton "Tous" - vue par défaut */}
          <button
            onClick={() => handleSetRoleFilter('')}
            className={`card text-left transition-all ${
              roleFilter === '' ? 'ring-2 ring-primary-500' : ''
            }`}
          >
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 rounded-full bg-gray-400" />
              <div>
                <p className="text-2xl font-bold text-gray-900">{totalItems}</p>
                <p className="text-xs text-gray-500">Tous</p>
              </div>
            </div>
          </button>

          {/* Boutons par rôle */}
          {(Object.entries(ROLES) as [UserRole, typeof ROLES[UserRole]][]).map(([role, info]) => (
            <button
              key={role}
              onClick={() => handleSetRoleFilter(roleFilter === role ? '' : role)}
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
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-600" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Rechercher un utilisateur..."
                className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div className="flex gap-2">
              <select
                value={roleFilter}
                onChange={(e) => handleSetRoleFilter(e.target.value as UserRole | '')}
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
                onChange={(e) => handleSetActiveFilter(e.target.value)}
                className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500"
              >
                <option value="">Tous</option>
                <option value="active">Actifs</option>
                <option value="inactive">Desactives</option>
              </select>
              {(search || roleFilter || activeFilter !== null) && (
                <button
                  onClick={handleClearFilters}
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
            <Users className="w-12 h-12 text-gray-500 mx-auto mb-4" />
            <p className="text-gray-500">Aucun utilisateur trouve</p>
            {(search || roleFilter || activeFilter !== null) && (
              <button
                onClick={handleClearFilters}
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
                  onToggleActive={() => handleToggleActiveWrapper(user)}
                />
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-center gap-2">
                <button
                  onClick={() => setPage(Math.max(1, page - 1))}
                  disabled={page === 1}
                  className="px-4 py-2 border rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                >
                  Precedent
                </button>
                <span className="px-4 py-2 text-gray-600">
                  Page {page} sur {totalPages}
                </span>
                <button
                  onClick={() => setPage(Math.min(totalPages, page + 1))}
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
            onSubmit={handleCreateUserWrapper}
          />
        )}

        {/* Invite Modal */}
        {showInviteModal && (
          <InviteUserModal
            onClose={() => setShowInviteModal(false)}
            onSubmit={handleInviteUserWrapper}
          />
        )}
      </div>
    </Layout>
  )
}
