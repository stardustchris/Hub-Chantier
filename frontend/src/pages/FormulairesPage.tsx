/**
 * FormulairesPage - Page principale du module Formulaires
 * CDC Section 8 (FOR-01 à FOR-11)
 */

import { useState, useEffect, useCallback } from 'react'
import { useSearchParams } from 'react-router-dom'
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
import { GeolocationConsentModal } from '../components/common/GeolocationConsentModal'
import { formulairesService } from '../services/formulaires'
import { chantiersService } from '../services/chantiers'
import { consentService } from '../services/consent'
import { useAuth } from '../contexts/AuthContext'
import type {
  TemplateFormulaire,
  TemplateFormulaireCreate,
  TemplateFormulaireUpdate,
  FormulaireRempli,
  FormulaireUpdate,
  CategorieFormulaire,
  Chantier,
} from '../types'
import { logger } from '../services/logger'
import { CATEGORIES_FORMULAIRES } from '../types'

// Mock templates pour démonstration
const MOCK_TEMPLATES: TemplateFormulaire[] = [
  {
    id: 1,
    nom: 'Contrôle qualité béton',
    categorie: 'reception',
    description: 'Vérification de la qualité du béton coulé',
    champs: [
      { id: 1, nom: 'temperature', label: 'Température ambiante (°C)', type_champ: 'number', obligatoire: true, ordre: 1 },
      { id: 2, nom: 'slump', label: 'Slump test (cm)', type_champ: 'number', obligatoire: true, ordre: 2 },
      { id: 3, nom: 'conforme', label: 'Conforme aux spécifications', type_champ: 'checkbox', obligatoire: true, ordre: 3 },
      { id: 4, nom: 'remarques', label: 'Remarques', type_champ: 'textarea', obligatoire: false, ordre: 4 },
    ],
    is_active: true,
    version: 1,
    nombre_champs: 4,
    a_signature: true,
    a_photo: true,
    created_at: new Date(Date.now() - 30 * 86400000).toISOString(),
    updated_at: new Date(Date.now() - 7 * 86400000).toISOString(),
  },
  {
    id: 2,
    nom: 'Inspection sécurité chantier',
    categorie: 'securite',
    description: 'Check-list sécurité quotidienne',
    champs: [
      { id: 5, nom: 'epi_ok', label: 'EPI portés par tous', type_champ: 'checkbox', obligatoire: true, ordre: 1 },
      { id: 6, nom: 'zone_securisee', label: 'Zone de travail sécurisée', type_champ: 'checkbox', obligatoire: true, ordre: 2 },
      { id: 7, nom: 'issues_secours', label: 'Issues de secours dégagées', type_champ: 'checkbox', obligatoire: true, ordre: 3 },
      { id: 8, nom: 'extincteurs', label: 'Extincteurs accessibles', type_champ: 'checkbox', obligatoire: true, ordre: 4 },
      { id: 9, nom: 'anomalies', label: 'Anomalies constatées', type_champ: 'textarea', obligatoire: false, ordre: 5 },
    ],
    is_active: true,
    version: 2,
    nombre_champs: 5,
    a_signature: true,
    a_photo: false,
    created_at: new Date(Date.now() - 60 * 86400000).toISOString(),
    updated_at: new Date(Date.now() - 3 * 86400000).toISOString(),
  },
  {
    id: 3,
    nom: 'Réception matériaux',
    categorie: 'approvisionnement',
    description: 'Contrôle à la réception des matériaux',
    champs: [
      { id: 10, nom: 'fournisseur', label: 'Fournisseur', type_champ: 'text', obligatoire: true, ordre: 1 },
      { id: 11, nom: 'bon_livraison', label: 'N° Bon de livraison', type_champ: 'text', obligatoire: true, ordre: 2 },
      { id: 12, nom: 'quantite_conforme', label: 'Quantité conforme', type_champ: 'checkbox', obligatoire: true, ordre: 3 },
      { id: 13, nom: 'etat_materiel', label: 'État du matériel', type_champ: 'select', obligatoire: true, ordre: 4, options: ['Bon', 'Acceptable', 'Endommagé'] },
    ],
    is_active: true,
    version: 1,
    nombre_champs: 4,
    a_signature: true,
    a_photo: true,
    created_at: new Date(Date.now() - 45 * 86400000).toISOString(),
    updated_at: new Date(Date.now() - 10 * 86400000).toISOString(),
  },
  {
    id: 4,
    nom: 'Rapport journalier',
    categorie: 'interventions',
    description: 'Rapport d\'activité quotidien',
    champs: [
      { id: 14, nom: 'meteo', label: 'Conditions météo', type_champ: 'select', obligatoire: true, ordre: 1, options: ['Beau', 'Nuageux', 'Pluie', 'Neige'] },
      { id: 15, nom: 'effectif', label: 'Effectif présent', type_champ: 'number', obligatoire: true, ordre: 2 },
      { id: 16, nom: 'travaux_realises', label: 'Travaux réalisés', type_champ: 'textarea', obligatoire: true, ordre: 3 },
      { id: 17, nom: 'incidents', label: 'Incidents', type_champ: 'textarea', obligatoire: false, ordre: 4 },
    ],
    is_active: true,
    version: 3,
    nombre_champs: 4,
    a_signature: false,
    a_photo: true,
    created_at: new Date(Date.now() - 90 * 86400000).toISOString(),
    updated_at: new Date(Date.now() - 1 * 86400000).toISOString(),
  },
]

// Mock formulaires remplis
const MOCK_FORMULAIRES: FormulaireRempli[] = [
  {
    id: 1,
    template_id: 1,
    template_nom: 'Contrôle qualité béton',
    template_categorie: 'reception',
    chantier_id: 1,
    chantier_nom: 'Villa Moderne Lyon',
    user_id: 1,
    user_nom: 'Pierre Martin',
    statut: 'soumis',
    champs: [],
    photos: [],
    est_signe: true,
    signature_nom: 'Pierre Martin',
    signature_timestamp: new Date(Date.now() - 2 * 86400000).toISOString(),
    est_geolocalise: true,
    localisation_latitude: 45.7640,
    localisation_longitude: 4.8357,
    soumis_at: new Date(Date.now() - 2 * 86400000).toISOString(),
    version: 1,
    created_at: new Date(Date.now() - 2 * 86400000).toISOString(),
    updated_at: new Date(Date.now() - 2 * 86400000).toISOString(),
  },
  {
    id: 2,
    template_id: 2,
    template_nom: 'Inspection sécurité chantier',
    template_categorie: 'securite',
    chantier_id: 2,
    chantier_nom: 'Résidence Les Pins',
    user_id: 2,
    user_nom: 'Marie Dupont',
    statut: 'valide',
    champs: [],
    photos: [],
    est_signe: true,
    signature_nom: 'Marie Dupont',
    est_geolocalise: true,
    soumis_at: new Date(Date.now() - 5 * 86400000).toISOString(),
    valide_at: new Date(Date.now() - 4 * 86400000).toISOString(),
    valide_by: 3,
    version: 1,
    created_at: new Date(Date.now() - 5 * 86400000).toISOString(),
    updated_at: new Date(Date.now() - 4 * 86400000).toISOString(),
  },
  {
    id: 3,
    template_id: 4,
    template_nom: 'Rapport journalier',
    template_categorie: 'interventions',
    chantier_id: 1,
    chantier_nom: 'Villa Moderne Lyon',
    user_id: 1,
    user_nom: 'Pierre Martin',
    statut: 'brouillon',
    champs: [],
    photos: [],
    est_signe: false,
    est_geolocalise: false,
    version: 1,
    created_at: new Date(Date.now() - 1 * 3600000).toISOString(),
    updated_at: new Date(Date.now() - 1 * 3600000).toISOString(),
  },
  {
    id: 4,
    template_id: 3,
    template_nom: 'Réception matériaux',
    template_categorie: 'approvisionnement',
    chantier_id: 3,
    chantier_nom: 'École Pasteur',
    user_id: 4,
    user_nom: 'Sophie Technique',
    statut: 'soumis',
    champs: [],
    photos: [],
    est_signe: true,
    signature_nom: 'Sophie Technique',
    est_geolocalise: true,
    soumis_at: new Date(Date.now() - 1 * 86400000).toISOString(),
    version: 1,
    created_at: new Date(Date.now() - 1 * 86400000).toISOString(),
    updated_at: new Date(Date.now() - 1 * 86400000).toISOString(),
  },
]

// Mock chantiers
const MOCK_CHANTIERS = [
  { id: '1', code: 'VML-001', nom: 'Villa Moderne Lyon', contact_nom: 'M. Durand', statut: 'en_cours', adresse: '45 rue de la République, Lyon', date_debut_prevue: '2026-01-10', date_fin_prevue: '2026-06-30', conducteurs: [], chefs: [], created_at: '2026-01-01' },
  { id: '2', code: 'RLP-002', nom: 'Résidence Les Pins', contact_nom: 'SCI Les Pins', statut: 'en_cours', adresse: '12 avenue des Pins, Villeurbanne', date_debut_prevue: '2025-11-01', date_fin_prevue: '2026-08-15', conducteurs: [], chefs: [], created_at: '2025-11-01' },
  { id: '3', code: 'EPA-003', nom: 'École Pasteur', contact_nom: 'Mairie de Lyon', statut: 'en_cours', adresse: '8 rue Pasteur, Lyon', date_debut_prevue: '2026-01-15', date_fin_prevue: '2026-12-01', conducteurs: [], chefs: [], created_at: '2026-01-15' },
] as Chantier[]

type TabType = 'templates' | 'formulaires'
type ViewMode = 'grid' | 'list'

export default function FormulairesPage() {
  const { user: currentUser } = useAuth()
  const [searchParams, setSearchParams] = useSearchParams()

  // State principal
  const [activeTab, setActiveTab] = useState<TabType>('formulaires')
  const [viewMode, setViewMode] = useState<ViewMode>('grid')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // Donnees
  const [templates, setTemplates] = useState<TemplateFormulaire[]>([])
  const [formulaires, setFormulaires] = useState<FormulaireRempli[]>([])
  const [chantiers, setChantiers] = useState<Chantier[]>([])
  const [selectedChantierId, setSelectedChantierId] = useState<string | null>(null)

  // Filtres
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

  // Consentement geolocalisation RGPD
  const [geoConsentModalOpen, setGeoConsentModalOpen] = useState(false)
  const [pendingTemplateId, setPendingTemplateId] = useState<number | null>(null)

  // Permissions
  const canManageTemplates = currentUser?.role === 'admin' || currentUser?.role === 'conducteur'

  // Charger les donnees
  const loadData = useCallback(async () => {
    setLoading(true)
    setError('')

    try {
      // Charger les templates
      const templatesResponse = await formulairesService.listTemplates({
        query: activeTab === 'templates' ? searchQuery : undefined,
        categorie: filterCategorie || undefined,
        active_only: activeTab === 'formulaires',
      })
      const loadedTemplates = templatesResponse?.templates || []
      setTemplates(loadedTemplates.length > 0 ? loadedTemplates : MOCK_TEMPLATES)

      // Charger les formulaires
      const formulairesResponse = await formulairesService.listFormulaires({
        chantier_id: filterChantierId || undefined,
        template_id: undefined,
      })
      const loadedFormulaires = formulairesResponse?.formulaires || []
      setFormulaires(loadedFormulaires.length > 0 ? loadedFormulaires : MOCK_FORMULAIRES)

      // Charger les chantiers
      const chantiersResponse = await chantiersService.list({ size: 100 })
      const loadedChantiers = chantiersResponse?.items || []
      setChantiers(loadedChantiers.length > 0 ? loadedChantiers : MOCK_CHANTIERS)
    } catch (err) {
      // En cas d'erreur, utiliser les mocks
      logger.error('Error loading data, using mocks', err, { context: 'FormulairesPage' })
      setTemplates(MOCK_TEMPLATES)
      setFormulaires(MOCK_FORMULAIRES)
      setChantiers(MOCK_CHANTIERS)
    } finally {
      setLoading(false)
    }
  }, [activeTab, searchQuery, filterCategorie, filterChantierId])

  useEffect(() => {
    loadData()
  }, [loadData])

  // Gestion de l'URL
  useEffect(() => {
    const tab = searchParams.get('tab')
    if (tab === 'templates' || tab === 'formulaires') {
      setActiveTab(tab)
    }
  }, [searchParams])

  const handleTabChange = (tab: TabType) => {
    setActiveTab(tab)
    setSearchParams({ tab })
  }

  // ===== TEMPLATES =====

  const handleSaveTemplate = async (data: TemplateFormulaireCreate | TemplateFormulaireUpdate) => {
    try {
      if (selectedTemplate) {
        await formulairesService.updateTemplate(selectedTemplate.id, data)
      } else {
        await formulairesService.createTemplate(data as TemplateFormulaireCreate)
      }
      await loadData()
      setTemplateModalOpen(false)
      setSelectedTemplate(null)
    } catch (err) {
      throw err
    }
  }

  const handleEditTemplate = (template: TemplateFormulaire) => {
    setSelectedTemplate(template)
    setTemplateModalOpen(true)
  }

  const handleDeleteTemplate = async (template: TemplateFormulaire) => {
    if (!confirm(`Supprimer le template "${template.nom}" ?`)) return

    try {
      await formulairesService.deleteTemplate(template.id)
      await loadData()
    } catch (err) {
      setError('Erreur lors de la suppression')
    }
  }

  const handleDuplicateTemplate = async (template: TemplateFormulaire) => {
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
  }

  const handleToggleTemplateActive = async (template: TemplateFormulaire) => {
    try {
      await formulairesService.updateTemplate(template.id, {
        is_active: !template.is_active,
      })
      await loadData()
    } catch (err) {
      setError('Erreur lors de la mise a jour')
    }
  }

  const handlePreviewTemplate = (template: TemplateFormulaire) => {
    setSelectedTemplate(template)
    setSelectedFormulaire(null)
    setFormulaireReadOnly(true)
    setFormulaireModalOpen(true)
  }

  // ===== FORMULAIRES =====

  /**
   * Finalise la creation du formulaire avec ou sans geolocalisation
   */
  const finalizeCreateFormulaire = async (templateId: number, withGeolocation: boolean) => {
    try {
      let latitude: number | undefined
      let longitude: number | undefined

      // Obtenir la position geographique si consentement donne et API disponible
      if (withGeolocation && navigator.geolocation) {
        try {
          const position = await new Promise<GeolocationPosition>((resolve, reject) => {
            navigator.geolocation.getCurrentPosition(resolve, reject, { timeout: 5000 })
          })
          latitude = position.coords.latitude
          longitude = position.coords.longitude
        } catch {
          // Geolocation non disponible ou refusee par le navigateur
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
  }

  /**
   * Gere le clic sur "Creer formulaire" avec verification du consentement RGPD
   */
  const handleCreateFormulaire = async (templateId: number) => {
    // Verifier qu'un chantier est selectionne
    if (!selectedChantierId) {
      setError('Veuillez selectionner un chantier')
      return
    }

    // Verifier si le consentement geolocalisation a deja ete demande
    if (!consentService.wasAsked('geolocation')) {
      // Afficher la modal de consentement et stocker le templateId en attente
      setPendingTemplateId(templateId)
      setGeoConsentModalOpen(true)
      return
    }

    // Consentement deja donne ou refuse, proceder avec le choix stocke
    const hasConsent = consentService.hasConsent('geolocation')
    await finalizeCreateFormulaire(templateId, hasConsent)
  }

  /**
   * Callback quand l'utilisateur accepte le consentement geolocalisation
   */
  const handleGeoConsentAccept = async () => {
    consentService.setConsent('geolocation', true)
    setGeoConsentModalOpen(false)
    if (pendingTemplateId !== null) {
      await finalizeCreateFormulaire(pendingTemplateId, true)
      setPendingTemplateId(null)
    }
  }

  /**
   * Callback quand l'utilisateur refuse le consentement geolocalisation
   */
  const handleGeoConsentDecline = async () => {
    consentService.setConsent('geolocation', false)
    setGeoConsentModalOpen(false)
    if (pendingTemplateId !== null) {
      await finalizeCreateFormulaire(pendingTemplateId, false)
      setPendingTemplateId(null)
    }
  }

  /**
   * Callback quand l'utilisateur ferme la modal sans choisir
   */
  const handleGeoConsentClose = () => {
    setGeoConsentModalOpen(false)
    setPendingTemplateId(null)
  }

  const handleViewFormulaire = async (formulaire: FormulaireRempli) => {
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
  }

  const handleEditFormulaire = async (formulaire: FormulaireRempli) => {
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
  }

  const handleSaveFormulaire = async (data: FormulaireUpdate) => {
    if (!selectedFormulaire) return

    try {
      const updated = await formulairesService.updateFormulaire(selectedFormulaire.id, data)
      setSelectedFormulaire(updated)
      await loadData()
    } catch (err) {
      throw err
    }
  }

  const handleSubmitFormulaire = async (signatureUrl?: string, signatureNom?: string) => {
    if (!selectedFormulaire) return

    try {
      await formulairesService.submitFormulaire(
        selectedFormulaire.id,
        signatureUrl,
        signatureNom
      )
      await loadData()
    } catch (err) {
      throw err
    }
  }

  const handleValidateFormulaire = async (formulaire: FormulaireRempli) => {
    if (!confirm('Valider ce formulaire ?')) return

    try {
      await formulairesService.validateFormulaire(formulaire.id)
      await loadData()
    } catch (err) {
      setError('Erreur lors de la validation')
    }
  }

  const handleExportPDF = async (formulaire: FormulaireRempli) => {
    try {
      await formulairesService.downloadPDF(formulaire.id)
    } catch (err) {
      setError('Erreur lors de l\'export PDF')
    }
  }

  // Filtrer les templates pour l'affichage
  const filteredTemplates = templates.filter((t) => {
    if (searchQuery && !t.nom.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false
    }
    return true
  })

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
                onClick={() => {
                  setSelectedTemplate(null)
                  setTemplateModalOpen(true)
                }}
                className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
              >
                <Plus className="w-5 h-5" />
                Nouveau template
              </button>
            )}
            {activeTab === 'formulaires' && (
              <button
                onClick={() => setNewFormulaireModalOpen(true)}
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
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
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
            <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
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
            loading={loading}
          />
        )}

        {/* Template Modal */}
        <TemplateModal
          isOpen={templateModalOpen}
          onClose={() => {
            setTemplateModalOpen(false)
            setSelectedTemplate(null)
          }}
          onSave={handleSaveTemplate}
          template={selectedTemplate}
        />

        {/* Formulaire Modal */}
        <FormulaireModal
          isOpen={formulaireModalOpen}
          onClose={() => {
            setFormulaireModalOpen(false)
            setSelectedFormulaire(null)
            setSelectedTemplate(null)
          }}
          onSave={handleSaveFormulaire}
          onSubmit={handleSubmitFormulaire}
          formulaire={selectedFormulaire}
          template={selectedTemplate}
          readOnly={formulaireReadOnly}
        />

        {/* New Formulaire Selection Modal */}
        <NewFormulaireModal
          isOpen={newFormulaireModalOpen}
          onClose={() => setNewFormulaireModalOpen(false)}
          onCreateFormulaire={handleCreateFormulaire}
          templates={templates}
          chantiers={chantiers}
          selectedChantierId={selectedChantierId}
          onChantierChange={setSelectedChantierId}
        />

        {/* Modal de consentement RGPD pour la geolocalisation */}
        <GeolocationConsentModal
          isOpen={geoConsentModalOpen}
          onAccept={handleGeoConsentAccept}
          onDecline={handleGeoConsentDecline}
          onClose={handleGeoConsentClose}
        />
      </div>
    </Layout>
  )
}
