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
    categorie: 'suivi_chantier',
    sections: [
      {
        titre: 'Informations générales',
        champs: [
          { nom: 'date', label: 'Date', type: 'date', obligatoire: true, ordre: 1 },
          { nom: 'meteo', label: 'Météo', type: 'text', obligatoire: false, ordre: 2 },
          { nom: 'effectif', label: 'Effectif présent', type: 'number', obligatoire: true, ordre: 3 }
        ]
      },
      {
        titre: 'Travaux réalisés',
        champs: [
          { nom: 'travaux', label: 'Description des travaux', type: 'textarea', obligatoire: true, ordre: 1 },
          { nom: 'avancement', label: 'Taux d\'avancement (%)', type: 'number', obligatoire: false, ordre: 2 }
        ]
      }
    ],
    is_active: true,
    created_at: '2026-01-15T10:00:00Z',
    updated_at: '2026-01-15T10:00:00Z'
  },
  {
    id: 2,
    nom: 'Contrôle qualité béton',
    description: 'Fiche de contrôle qualité pour coulage béton',
    categorie: 'qualite',
    sections: [
      {
        titre: 'Identification',
        champs: [
          { nom: 'date_coulage', label: 'Date de coulage', type: 'date', obligatoire: true, ordre: 1 },
          { nom: 'zone', label: 'Zone de coulage', type: 'text', obligatoire: true, ordre: 2 },
          { nom: 'fournisseur', label: 'Fournisseur béton', type: 'text', obligatoire: true, ordre: 3 }
        ]
      },
      {
        titre: 'Contrôles',
        champs: [
          { nom: 'consistance', label: 'Consistance (slump test)', type: 'text', obligatoire: true, ordre: 1 },
          { nom: 'temperature', label: 'Température (°C)', type: 'number', obligatoire: true, ordre: 2 },
          { nom: 'conforme', label: 'Conforme', type: 'checkbox', obligatoire: true, ordre: 3 }
        ]
      }
    ],
    is_active: true,
    created_at: '2026-01-10T14:30:00Z',
    updated_at: '2026-01-10T14:30:00Z'
  },
  {
    id: 3,
    nom: 'Fiche d\'intervention sécurité',
    description: 'Rapport d\'incident ou d\'observation sécurité',
    categorie: 'securite',
    sections: [
      {
        titre: 'Incident',
        champs: [
          { nom: 'date_incident', label: 'Date et heure', type: 'datetime-local', obligatoire: true, ordre: 1 },
          { nom: 'lieu', label: 'Lieu de l\'incident', type: 'text', obligatoire: true, ordre: 2 },
          { nom: 'description', label: 'Description', type: 'textarea', obligatoire: true, ordre: 3 },
          { nom: 'gravite', label: 'Gravité', type: 'select', obligatoire: true, ordre: 4, options: ['Faible', 'Moyenne', 'Élevée', 'Critique'] }
        ]
      }
    ],
    is_active: true,
    created_at: '2026-01-20T09:00:00Z',
    updated_at: '2026-01-20T09:00:00Z'
  }
]

const MOCK_FORMULAIRES: FormulaireRempli[] = [
  {
    id: 1,
    template_id: 1,
    template_nom: 'Rapport journalier chantier',
    template_categorie: 'suivi_chantier',
    chantier_id: 5,
    chantier_nom: 'Residence Les Jardins',
    user_id: 1,
    user_nom: 'Super ADMIN',
    statut: 'brouillon',
    champs: [
      { champ_id: 1, nom: 'date', valeur: '2026-01-29' },
      { champ_id: 2, nom: 'meteo', valeur: 'Ensoleillé' },
      { champ_id: 3, nom: 'effectif', valeur: '8' },
      { champ_id: 4, nom: 'travaux', valeur: 'Coulage dalle étage 2, pose des menuiseries' },
      { champ_id: 5, nom: 'avancement', valeur: '75' }
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
    template_categorie: 'suivi_chantier',
    chantier_id: 6,
    chantier_nom: 'Centre Commercial Grand Place',
    user_id: 2,
    user_nom: 'Sophie PETIT',
    statut: 'soumis',
    champs: [
      { champ_id: 1, nom: 'date', valeur: '2026-01-28' },
      { champ_id: 2, nom: 'meteo', valeur: 'Nuageux' },
      { champ_id: 3, nom: 'effectif', valeur: '12' },
      { champ_id: 4, nom: 'travaux', valeur: 'Fondations zone B terminées, début élévation murs' },
      { champ_id: 5, nom: 'avancement', valeur: '45' }
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
    template_categorie: 'qualite',
    chantier_id: 5,
    chantier_nom: 'Residence Les Jardins',
    user_id: 3,
    user_nom: 'Pierre BERNARD',
    statut: 'valide',
    champs: [
      { champ_id: 1, nom: 'date_coulage', valeur: '2026-01-27' },
      { champ_id: 2, nom: 'zone', valeur: 'Dalle étage 2 - Appartements 201-205' },
      { champ_id: 3, nom: 'fournisseur', valeur: 'Béton Plus' },
      { champ_id: 4, nom: 'consistance', valeur: 'S3 - 150mm' },
      { champ_id: 5, nom: 'temperature', valeur: '18' },
      { champ_id: 6, nom: 'conforme', valeur: 'true' }
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
