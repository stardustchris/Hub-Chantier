/**
 * useFormulairesData - Hook pour la gestion des données formulaires
 *
 * Responsabilités :
 * - Chargement des données (templates, formulaires, chantiers)
 * - Opérations CRUD templates
 * - Opérations CRUD formulaires
 */

import { useState, useCallback } from 'react'
import { formulairesService } from '../services/formulaires'
import { chantiersService } from '../services/chantiers'
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

export interface UseFormulairesDataReturn {
  // State
  loading: boolean
  error: string
  setError: (error: string) => void

  // Data
  templates: TemplateFormulaire[]
  formulaires: FormulaireRempli[]
  chantiers: Chantier[]

  // Actions
  loadData: (params?: {
    activeTab?: 'templates' | 'formulaires'
    searchQuery?: string
    filterCategorie?: CategorieFormulaire | ''
    filterChantierId?: number | null
  }) => Promise<void>

  // Template CRUD
  createTemplate: (data: TemplateFormulaireCreate) => Promise<void>
  updateTemplate: (id: number, data: TemplateFormulaireUpdate) => Promise<void>
  deleteTemplate: (id: number) => Promise<void>
  duplicateTemplate: (template: TemplateFormulaire) => Promise<void>
  toggleTemplateActive: (id: number, isActive: boolean) => Promise<void>

  // Formulaire CRUD
  createFormulaire: (templateId: number, chantierId: number) => Promise<FormulaireRempli>
  getFormulaire: (id: number) => Promise<FormulaireRempli>
  updateFormulaire: (id: number, data: FormulaireUpdate) => Promise<FormulaireRempli>
  submitFormulaire: (id: number, signatureUrl?: string, signatureNom?: string) => Promise<void>
  validateFormulaire: (id: number) => Promise<void>
  rejectFormulaire: (id: number) => Promise<void>
  exportPDF: (id: number) => Promise<void>

  // Template fetching
  getTemplate: (id: number) => Promise<TemplateFormulaire>
}

// Default mock data
const MOCK_TEMPLATES: TemplateFormulaire[] = []
const MOCK_FORMULAIRES: FormulaireRempli[] = []
const MOCK_CHANTIERS: Chantier[] = []

export function useFormulairesData(): UseFormulairesDataReturn {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [templates, setTemplates] = useState<TemplateFormulaire[]>([])
  const [formulaires, setFormulaires] = useState<FormulaireRempli[]>([])
  const [chantiers, setChantiers] = useState<Chantier[]>([])

  // Load data with optional filters
  const loadData = useCallback(async (params?: {
    activeTab?: 'templates' | 'formulaires'
    searchQuery?: string
    filterCategorie?: CategorieFormulaire | ''
    filterChantierId?: number | null
  }) => {
    setLoading(true)
    setError('')

    try {
      // Load templates
      const templatesResponse = await formulairesService.listTemplates({
        query: params?.activeTab === 'templates' ? params?.searchQuery : undefined,
        categorie: params?.filterCategorie || undefined,
        active_only: params?.activeTab === 'formulaires',
      })
      const loadedTemplates = templatesResponse?.templates || []
      setTemplates(loadedTemplates.length > 0 ? loadedTemplates : MOCK_TEMPLATES)

      // Load formulaires
      const formulairesResponse = await formulairesService.listFormulaires({
        chantier_id: params?.filterChantierId || undefined,
        template_id: undefined,
      })
      const loadedFormulaires = formulairesResponse?.formulaires || []
      setFormulaires(loadedFormulaires.length > 0 ? loadedFormulaires : MOCK_FORMULAIRES)

      // Load chantiers
      const chantiersResponse = await chantiersService.list({ size: 100 })
      const loadedChantiers = chantiersResponse?.items || []
      setChantiers(loadedChantiers.length > 0 ? loadedChantiers : MOCK_CHANTIERS)
    } catch (err) {
      logger.error('Error loading data, using mocks', err, { context: 'useFormulairesData' })
      setTemplates(MOCK_TEMPLATES)
      setFormulaires(MOCK_FORMULAIRES)
      setChantiers(MOCK_CHANTIERS)
    } finally {
      setLoading(false)
    }
  }, [])

  // ===== TEMPLATE CRUD =====

  const createTemplate = useCallback(async (data: TemplateFormulaireCreate) => {
    await formulairesService.createTemplate(data)
    await loadData()
  }, [loadData])

  const updateTemplate = useCallback(async (id: number, data: TemplateFormulaireUpdate) => {
    await formulairesService.updateTemplate(id, data)
    await loadData()
  }, [loadData])

  const deleteTemplate = useCallback(async (id: number) => {
    await formulairesService.deleteTemplate(id)
    await loadData()
  }, [loadData])

  const duplicateTemplate = useCallback(async (template: TemplateFormulaire) => {
    await formulairesService.createTemplate({
      nom: `${template.nom} (copie)`,
      categorie: template.categorie,
      description: template.description,
      champs: template.champs,
    })
    await loadData()
  }, [loadData])

  const toggleTemplateActive = useCallback(async (id: number, isActive: boolean) => {
    await formulairesService.updateTemplate(id, {
      is_active: !isActive,
    })
    await loadData()
  }, [loadData])

  const getTemplate = useCallback(async (id: number) => {
    return await formulairesService.getTemplate(id)
  }, [])

  // ===== FORMULAIRE CRUD =====

  const createFormulaire = useCallback(async (templateId: number, chantierId: number) => {
    return await formulairesService.createFormulaire({
      template_id: templateId,
      chantier_id: chantierId,
    })
  }, [])

  const getFormulaire = useCallback(async (id: number) => {
    return await formulairesService.getFormulaire(id)
  }, [])

  const updateFormulaire = useCallback(async (id: number, data: FormulaireUpdate) => {
    const updated = await formulairesService.updateFormulaire(id, data)
    await loadData()
    return updated
  }, [loadData])

  const submitFormulaire = useCallback(async (
    id: number,
    signatureUrl?: string,
    signatureNom?: string
  ) => {
    await formulairesService.submitFormulaire(id, signatureUrl, signatureNom)
    await loadData()
  }, [loadData])

  const validateFormulaire = useCallback(async (id: number) => {
    await formulairesService.validateFormulaire(id)
    await loadData()
  }, [loadData])

  const rejectFormulaire = useCallback(async (id: number) => {
    await formulairesService.rejectFormulaire(id)
    await loadData()
  }, [loadData])

  const exportPDF = useCallback(async (id: number) => {
    await formulairesService.downloadPDF(id)
  }, [])

  return {
    // State
    loading,
    error,
    setError,

    // Data
    templates,
    formulaires,
    chantiers,

    // Actions
    loadData,

    // Template CRUD
    createTemplate,
    updateTemplate,
    deleteTemplate,
    duplicateTemplate,
    toggleTemplateActive,
    getTemplate,

    // Formulaire CRUD
    createFormulaire,
    getFormulaire,
    updateFormulaire,
    submitFormulaire,
    validateFormulaire,
    rejectFormulaire,
    exportPDF,
  }
}
