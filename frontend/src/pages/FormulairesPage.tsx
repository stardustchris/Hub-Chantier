/**
 * FormulairesPage - Page principale du module Formulaires
 * CDC Section 8 (FOR-01 a FOR-11)
 */

import { useState } from 'react'
import {
  Plus,
  FileText,
  Search,
  RefreshCw,
  LayoutGrid,
  List,
  ChevronDown,
} from 'lucide-react'
import Layout from '../components/Layout'
import {
  TemplateList,
  TemplateModal,
  FormulaireList,
  FormulaireModal,
  NewFormulaireModal,
} from '../components/formulaires'
import { useFormulaires } from '../hooks'
import { CATEGORIES_FORMULAIRES } from '../types'
import { useDocumentTitle } from '../hooks/useDocumentTitle'
import type { CategorieFormulaire } from '../types'

type ViewMode = 'grid' | 'list'

export default function FormulairesPage() {
  useDocumentTitle('Formulaires')
  const [viewMode, setViewMode] = useState<ViewMode>('grid')

  const {
    // State
    activeTab,
    loading,
    error,

    // Data
    templates,
    formulaires,
    chantiers,
    filteredTemplates,

    // Filters
    searchQuery,
    filterCategorie,
    setSearchQuery,
    setFilterCategorie,

    // Selection
    selectedChantierId,
    setSelectedChantierId,
    selectedTemplate,
    selectedFormulaire,

    // Permissions
    canManageTemplates,

    // Modal states
    templateModalOpen,
    formulaireModalOpen,
    newFormulaireModalOpen,
    formulaireReadOnly,

    // Tab actions
    handleTabChange,

    // Template actions
    openNewTemplateModal,
    closeTemplateModal,
    handleSaveTemplate,
    handleEditTemplate,
    handleDeleteTemplate,
    handleDuplicateTemplate,
    handleToggleTemplateActive,
    handlePreviewTemplate,

    // Formulaire actions
    openNewFormulaireModal,
    closeNewFormulaireModal,
    closeFormulaireModal,
    handleCreateFormulaire,
    handleViewFormulaire,
    handleEditFormulaire,
    handleSaveFormulaire,
    handleSubmitFormulaire,
    handleValidateFormulaire,
    handleRejectFormulaire,
    handleExportPDF,

    // Reload
    loadData,
  } = useFormulaires()

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Formulaires</h1>
            <p className="text-gray-500 mt-1">
              Gerez vos templates et formulaires terrain
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => loadData()}
              className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              title="Actualiser"
            >
              <RefreshCw className="w-5 h-5" />
            </button>
            {activeTab === 'templates' && canManageTemplates && (
              <button
                onClick={openNewTemplateModal}
                className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
              >
                <Plus className="w-5 h-5" />
                Nouveau template
              </button>
            )}
            {activeTab === 'formulaires' && (
              <button
                onClick={openNewFormulaireModal}
                className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
              >
                <Plus className="w-5 h-5" />
                Nouveau formulaire
              </button>
            )}
          </div>
        </div>

        {/* Tabs */}
        <div className="flex items-center gap-1 bg-gray-100 p-1 rounded-lg w-fit">
          <button
            onClick={() => handleTabChange('formulaires')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'formulaires'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <FileText className="w-4 h-4 inline-block mr-2" />
            Formulaires
          </button>
          {canManageTemplates && (
            <button
              onClick={() => handleTabChange('templates')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'templates'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <LayoutGrid className="w-4 h-4 inline-block mr-2" />
              Templates
            </button>
          )}
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative flex-1 min-w-[200px] max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-600" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Rechercher..."
              className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>

          <div className="relative">
            <select
              value={filterCategorie}
              onChange={(e) => setFilterCategorie(e.target.value as CategorieFormulaire | '')}
              className="appearance-none pl-3 pr-10 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="">Toutes categories</option>
              {Object.entries(CATEGORIES_FORMULAIRES).map(([key, value]) => (
                <option key={key} value={key}>
                  {value.label}
                </option>
              ))}
            </select>
            <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-600 pointer-events-none" />
          </div>

          {activeTab === 'templates' && (
            <div className="flex items-center gap-1 bg-gray-100 p-1 rounded-lg">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 rounded ${viewMode === 'grid' ? 'bg-white shadow-sm' : ''}`}
              >
                <LayoutGrid className="w-4 h-4" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 rounded ${viewMode === 'list' ? 'bg-white shadow-sm' : ''}`}
              >
                <List className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>

        {/* Error */}
        {error && (
          <div role="alert" className="p-4 bg-red-50 text-red-700 rounded-lg">
            {error}
          </div>
        )}

        {/* Content */}
        {activeTab === 'templates' ? (
          <TemplateList
            templates={filteredTemplates}
            onEdit={handleEditTemplate}
            onDelete={handleDeleteTemplate}
            onDuplicate={handleDuplicateTemplate}
            onToggleActive={handleToggleTemplateActive}
            onPreview={handlePreviewTemplate}
            loading={loading}
          />
        ) : (
          <FormulaireList
            formulaires={formulaires}
            onView={handleViewFormulaire}
            onEdit={handleEditFormulaire}
            onExportPDF={handleExportPDF}
            onValidate={canManageTemplates ? handleValidateFormulaire : undefined}
            onReject={canManageTemplates ? handleRejectFormulaire : undefined}
            loading={loading}
          />
        )}

        {/* Template Modal */}
        <TemplateModal
          isOpen={templateModalOpen}
          onClose={closeTemplateModal}
          onSave={handleSaveTemplate}
          template={selectedTemplate}
        />

        {/* Formulaire Modal */}
        <FormulaireModal
          isOpen={formulaireModalOpen}
          onClose={closeFormulaireModal}
          onSave={handleSaveFormulaire}
          onSubmit={handleSubmitFormulaire}
          formulaire={selectedFormulaire}
          template={selectedTemplate}
          readOnly={formulaireReadOnly}
        />

        {/* New Formulaire Selection Modal */}
        <NewFormulaireModal
          isOpen={newFormulaireModalOpen}
          onClose={closeNewFormulaireModal}
          onCreateFormulaire={handleCreateFormulaire}
          templates={templates}
          chantiers={chantiers}
          selectedChantierId={selectedChantierId}
          onChantierChange={setSelectedChantierId}
        />

      </div>
    </Layout>
  )
}
