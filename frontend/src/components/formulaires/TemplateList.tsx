/**
 * TemplateList - Liste des templates de formulaires (FOR-01)
 * Affiche les templates disponibles avec leurs informations
 */

import { FileText, Edit, Trash2, Copy, Eye, ToggleLeft, ToggleRight } from 'lucide-react'
import type { TemplateFormulaire, CategorieFormulaire } from '../../types'
import { CATEGORIES_FORMULAIRES } from '../../types'

interface TemplateListProps {
  templates: TemplateFormulaire[]
  onEdit: (template: TemplateFormulaire) => void
  onDelete: (template: TemplateFormulaire) => void
  onDuplicate: (template: TemplateFormulaire) => void
  onToggleActive: (template: TemplateFormulaire) => void
  onPreview: (template: TemplateFormulaire) => void
  loading?: boolean
}

export default function TemplateList({
  templates,
  onEdit,
  onDelete,
  onDuplicate,
  onToggleActive,
  onPreview,
  loading = false,
}: TemplateListProps) {
  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="bg-white rounded-xl border p-4 animate-pulse">
            <div className="h-6 bg-gray-200 rounded w-3/4 mb-3" />
            <div className="h-4 bg-gray-200 rounded w-1/2 mb-2" />
            <div className="h-4 bg-gray-200 rounded w-full" />
          </div>
        ))}
      </div>
    )
  }

  if (templates.length === 0) {
    return (
      <div className="text-center py-12 bg-white rounded-xl border">
        <FileText className="w-12 h-12 mx-auto text-gray-500 mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-1">Aucun template</h3>
        <p className="text-gray-500">Creez votre premier template de formulaire</p>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {templates.map((template) => {
        const categorieInfo = CATEGORIES_FORMULAIRES[template.categorie as CategorieFormulaire]
        return (
          <div
            key={template.id}
            className={`bg-white rounded-xl border p-4 transition-shadow hover:shadow-md ${
              !template.is_active ? 'opacity-60' : ''
            }`}
          >
            {/* Header */}
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-2">
                <div
                  className="w-10 h-10 rounded-lg flex items-center justify-center"
                  style={{ backgroundColor: categorieInfo?.color + '20' }}
                >
                  <FileText
                    className="w-5 h-5"
                    style={{ color: categorieInfo?.color }}
                  />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 line-clamp-1">
                    {template.nom}
                  </h3>
                  <span
                    className="text-xs px-2 py-0.5 rounded-full"
                    style={{
                      backgroundColor: categorieInfo?.color + '20',
                      color: categorieInfo?.color,
                    }}
                  >
                    {categorieInfo?.label || template.categorie}
                  </span>
                </div>
              </div>
              <button
                onClick={() => onToggleActive(template)}
                className="p-1.5 rounded-lg hover:bg-gray-100 transition-colors"
                title={template.is_active ? 'Desactiver' : 'Activer'}
              >
                {template.is_active ? (
                  <ToggleRight className="w-5 h-5 text-green-500" />
                ) : (
                  <ToggleLeft className="w-5 h-5 text-gray-600" />
                )}
              </button>
            </div>

            {/* Description */}
            {template.description && (
              <p className="text-sm text-gray-500 mb-3 line-clamp-2">
                {template.description}
              </p>
            )}

            {/* Stats */}
            <div className="flex items-center gap-4 text-sm text-gray-500 mb-4">
              <span>{template.nombre_champs} champs</span>
              {template.a_photo && (
                <span className="flex items-center gap-1">
                  📷 Photos
                </span>
              )}
              {template.a_signature && (
                <span className="flex items-center gap-1">
                  ✍️ Signature
                </span>
              )}
            </div>

            {/* Actions */}
            <div className="flex items-center gap-2 pt-3 border-t">
              <button
                onClick={() => onPreview(template)}
                className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <Eye className="w-4 h-4" />
                Apercu
              </button>
              <button
                onClick={() => onEdit(template)}
                className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 text-sm text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
              >
                <Edit className="w-4 h-4" />
                Modifier
              </button>
              <button
                onClick={() => onDuplicate(template)}
                className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
                title="Dupliquer"
              >
                <Copy className="w-4 h-4" />
              </button>
              <button
                onClick={() => onDelete(template)}
                className="p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                title="Supprimer"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>
        )
      })}
    </div>
  )
}
