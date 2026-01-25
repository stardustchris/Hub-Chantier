/**
 * Hook useTemplateForm - Gestion de l'état du formulaire de template
 */

import { useState, useEffect } from 'react'
import type {
  TemplateFormulaire,
  TemplateFormulaireCreate,
  TemplateFormulaireUpdate,
  ChampTemplate,
  CategorieFormulaire,
} from '../../types'

interface UseTemplateFormProps {
  template?: TemplateFormulaire | null
  isOpen: boolean
  onSave: (data: TemplateFormulaireCreate | TemplateFormulaireUpdate) => Promise<void>
  onClose: () => void
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

export function useTemplateForm({
  template,
  isOpen,
  onSave,
  onClose,
}: UseTemplateFormProps) {
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
      if (
        (champ.type_champ === 'select' || champ.type_champ === 'radio') &&
        (!champ.options || champ.options.length === 0)
      ) {
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
    setExpandedChamp(formData.champs?.length || 0)
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

  const updateFormField = (field: keyof TemplateFormulaireCreate, value: string | CategorieFormulaire) => {
    setFormData({ ...formData, [field]: value })
  }

  return {
    // State
    formData,
    isEditing,
    isSubmitting,
    error,
    expandedChamp,
    // Actions
    handleSubmit,
    addChamp,
    updateChamp,
    removeChamp,
    moveChamp,
    setExpandedChamp,
    updateFormField,
  }
}
