/**
 * Composant TemplateImportModal - Modal d'import de modeles (TAC-04, TAC-05)
 * Permet de choisir un template a importer dans le chantier
 */

import { useState, useEffect } from 'react'
import { X, Loader2, Search, FileText, ChevronRight } from 'lucide-react'
import { tachesService } from '../../services/taches'
import { logger } from '../../services/logger'
import { useToast } from '../../contexts/ToastContext'
import type { TemplateModele } from '../../types'
import { UNITES_MESURE, UniteMesure } from '../../types'

interface TemplateImportModalProps {
  onClose: () => void
  onImport: (templateId: number) => Promise<void>
}

export default function TemplateImportModal({
  onClose,
  onImport,
}: TemplateImportModalProps) {
  const { addToast } = useToast()
  const [templates, setTemplates] = useState<TemplateModele[]>([])
  const [categories, setCategories] = useState<string[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategorie, setSelectedCategorie] = useState<string>('')
  const [selectedTemplate, setSelectedTemplate] = useState<TemplateModele | null>(null)
  const [isImporting, setIsImporting] = useState(false)

  useEffect(() => {
    loadTemplates()
  }, [searchQuery, selectedCategorie])

  const loadTemplates = async () => {
    try {
      setIsLoading(true)
      const response = await tachesService.listTemplates({
        query: searchQuery || undefined,
        categorie: selectedCategorie || undefined,
      })
      setTemplates(response.items)
      if (response.categories) {
        setCategories(response.categories)
      }
    } catch (error) {
      logger.error('Erreur chargement templates', error, { context: 'TemplateImportModal' })
      addToast({ message: 'Erreur lors du chargement des modeles', type: 'error' })
    } finally {
      setIsLoading(false)
    }
  }

  const handleImport = async () => {
    if (!selectedTemplate) return

    setIsImporting(true)
    try {
      await onImport(selectedTemplate.id)
    } finally {
      setIsImporting(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="fixed inset-0 bg-black/50" onClick={onClose} />
      <div className="relative bg-white rounded-xl shadow-xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="border-b px-6 py-4 flex items-center justify-between shrink-0">
          <h2 className="text-lg font-semibold">Importer un modele de taches</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Recherche et filtres */}
        <div className="p-4 border-b space-y-3 shrink-0">
          {/* Barre de recherche */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-600" />
            <input
              type="text"
              placeholder="Rechercher un modele..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="input pl-9 w-full"
            />
          </div>

          {/* Categories */}
          {categories.length > 0 && (
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => setSelectedCategorie('')}
                className={`px-3 py-1.5 rounded-full text-sm transition-colors ${
                  !selectedCategorie
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                Toutes
              </button>
              {categories.map((cat) => (
                <button
                  key={cat}
                  onClick={() => setSelectedCategorie(cat)}
                  className={`px-3 py-1.5 rounded-full text-sm transition-colors ${
                    selectedCategorie === cat
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Liste des templates */}
        <div className="flex-1 overflow-y-auto p-4">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-6 h-6 animate-spin text-primary-600" />
            </div>
          ) : templates.length === 0 ? (
            <div className="text-center py-12">
              <FileText className="w-12 h-12 text-gray-500 mx-auto mb-3" />
              <p className="text-gray-500">
                {searchQuery
                  ? 'Aucun modele trouve'
                  : 'Aucun modele disponible'}
              </p>
            </div>
          ) : (
            <div className="space-y-2">
              {templates.map((template) => (
                <button
                  key={template.id}
                  onClick={() => setSelectedTemplate(template)}
                  className={`w-full text-left p-4 rounded-lg border transition-colors ${
                    selectedTemplate?.id === template.id
                      ? 'border-primary-500 bg-primary-50'
                      : 'border-gray-200 hover:bg-gray-50'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-medium text-gray-900">
                        {template.nom}
                      </h3>
                      {template.description && (
                        <p className="text-sm text-gray-500 mt-0.5">
                          {template.description}
                        </p>
                      )}
                      <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
                        {template.categorie && (
                          <span className="bg-gray-100 px-2 py-0.5 rounded">
                            {template.categorie}
                          </span>
                        )}
                        <span>{template.nombre_sous_taches} sous-taches</span>
                        {template.unite_mesure && (
                          <span>
                            {UNITES_MESURE[template.unite_mesure as UniteMesure]?.symbol}
                          </span>
                        )}
                        {template.heures_estimees_defaut && (
                          <span>{template.heures_estimees_defaut}h</span>
                        )}
                      </div>
                    </div>
                    <ChevronRight
                      className={`w-5 h-5 ${
                        selectedTemplate?.id === template.id
                          ? 'text-primary-600'
                          : 'text-gray-600'
                      }`}
                    />
                  </div>

                  {/* Preview sous-taches si selectionne */}
                  {selectedTemplate?.id === template.id &&
                    template.sous_taches &&
                    template.sous_taches.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-primary-200">
                        <p className="text-xs text-gray-500 mb-2">
                          Sous-taches incluses:
                        </p>
                        <ul className="space-y-1">
                          {template.sous_taches.map((st, index) => (
                            <li
                              key={index}
                              className="text-sm text-gray-700 flex items-center gap-2"
                            >
                              <span className="w-1.5 h-1.5 bg-primary-400 rounded-full" />
                              {st.titre}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="border-t p-4 flex gap-3 shrink-0">
          <button
            type="button"
            onClick={onClose}
            className="flex-1 btn btn-outline"
            disabled={isImporting}
          >
            Annuler
          </button>
          <button
            onClick={handleImport}
            disabled={!selectedTemplate || isImporting}
            className="flex-1 btn btn-primary flex items-center justify-center gap-2"
          >
            {isImporting && <Loader2 className="w-4 h-4 animate-spin" />}
            Importer
          </button>
        </div>
      </div>
    </div>
  )
}
