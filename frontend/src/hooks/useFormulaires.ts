/**
 * useFormulaires - Hook composé pour la gestion des formulaires et templates
 *
 * Ce hook est maintenant refactorisé en 3 sous-hooks :
 * - useFormulairesData : Gestion données et CRUD
 * - useFormulairesUI : Gestion modals, tabs, selections
 * - useFormulairesFilters : Gestion filtres et recherche
 *
 * Garde la même interface pour compatibilité avec FormulairesPage
 */

import { useEffect, useCallback } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { useFormulairesData } from './useFormulairesData'
import { useFormulairesUI, type FormulairesTabType } from './useFormulairesUI'
import { useFormulairesFilters } from './useFormulairesFilters'
import type {
  TemplateFormulaire,
  TemplateFormulaireCreate,
  TemplateFormulaireUpdate,
  FormulaireRempli,
  FormulaireUpdate,
  CategorieFormulaire,
  Chantier,
} from '../types'

// Import type unifié depuis useFormulairesUI
type TabType = FormulairesTabType

// Interface publique exportée pour réutilisation
export interface UseFormulairesReturn {
  // State
  activeTab: TabType
  loading: boolean
  error: string

  // Data
  templates: TemplateFormulaire[]
  formulaires: FormulaireRempli[]
  chantiers: Chantier[]
  filteredTemplates: TemplateFormulaire[]

  // Filters
  searchQuery: string
  filterCategorie: CategorieFormulaire | ''
  setSearchQuery: (query: string) => void
  setFilterCategorie: (categorie: CategorieFormulaire | '') => void

  // Selection
  selectedChantierId: string | null
  setSelectedChantierId: (id: string | null) => void
  selectedTemplate: TemplateFormulaire | null
  selectedFormulaire: FormulaireRempli | null

  // Permissions
  canManageTemplates: boolean

  // Modal states
  templateModalOpen: boolean
  formulaireModalOpen: boolean
  newFormulaireModalOpen: boolean
  formulaireReadOnly: boolean

  // Tab actions
  handleTabChange: (tab: TabType) => void

  // Template actions
  openNewTemplateModal: () => void
  closeTemplateModal: () => void
  handleSaveTemplate: (data: TemplateFormulaireCreate | TemplateFormulaireUpdate) => Promise<void>
  handleEditTemplate: (template: TemplateFormulaire) => void
  handleDeleteTemplate: (template: TemplateFormulaire) => Promise<void>
  handleDuplicateTemplate: (template: TemplateFormulaire) => Promise<void>
  handleToggleTemplateActive: (template: TemplateFormulaire) => Promise<void>
  handlePreviewTemplate: (template: TemplateFormulaire) => void

  // Formulaire actions
  openNewFormulaireModal: () => void
  closeNewFormulaireModal: () => void
  closeFormulaireModal: () => void
  handleCreateFormulaire: (templateId: number) => Promise<void>
  handleViewFormulaire: (formulaire: FormulaireRempli) => Promise<void>
  handleEditFormulaire: (formulaire: FormulaireRempli) => Promise<void>
  handleSaveFormulaire: (data: FormulaireUpdate) => Promise<void>
  handleSubmitFormulaire: (signatureUrl?: string, signatureNom?: string) => Promise<void>
  handleValidateFormulaire: (formulaire: FormulaireRempli) => Promise<void>
  handleRejectFormulaire: (formulaire: FormulaireRempli) => Promise<void>
  handleExportPDF: (formulaire: FormulaireRempli) => Promise<void>

  // Reload
  loadData: () => Promise<void>
}

export function useFormulaires(): UseFormulairesReturn {
  const { user: currentUser } = useAuth()

  // Compose sub-hooks
  const data = useFormulairesData()
  const ui = useFormulairesUI()
  const filters = useFormulairesFilters()

  // Permissions
  const canManageTemplates = currentUser?.role === 'admin' || currentUser?.role === 'conducteur'

  // Initial load with filters
  useEffect(() => {
    data.loadData({
      activeTab: ui.activeTab,
      searchQuery: filters.searchQuery,
      filterCategorie: filters.filterCategorie,
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data.loadData, ui.activeTab, filters.searchQuery, filters.filterCategorie])

  // Reload with current filters
  const loadData = useCallback(async () => {
    await data.loadData({
      activeTab: ui.activeTab,
      searchQuery: filters.searchQuery,
      filterCategorie: filters.filterCategorie,
    })
  }, [data.loadData, ui.activeTab, filters.searchQuery, filters.filterCategorie])

  // ===== TEMPLATE ACTIONS =====

  const handleSaveTemplate = useCallback(async (
    templateData: TemplateFormulaireCreate | TemplateFormulaireUpdate
  ) => {
    if (ui.selectedTemplate) {
      await data.updateTemplate(ui.selectedTemplate.id, templateData)
    } else {
      await data.createTemplate(templateData as TemplateFormulaireCreate)
    }
    ui.closeTemplateModal()
  }, [ui, data])

  const handleEditTemplate = useCallback((template: TemplateFormulaire) => {
    ui.openEditTemplateModal(template)
  }, [ui])

  const handleDeleteTemplate = useCallback(async (template: TemplateFormulaire) => {
    if (!confirm(`Supprimer le template "${template.nom}" ?`)) return

    try {
      await data.deleteTemplate(template.id)
    } catch (err) {
      data.setError('Erreur lors de la suppression')
    }
  }, [data])

  const handleDuplicateTemplate = useCallback(async (template: TemplateFormulaire) => {
    try {
      await data.duplicateTemplate(template)
    } catch (err) {
      data.setError('Erreur lors de la duplication')
    }
  }, [data])

  const handleToggleTemplateActive = useCallback(async (template: TemplateFormulaire) => {
    try {
      await data.toggleTemplateActive(template.id, template.is_active)
    } catch (err) {
      data.setError('Erreur lors de la mise à jour')
    }
  }, [data])

  const handlePreviewTemplate = useCallback((template: TemplateFormulaire) => {
    ui.openPreviewTemplateModal(template)
  }, [ui])

  // ===== FORMULAIRE ACTIONS =====

  const handleCreateFormulaire = useCallback(async (templateId: number) => {
    if (!ui.selectedChantierId) {
      data.setError('Veuillez sélectionner un chantier')
      return
    }

    try {
      const formulaire = await data.createFormulaire(
        templateId,
        parseInt(ui.selectedChantierId, 10)
      )
      const template = data.templates.find((t) => t.id === templateId)

      if (template) {
        ui.openCreatedFormulaireModal(formulaire, template)
      }
    } catch (err) {
      data.setError('Erreur lors de la création du formulaire')
    }
  }, [ui, data])

  const handleViewFormulaire = useCallback(async (formulaire: FormulaireRempli) => {
    try {
      const fullFormulaire = await data.getFormulaire(formulaire.id)
      const template = await data.getTemplate(formulaire.template_id)
      ui.openViewFormulaireModal(fullFormulaire, template)
    } catch (err) {
      data.setError('Erreur lors du chargement du formulaire')
    }
  }, [data, ui])

  const handleEditFormulaire = useCallback(async (formulaire: FormulaireRempli) => {
    try {
      const fullFormulaire = await data.getFormulaire(formulaire.id)
      const template = await data.getTemplate(formulaire.template_id)
      ui.openEditFormulaireModal(fullFormulaire, template)
    } catch (err) {
      data.setError('Erreur lors du chargement du formulaire')
    }
  }, [data, ui])

  const handleSaveFormulaire = useCallback(async (formulaireData: FormulaireUpdate) => {
    if (!ui.selectedFormulaire) return

    const updated = await data.updateFormulaire(ui.selectedFormulaire.id, formulaireData)
    ui.setSelectedFormulaire(updated)
  }, [ui, data])

  const handleSubmitFormulaire = useCallback(async (
    signatureUrl?: string,
    signatureNom?: string
  ) => {
    if (!ui.selectedFormulaire) return

    await data.submitFormulaire(ui.selectedFormulaire.id, signatureUrl, signatureNom)
  }, [ui, data])

  const handleValidateFormulaire = useCallback(async (formulaire: FormulaireRempli) => {
    if (!confirm('Valider ce formulaire ?')) return

    try {
      await data.validateFormulaire(formulaire.id)
    } catch (err) {
      data.setError('Erreur lors de la validation')
    }
  }, [data])

  const handleRejectFormulaire = useCallback(async (formulaire: FormulaireRempli) => {
    if (!confirm('Refuser ce formulaire et le renvoyer en brouillon ?')) return

    try {
      await data.rejectFormulaire(formulaire.id)
    } catch (err) {
      data.setError('Erreur lors du refus du formulaire')
    }
  }, [data])

  const handleExportPDF = useCallback(async (formulaire: FormulaireRempli) => {
    try {
      await data.exportPDF(formulaire.id)
    } catch (err) {
      data.setError("Erreur lors de l'export PDF")
    }
  }, [data])

  // Filtered templates (using filter hook)
  const filteredTemplates = filters.filterTemplates(data.templates)

  return {
    // State
    activeTab: ui.activeTab,
    loading: data.loading,
    error: data.error,

    // Data
    templates: data.templates,
    formulaires: data.formulaires,
    chantiers: data.chantiers,
    filteredTemplates,

    // Filters
    searchQuery: filters.searchQuery,
    filterCategorie: filters.filterCategorie,
    setSearchQuery: filters.setSearchQuery,
    setFilterCategorie: filters.setFilterCategorie,

    // Selection
    selectedChantierId: ui.selectedChantierId,
    setSelectedChantierId: ui.setSelectedChantierId,
    selectedTemplate: ui.selectedTemplate,
    selectedFormulaire: ui.selectedFormulaire,

    // Permissions
    canManageTemplates,

    // Modal states
    templateModalOpen: ui.templateModalOpen,
    formulaireModalOpen: ui.formulaireModalOpen,
    newFormulaireModalOpen: ui.newFormulaireModalOpen,
    formulaireReadOnly: ui.formulaireReadOnly,

    // Tab actions
    handleTabChange: ui.handleTabChange,

    // Template actions
    openNewTemplateModal: ui.openNewTemplateModal,
    closeTemplateModal: ui.closeTemplateModal,
    handleSaveTemplate,
    handleEditTemplate,
    handleDeleteTemplate,
    handleDuplicateTemplate,
    handleToggleTemplateActive,
    handlePreviewTemplate,

    // Formulaire actions
    openNewFormulaireModal: ui.openNewFormulaireModal,
    closeNewFormulaireModal: ui.closeNewFormulaireModal,
    closeFormulaireModal: ui.closeFormulaireModal,
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
  }
}

export default useFormulaires
