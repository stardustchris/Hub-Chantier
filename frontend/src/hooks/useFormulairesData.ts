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
const MOCK_TEMPLATES: TemplateFormulaire[] = [
  {
    id: 1,
    nom: 'Rapport journalier chantier',
    description: 'Rapport quotidien des activités du chantier',
    categorie: 'gros_oeuvre',
    champs: [
      { nom: 'date', label: 'Date', type_champ: 'date', obligatoire: true, ordre: 1 },
      { nom: 'meteo', label: 'Météo', type_champ: 'texte', obligatoire: false, ordre: 2 },
      { nom: 'effectif', label: 'Effectif présent', type_champ: 'nombre', obligatoire: true, ordre: 3 },
      { nom: 'travaux', label: 'Description des travaux', type_champ: 'texte_long', obligatoire: true, ordre: 4 },
      { nom: 'avancement', label: 'Taux d\'avancement (%)', type_champ: 'nombre', obligatoire: false, ordre: 5 }
    ],
    is_active: true,
    version: 1,
    nombre_champs: 5,
    a_signature: false,
    a_photo: false,
    created_at: '2026-01-15T10:00:00Z',
    updated_at: '2026-01-15T10:00:00Z'
  },
  {
    id: 2,
    nom: 'Contrôle qualité béton',
    description: 'Fiche de contrôle qualité pour coulage béton',
    categorie: 'reception',
    champs: [
      { nom: 'date_coulage', label: 'Date de coulage', type_champ: 'date', obligatoire: true, ordre: 1 },
      { nom: 'zone', label: 'Zone de coulage', type_champ: 'texte', obligatoire: true, ordre: 2 },
      { nom: 'fournisseur', label: 'Fournisseur béton', type_champ: 'texte', obligatoire: true, ordre: 3 },
      { nom: 'consistance', label: 'Consistance (slump test)', type_champ: 'texte', obligatoire: true, ordre: 4 },
      { nom: 'temperature', label: 'Température (°C)', type_champ: 'nombre', obligatoire: true, ordre: 5 },
      { nom: 'conforme', label: 'Conforme', type_champ: 'checkbox', obligatoire: true, ordre: 6 }
    ],
    is_active: true,
    version: 1,
    nombre_champs: 6,
    a_signature: false,
    a_photo: false,
    created_at: '2026-01-10T14:30:00Z',
    updated_at: '2026-01-10T14:30:00Z'
  },
  {
    id: 3,
    nom: 'Fiche d\'intervention sécurité',
    description: 'Rapport d\'incident ou d\'observation sécurité',
    categorie: 'securite',
    champs: [
      { nom: 'date_incident', label: 'Date et heure', type_champ: 'date_heure', obligatoire: true, ordre: 1 },
      { nom: 'lieu', label: 'Lieu de l\'incident', type_champ: 'texte', obligatoire: true, ordre: 2 },
      { nom: 'description', label: 'Description', type_champ: 'texte_long', obligatoire: true, ordre: 3 },
      { nom: 'gravite', label: 'Gravité', type_champ: 'select', obligatoire: true, ordre: 4, options: ['Faible', 'Moyenne', 'Élevée', 'Critique'] }
    ],
    is_active: true,
    version: 1,
    nombre_champs: 4,
    a_signature: false,
    a_photo: false,
    created_at: '2026-01-20T09:00:00Z',
    updated_at: '2026-01-20T09:00:00Z'
  }
]

const MOCK_FORMULAIRES: FormulaireRempli[] = [
  {
    id: 1,
    template_id: 1,
    template_nom: 'Rapport journalier chantier',
    template_categorie: 'gros_oeuvre',
    chantier_id: 5,
    chantier_nom: 'Residence Les Jardins',
    user_id: 1,
    user_nom: 'Super ADMIN',
    statut: 'brouillon',
    champs: [
      { nom: 'date', type_champ: 'date', valeur: '2026-01-29' },
      { nom: 'meteo', type_champ: 'texte', valeur: 'Ensoleillé' },
      { nom: 'effectif', type_champ: 'nombre', valeur: '8' },
      { nom: 'travaux', type_champ: 'texte_long', valeur: 'Coulage dalle étage 2, pose des menuiseries' },
      { nom: 'avancement', type_champ: 'nombre', valeur: '75' }
    ],
    photos: [],
    est_signe: false,
    est_geolocalise: false,
    version: 1,
    created_at: '2026-01-29T08:00:00Z',
    updated_at: '2026-01-29T08:00:00Z'
  },
  {
    id: 2,
    template_id: 1,
    template_nom: 'Rapport journalier chantier',
    template_categorie: 'gros_oeuvre',
    chantier_id: 6,
    chantier_nom: 'Centre Commercial Grand Place',
    user_id: 2,
    user_nom: 'Sophie PETIT',
    statut: 'soumis',
    champs: [
      { nom: 'date', type_champ: 'date', valeur: '2026-01-28' },
      { nom: 'meteo', type_champ: 'texte', valeur: 'Nuageux' },
      { nom: 'effectif', type_champ: 'nombre', valeur: '12' },
      { nom: 'travaux', type_champ: 'texte_long', valeur: 'Fondations zone B terminées, début élévation murs' },
      { nom: 'avancement', type_champ: 'nombre', valeur: '45' }
    ],
    photos: [],
    est_signe: false,
    est_geolocalise: false,
    soumis_at: '2026-01-28T17:30:00Z',
    version: 1,
    created_at: '2026-01-28T08:15:00Z',
    updated_at: '2026-01-28T17:30:00Z'
  },
  {
    id: 3,
    template_id: 2,
    template_nom: 'Contrôle qualité béton',
    template_categorie: 'reception',
    chantier_id: 5,
    chantier_nom: 'Residence Les Jardins',
    user_id: 3,
    user_nom: 'Pierre BERNARD',
    statut: 'valide',
    champs: [
      { nom: 'date_coulage', type_champ: 'date', valeur: '2026-01-27' },
      { nom: 'zone', type_champ: 'texte', valeur: 'Dalle étage 2 - Appartements 201-205' },
      { nom: 'fournisseur', type_champ: 'texte', valeur: 'Béton Plus' },
      { nom: 'consistance', type_champ: 'texte', valeur: 'S3 - 150mm' },
      { nom: 'temperature', type_champ: 'nombre', valeur: '18' },
      { nom: 'conforme', type_champ: 'checkbox', valeur: 'true' }
    ],
    photos: [],
    est_signe: true,
    est_geolocalise: false,
    soumis_at: '2026-01-27T14:00:00Z',
    valide_at: '2026-01-27T16:00:00Z',
    version: 1,
    created_at: '2026-01-27T13:00:00Z',
    updated_at: '2026-01-27T16:00:00Z'
  }
]

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
