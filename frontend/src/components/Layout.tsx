import { ReactNode, useState, useEffect } from 'react'
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
  RefreshCw,
  HelpCircle,
  Search,
  Flame,
} from 'lucide-react'
import { ROLES } from '../types'
import type { UserRole } from '../types'
import { useNotifications } from '../hooks/useNotifications'
import NotificationDropdown from './notifications/NotificationDropdown'
import FloatingActionButton from './common/FloatingActionButton'
import OnboardingProvider, { useOnboarding } from './onboarding/OnboardingProvider'
import { useCommandPalette } from '../hooks/useCommandPalette'
import PageHelp from './common/PageHelp'
import Tooltip from './ui/Tooltip'

interface LayoutProps {
  children: ReactNode
}

interface NavItem {
  name: string
  href: string
  icon: typeof Home
  disabled?: boolean
  roles?: UserRole[]
  children?: NavItem[]
  tourId?: string
}

const navigation: NavItem[] = [
  { name: 'Tableau de bord', href: '/', icon: Home, tourId: 'nav-dashboard' },
  { name: 'Chantiers', href: '/chantiers', icon: Building2, tourId: 'nav-chantiers' },
  { name: 'Utilisateurs', href: '/utilisateurs', icon: Users, roles: ['admin', 'conducteur'], tourId: 'nav-utilisateurs' },
  { name: 'Planning', href: '/planning', icon: Calendar, tourId: 'nav-planning' },
  { name: 'Feuilles d\'heures', href: '/feuilles-heures', icon: Clock, tourId: 'nav-feuilles-heures' },
  {
    name: 'Finances',
    href: '/finances',
    icon: BarChart3,
    roles: ['admin', 'conducteur', 'chef_chantier'],
    tourId: 'nav-finances',
    children: [
      { name: 'Budgets', href: '/budgets', icon: Euro },
      { name: 'Achats', href: '/achats', icon: ShoppingCart },
      { name: 'Fournisseurs', href: '/fournisseurs', icon: Handshake },
      { name: 'Pennylane', href: '/financier/pennylane', icon: RefreshCw },
    ],
  },
  {
    name: 'Devis',
    href: '/devis',
    icon: FileText,
    roles: ['admin', 'conducteur', 'chef_chantier'],
    tourId: 'nav-devis',
    children: [
      { name: 'Pipeline', href: '/devis/dashboard', icon: PieChart },
      { name: 'Liste devis', href: '/devis', icon: FileText },
      { name: 'Articles', href: '/devis/articles', icon: Package },
    ],
  },
  { name: 'Formulaires', href: '/formulaires', icon: FileText, roles: ['admin', 'conducteur', 'chef_chantier'] },
  { name: 'Documents', href: '/documents', icon: FolderOpen },
  { name: 'Logistique', href: '/logistique', icon: Truck, roles: ['admin', 'conducteur', 'chef_chantier'] },
  { name: 'Webhooks', href: '/webhooks', icon: Webhook, roles: ['admin'], tourId: 'nav-webhooks' },
]

// Composant de navigation reutilisable (DRY)
interface NavLinksProps {
  currentPath: string
  onItemClick?: () => void
  userRole?: UserRole
}

function NavLinks({ currentPath, onItemClick, userRole }: NavLinksProps) {
  // Fonction pour filtrer les items selon le role utilisateur
  const filterByRole = (item: NavItem): boolean => {
    // Si pas de roles definis, visible par tous
    if (!item.roles) return true
    // Si un role est defini, verifier que l'utilisateur a ce role
    if (!userRole) return false
    return item.roles.includes(userRole)
  }
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
      {navigation.filter(filterByRole).map((item) => {
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
                  data-tour={item.tourId}
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
                  className="min-w-[44px] min-h-[44px] flex items-center justify-center rounded-lg hover:bg-gray-100 text-gray-600"
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
            data-tour={item.tourId}
            className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
              item.disabled
                ? 'text-gray-600 cursor-not-allowed opacity-50'
                : isActive
                ? 'bg-primary-50 text-primary-600'
                : 'text-gray-800 hover:bg-gray-100'
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

function LayoutContent({ children }: LayoutProps) {
  const { user, logout } = useAuth()
  const location = useLocation()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [userMenuOpen, setUserMenuOpen] = useState(false)
  const [notificationsOpen, setNotificationsOpen] = useState(false)

  // Gamification toggle (CDC Section 5.4.4)
  const [gamificationEnabled, setGamificationEnabled] = useState(true)

  // Charger l'etat de la gamification depuis localStorage
  useEffect(() => {
    const enabled = localStorage.getItem('hub_gamification_enabled')
    setGamificationEnabled(enabled !== 'false')
  }, [])

  // Basculer la gamification
  const toggleGamification = () => {
    const newValue = !gamificationEnabled
    setGamificationEnabled(newValue)
    localStorage.setItem('hub_gamification_enabled', String(newValue))
  }

  // Notifications depuis l'API
  const { unreadCount } = useNotifications()

  // Onboarding
  const { startTour } = useOnboarding()

  // Command Palette
  const { open: openCommandPalette } = useCommandPalette()

  const roleInfo = user?.role ? ROLES[user.role as UserRole] : null

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Skip link pour accessibilite */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:bg-white focus:px-4 focus:py-2 focus:rounded focus:shadow-lg focus:outline-none focus:ring-2 focus:ring-primary-600"
      >
        Aller au contenu principal
      </a>

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
            <picture>
              <source srcSet="/logo.webp?v=2" type="image/webp" />
              <img
                src="/logo.png?v=2"
                alt="Hub Chantier"
                className="w-16 h-16 object-contain aspect-square"
                loading="lazy"
                decoding="async"
              />
            </picture>
            <span className="text-xl font-bold text-primary-600">Hub Chantier</span>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="min-w-[44px] min-h-[44px] flex items-center justify-center rounded-lg hover:bg-gray-100"
            aria-label="Fermer le menu"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        <nav aria-label="Navigation principale" className="px-2 py-4 space-y-1 overflow-y-auto flex-1">
          <NavLinks currentPath={location.pathname} onItemClick={() => setSidebarOpen(false)} userRole={user?.role} />
        </nav>
      </div>

      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col">
        <div className="flex flex-col flex-grow bg-white border-r">
          {/* Logo */}
          <div className="flex items-center h-16 px-6 border-b">
            <picture>
              <source srcSet="/logo.webp?v=2" type="image/webp" />
              <img
                src="/logo.png?v=2"
                alt="Hub Chantier"
                className="w-16 h-16 object-contain aspect-square"
                loading="eager"
                decoding="async"
              />
            </picture>
            <span className="ml-3 text-xl font-bold text-primary-600">Hub Chantier</span>
          </div>

          {/* Navigation */}
          <nav aria-label="Navigation principale" className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
            <NavLinks currentPath={location.pathname} userRole={user?.role} />
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
            <Tooltip content="Ouvrir le menu">
              <button
                onClick={() => setSidebarOpen(true)}
                className="lg:hidden min-w-[44px] min-h-[44px] flex items-center justify-center rounded-lg hover:bg-gray-100"
                aria-label="Ouvrir le menu"
              >
                <Menu className="w-6 h-6" />
              </button>
            </Tooltip>

            {/* Page title - hidden on mobile */}
            <div className="hidden lg:block">
              <h1 className="text-lg font-semibold text-gray-900">
                Greg Constructions
              </h1>
            </div>

            {/* Mobile logo */}
            <div className="lg:hidden flex items-center gap-3">
              <picture>
                <source srcSet="/logo.webp?v=2" type="image/webp" />
                <img
                  src="/logo.png?v=2"
                  alt="Hub Chantier"
                  className="w-16 h-16 object-contain aspect-square"
                  loading="eager"
                  decoding="async"
                />
              </picture>
              <span className="text-lg font-bold text-primary-600">Hub Chantier</span>
            </div>

            {/* Right side */}
            <div className="flex items-center gap-2">
              {/* Search Button */}
              <Tooltip content="Rechercher dans l'application (Cmd+K)">
                <button
                  onClick={openCommandPalette}
                  className="hidden sm:flex items-center gap-2 min-h-[44px] px-3 py-2 rounded-lg hover:bg-gray-100 text-gray-600 border border-gray-200"
                  aria-label="Rechercher"
                >
                  <Search className="w-4 h-4" />
                  <span className="text-sm">Rechercher</span>
                  <kbd className="hidden lg:block px-1.5 py-0.5 text-xs font-semibold bg-gray-100 border border-gray-300 rounded">
                    ⌘K
                  </kbd>
                </button>
              </Tooltip>

              {/* Search Icon (mobile only) */}
              <Tooltip content="Rechercher">
                <button
                  onClick={openCommandPalette}
                  className="sm:hidden min-w-[44px] min-h-[44px] flex items-center justify-center rounded-lg hover:bg-gray-100"
                  aria-label="Rechercher"
                >
                  <Search className="w-5 h-5 text-gray-600" />
                </button>
              </Tooltip>

              {/* Help Button */}
              <PageHelp />

              {/* Notifications */}
              <div className="relative">
                <Tooltip content={unreadCount > 0 ? `${unreadCount} notifications non lues` : 'Notifications'}>
                  <button
                    onClick={() => setNotificationsOpen(!notificationsOpen)}
                    className="min-w-[44px] min-h-[44px] flex items-center justify-center rounded-lg hover:bg-gray-100 relative"
                    aria-label={`Notifications${unreadCount > 0 ? ` (${unreadCount} non lues)` : ''}`}
                    aria-expanded={notificationsOpen}
                  >
                    <Bell className="w-5 h-5 text-gray-600" />
                    {unreadCount > 0 && (
                      <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
                    )}
                  </button>
                </Tooltip>

                <NotificationDropdown
                  isOpen={notificationsOpen}
                  onClose={() => setNotificationsOpen(false)}
                />
              </div>

              {/* User menu */}
              <div className="relative">
                <Tooltip content="Profil et paramètres">
                  <button
                    onClick={() => setUserMenuOpen(!userMenuOpen)}
                    className="flex items-center gap-2 min-h-[44px] px-2 rounded-lg hover:bg-gray-100"
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
                    <ChevronDown className="w-4 h-4 text-gray-600 hidden sm:block" />
                  </button>
                </Tooltip>

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
                          <p className="text-xs text-gray-600">{user?.email}</p>
                        </div>
                        {user?.role === 'admin' && (
                          <Link
                            to="/parametres-entreprise"
                            className="flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                            onClick={() => setUserMenuOpen(false)}
                          >
                            <Settings className="w-4 h-4" />
                            Parametres entreprise
                          </Link>
                        )}
                        <Link
                          to="/security"
                          className="flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                          onClick={() => setUserMenuOpen(false)}
                        >
                          <Settings className="w-4 h-4" />
                          Securite
                        </Link>
                        <button
                          onClick={toggleGamification}
                          className="flex items-center gap-2 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                        >
                          <Flame className="w-4 h-4" />
                          <span className="flex-1 text-left">Gamification</span>
                          <div
                            className={`w-10 h-5 rounded-full transition-colors ${
                              gamificationEnabled ? 'bg-green-500' : 'bg-gray-300'
                            }`}
                          >
                            <div
                              className={`w-4 h-4 bg-white rounded-full shadow-sm transition-transform ${
                                gamificationEnabled ? 'translate-x-5' : 'translate-x-0.5'
                              } mt-0.5`}
                            />
                          </div>
                        </button>
                        <button
                          onClick={() => {
                            setUserMenuOpen(false)
                            startTour()
                          }}
                          className="flex items-center gap-2 w-full px-4 py-2 text-sm text-primary-600 hover:bg-primary-50"
                        >
                          <HelpCircle className="w-4 h-4" />
                          Guide de demarrage
                        </button>
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
        <main id="main-content" className="p-4 sm:p-6 lg:p-8">{children}</main>
      </div>

      {/* Floating Action Button (mobile uniquement) */}
      {user && <FloatingActionButton />}
    </div>
  )
}

export default function Layout({ children }: LayoutProps) {
  return (
    <OnboardingProvider>
      <LayoutContent>{children}</LayoutContent>
    </OnboardingProvider>
  )
}
