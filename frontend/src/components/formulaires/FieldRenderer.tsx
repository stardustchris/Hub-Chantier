/**
 * FieldRenderer - Rendu des champs de formulaire selon leur type
 * Utilise pour l'affichage et la saisie des champs dans les formulaires
 *
 * Refactored: Utilise un pattern de mapping de composants au lieu d'un switch
 */

import { useState, useEffect, memo, useCallback } from 'react'
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
import PhotoCapture from './PhotoCapture'
import SignaturePad from './SignaturePad'

interface FieldRendererProps {
  champ: ChampTemplate
  value?: string | number | boolean | string[]
  onChange: (value: string | number | boolean | string[]) => void
  readOnly?: boolean
  error?: string
}

// Props communes pour tous les composants de champ
interface FieldComponentProps {
  champ: ChampTemplate
  value: string | number | boolean | string[]
  onChange: (value: string | number | boolean | string[]) => void
  readOnly: boolean
  inputClass: string
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

// Composants de champ individuels
const TextField = memo(({ champ, value, onChange, readOnly, inputClass }: FieldComponentProps) => (
  <input
    type="text"
    value={value as string}
    onChange={(e) => onChange(e.target.value)}
    placeholder={champ.placeholder}
    disabled={readOnly}
    className={inputClass}
    pattern={champ.validation_regex}
  />
))
TextField.displayName = 'TextField'

const TextareaField = memo(({ champ, value, onChange, readOnly, inputClass }: FieldComponentProps) => (
  <textarea
    value={value as string}
    onChange={(e) => onChange(e.target.value)}
    placeholder={champ.placeholder}
    disabled={readOnly}
    className={`${inputClass} min-h-[100px] resize-y`}
    rows={4}
  />
))
TextareaField.displayName = 'TextareaField'

const NumberField = memo(({ champ, value, onChange, readOnly, inputClass }: FieldComponentProps) => (
  <input
    type="number"
    value={value as number}
    onChange={(e) => onChange(parseFloat(e.target.value) || 0)}
    placeholder={champ.placeholder}
    disabled={readOnly}
    className={inputClass}
    min={champ.min_value}
    max={champ.max_value}
  />
))
NumberField.displayName = 'NumberField'

const EmailField = memo(({ champ, value, onChange, readOnly, inputClass }: FieldComponentProps) => (
  <input
    type="email"
    value={value as string}
    onChange={(e) => onChange(e.target.value)}
    placeholder={champ.placeholder || 'exemple@email.com'}
    disabled={readOnly}
    className={inputClass}
  />
))
EmailField.displayName = 'EmailField'

const DateField = memo(({ value, onChange, readOnly, inputClass }: FieldComponentProps) => (
  <input
    type="date"
    value={value as string}
    onChange={(e) => onChange(e.target.value)}
    disabled={readOnly}
    className={inputClass}
  />
))
DateField.displayName = 'DateField'

const TimeField = memo(({ value, onChange, readOnly, inputClass }: FieldComponentProps) => (
  <input
    type="time"
    value={value as string}
    onChange={(e) => onChange(e.target.value)}
    disabled={readOnly}
    className={inputClass}
  />
))
TimeField.displayName = 'TimeField'

const SelectField = memo(({ champ, value, onChange, readOnly, inputClass }: FieldComponentProps) => (
  <select
    value={value as string}
    onChange={(e) => onChange(e.target.value)}
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
))
SelectField.displayName = 'SelectField'

const CheckboxField = memo(({ champ, value, onChange, readOnly }: FieldComponentProps) => (
  <div className="flex items-center gap-2">
    <input
      type="checkbox"
      checked={value as boolean}
      onChange={(e) => onChange(e.target.checked)}
      disabled={readOnly}
      className="w-5 h-5 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
    />
    <span className="text-sm text-gray-600">{champ.placeholder || 'Oui'}</span>
  </div>
))
CheckboxField.displayName = 'CheckboxField'

const RadioField = memo(({ champ, value, onChange, readOnly }: FieldComponentProps) => (
  <div className="space-y-2">
    {champ.options?.map((option) => (
      <label key={option} className="flex items-center gap-2 cursor-pointer">
        <input
          type="radio"
          name={champ.nom}
          value={option}
          checked={value === option}
          onChange={(e) => onChange(e.target.value)}
          disabled={readOnly}
          className="w-4 h-4 text-primary-600 border-gray-300 focus:ring-primary-500"
        />
        <span className="text-sm text-gray-700">{option}</span>
      </label>
    ))}
  </div>
))
RadioField.displayName = 'RadioField'

const PhotoField = memo(({ champ, value, onChange, readOnly }: FieldComponentProps) => (
  <PhotoCapture
    value={value as string}
    onChange={(val) => onChange(val)}
    readOnly={readOnly}
    label={champ.label}
  />
))
PhotoField.displayName = 'PhotoField'

const SignatureField = memo(({ value, onChange, readOnly }: FieldComponentProps) => (
  <SignaturePad
    value={value as string}
    onChange={(val) => onChange(val)}
    readOnly={readOnly}
  />
))
SignatureField.displayName = 'SignatureField'

// Mapping des composants par type de champ
const FIELD_COMPONENTS: Record<TypeChamp, React.ComponentType<FieldComponentProps>> = {
  text: TextField,
  textarea: TextareaField,
  number: NumberField,
  email: EmailField,
  date: DateField,
  time: TimeField,
  select: SelectField,
  checkbox: CheckboxField,
  radio: RadioField,
  photo: PhotoField,
  signature: SignatureField,
}

function FieldRenderer({
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

  const handleChange = useCallback((newValue: string | number | boolean | string[]) => {
    setLocalValue(newValue)
    onChange(newValue)
  }, [onChange])

  const inputClass = `w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
    error ? 'border-red-500' : 'border-gray-300'
  } ${readOnly ? 'bg-gray-100 cursor-not-allowed' : ''}`

  // Obtenir le composant de champ ou utiliser TextField par defaut
  const FieldComponent = FIELD_COMPONENTS[champ.type_champ] || TextField

  return (
    <div className="space-y-1">
      <label className="flex items-center gap-2 text-sm font-medium text-gray-700">
        <Icon className="w-4 h-4 text-gray-400" />
        {champ.label}
        {champ.obligatoire && <span className="text-red-500">*</span>}
      </label>
      <FieldComponent
        champ={champ}
        value={localValue}
        onChange={handleChange}
        readOnly={readOnly}
        inputClass={inputClass}
      />
      {error && <p className="text-sm text-red-500">{error}</p>}
    </div>
  )
}

export default memo(FieldRenderer)
