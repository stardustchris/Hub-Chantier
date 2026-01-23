/**
 * TemplateModal - Modal de creation/edition de template (FOR-01)
 * Permet de definir les champs et proprietes d'un template
 */

import { useState, useEffect } from 'react'
import {
  X,
  Plus,
  Trash2,
  GripVertical,
  ChevronDown,
  ChevronUp,
} from 'lucide-react'
import type {
  TemplateFormulaire,
  TemplateFormulaireCreate,
  TemplateFormulaireUpdate,
  ChampTemplate,
  CategorieFormulaire,
  TypeChamp,
} from '../../types'
import { CATEGORIES_FORMULAIRES, TYPES_CHAMPS } from '../../types'

interface TemplateModalProps {
  isOpen: boolean
  onClose: () => void
  onSave: (data: TemplateFormulaireCreate | TemplateFormulaireUpdate) => Promise<void>
  template?: TemplateFormulaire | null
}

const DEFAULT_CHAMP: ChampTemplate = {
  nom: '',
  label: '',
  type_champ: 'text',
  obligatoire: false,
  ordre: 0,
  placeholder: '',
  options: [],
}

export default function TemplateModal({
  isOpen,
  onClose,
  onSave,
  template,
}: TemplateModalProps) {
  const isEditing = !!template
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [expandedChamp, setExpandedChamp] = useState<number | null>(null)

  const [formData, setFormData] = useState<TemplateFormulaireCreate>({
    nom: '',
    categorie: 'autre',
    description: '',
    champs: [],
  })

  useEffect(() => {
    if (template) {
      setFormData({
        nom: template.nom,
        categorie: template.categorie,
        description: template.description || '',
        champs: template.champs || [],
      })
    } else {
      setFormData({
        nom: '',
        categorie: 'autre',
        description: '',
        champs: [],
      })
    }
    setError('')
    setExpandedChamp(null)
  }, [template, isOpen])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    // Validation
    if (!formData.nom.trim()) {
      setError('Le nom du template est requis')
      return
    }

    // Valider les champs
    const champs = formData.champs || []
    for (let i = 0; i < champs.length; i++) {
      const champ = champs[i]
      if (!champ.nom.trim() || !champ.label.trim()) {
        setError(`Le champ ${i + 1} doit avoir un nom et un label`)
        return
      }
      if ((champ.type_champ === 'select' || champ.type_champ === 'radio') &&
          (!champ.options || champ.options.length === 0)) {
        setError(`Le champ "${champ.label}" doit avoir au moins une option`)
        return
      }
    }

    setIsSubmitting(true)
    try {
      // Mettre a jour les ordres
      const champsWithOrder = formData.champs?.map((c, idx) => ({
        ...c,
        ordre: idx,
        nom: c.nom || c.label.toLowerCase().replace(/[^a-z0-9]/g, '_'),
      }))

      await onSave({
        ...formData,
        champs: champsWithOrder,
      })
      onClose()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors de la sauvegarde')
    } finally {
      setIsSubmitting(false)
    }
  }

  const addChamp = () => {
    const newChamp: ChampTemplate = {
      ...DEFAULT_CHAMP,
      ordre: formData.champs?.length || 0,
    }
    setFormData({
      ...formData,
      champs: [...(formData.champs || []), newChamp],
    })
    setExpandedChamp((formData.champs?.length || 0))
  }

  const updateChamp = (index: number, updates: Partial<ChampTemplate>) => {
    const newChamps = [...(formData.champs || [])]
    newChamps[index] = { ...newChamps[index], ...updates }
    setFormData({ ...formData, champs: newChamps })
  }

  const removeChamp = (index: number) => {
    const newChamps = (formData.champs || []).filter((_, i) => i !== index)
    setFormData({ ...formData, champs: newChamps })
    if (expandedChamp === index) {
      setExpandedChamp(null)
    }
  }

  const moveChamp = (index: number, direction: 'up' | 'down') => {
    const newChamps = [...(formData.champs || [])]
    const newIndex = direction === 'up' ? index - 1 : index + 1
    if (newIndex < 0 || newIndex >= newChamps.length) return

    const temp = newChamps[index]
    newChamps[index] = newChamps[newIndex]
    newChamps[newIndex] = temp

    setFormData({ ...formData, champs: newChamps })
    setExpandedChamp(newIndex)
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="fixed inset-0 bg-black/50" onClick={onClose} />
      <div className="relative bg-white rounded-xl shadow-xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b">
          <h2 className="text-xl font-semibold text-gray-900">
            {isEditing ? 'Modifier le template' : 'Nouveau template'}
          </h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto p-6">
          {error && (
            <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-lg text-sm">
              {error}
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
                value={formData.nom}
                onChange={(e) => setFormData({ ...formData, nom: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="Ex: Rapport journalier"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Categorie <span className="text-red-500">*</span>
              </label>
              <select
                value={formData.categorie}
                onChange={(e) =>
                  setFormData({ ...formData, categorie: e.target.value as CategorieFormulaire })
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
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
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
                onClick={addChamp}
                className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
              >
                <Plus className="w-4 h-4" />
                Ajouter un champ
              </button>
            </div>

            <div className="space-y-2">
              {(formData.champs || []).map((champ, index) => (
                <div
                  key={index}
                  className="border rounded-lg overflow-hidden"
                >
                  {/* Champ header */}
                  <div
                    className="flex items-center gap-2 px-3 py-2 bg-gray-50 cursor-pointer"
                    onClick={() => setExpandedChamp(expandedChamp === index ? null : index)}
                  >
                    <GripVertical className="w-4 h-4 text-gray-400" />
                    <span className="flex-1 font-medium text-sm">
                      {champ.label || `Champ ${index + 1}`}
                    </span>
                    <span className="text-xs text-gray-500 bg-gray-200 px-2 py-0.5 rounded">
                      {TYPES_CHAMPS[champ.type_champ]?.label || champ.type_champ}
                    </span>
                    {champ.obligatoire && (
                      <span className="text-xs text-red-500">*</span>
                    )}
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation()
                        moveChamp(index, 'up')
                      }}
                      disabled={index === 0}
                      className="p-1 hover:bg-gray-200 rounded disabled:opacity-30"
                    >
                      <ChevronUp className="w-4 h-4" />
                    </button>
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation()
                        moveChamp(index, 'down')
                      }}
                      disabled={index === (formData.champs?.length || 0) - 1}
                      className="p-1 hover:bg-gray-200 rounded disabled:opacity-30"
                    >
                      <ChevronDown className="w-4 h-4" />
                    </button>
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation()
                        removeChamp(index)
                      }}
                      className="p-1 hover:bg-red-100 text-red-500 rounded"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>

                  {/* Champ expanded content */}
                  {expandedChamp === index && (
                    <div className="p-4 space-y-3 border-t">
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <label className="block text-xs font-medium text-gray-600 mb-1">
                            Label <span className="text-red-500">*</span>
                          </label>
                          <input
                            type="text"
                            value={champ.label}
                            onChange={(e) => updateChamp(index, { label: e.target.value })}
                            className="w-full px-2 py-1.5 text-sm border rounded focus:ring-1 focus:ring-primary-500"
                            placeholder="Label affiche"
                          />
                        </div>
                        <div>
                          <label className="block text-xs font-medium text-gray-600 mb-1">
                            Nom technique
                          </label>
                          <input
                            type="text"
                            value={champ.nom}
                            onChange={(e) => updateChamp(index, { nom: e.target.value })}
                            className="w-full px-2 py-1.5 text-sm border rounded focus:ring-1 focus:ring-primary-500"
                            placeholder="nom_technique"
                          />
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <label className="block text-xs font-medium text-gray-600 mb-1">
                            Type de champ
                          </label>
                          <select
                            value={champ.type_champ}
                            onChange={(e) =>
                              updateChamp(index, { type_champ: e.target.value as TypeChamp })
                            }
                            className="w-full px-2 py-1.5 text-sm border rounded focus:ring-1 focus:ring-primary-500"
                          >
                            {Object.entries(TYPES_CHAMPS).map(([key, value]) => (
                              <option key={key} value={key}>
                                {value.label}
                              </option>
                            ))}
                          </select>
                        </div>
                        <div>
                          <label className="block text-xs font-medium text-gray-600 mb-1">
                            Placeholder
                          </label>
                          <input
                            type="text"
                            value={champ.placeholder || ''}
                            onChange={(e) => updateChamp(index, { placeholder: e.target.value })}
                            className="w-full px-2 py-1.5 text-sm border rounded focus:ring-1 focus:ring-primary-500"
                            placeholder="Texte d'aide"
                          />
                        </div>
                      </div>

                      {/* Options pour select/radio */}
                      {(champ.type_champ === 'select' || champ.type_champ === 'radio') && (
                        <div>
                          <label className="block text-xs font-medium text-gray-600 mb-1">
                            Options (une par ligne)
                          </label>
                          <textarea
                            value={(champ.options || []).join('\n')}
                            onChange={(e) =>
                              updateChamp(index, {
                                options: e.target.value.split('\n').filter((o) => o.trim()),
                              })
                            }
                            className="w-full px-2 py-1.5 text-sm border rounded focus:ring-1 focus:ring-primary-500"
                            rows={3}
                            placeholder="Option 1&#10;Option 2&#10;Option 3"
                          />
                        </div>
                      )}

                      {/* Min/Max pour number */}
                      {champ.type_champ === 'number' && (
                        <div className="grid grid-cols-2 gap-3">
                          <div>
                            <label className="block text-xs font-medium text-gray-600 mb-1">
                              Valeur min
                            </label>
                            <input
                              type="number"
                              value={champ.min_value ?? ''}
                              onChange={(e) =>
                                updateChamp(index, {
                                  min_value: e.target.value ? parseFloat(e.target.value) : undefined,
                                })
                              }
                              className="w-full px-2 py-1.5 text-sm border rounded focus:ring-1 focus:ring-primary-500"
                            />
                          </div>
                          <div>
                            <label className="block text-xs font-medium text-gray-600 mb-1">
                              Valeur max
                            </label>
                            <input
                              type="number"
                              value={champ.max_value ?? ''}
                              onChange={(e) =>
                                updateChamp(index, {
                                  max_value: e.target.value ? parseFloat(e.target.value) : undefined,
                                })
                              }
                              className="w-full px-2 py-1.5 text-sm border rounded focus:ring-1 focus:ring-primary-500"
                            />
                          </div>
                        </div>
                      )}

                      <div className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          id={`obligatoire-${index}`}
                          checked={champ.obligatoire}
                          onChange={(e) => updateChamp(index, { obligatoire: e.target.checked })}
                          className="w-4 h-4 rounded border-gray-300 text-primary-600"
                        />
                        <label
                          htmlFor={`obligatoire-${index}`}
                          className="text-sm text-gray-700"
                        >
                          Champ obligatoire
                        </label>
                      </div>
                    </div>
                  )}
                </div>
              ))}

              {(formData.champs?.length || 0) === 0 && (
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
            disabled={isSubmitting}
          >
            Annuler
          </button>
          <button
            onClick={handleSubmit}
            disabled={isSubmitting}
            className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50"
          >
            {isSubmitting ? 'Enregistrement...' : isEditing ? 'Enregistrer' : 'Creer'}
          </button>
        </div>
      </div>
    </div>
  )
}
