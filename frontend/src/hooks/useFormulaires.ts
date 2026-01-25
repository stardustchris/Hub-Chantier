/**
 * useFormulaires - Hook pour la gestion des formulaires et templates
 *
 * Extrait la logique metier de FormulairesPage:
 * - Gestion des templates (CRUD)
 * - Gestion des formulaires (CRUD, soumission, validation)
 * - Consentement geolocalisation RGPD
 */

import { useState, useEffect, useCallback } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { formulairesService } from '../services/formulaires'
import { chantiersService } from '../services/chantiers'
import { consentService } from '../services/consent'
import { logger } from '../services/logger'
import type {
  TemplateFormulaire,
  TemplateFormulaireCreate,
  TemplateFormulaireUpdate,
  FormulaireRempli,
  FormulaireUpdate,
  CategorieFormulaire,
  Chantier,
} from '../types'

type TabType = 'templates' | 'formulaires'

interface UseFormulairesReturn {
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
  geoConsentModalOpen: boolean
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
  handleExportPDF: (formulaire: FormulaireRempli) => Promise<void>

  // Geolocation consent actions
  handleGeoConsentAccept: () => Promise<void>
  handleGeoConsentDecline: () => Promise<void>
  handleGeoConsentClose: () => void

  // Reload
  loadData: () => Promise<void>
}

// Default mock data
const MOCK_TEMPLATES: TemplateFormulaire[] = []
const MOCK_FORMULAIRES: FormulaireRempli[] = []
const MOCK_CHANTIERS: Chantier[] = []

export function useFormulaires(): UseFormulairesReturn {
  const { user: currentUser } = useAuth()
  const [searchParams, setSearchParams] = useSearchParams()

  // Main state
  const [activeTab, setActiveTab] = useState<TabType>('formulaires')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // Data
  const [templates, setTemplates] = useState<TemplateFormulaire[]>([])
  const [formulaires, setFormulaires] = useState<FormulaireRempli[]>([])
  const [chantiers, setChantiers] = useState<Chantier[]>([])
  const [selectedChantierId, setSelectedChantierId] = useState<string | null>(null)

  // Filters
  const [searchQuery, setSearchQuery] = useState('')
  const [filterCategorie, setFilterCategorie] = useState<CategorieFormulaire | ''>('')
  const [filterChantierId] = useState<number | null>(null)

  // Modals
  const [templateModalOpen, setTemplateModalOpen] = useState(false)
  const [formulaireModalOpen, setFormulaireModalOpen] = useState(false)
  const [newFormulaireModalOpen, setNewFormulaireModalOpen] = useState(false)
  const [selectedTemplate, setSelectedTemplate] = useState<TemplateFormulaire | null>(null)
  const [selectedFormulaire, setSelectedFormulaire] = useState<FormulaireRempli | null>(null)
  const [formulaireReadOnly, setFormulaireReadOnly] = useState(false)

  // Geolocation consent RGPD
  const [geoConsentModalOpen, setGeoConsentModalOpen] = useState(false)
  const [pendingTemplateId, setPendingTemplateId] = useState<number | null>(null)

  // Permissions
  const canManageTemplates = currentUser?.role === 'admin' || currentUser?.role === 'conducteur'

  // Load data
  const loadData = useCallback(async () => {
    setLoading(true)
    setError('')

    try {
      // Load templates
      const templatesResponse = await formulairesService.listTemplates({
        query: activeTab === 'templates' ? searchQuery : undefined,
        categorie: filterCategorie || undefined,
        active_only: activeTab === 'formulaires',
      })
      const loadedTemplates = templatesResponse?.templates || []
      setTemplates(loadedTemplates.length > 0 ? loadedTemplates : MOCK_TEMPLATES)

      // Load formulaires
      const formulairesResponse = await formulairesService.listFormulaires({
        chantier_id: filterChantierId || undefined,
        template_id: undefined,
      })
      const loadedFormulaires = formulairesResponse?.formulaires || []
      setFormulaires(loadedFormulaires.length > 0 ? loadedFormulaires : MOCK_FORMULAIRES)

      // Load chantiers
      const chantiersResponse = await chantiersService.list({ size: 100 })
      const loadedChantiers = chantiersResponse?.items || []
      setChantiers(loadedChantiers.length > 0 ? loadedChantiers : MOCK_CHANTIERS)
    } catch (err) {
      logger.error('Error loading data, using mocks', err, { context: 'useFormulaires' })
      setTemplates(MOCK_TEMPLATES)
      setFormulaires(MOCK_FORMULAIRES)
      setChantiers(MOCK_CHANTIERS)
    } finally {
      setLoading(false)
    }
  }, [activeTab, searchQuery, filterCategorie, filterChantierId])

  // Initial load
  useEffect(() => {
    loadData()
  }, [loadData])

  // URL management
  useEffect(() => {
    const tab = searchParams.get('tab')
    if (tab === 'templates' || tab === 'formulaires') {
      setActiveTab(tab)
    }
  }, [searchParams])

  const handleTabChange = useCallback((tab: TabType) => {
    setActiveTab(tab)
    setSearchParams({ tab })
  }, [setSearchParams])

  // ===== TEMPLATES =====

  const openNewTemplateModal = useCallback(() => {
    setSelectedTemplate(null)
    setTemplateModalOpen(true)
  }, [])

  const closeTemplateModal = useCallback(() => {
    setTemplateModalOpen(false)
    setSelectedTemplate(null)
  }, [])

  const handleSaveTemplate = useCallback(async (data: TemplateFormulaireCreate | TemplateFormulaireUpdate) => {
    if (selectedTemplate) {
      await formulairesService.updateTemplate(selectedTemplate.id, data)
    } else {
      await formulairesService.createTemplate(data as TemplateFormulaireCreate)
    }
    await loadData()
    setTemplateModalOpen(false)
    setSelectedTemplate(null)
  }, [selectedTemplate, loadData])

  const handleEditTemplate = useCallback((template: TemplateFormulaire) => {
    setSelectedTemplate(template)
    setTemplateModalOpen(true)
  }, [])

  const handleDeleteTemplate = useCallback(async (template: TemplateFormulaire) => {
    if (!confirm(`Supprimer le template "${template.nom}" ?`)) return

    try {
      await formulairesService.deleteTemplate(template.id)
      await loadData()
    } catch (err) {
      setError('Erreur lors de la suppression')
    }
  }, [loadData])

  const handleDuplicateTemplate = useCallback(async (template: TemplateFormulaire) => {
    try {
      await formulairesService.createTemplate({
        nom: `${template.nom} (copie)`,
        categorie: template.categorie,
        description: template.description,
        champs: template.champs,
      })
      await loadData()
    } catch (err) {
      setError('Erreur lors de la duplication')
    }
  }, [loadData])

  const handleToggleTemplateActive = useCallback(async (template: TemplateFormulaire) => {
    try {
      await formulairesService.updateTemplate(template.id, {
        is_active: !template.is_active,
      })
      await loadData()
    } catch (err) {
      setError('Erreur lors de la mise a jour')
    }
  }, [loadData])

  const handlePreviewTemplate = useCallback((template: TemplateFormulaire) => {
    setSelectedTemplate(template)
    setSelectedFormulaire(null)
    setFormulaireReadOnly(true)
    setFormulaireModalOpen(true)
  }, [])

  // ===== FORMULAIRES =====

  const openNewFormulaireModal = useCallback(() => {
    setNewFormulaireModalOpen(true)
  }, [])

  const closeNewFormulaireModal = useCallback(() => {
    setNewFormulaireModalOpen(false)
  }, [])

  const closeFormulaireModal = useCallback(() => {
    setFormulaireModalOpen(false)
    setSelectedFormulaire(null)
    setSelectedTemplate(null)
  }, [])

  // Finalize formulaire creation with or without geolocation
  const finalizeCreateFormulaire = useCallback(async (templateId: number, withGeolocation: boolean) => {
    try {
      let latitude: number | undefined
      let longitude: number | undefined

      if (withGeolocation && navigator.geolocation) {
        try {
          const position = await new Promise<GeolocationPosition>((resolve, reject) => {
            navigator.geolocation.getCurrentPosition(resolve, reject, { timeout: 5000 })
          })
          latitude = position.coords.latitude
          longitude = position.coords.longitude
        } catch {
          // Geolocation not available or refused
        }
      }

      const formulaire = await formulairesService.createFormulaire({
        template_id: templateId,
        chantier_id: parseInt(selectedChantierId!, 10),
        latitude,
        longitude,
      })

      const template = templates.find((t) => t.id === templateId)
      setSelectedTemplate(template || null)
      setSelectedFormulaire(formulaire)
      setFormulaireReadOnly(false)
      setFormulaireModalOpen(true)
      setNewFormulaireModalOpen(false)
      await loadData()
    } catch (err) {
      setError('Erreur lors de la creation du formulaire')
    }
  }, [selectedChantierId, templates, loadData])

  // Handle create formulaire with RGPD consent check
  const handleCreateFormulaire = useCallback(async (templateId: number) => {
    if (!selectedChantierId) {
      setError('Veuillez selectionner un chantier')
      return
    }

    if (!consentService.wasAsked('geolocation')) {
      setPendingTemplateId(templateId)
      setGeoConsentModalOpen(true)
      return
    }

    const hasConsent = consentService.hasConsent('geolocation')
    await finalizeCreateFormulaire(templateId, hasConsent)
  }, [selectedChantierId, finalizeCreateFormulaire])

  // Geolocation consent handlers
  const handleGeoConsentAccept = useCallback(async () => {
    consentService.setConsent('geolocation', true)
    setGeoConsentModalOpen(false)
    if (pendingTemplateId !== null) {
      await finalizeCreateFormulaire(pendingTemplateId, true)
      setPendingTemplateId(null)
    }
  }, [pendingTemplateId, finalizeCreateFormulaire])

  const handleGeoConsentDecline = useCallback(async () => {
    consentService.setConsent('geolocation', false)
    setGeoConsentModalOpen(false)
    if (pendingTemplateId !== null) {
      await finalizeCreateFormulaire(pendingTemplateId, false)
      setPendingTemplateId(null)
    }
  }, [pendingTemplateId, finalizeCreateFormulaire])

  const handleGeoConsentClose = useCallback(() => {
    setGeoConsentModalOpen(false)
    setPendingTemplateId(null)
  }, [])

  // View formulaire
  const handleViewFormulaire = useCallback(async (formulaire: FormulaireRempli) => {
    try {
      const fullFormulaire = await formulairesService.getFormulaire(formulaire.id)
      const template = await formulairesService.getTemplate(formulaire.template_id)
      setSelectedTemplate(template)
      setSelectedFormulaire(fullFormulaire)
      setFormulaireReadOnly(true)
      setFormulaireModalOpen(true)
    } catch (err) {
      setError('Erreur lors du chargement du formulaire')
    }
  }, [])

  // Edit formulaire
  const handleEditFormulaire = useCallback(async (formulaire: FormulaireRempli) => {
    try {
      const fullFormulaire = await formulairesService.getFormulaire(formulaire.id)
      const template = await formulairesService.getTemplate(formulaire.template_id)
      setSelectedTemplate(template)
      setSelectedFormulaire(fullFormulaire)
      setFormulaireReadOnly(false)
      setFormulaireModalOpen(true)
    } catch (err) {
      setError('Erreur lors du chargement du formulaire')
    }
  }, [])

  // Save formulaire
  const handleSaveFormulaire = useCallback(async (data: FormulaireUpdate) => {
    if (!selectedFormulaire) return

    const updated = await formulairesService.updateFormulaire(selectedFormulaire.id, data)
    setSelectedFormulaire(updated)
    await loadData()
  }, [selectedFormulaire, loadData])

  // Submit formulaire
  const handleSubmitFormulaire = useCallback(async (signatureUrl?: string, signatureNom?: string) => {
    if (!selectedFormulaire) return

    await formulairesService.submitFormulaire(
      selectedFormulaire.id,
      signatureUrl,
      signatureNom
    )
    await loadData()
  }, [selectedFormulaire, loadData])

  // Validate formulaire
  const handleValidateFormulaire = useCallback(async (formulaire: FormulaireRempli) => {
    if (!confirm('Valider ce formulaire ?')) return

    try {
      await formulairesService.validateFormulaire(formulaire.id)
      await loadData()
    } catch (err) {
      setError('Erreur lors de la validation')
    }
  }, [loadData])

  // Export PDF
  const handleExportPDF = useCallback(async (formulaire: FormulaireRempli) => {
    try {
      await formulairesService.downloadPDF(formulaire.id)
    } catch (err) {
      setError("Erreur lors de l'export PDF")
    }
  }, [])

  // Filter templates
  const filteredTemplates = templates.filter((t) => {
    if (searchQuery && !t.nom.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false
    }
    return true
  })

  return {
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
    geoConsentModalOpen,
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
    handleExportPDF,

    // Geolocation consent
    handleGeoConsentAccept,
    handleGeoConsentDecline,
    handleGeoConsentClose,

    // Reload
    loadData,
  }
}

export default useFormulaires
