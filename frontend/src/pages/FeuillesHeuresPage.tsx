import { useState } from 'react'
import { Filter, Users, Building2, Settings } from 'lucide-react'
import Layout from '../components/Layout'
import { TimesheetWeekNavigation, TimesheetGrid, TimesheetChantierGrid, PointageModal, PayrollMacrosConfig } from '../components/pointages'
import type { PayrollConfig } from '../components/pointages'
import { useFeuillesHeures } from '../hooks/useFeuillesHeures'
import { useAuth } from '../contexts/AuthContext'

export default function FeuillesHeuresPage() {
  const fh = useFeuillesHeures()
  const { user } = useAuth()
  const [showMacrosConfig, setShowMacrosConfig] = useState(false)
  const [payrollConfig, setPayrollConfig] = useState<PayrollConfig | undefined>()

  const handleSaveMacros = (config: PayrollConfig) => {
    setPayrollConfig(config)
    // TODO: Persist to backend when API is ready
  }

  const isAdmin = user?.role === 'admin'

  return (
    <Layout>
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Feuilles d'heures</h1>
            <p className="text-gray-600">Saisie et validation des heures travaillees</p>
          </div>
        </div>

        {/* Onglets de vue */}
        <div className="flex items-center gap-4">
          <div className="flex rounded-lg bg-gray-100 p-1">
            <button
              onClick={() => fh.setViewTab('compagnons')}
              className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                fh.viewTab === 'compagnons' ? 'bg-white text-gray-900 shadow' : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Users className="w-4 h-4" />
              Compagnons
            </button>
            <button
              onClick={() => fh.setViewTab('chantiers')}
              className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                fh.viewTab === 'chantiers' ? 'bg-white text-gray-900 shadow' : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Building2 className="w-4 h-4" />
              Chantiers
            </button>
          </div>

          {/* Bouton filtres */}
          <button
            onClick={() => fh.setShowFilters(!fh.showFilters)}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
              fh.showFilters || fh.filterUtilisateurs.length > 0 || fh.filterChantiers.length > 0
                ? 'bg-primary-100 text-primary-700'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            <Filter className="w-4 h-4" />
            Filtres
            {(fh.filterUtilisateurs.length > 0 || fh.filterChantiers.length > 0) && (
              <span className="bg-primary-600 text-white text-xs px-1.5 py-0.5 rounded-full">
                {fh.filterUtilisateurs.length + fh.filterChantiers.length}
              </span>
            )}
          </button>

          {/* Toggle weekend */}
          <label className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm bg-gray-100 cursor-pointer hover:bg-gray-200 transition-colors">
            <input
              type="checkbox"
              checked={fh.showWeekend}
              onChange={(e) => fh.setShowWeekend(e.target.checked)}
              className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
            <span className="text-gray-700">Weekend</span>
          </label>

          {/* Bouton Variables de paie - visible uniquement sur l'onglet Compagnons */}
          {isAdmin && fh.viewTab === 'compagnons' && (
            <button
              onClick={() => setShowMacrosConfig(true)}
              className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium bg-gray-100 text-gray-700 hover:bg-gray-200 transition-colors"
              aria-label="Configurer les variables de paie"
            >
              <Settings className="w-4 h-4" />
              Variables de paie
            </button>
          )}
        </div>

        {/* Filtres dépliables */}
        {fh.showFilters && (
          <div className="bg-white rounded-lg shadow p-4 space-y-4">
            <div>
              <span className="text-sm font-medium text-gray-700 mr-2">Utilisateurs :</span>
              {(['admin', 'conducteur', 'chef_chantier', 'compagnon'] as const).map((role) => {
                const usersForRole = fh.utilisateurs.filter((u) => u.role === role)
                if (usersForRole.length === 0) return null
                const roleLabels: Record<string, string> = {
                  admin: 'Direction',
                  conducteur: 'Conducteurs de travaux',
                  chef_chantier: 'Chefs de chantier',
                  compagnon: 'Compagnons',
                }
                return (
                  <div key={role} className="mt-2">
                    <span className="text-xs text-gray-500 font-medium">{roleLabels[role]}</span>
                    <div className="flex flex-wrap gap-2 mt-1">
                      {usersForRole.map((user) => (
                        <button
                          key={user.id}
                          onClick={() => fh.handleFilterUtilisateur(Number(user.id))}
                          className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                            fh.filterUtilisateurs.includes(Number(user.id))
                              ? 'bg-primary-600 text-white'
                              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                          }`}
                        >
                          {user.prenom} {user.nom}
                        </button>
                      ))}
                    </div>
                  </div>
                )
              })}
              {fh.filterUtilisateurs.length > 0 && (
                <button onClick={fh.clearFilterUtilisateurs} className="text-xs text-gray-500 hover:text-gray-700 mt-2">
                  Effacer
                </button>
              )}
            </div>

            <div>
              <span className="text-sm font-medium text-gray-700 mr-2">Chantiers :</span>
              <div className="flex flex-wrap gap-2 mt-2">
                {fh.chantiers.map((chantier) => (
                  <button
                    key={chantier.id}
                    onClick={() => fh.handleFilterChantier(Number(chantier.id))}
                    className={`flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                      fh.filterChantiers.includes(Number(chantier.id))
                        ? 'text-white'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                    style={
                      fh.filterChantiers.includes(Number(chantier.id))
                        ? { backgroundColor: chantier.couleur || '#3498DB' }
                        : undefined
                    }
                  >
                    <span className="w-2 h-2 rounded-full" style={{ backgroundColor: chantier.couleur || '#9E9E9E' }} />
                    {chantier.nom}
                  </button>
                ))}
                {fh.filterChantiers.length > 0 && (
                  <button onClick={fh.clearFilterChantiers} className="text-xs text-gray-500 hover:text-gray-700 ml-2">
                    Effacer
                  </button>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Navigation semaine */}
        <TimesheetWeekNavigation
          currentDate={fh.currentDate}
          onDateChange={fh.setCurrentDate}
          onExport={fh.handleExport}
          isExporting={fh.isExporting}
        />

        {/* Erreur */}
        {fh.error && <div className="bg-red-50 text-red-700 p-4 rounded-lg">{fh.error}</div>}

        {/* Grille */}
        {fh.loading ? (
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <div className="animate-spin w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full mx-auto" />
            <p className="mt-4 text-gray-600">Chargement des feuilles d'heures...</p>
          </div>
        ) : fh.viewTab === 'compagnons' ? (
          <TimesheetGrid
            currentDate={fh.currentDate}
            vueCompagnons={fh.vueCompagnons}
            onCellClick={fh.handleCellClick}
            onPointageClick={fh.handlePointageClick}
            showWeekend={fh.showWeekend}
            canEdit={fh.canEdit}
          />
        ) : (
          <TimesheetChantierGrid
            currentDate={fh.currentDate}
            vueChantiers={fh.vueChantiers}
            heuresPrevuesParChantier={fh.heuresPrevuesParChantier}
            onCellClick={fh.handleChantierCellClick}
            onPointageClick={fh.handlePointageClick}
            showWeekend={fh.showWeekend}
            canEdit={fh.canEdit}
          />
        )}

        {/* Modal Pointage */}
        <PointageModal
          isOpen={fh.modalOpen}
          onClose={fh.closeModal}
          onSave={fh.handleSavePointage}
          onDelete={fh.editingPointage ? fh.handleDeletePointage : undefined}
          onSign={fh.editingPointage ? fh.handleSignPointage : undefined}
          onSubmit={fh.editingPointage ? fh.handleSubmitPointage : undefined}
          onValidate={fh.isValidateur && fh.editingPointage ? fh.handleValidatePointage : undefined}
          onReject={fh.isValidateur && fh.editingPointage ? fh.handleRejectPointage : undefined}
          pointage={fh.editingPointage}
          chantiers={fh.chantiers}
          selectedDate={fh.selectedDate}
          selectedUserId={fh.selectedUserId}
          selectedChantierId={fh.selectedChantierId}
          isValidateur={fh.isValidateur}
        />

        {/* Modal Variables de paie */}
        <PayrollMacrosConfig
          isOpen={showMacrosConfig}
          onClose={() => setShowMacrosConfig(false)}
          config={payrollConfig}
          onSave={handleSaveMacros}
        />
      </div>
    </Layout>
  )
}
