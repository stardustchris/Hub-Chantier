/**
 * FormulaireModal - Modal de remplissage/visualisation de formulaire (FOR-02)
 * Permet de saisir les donnees d'un formulaire selon son template
 */

import { useState, useEffect } from 'react'
import { formatDateDayMonthYearTime, formatDateTimeShort } from '../../utils/dates'
import {
  X,
  Send,
  Save,
  Clock,
  User,
  Building2,
  FileText,
  CheckCircle,
  AlertCircle,
} from 'lucide-react'
import type {
  FormulaireRempli,
  FormulaireUpdate,
  TemplateFormulaire,
  TypeChamp,
} from '../../types'
import { CATEGORIES_FORMULAIRES, STATUTS_FORMULAIRE } from '../../types'
import FieldRenderer from './FieldRenderer'

interface FormulaireModalProps {
  isOpen: boolean
  onClose: () => void
  onSave: (data: FormulaireUpdate) => Promise<void>
  onSubmit: (signatureUrl?: string, signatureNom?: string) => Promise<void>
  formulaire: FormulaireRempli | null
  template: TemplateFormulaire | null
  readOnly?: boolean
}

export default function FormulaireModal({
  isOpen,
  onClose,
  onSave,
  onSubmit,
  formulaire,
  template,
  readOnly = false,
}: FormulaireModalProps) {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [values, setValues] = useState<Record<string, string | number | boolean | string[]>>({})
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({})

  // Initialiser les valeurs depuis le formulaire existant
  useEffect(() => {
    if (formulaire && formulaire.champs) {
      const initialValues: Record<string, string | number | boolean | string[]> = {}
      formulaire.champs.forEach((champ) => {
        initialValues[champ.nom] = champ.valeur ?? ''
      })
      setValues(initialValues)
    } else if (template && template.champs) {
      const initialValues: Record<string, string | number | boolean | string[]> = {}
      template.champs.forEach((champ) => {
        initialValues[champ.nom] = champ.valeur_defaut ?? ''
      })
      setValues(initialValues)
    }
    setError('')
    setValidationErrors({})
  }, [formulaire, template, isOpen])

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {}

    template?.champs.forEach((champ) => {
      if (champ.obligatoire) {
        const value = values[champ.nom]
        if (value === undefined || value === '' || value === null) {
          errors[champ.nom] = 'Ce champ est requis'
        }
      }
    })

    setValidationErrors(errors)
    return Object.keys(errors).length === 0
  }

  const handleSave = async () => {
    setError('')
    setIsSubmitting(true)

    try {
      const champs: { nom: string; valeur: string | number | boolean | string[]; type_champ: TypeChamp }[] = []

      template?.champs.forEach((champ) => {
        champs.push({
          nom: champ.nom,
          valeur: values[champ.nom] ?? '',
          type_champ: champ.type_champ,
        })
      })

      await onSave({ champs })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors de la sauvegarde')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleSubmit = async () => {
    if (!validateForm()) {
      setError('Veuillez remplir tous les champs obligatoires')
      return
    }

    setError('')
    setIsSubmitting(true)

    try {
      // D'abord sauvegarder
      await handleSave()
      // Puis soumettre
      await onSubmit()
      onClose()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors de la soumission')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleValueChange = (champNom: string, value: string | number | boolean | string[]) => {
    setValues((prev) => ({ ...prev, [champNom]: value }))
    // Clear validation error when field is modified
    if (validationErrors[champNom]) {
      setValidationErrors((prev) => {
        const newErrors = { ...prev }
        delete newErrors[champNom]
        return newErrors
      })
    }
  }

  if (!isOpen || !template) return null

  const categorieInfo = CATEGORIES_FORMULAIRES[template.categorie]
  const statutInfo = formulaire ? STATUTS_FORMULAIRE[formulaire.statut] : null
  const isEditable = !readOnly && (!formulaire || formulaire.statut === 'brouillon')

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="fixed inset-0 bg-black/50" onClick={onClose} />
      <div className="relative bg-white rounded-xl shadow-xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b">
          <div className="flex items-center gap-3">
            <div
              className="w-10 h-10 rounded-lg flex items-center justify-center"
              style={{ backgroundColor: categorieInfo?.color + '20' }}
            >
              <FileText className="w-5 h-5" style={{ color: categorieInfo?.color }} />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-900">{template.nom}</h2>
              {statutInfo && (
                <span
                  className="text-xs px-2 py-0.5 rounded-full"
                  style={{
                    backgroundColor: statutInfo.bgColor,
                    color: statutInfo.color,
                  }}
                >
                  {statutInfo.label}
                </span>
              )}
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Metadata */}
        {formulaire && (
          <div className="px-6 py-3 bg-gray-50 border-b flex flex-wrap items-center gap-4 text-sm text-gray-600">
            {formulaire.chantier_nom && (
              <span className="flex items-center gap-1.5">
                <Building2 className="w-4 h-4" />
                {formulaire.chantier_nom}
              </span>
            )}
            {formulaire.user_nom && (
              <span className="flex items-center gap-1.5">
                <User className="w-4 h-4" />
                {formulaire.user_nom}
              </span>
            )}
            <span className="flex items-center gap-1.5">
              <Clock className="w-4 h-4" />
              {formatDateDayMonthYearTime(formulaire.created_at)}
            </span>
          </div>
        )}

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {error && (
            <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-lg text-sm flex items-center gap-2">
              <AlertCircle className="w-5 h-5 flex-shrink-0" />
              {error}
            </div>
          )}

          {template.description && (
            <p className="text-sm text-gray-500 mb-6">{template.description}</p>
          )}

          {/* Champs du formulaire */}
          <div className="space-y-5">
            {template.champs
              .sort((a, b) => a.ordre - b.ordre)
              .map((champ) => {
                // Pour les champs photo, filtrer les photos attachees par champ_nom
                const champPhotos = (champ.type_champ === 'photo' || champ.type_champ === 'photo_multiple')
                  ? formulaire?.photos.filter((p) => p.champ_nom === champ.nom) || []
                  : undefined

                return (
                  <FieldRenderer
                    key={champ.nom}
                    champ={champ}
                    value={values[champ.nom]}
                    onChange={(value) => handleValueChange(champ.nom, value)}
                    readOnly={!isEditable}
                    error={validationErrors[champ.nom]}
                    photos={champPhotos}
                  />
                )
              })}
          </div>

          {/* Photos non liees a un champ photo (evite la duplication) */}
          {formulaire && (() => {
            const photoFieldNames = new Set(
              template.champs
                .filter((c) => c.type_champ === 'photo' || c.type_champ === 'photo_multiple')
                .map((c) => c.nom)
            )
            const unmatchedPhotos = formulaire.photos.filter(
              (p) => !photoFieldNames.has(p.champ_nom)
            )
            return unmatchedPhotos.length > 0 ? (
              <div className="mt-6 pt-6 border-t">
                <h3 className="font-medium text-gray-900 mb-3">
                  Photos ({unmatchedPhotos.length})
                </h3>
                <div className="grid grid-cols-3 gap-3">
                  {unmatchedPhotos.map((photo, index) => (
                    <div key={index} className="aspect-square bg-gray-100 rounded-lg overflow-hidden">
                      <img
                        src={photo.url}
                        alt={photo.nom_fichier}
                        className="w-full h-full object-cover"
                      />
                    </div>
                  ))}
                </div>
              </div>
            ) : null
          })()}

          {/* Signature */}
          {formulaire?.est_signe && (
            <div className="mt-6 pt-6 border-t">
              <h3 className="font-medium text-gray-900 mb-2 flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-500" />
                Signature
              </h3>
              <p className="text-sm text-gray-600">
                Signe par {formulaire.signature_nom}
                {formulaire.signature_timestamp && (
                  <span className="text-gray-600">
                    {' '}le {formatDateTimeShort(formulaire.signature_timestamp)}
                  </span>
                )}
              </p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between gap-3 px-6 py-4 border-t bg-gray-50">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            disabled={isSubmitting}
          >
            {isEditable ? 'Annuler' : 'Fermer'}
          </button>

          {isEditable && (
            <div className="flex items-center gap-2">
              <button
                onClick={handleSave}
                disabled={isSubmitting}
                className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
              >
                <Save className="w-4 h-4" />
                Sauvegarder
              </button>
              <button
                onClick={handleSubmit}
                disabled={isSubmitting}
                className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50"
              >
                <Send className="w-4 h-4" />
                Soumettre
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
