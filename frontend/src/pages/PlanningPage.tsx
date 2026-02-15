import Layout from '../components/Layout'
import { PlanningGrid, PlanningChantierGrid, WeekNavigation, AffectationModal } from '../components/planning'
import { PlanningToolbar, PlanningFiltersPanel } from '../components/planning/PlanningToolbar'
import { usePlanning } from '../hooks/usePlanning'
import { useDocumentTitle } from '../hooks/useDocumentTitle'

export default function PlanningPage() {
  useDocumentTitle('Planning')
  const planning = usePlanning()

  return (
    <Layout>
      <div className="space-y-4">
        <PlanningToolbar
          canEdit={planning.canEdit}
          viewTab={planning.viewTab}
          onViewTabChange={planning.setViewTab}
          nonPlanifiesCount={planning.nonPlanifiesCount}
          showNonPlanifiesOnly={planning.showNonPlanifiesOnly}
          onToggleNonPlanifies={() => planning.setShowNonPlanifiesOnly(!planning.showNonPlanifiesOnly)}
          filterChantier={planning.filterChantier}
          onFilterChantierChange={planning.setFilterChantier}
          chantiers={planning.chantiers}
          showFilters={planning.showFilters}
          onToggleFilters={() => planning.setShowFilters(!planning.showFilters)}
          filterMetiers={planning.filterMetiers}
          showWeekend={planning.showWeekend}
          onToggleWeekend={planning.setShowWeekend}
          onCreateClick={planning.openCreateModal}
        />

        <PlanningFiltersPanel
          show={planning.showFilters}
          filterMetiers={planning.filterMetiers}
          onToggleMetier={planning.toggleFilterMetier}
          onClear={planning.clearFilterMetiers}
        />

        <WeekNavigation
          currentDate={planning.currentDate}
          onDateChange={planning.setCurrentDate}
          viewMode={planning.viewMode}
          onViewModeChange={planning.setViewMode}
        />

        {planning.error && (
          <div className="bg-red-50 text-red-700 p-4 rounded-lg">
            {planning.error}
          </div>
        )}

        {planning.loading ? (
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <div className="animate-spin w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full mx-auto" />
            <p className="mt-4 text-gray-600">Chargement du planning...</p>
          </div>
        ) : planning.viewTab === 'utilisateurs' ? (
          <PlanningGrid
            currentDate={planning.currentDate}
            affectations={planning.filteredAffectations}
            utilisateurs={planning.filteredUtilisateurs}
            onAffectationClick={planning.handleAffectationClick}
            onAffectationDelete={planning.handleAffectationDelete}
            onCellClick={planning.handleCellClick}
            onDuplicate={planning.handleDuplicate}
            expandedMetiers={planning.expandedMetiers}
            onToggleMetier={planning.handleToggleMetier}
            showWeekend={planning.showWeekend}
            viewMode={planning.viewMode}
            onAffectationMove={planning.canEdit ? planning.handleAffectationMove : undefined}
            onAffectationResize={planning.canEdit ? planning.handleAffectationResize : undefined}
            onAffectationsDelete={planning.canEdit ? planning.handleAffectationsDelete : undefined}
          />
        ) : (
          <PlanningChantierGrid
            currentDate={planning.currentDate}
            affectations={planning.filteredAffectations}
            chantiers={planning.chantiers}
            onAffectationClick={planning.handleAffectationClick}
            onCellClick={planning.handleChantierCellClick}
            onDuplicateChantier={planning.handleDuplicateChantier}
            showWeekend={planning.showWeekend}
            viewMode={planning.viewMode}
            onAffectationMove={planning.canEdit ? planning.handleAffectationMove : undefined}
          />
        )}

        <AffectationModal
          isOpen={planning.modalOpen}
          onClose={planning.closeModal}
          onSave={planning.handleSaveAffectation}
          onDelete={planning.canEdit ? planning.handleAffectationDeleteFromModal : undefined}
          affectation={planning.editingAffectation}
          utilisateurs={planning.utilisateurs}
          chantiers={planning.chantiers}
          selectedDate={planning.selectedDate}
          selectedUserId={planning.selectedUserId}
          selectedChantierId={planning.selectedChantierId}
        />
      </div>
    </Layout>
  )
}
