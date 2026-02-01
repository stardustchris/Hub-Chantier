import { ReactNode, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import {
  Home,
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
  ChevronRight,
  Webhook,
  Building2,
  Handshake,
  Euro,
  ShoppingCart,
  BarChart3,
  Package,
  PieChart,
} from 'lucide-react'
import { ROLES } from '../types'
import type { UserRole } from '../types'
import { useNotifications } from '../hooks/useNotifications'
import NotificationDropdown from './notifications/NotificationDropdown'

interface LayoutProps {
  children: ReactNode
}

interface NavItem {
  name: string
  href: string
  icon: typeof Home
  disabled?: boolean
  children?: NavItem[]
}

const navigation: NavItem[] = [
  { name: 'Tableau de bord', href: '/', icon: Home },
  { name: 'Chantiers', href: '/chantiers', icon: Building2 },
  { name: 'Utilisateurs', href: '/utilisateurs', icon: Users },
  { name: 'Planning', href: '/planning', icon: Calendar },
  { name: 'Feuilles d\'heures', href: '/feuilles-heures', icon: Clock },
  {
    name: 'Finances',
    href: '/finances',
    icon: BarChart3,
    children: [
      { name: 'Budgets', href: '/budgets', icon: Euro },
      { name: 'Achats', href: '/achats', icon: ShoppingCart },
      { name: 'Fournisseurs', href: '/fournisseurs', icon: Handshake },
    ],
  },
  {
    name: 'Devis',
    href: '/devis',
    icon: FileText,
    children: [
      { name: 'Pipeline', href: '/devis/dashboard', icon: PieChart },
      { name: 'Liste devis', href: '/devis', icon: FileText },
      { name: 'Articles', href: '/devis/articles', icon: Package },
    ],
  },
  { name: 'Formulaires', href: '/formulaires', icon: FileText },
  { name: 'Documents', href: '/documents', icon: FolderOpen },
  { name: 'Logistique', href: '/logistique', icon: Truck },
  { name: 'Webhooks', href: '/webhooks', icon: Webhook },
]

// Composant de navigation reutilisable (DRY)
interface NavLinksProps {
  currentPath: string
  onItemClick?: () => void
}

function NavLinks({ currentPath, onItemClick }: NavLinksProps) {
  // Determine which groups are active based on current path
  const getGroupPaths = (item: NavItem): string[] => {
    const paths = [item.href]
    item.children?.forEach((child) => paths.push(child.href))
    return paths
  }

  const isGroupActive = (item: NavItem): boolean => {
    const paths = getGroupPaths(item)
    return paths.some((p) => currentPath === p || currentPath.startsWith(p + '/'))
  }

  // Track open state per group, defaulting to open if any child is active
  const [openGroups, setOpenGroups] = useState<Record<string, boolean>>(() => {
    const initial: Record<string, boolean> = {}
    navigation.forEach((item) => {
      if (item.children) {
        initial[item.name] = isGroupActive(item)
      }
    })
    return initial
  })

  const toggleGroup = (name: string) => {
    setOpenGroups((prev) => ({ ...prev, [name]: !prev[name] }))
  }

  return (
    <>
      {navigation.map((item) => {
        if (item.children) {
          const groupActive = isGroupActive(item)
          const isParentActive = currentPath === item.href
          const isOpen = openGroups[item.name] ?? false
          return (
            <div key={item.name}>
              <div className="flex items-center">
                <Link
                  to={item.href}
                  onClick={() => onItemClick?.()}
                  className={`flex-1 flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                    isParentActive
                      ? 'bg-primary-50 text-primary-600'
                      : groupActive
                      ? 'text-primary-600'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <item.icon className="w-5 h-5" />
                  <span className="font-medium">{item.name}</span>
                </Link>
                <button
                  onClick={() => toggleGroup(item.name)}
                  className="p-2 rounded-lg hover:bg-gray-100 text-gray-500"
                  aria-label={isOpen ? 'Replier le sous-menu' : 'Déplier le sous-menu'}
                >
                  {isOpen ? (
                    <ChevronDown className="w-4 h-4" />
                  ) : (
                    <ChevronRight className="w-4 h-4" />
                  )}
                </button>
              </div>
              {isOpen && (
                <div className="ml-4 mt-1 space-y-1 border-l-2 border-gray-200 pl-2">
                  {item.children.map((child) => {
                    const isChildActive = currentPath === child.href || currentPath.startsWith(child.href + '/')
                    return (
                      <Link
                        key={child.name}
                        to={child.href}
                        onClick={() => onItemClick?.()}
                        className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors text-sm ${
                          isChildActive
                            ? 'bg-primary-50 text-primary-600'
                            : 'text-gray-600 hover:bg-gray-100'
                        }`}
                      >
                        <child.icon className="w-4 h-4" />
                        <span className="font-medium">{child.name}</span>
                      </Link>
                    )
                  })}
                </div>
              )}
            </div>
          )
        }

        const isActive = currentPath === item.href
        return (
          <Link
            key={item.name}
            to={item.disabled ? '#' : item.href}
            onClick={() => !item.disabled && onItemClick?.()}
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
    </>
  )
}

export default function Layout({ children }: LayoutProps) {
  const { user, logout } = useAuth()
  const location = useLocation()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [userMenuOpen, setUserMenuOpen] = useState(false)
  const [notificationsOpen, setNotificationsOpen] = useState(false)

  // Notifications depuis l'API
  const { unreadCount } = useNotifications()

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
          <div className="flex items-center gap-3">
            <img src="/logo.png?v=2" alt="Hub Chantier" className="w-20 h-20 object-contain" />
            <span className="text-xl font-bold text-primary-600">Hub Chantier</span>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="p-2 rounded-lg hover:bg-gray-100"
            aria-label="Fermer le menu"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        <nav className="px-2 py-4 space-y-1 overflow-y-auto flex-1">
          <NavLinks currentPath={location.pathname} onItemClick={() => setSidebarOpen(false)} />
        </nav>
      </div>

      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col">
        <div className="flex flex-col flex-grow bg-white border-r">
          {/* Logo */}
          <div className="flex items-center h-16 px-6 border-b">
            <img src="/logo.png?v=2" alt="Hub Chantier" className="w-20 h-20 object-contain" />
            <span className="ml-3 text-xl font-bold text-primary-600">Hub Chantier</span>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
            <NavLinks currentPath={location.pathname} />
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
              aria-label="Ouvrir le menu"
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
            <div className="lg:hidden flex items-center gap-3">
              <img src="/logo.png?v=2" alt="Hub Chantier" className="w-20 h-20 object-contain" />
              <span className="text-lg font-bold text-primary-600">Hub Chantier</span>
            </div>

            {/* Right side */}
            <div className="flex items-center gap-2">
              {/* Notifications */}
              <div className="relative">
                <button
                  onClick={() => setNotificationsOpen(!notificationsOpen)}
                  className="p-2 rounded-lg hover:bg-gray-100 relative"
                  aria-label={`Notifications${unreadCount > 0 ? ` (${unreadCount} non lues)` : ''}`}
                  aria-expanded={notificationsOpen}
                >
                  <Bell className="w-5 h-5 text-gray-600" />
                  {unreadCount > 0 && (
                    <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
                  )}
                </button>

                <NotificationDropdown
                  isOpen={notificationsOpen}
                  onClose={() => setNotificationsOpen(false)}
                />
              </div>

              {/* User menu */}
              <div className="relative">
                <button
                  onClick={() => setUserMenuOpen(!userMenuOpen)}
                  className="flex items-center gap-2 p-2 rounded-lg hover:bg-gray-100"
                  aria-label="Menu utilisateur"
                  aria-expanded={userMenuOpen}
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
                          to="/security"
                          className="flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                          onClick={() => setUserMenuOpen(false)}
                        >
                          <Settings className="w-4 h-4" />
                          Sécurité
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
