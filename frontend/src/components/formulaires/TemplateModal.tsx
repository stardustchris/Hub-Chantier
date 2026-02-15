/**
 * TemplateModal - Modal de creation/edition de template (FOR-01)
 * Refactorisé pour utiliser des sous-composants (P1-5)
 */

import { X, Plus } from 'lucide-react'
import type {
  TemplateFormulaire,
  TemplateFormulaireCreate,
  TemplateFormulaireUpdate,
  CategorieFormulaire,
} from '../../types'
import { CATEGORIES_FORMULAIRES } from '../../types'
import { useTemplateForm } from './useTemplateForm'
import { ChampEditor } from './ChampEditor'
import { useFocusTrap } from '../../hooks/useFocusTrap'

interface TemplateModalProps {
  isOpen: boolean
  onClose: () => void
  onSave: (data: TemplateFormulaireCreate | TemplateFormulaireUpdate) => Promise<void>
  template?: TemplateFormulaire | null
}

export default function TemplateModal({
  isOpen,
  onClose,
  onSave,
  template,
}: TemplateModalProps) {
  const form = useTemplateForm({
    template,
    isOpen,
    onSave,
    onClose,
  })
  const focusTrapRef = useFocusTrap({ enabled: isOpen, onClose })

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="fixed inset-0 bg-black/50" onClick={onClose} />
      <div ref={focusTrapRef} role="dialog" aria-modal="true" aria-labelledby="modal-title" className="relative bg-white rounded-xl shadow-xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b">
          <h2 id="modal-title" className="text-xl font-semibold text-gray-900">
            {form.isEditing ? 'Modifier le template' : 'Nouveau template'}
          </h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <form onSubmit={form.handleSubmit} className="flex-1 overflow-y-auto p-6">
          {form.error && (
            <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-lg text-sm">
              {form.error}
            </div>
          )}

          {/* Informations de base */}
          <div className="space-y-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nom du template <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={form.formData.nom}
                onChange={(e) => form.updateFormField('nom', e.target.value)}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="Ex: Rapport journalier"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Categorie <span className="text-red-500">*</span>
              </label>
              <select
                value={form.formData.categorie}
                onChange={(e) =>
                  form.updateFormField('categorie', e.target.value as CategorieFormulaire)
                }
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                {Object.entries(CATEGORIES_FORMULAIRES).map(([key, value]) => (
                  <option key={key} value={key}>
                    {value.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description
              </label>
              <textarea
                value={form.formData.description}
                onChange={(e) => form.updateFormField('description', e.target.value)}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="Description du template..."
                rows={2}
              />
            </div>
          </div>

          {/* Champs */}
          <div className="border-t pt-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-900">Champs du formulaire</h3>
              <button
                type="button"
                onClick={form.addChamp}
                className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
              >
                <Plus className="w-4 h-4" />
                Ajouter un champ
              </button>
            </div>

            <div className="space-y-2">
              {(form.formData.champs || []).map((champ, index) => (
                <ChampEditor
                  key={index}
                  champ={champ}
                  index={index}
                  isExpanded={form.expandedChamp === index}
                  isFirst={index === 0}
                  isLast={index === (form.formData.champs?.length || 0) - 1}
                  onToggleExpand={() =>
                    form.setExpandedChamp(form.expandedChamp === index ? null : index)
                  }
                  onUpdate={(updates) => form.updateChamp(index, updates)}
                  onRemove={() => form.removeChamp(index)}
                  onMoveUp={() => form.moveChamp(index, 'up')}
                  onMoveDown={() => form.moveChamp(index, 'down')}
                />
              ))}

              {(form.formData.champs?.length || 0) === 0 && (
                <div className="text-center py-8 text-gray-500 border-2 border-dashed rounded-lg">
                  <p>Aucun champ defini</p>
                  <p className="text-sm">Cliquez sur "Ajouter un champ" pour commencer</p>
                </div>
              )}
            </div>
          </div>
        </form>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 px-6 py-4 border-t bg-gray-50">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            disabled={form.isSubmitting}
          >
            Annuler
          </button>
          <button
            onClick={form.handleSubmit}
            disabled={form.isSubmitting}
            className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50"
          >
            {form.isSubmitting ? 'Enregistrement...' : form.isEditing ? 'Enregistrer' : 'Creer'}
          </button>
        </div>
      </div>
    </div>
  )
}
