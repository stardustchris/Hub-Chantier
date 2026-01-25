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
import { formulairesService } from '../services/formulaires'
import { chantiersService } from '../services/chantiers'
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
      setTemplates(templatesResponse.templates)

      // Charger les formulaires
      const formulairesResponse = await formulairesService.listFormulaires({
        chantier_id: filterChantierId || undefined,
        template_id: undefined,
      })
      setFormulaires(formulairesResponse.formulaires)

      // Charger les chantiers
      const chantiersResponse = await chantiersService.list({ size: 100 })
      setChantiers(chantiersResponse.items)
    } catch (err) {
      setError('Erreur lors du chargement des donnees')
      logger.error('Error loading data', err, { context: 'FormulairesPage' })
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

  const handleCreateFormulaire = async (templateId: number) => {
    // Verifier qu'un chantier est selectionne
    if (!selectedChantierId) {
      setError('Veuillez selectionner un chantier')
      return
    }

    try {
      // Obtenir la position geographique si disponible
      let latitude: number | undefined
      let longitude: number | undefined

      if (navigator.geolocation) {
        try {
          const position = await new Promise<GeolocationPosition>((resolve, reject) => {
            navigator.geolocation.getCurrentPosition(resolve, reject, { timeout: 5000 })
          })
          latitude = position.coords.latitude
          longitude = position.coords.longitude
        } catch {
          // Geolocation non disponible ou refusee
        }
      }

      const formulaire = await formulairesService.createFormulaire({
        template_id: templateId,
        chantier_id: parseInt(selectedChantierId, 10),
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
      </div>
    </Layout>
  )
}
