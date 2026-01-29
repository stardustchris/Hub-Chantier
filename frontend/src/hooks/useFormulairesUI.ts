/**
 * useFormulairesUI - Hook pour la gestion UI formulaires
 *
 * Responsabilités :
 * - Gestion des onglets (templates / formulaires)
 * - Gestion des modals (ouverture/fermeture)
 * - Gestion des sélections (template, formulaire)
 * - États read-only
 */

import { useState, useCallback, useEffect } from 'react'
import { useSearchParams} from 'react-router-dom'
import type { TemplateFormulaire, FormulaireRempli } from '../types'

// Type exporté pour réutilisation dans d'autres hooks/composants
export type FormulairesTabType = 'templates' | 'formulaires'
// Alias pour compatibilité
export type TabType = FormulairesTabType

export interface UseFormulairesUIReturn {
  // Tab state
  activeTab: TabType
  handleTabChange: (tab: TabType) => void

  // Selection state
  selectedTemplate: TemplateFormulaire | null
  selectedFormulaire: FormulaireRempli | null
  selectedChantierId: string | null
  setSelectedTemplate: (template: TemplateFormulaire | null) => void
  setSelectedFormulaire: (formulaire: FormulaireRempli | null) => void
  setSelectedChantierId: (id: string | null) => void

  // Modal states
  templateModalOpen: boolean
  formulaireModalOpen: boolean
  newFormulaireModalOpen: boolean
  formulaireReadOnly: boolean

  // Template modal actions
  openNewTemplateModal: () => void
  openEditTemplateModal: (template: TemplateFormulaire) => void
  openPreviewTemplateModal: (template: TemplateFormulaire) => void
  closeTemplateModal: () => void

  // Formulaire modal actions
  openNewFormulaireModal: () => void
  openViewFormulaireModal: (formulaire: FormulaireRempli, template: TemplateFormulaire) => void
  openEditFormulaireModal: (formulaire: FormulaireRempli, template: TemplateFormulaire) => void
  openCreatedFormulaireModal: (
    formulaire: FormulaireRempli,
    template: TemplateFormulaire
  ) => void
  closeNewFormulaireModal: () => void
  closeFormulaireModal: () => void
}

export function useFormulairesUI(): UseFormulairesUIReturn {
  const [searchParams, setSearchParams] = useSearchParams()

  // Tab state - lire depuis l'URL au démarrage
  const getInitialTab = (): TabType => {
    const tab = searchParams.get('tab')
    return (tab === 'templates' || tab === 'formulaires') ? tab : 'formulaires'
  }
  const [activeTab, setActiveTab] = useState<TabType>(getInitialTab())

  // Selection state
  const [selectedTemplate, setSelectedTemplate] = useState<TemplateFormulaire | null>(null)
  const [selectedFormulaire, setSelectedFormulaire] = useState<FormulaireRempli | null>(null)
  const [selectedChantierId, setSelectedChantierId] = useState<string | null>(null)

  // Modal states
  const [templateModalOpen, setTemplateModalOpen] = useState(false)
  const [formulaireModalOpen, setFormulaireModalOpen] = useState(false)
  const [newFormulaireModalOpen, setNewFormulaireModalOpen] = useState(false)
  const [formulaireReadOnly, setFormulaireReadOnly] = useState(false)

  // Sync tab with URL params
  useEffect(() => {
    const tab = searchParams.get('tab')
    if (tab === 'templates' || tab === 'formulaires') {
      setActiveTab(tab)
    }
  }, [searchParams])

  // Tab change handler
  const handleTabChange = useCallback((tab: TabType) => {
    setActiveTab(tab)
    setSearchParams({ tab })
  }, [setSearchParams])

  // ===== TEMPLATE MODAL ACTIONS =====

  const openNewTemplateModal = useCallback(() => {
    setSelectedTemplate(null)
    setTemplateModalOpen(true)
  }, [])

  const openEditTemplateModal = useCallback((template: TemplateFormulaire) => {
    setSelectedTemplate(template)
    setTemplateModalOpen(true)
  }, [])

  const openPreviewTemplateModal = useCallback((template: TemplateFormulaire) => {
    setSelectedTemplate(template)
    setSelectedFormulaire(null)
    setFormulaireReadOnly(true)
    setFormulaireModalOpen(true)
  }, [])

  const closeTemplateModal = useCallback(() => {
    setTemplateModalOpen(false)
    setSelectedTemplate(null)
  }, [])

  // ===== FORMULAIRE MODAL ACTIONS =====

  const openNewFormulaireModal = useCallback(() => {
    setNewFormulaireModalOpen(true)
  }, [])

  const openViewFormulaireModal = useCallback((
    formulaire: FormulaireRempli,
    template: TemplateFormulaire
  ) => {
    setSelectedTemplate(template)
    setSelectedFormulaire(formulaire)
    setFormulaireReadOnly(true)
    setFormulaireModalOpen(true)
  }, [])

  const openEditFormulaireModal = useCallback((
    formulaire: FormulaireRempli,
    template: TemplateFormulaire
  ) => {
    setSelectedTemplate(template)
    setSelectedFormulaire(formulaire)
    setFormulaireReadOnly(false)
    setFormulaireModalOpen(true)
  }, [])

  const openCreatedFormulaireModal = useCallback((
    formulaire: FormulaireRempli,
    template: TemplateFormulaire
  ) => {
    setSelectedTemplate(template)
    setSelectedFormulaire(formulaire)
    setFormulaireReadOnly(false)
    setFormulaireModalOpen(true)
    setNewFormulaireModalOpen(false)
  }, [])

  const closeNewFormulaireModal = useCallback(() => {
    setNewFormulaireModalOpen(false)
  }, [])

  const closeFormulaireModal = useCallback(() => {
    setFormulaireModalOpen(false)
    setSelectedFormulaire(null)
    setSelectedTemplate(null)
  }, [])

  return {
    // Tab state
    activeTab,
    handleTabChange,

    // Selection state
    selectedTemplate,
    selectedFormulaire,
    selectedChantierId,
    setSelectedTemplate,
    setSelectedFormulaire,
    setSelectedChantierId,

    // Modal states
    templateModalOpen,
    formulaireModalOpen,
    newFormulaireModalOpen,
    formulaireReadOnly,

    // Template modal actions
    openNewTemplateModal,
    openEditTemplateModal,
    openPreviewTemplateModal,
    closeTemplateModal,

    // Formulaire modal actions
    openNewFormulaireModal,
    openViewFormulaireModal,
    openEditFormulaireModal,
    openCreatedFormulaireModal,
    closeNewFormulaireModal,
    closeFormulaireModal,
  }
}
