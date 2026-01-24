import { ReactNode, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import {
  Home,
  Building2,
  Users,
  Calendar,
  Clock,
  FileText,
  FolderOpen,
  Truck,
  Settings,
  LogOut,
  Menu,
  X,
  Bell,
  ChevronDown,
} from 'lucide-react'
import { ROLES } from '../types'
import type { UserRole } from '../types'

interface LayoutProps {
  children: ReactNode
}

interface NavItem {
  name: string
  href: string
  icon: typeof Home
  disabled?: boolean
}

const navigation: NavItem[] = [
  { name: 'Tableau de bord', href: '/', icon: Home },
  { name: 'Chantiers', href: '/chantiers', icon: Building2 },
  { name: 'Utilisateurs', href: '/utilisateurs', icon: Users },
  { name: 'Planning', href: '/planning', icon: Calendar },
  { name: 'Feuilles d\'heures', href: '/feuilles-heures', icon: Clock },
  { name: 'Formulaires', href: '/formulaires', icon: FileText },
  { name: 'Documents', href: '/documents', icon: FolderOpen },
  { name: 'Logistique', href: '/logistique', icon: Truck },
]

export default function Layout({ children }: LayoutProps) {
  const { user, logout } = useAuth()
  const location = useLocation()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [userMenuOpen, setUserMenuOpen] = useState(false)
  const [notificationsOpen, setNotificationsOpen] = useState(false)

  // TODO: Remplacer par de vraies notifications depuis l'API
  const notifications = [
    { id: 1, message: 'Nouvelle affectation sur le chantier Villa Duplex', time: 'Il y a 5 min', read: false },
    { id: 2, message: 'Feuille d\'heures validée pour la semaine 3', time: 'Il y a 1h', read: false },
    { id: 3, message: 'Document ajouté: Plan électrique v2', time: 'Il y a 2h', read: true },
  ]
  const unreadCount = notifications.filter(n => !n.read).length

  const roleInfo = user?.role ? ROLES[user.role as UserRole] : null

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-gray-600 bg-opacity-75 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Mobile sidebar */}
      <div
        className={`fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-xl transform transition-transform duration-300 ease-in-out lg:hidden ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex items-center justify-between h-16 px-4 border-b">
          <span className="text-xl font-bold text-primary-600">Hub Chantier</span>
          <button
            onClick={() => setSidebarOpen(false)}
            className="p-2 rounded-lg hover:bg-gray-100"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        <nav className="px-2 py-4">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href
            return (
              <Link
                key={item.name}
                to={item.disabled ? '#' : item.href}
                onClick={() => !item.disabled && setSidebarOpen(false)}
                className={`flex items-center gap-3 px-4 py-3 mb-1 rounded-lg transition-colors ${
                  item.disabled
                    ? 'text-gray-400 cursor-not-allowed'
                    : isActive
                    ? 'bg-primary-50 text-primary-600'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                <item.icon className="w-5 h-5" />
                <span className="font-medium">{item.name}</span>
                {item.disabled && (
                  <span className="ml-auto text-xs bg-gray-200 px-2 py-0.5 rounded">
                    Bientot
                  </span>
                )}
              </Link>
            )
          })}
        </nav>
      </div>

      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col">
        <div className="flex flex-col flex-grow bg-white border-r">
          {/* Logo */}
          <div className="flex items-center h-16 px-6 border-b">
            <Building2 className="w-8 h-8 text-primary-600" />
            <span className="ml-3 text-xl font-bold text-primary-600">Hub Chantier</span>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-3 py-4 space-y-1">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href
              return (
                <Link
                  key={item.name}
                  to={item.disabled ? '#' : item.href}
                  className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                    item.disabled
                      ? 'text-gray-400 cursor-not-allowed'
                      : isActive
                      ? 'bg-primary-50 text-primary-600'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <item.icon className="w-5 h-5" />
                  <span className="font-medium">{item.name}</span>
                  {item.disabled && (
                    <span className="ml-auto text-xs bg-gray-200 px-2 py-0.5 rounded">
                      Bientot
                    </span>
                  )}
                </Link>
              )
            })}
          </nav>

          {/* User info */}
          <div className="border-t p-4">
            <div className="flex items-center gap-3">
              <div
                className="w-10 h-10 rounded-full flex items-center justify-center text-white font-semibold"
                style={{ backgroundColor: user?.couleur || '#3498DB' }}
              >
                {user?.prenom?.[0]}
                {user?.nom?.[0]}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {user?.prenom} {user?.nom}
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
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Top header */}
        <header className="sticky top-0 z-30 bg-white border-b">
          <div className="flex items-center justify-between h-16 px-4 sm:px-6 lg:px-8">
            {/* Mobile menu button */}
            <button
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden p-2 rounded-lg hover:bg-gray-100"
            >
              <Menu className="w-6 h-6" />
            </button>

            {/* Page title - hidden on mobile */}
            <div className="hidden lg:block">
              <h1 className="text-lg font-semibold text-gray-900">
                Greg Construction
              </h1>
            </div>

            {/* Mobile logo */}
            <span className="lg:hidden text-lg font-bold text-primary-600">
              Hub Chantier
            </span>

            {/* Right side */}
            <div className="flex items-center gap-2">
              {/* Notifications */}
              <div className="relative">
                <button
                  onClick={() => setNotificationsOpen(!notificationsOpen)}
                  className="p-2 rounded-lg hover:bg-gray-100 relative"
                >
                  <Bell className="w-5 h-5 text-gray-600" />
                  {unreadCount > 0 && (
                    <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
                  )}
                </button>

                {notificationsOpen && (
                  <>
                    <div
                      className="fixed inset-0 z-10"
                      onClick={() => setNotificationsOpen(false)}
                    />
                    <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg border z-20">
                      <div className="px-4 py-3 border-b">
                        <h3 className="font-semibold text-gray-900">Notifications</h3>
                      </div>
                      <div className="max-h-96 overflow-y-auto">
                        {notifications.length === 0 ? (
                          <div className="px-4 py-8 text-center text-gray-500">
                            Aucune notification
                          </div>
                        ) : (
                          notifications.map(notif => (
                            <div
                              key={notif.id}
                              className={`px-4 py-3 border-b last:border-b-0 hover:bg-gray-50 cursor-pointer ${
                                !notif.read ? 'bg-blue-50' : ''
                              }`}
                            >
                              <p className="text-sm text-gray-900">{notif.message}</p>
                              <p className="text-xs text-gray-500 mt-1">{notif.time}</p>
                            </div>
                          ))
                        )}
                      </div>
                      <div className="px-4 py-2 border-t">
                        <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">
                          Tout marquer comme lu
                        </button>
                      </div>
                    </div>
                  </>
                )}
              </div>

              {/* User menu */}
              <div className="relative">
                <button
                  onClick={() => setUserMenuOpen(!userMenuOpen)}
                  className="flex items-center gap-2 p-2 rounded-lg hover:bg-gray-100"
                >
                  <div
                    className="w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-semibold"
                    style={{ backgroundColor: user?.couleur || '#3498DB' }}
                  >
                    {user?.prenom?.[0]}
                    {user?.nom?.[0]}
                  </div>
                  <ChevronDown className="w-4 h-4 text-gray-500 hidden sm:block" />
                </button>

                {userMenuOpen && (
                  <>
                    <div
                      className="fixed inset-0 z-10"
                      onClick={() => setUserMenuOpen(false)}
                    />
                    <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border z-20">
                      <div className="py-1">
                        <div className="px-4 py-2 border-b">
                          <p className="text-sm font-medium">
                            {user?.prenom} {user?.nom}
                          </p>
                          <p className="text-xs text-gray-500">{user?.email}</p>
                        </div>
                        <Link
                          to="/parametres"
                          className="flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                          onClick={() => setUserMenuOpen(false)}
                        >
                          <Settings className="w-4 h-4" />
                          Parametres
                        </Link>
                        <button
                          onClick={() => {
                            setUserMenuOpen(false)
                            logout()
                          }}
                          className="flex items-center gap-2 w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                        >
                          <LogOut className="w-4 h-4" />
                          Deconnexion
                        </button>
                      </div>
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="p-4 sm:p-6 lg:p-8">{children}</main>
      </div>
    </div>
  )
}
