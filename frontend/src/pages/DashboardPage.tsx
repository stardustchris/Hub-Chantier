import { useAuth } from '../contexts/AuthContext'

export default function DashboardPage() {
  const { user, logout } = useAuth()

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-primary-600">Hub Chantier</h1>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600">
              {user?.prenom} {user?.nom}
            </span>
            <span className="px-2 py-1 bg-primary-100 text-primary-700 text-xs rounded-full">
              {user?.role}
            </span>
            <button
              onClick={logout}
              className="btn btn-outline text-sm"
            >
              Deconnexion
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900">
            Bienvenue, {user?.prenom} !
          </h2>
          <p className="text-gray-600">
            Voici votre tableau de bord Hub Chantier.
          </p>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <QuickActionCard
            title="Pointer"
            description="Enregistrer votre entree ou sortie"
            icon="clock"
            color="primary"
          />
          <QuickActionCard
            title="Planning"
            description="Voir votre planning de la semaine"
            icon="calendar"
            color="secondary"
          />
          <QuickActionCard
            title="Chantiers"
            description="Liste des chantiers actifs"
            icon="building"
            color="primary"
          />
          <QuickActionCard
            title="Documents"
            description="Acceder aux documents"
            icon="folder"
            color="secondary"
          />
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="card">
            <h3 className="font-semibold text-gray-700 mb-4">Cette semaine</h3>
            <div className="text-3xl font-bold text-primary-600">32h</div>
            <p className="text-sm text-gray-500">heures travaillees</p>
          </div>
          <div className="card">
            <h3 className="font-semibold text-gray-700 mb-4">Chantier actuel</h3>
            <div className="text-xl font-bold text-gray-900">Residence Les Pins</div>
            <p className="text-sm text-gray-500">Lyon 3eme</p>
          </div>
          <div className="card">
            <h3 className="font-semibold text-gray-700 mb-4">Prochaine tache</h3>
            <div className="text-lg font-medium text-gray-900">Installation electricite</div>
            <p className="text-sm text-gray-500">Demain 8h00</p>
          </div>
        </div>
      </main>
    </div>
  )
}

interface QuickActionCardProps {
  title: string
  description: string
  icon: string
  color: 'primary' | 'secondary'
}

function QuickActionCard({ title, description, color }: QuickActionCardProps) {
  const bgColor = color === 'primary' ? 'bg-primary-50' : 'bg-secondary-50'
  const textColor = color === 'primary' ? 'text-primary-600' : 'text-secondary-600'

  return (
    <div className={`card cursor-pointer hover:shadow-md transition-shadow ${bgColor}`}>
      <h3 className={`font-semibold ${textColor}`}>{title}</h3>
      <p className="text-sm text-gray-600 mt-1">{description}</p>
    </div>
  )
}
