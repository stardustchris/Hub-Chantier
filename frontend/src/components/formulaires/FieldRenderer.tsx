/**
 * FieldRenderer - Rendu des champs de formulaire selon leur type
 * Utilise pour l'affichage et la saisie des champs dans les formulaires
 */

import { useState, useEffect } from 'react'
import {
  Camera,
  PenTool,
  Calendar,
  Clock,
  Hash,
  Mail,
  FileText,
  CheckSquare,
  Circle,
  List,
  Type,
} from 'lucide-react'
import type { ChampTemplate, TypeChamp } from '../../types'

interface FieldRendererProps {
  champ: ChampTemplate
  value?: string | number | boolean | string[]
  onChange: (value: string | number | boolean | string[]) => void
  readOnly?: boolean
  error?: string
}

// Mapping des icones par type de champ
const FIELD_ICONS: Record<TypeChamp, React.ElementType> = {
  text: Type,
  textarea: FileText,
  number: Hash,
  email: Mail,
  date: Calendar,
  time: Clock,
  select: List,
  checkbox: CheckSquare,
  radio: Circle,
  photo: Camera,
  signature: PenTool,
}

export default function FieldRenderer({
  champ,
  value,
  onChange,
  readOnly = false,
  error,
}: FieldRendererProps) {
  const [localValue, setLocalValue] = useState(value ?? champ.valeur_defaut ?? '')
  const Icon = FIELD_ICONS[champ.type_champ] || Type

  // Synchronize local state with prop changes
  useEffect(() => {
    setLocalValue(value ?? champ.valeur_defaut ?? '')
  }, [value, champ.valeur_defaut])

  const handleChange = (newValue: string | number | boolean | string[]) => {
    setLocalValue(newValue)
    onChange(newValue)
  }

  const inputClass = `w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
    error ? 'border-red-500' : 'border-gray-300'
  } ${readOnly ? 'bg-gray-100 cursor-not-allowed' : ''}`

  const renderField = () => {
    switch (champ.type_champ) {
      case 'text':
        return (
          <input
            type="text"
            value={localValue as string}
            onChange={(e) => handleChange(e.target.value)}
            placeholder={champ.placeholder}
            disabled={readOnly}
            className={inputClass}
            pattern={champ.validation_regex}
          />
        )

      case 'textarea':
        return (
          <textarea
            value={localValue as string}
            onChange={(e) => handleChange(e.target.value)}
            placeholder={champ.placeholder}
            disabled={readOnly}
            className={`${inputClass} min-h-[100px] resize-y`}
            rows={4}
          />
        )

      case 'number':
        return (
          <input
            type="number"
            value={localValue as number}
            onChange={(e) => handleChange(parseFloat(e.target.value) || 0)}
            placeholder={champ.placeholder}
            disabled={readOnly}
            className={inputClass}
            min={champ.min_value}
            max={champ.max_value}
          />
        )

      case 'email':
        return (
          <input
            type="email"
            value={localValue as string}
            onChange={(e) => handleChange(e.target.value)}
            placeholder={champ.placeholder || 'exemple@email.com'}
            disabled={readOnly}
            className={inputClass}
          />
        )

      case 'date':
        return (
          <input
            type="date"
            value={localValue as string}
            onChange={(e) => handleChange(e.target.value)}
            disabled={readOnly}
            className={inputClass}
          />
        )

      case 'time':
        return (
          <input
            type="time"
            value={localValue as string}
            onChange={(e) => handleChange(e.target.value)}
            disabled={readOnly}
            className={inputClass}
          />
        )

      case 'select':
        return (
          <select
            value={localValue as string}
            onChange={(e) => handleChange(e.target.value)}
            disabled={readOnly}
            className={inputClass}
          >
            <option value="">Selectionnez...</option>
            {champ.options?.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        )

      case 'checkbox':
        return (
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={localValue as boolean}
              onChange={(e) => handleChange(e.target.checked)}
              disabled={readOnly}
              className="w-5 h-5 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
            <span className="text-sm text-gray-600">{champ.placeholder || 'Oui'}</span>
          </div>
        )

      case 'radio':
        return (
          <div className="space-y-2">
            {champ.options?.map((option) => (
              <label key={option} className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name={champ.nom}
                  value={option}
                  checked={localValue === option}
                  onChange={(e) => handleChange(e.target.value)}
                  disabled={readOnly}
                  className="w-4 h-4 text-primary-600 border-gray-300 focus:ring-primary-500"
                />
                <span className="text-sm text-gray-700">{option}</span>
              </label>
            ))}
          </div>
        )

      case 'photo':
        return (
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center">
            <Camera className="w-10 h-10 mx-auto text-gray-400 mb-2" />
            <p className="text-sm text-gray-500">
              {readOnly ? 'Aucune photo' : 'Cliquez pour ajouter une photo'}
            </p>
            {!readOnly && (
              <button
                type="button"
                className="mt-2 px-4 py-2 bg-primary-50 text-primary-600 rounded-lg text-sm font-medium hover:bg-primary-100"
              >
                Prendre une photo
              </button>
            )}
          </div>
        )

      case 'signature':
        return (
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center">
            <PenTool className="w-10 h-10 mx-auto text-gray-400 mb-2" />
            <p className="text-sm text-gray-500">
              {readOnly ? 'Aucune signature' : 'Cliquez pour signer'}
            </p>
            {!readOnly && (
              <button
                type="button"
                className="mt-2 px-4 py-2 bg-primary-50 text-primary-600 rounded-lg text-sm font-medium hover:bg-primary-100"
              >
                Signer
              </button>
            )}
          </div>
        )

      default:
        return (
          <input
            type="text"
            value={localValue as string}
            onChange={(e) => handleChange(e.target.value)}
            placeholder={champ.placeholder}
            disabled={readOnly}
            className={inputClass}
          />
        )
    }
  }

  return (
    <div className="space-y-1">
      <label className="flex items-center gap-2 text-sm font-medium text-gray-700">
        <Icon className="w-4 h-4 text-gray-400" />
        {champ.label}
        {champ.obligatoire && <span className="text-red-500">*</span>}
      </label>
      {renderField()}
      {error && <p className="text-sm text-red-500">{error}</p>}
    </div>
  )
}
