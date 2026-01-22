import { useState, useEffect } from 'react'
import { AlertCircle, Check } from 'lucide-react'
import {
  COUNTRY_CODES,
  isValidPhone,
  formatPhone,
  detectCountry,
  getPhoneValidationError,
} from '../utils/phone'

interface PhoneInputProps {
  /** Valeur actuelle */
  value: string
  /** Callback de changement */
  onChange: (value: string) => void
  /** Label du champ */
  label?: string
  /** Placeholder */
  placeholder?: string
  /** Classes CSS additionnelles */
  className?: string
  /** Requis */
  required?: boolean
  /** Désactivé */
  disabled?: boolean
}

/**
 * Composant de saisie de téléphone international (USR-08).
 * Avec sélecteur de pays et validation en temps réel.
 */
export default function PhoneInput({
  value,
  onChange,
  label = 'Téléphone',
  placeholder = '06 12 34 56 78',
  className = '',
  required = false,
  disabled = false,
}: PhoneInputProps) {
  const [selectedCountry, setSelectedCountry] = useState<typeof COUNTRY_CODES[number]>(COUNTRY_CODES[0])
  const [showDropdown, setShowDropdown] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isTouched, setIsTouched] = useState(false)

  // Détecter le pays automatiquement
  useEffect(() => {
    if (value) {
      const detected = detectCountry(value)
      if (detected) {
        setSelectedCountry(detected)
      }
    }
  }, [])

  // Valider à la saisie
  useEffect(() => {
    if (isTouched) {
      const err = getPhoneValidationError(value)
      setError(err)
    }
  }, [value, isTouched])

  const handleCountrySelect = (country: typeof COUNTRY_CODES[number]) => {
    setSelectedCountry(country)
    setShowDropdown(false)

    // Remplacer le code pays si déjà présent
    if (value) {
      const hasPlus = value.startsWith('+')
      if (hasPlus) {
        // Trouver et remplacer le code pays actuel
        for (const c of COUNTRY_CODES) {
          if (value.startsWith(c.code)) {
            onChange(value.replace(c.code, country.code))
            return
          }
        }
      }
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    let newValue = e.target.value

    // Permettre seulement chiffres, +, espaces et tirets
    newValue = newValue.replace(/[^0-9+\-.\s()]/g, '')

    onChange(newValue)
    setIsTouched(true)
  }

  const handleBlur = () => {
    setIsTouched(true)
    // Formater le numéro à la perte de focus
    if (value && isValidPhone(value)) {
      onChange(formatPhone(value))
    }
  }

  const isValid = !error && value && isValidPhone(value)

  return (
    <div className={className}>
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}

      <div className="relative flex">
        {/* Sélecteur pays */}
        <div className="relative">
          <button
            type="button"
            onClick={() => !disabled && setShowDropdown(!showDropdown)}
            disabled={disabled}
            className="h-full px-3 border border-r-0 border-gray-300 rounded-l-lg bg-gray-50 hover:bg-gray-100 flex items-center gap-1 text-sm disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span>{selectedCountry.flag}</span>
            <span className="text-gray-600">{selectedCountry.code}</span>
          </button>

          {/* Dropdown pays */}
          {showDropdown && (
            <div className="absolute top-full left-0 mt-1 w-56 bg-white border border-gray-200 rounded-lg shadow-lg z-50 max-h-60 overflow-auto">
              {COUNTRY_CODES.map((country) => (
                <button
                  key={country.code}
                  type="button"
                  onClick={() => handleCountrySelect(country)}
                  className={`w-full px-3 py-2 text-left hover:bg-gray-50 flex items-center gap-2 text-sm ${
                    selectedCountry.code === country.code ? 'bg-primary-50' : ''
                  }`}
                >
                  <span>{country.flag}</span>
                  <span className="font-medium">{country.code}</span>
                  <span className="text-gray-500">{country.country}</span>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Input téléphone */}
        <div className="flex-1 relative">
          <input
            type="tel"
            value={value}
            onChange={handleChange}
            onBlur={handleBlur}
            placeholder={placeholder}
            disabled={disabled}
            className={`w-full px-3 py-2 border rounded-r-lg focus:outline-none focus:ring-2 focus:ring-primary-500 ${
              error && isTouched
                ? 'border-red-300 focus:ring-red-500'
                : isValid
                ? 'border-green-300'
                : 'border-gray-300'
            } disabled:bg-gray-100 disabled:cursor-not-allowed`}
          />

          {/* Indicateur de validation */}
          {isTouched && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2">
              {error ? (
                <AlertCircle className="w-4 h-4 text-red-500" />
              ) : isValid ? (
                <Check className="w-4 h-4 text-green-500" />
              ) : null}
            </div>
          )}
        </div>
      </div>

      {/* Message d'erreur */}
      {error && isTouched && (
        <p className="mt-1 text-sm text-red-500 flex items-center gap-1">
          <AlertCircle className="w-3 h-3" />
          {error}
        </p>
      )}
    </div>
  )
}
