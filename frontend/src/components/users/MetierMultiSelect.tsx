/**
 * MetierMultiSelect - Composant de sélection multi-métiers avec badges colorés
 * Permet de sélectionner plusieurs métiers avec limite de 5
 */

import { useState, useRef, useEffect } from 'react'
import { X, ChevronDown } from 'lucide-react'
import type { Metier } from '../../types'
import { METIERS } from '../../types'

const MAX_METIERS = 5

interface MetierMultiSelectProps {
  value: Metier[]
  onChange: (metiers: Metier[]) => void
  disabled?: boolean
}

export function MetierMultiSelect({ value, onChange, disabled = false }: MetierMultiSelectProps) {
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  // Fermer le dropdown au clic extérieur
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
      return () => document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isOpen])

  const handleAdd = (metier: Metier) => {
    if (value.includes(metier)) {
      return
    }
    if (value.length >= MAX_METIERS) {
      return
    }
    onChange([...value, metier])
    setIsOpen(false)
  }

  const handleRemove = (metier: Metier) => {
    onChange(value.filter(m => m !== metier))
  }

  // Métiers disponibles (non sélectionnés)
  const availableMetiers = (Object.keys(METIERS) as Metier[]).filter(
    metier => !value.includes(metier)
  )

  return (
    <div className="space-y-2">
      {/* Badges des métiers sélectionnés */}
      {value.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {value.map(metier => {
            const metierInfo = METIERS[metier]
            return (
              <span
                key={metier}
                className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium"
                style={{
                  backgroundColor: metierInfo.color + '20',
                  color: metierInfo.color,
                }}
              >
                {metierInfo.label}
                {!disabled && (
                  <button
                    type="button"
                    onClick={() => handleRemove(metier)}
                    className="hover:bg-black/10 rounded-full p-0.5 transition-colors"
                    aria-label={`Retirer ${metierInfo.label}`}
                  >
                    <X className="w-3 h-3" />
                  </button>
                )}
              </span>
            )
          })}
        </div>
      )}

      {/* Dropdown pour ajouter un métier */}
      {!disabled && (
        <div ref={dropdownRef} className="relative">
          <button
            type="button"
            onClick={() => setIsOpen(!isOpen)}
            disabled={value.length >= MAX_METIERS}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-left flex items-center justify-between hover:bg-gray-50 transition-colors disabled:bg-gray-100 disabled:cursor-not-allowed"
          >
            <span className="text-sm text-gray-600">
              {value.length >= MAX_METIERS
                ? `Maximum ${MAX_METIERS} métiers atteint`
                : value.length === 0
                ? 'Sélectionner un métier'
                : 'Ajouter un métier'}
            </span>
            <ChevronDown
              className={`w-4 h-4 text-gray-600 transition-transform ${
                isOpen ? 'rotate-180' : ''
              }`}
            />
          </button>

          {/* Liste déroulante */}
          {isOpen && availableMetiers.length > 0 && (
            <div className="absolute z-10 mt-1 w-full bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto">
              {availableMetiers.map(metier => {
                const metierInfo = METIERS[metier]
                return (
                  <button
                    key={metier}
                    type="button"
                    onClick={() => handleAdd(metier)}
                    className="w-full px-3 py-2 text-left hover:bg-gray-50 transition-colors flex items-center gap-2"
                  >
                    <span
                      className="w-3 h-3 rounded-full flex-shrink-0"
                      style={{ backgroundColor: metierInfo.color }}
                    />
                    <span className="text-sm text-gray-700">{metierInfo.label}</span>
                  </button>
                )
              })}
            </div>
          )}
        </div>
      )}

      {/* Indication du nombre de métiers */}
      <p className="text-xs text-gray-500">
        {value.length} / {MAX_METIERS} métiers sélectionnés
      </p>
    </div>
  )
}

export default MetierMultiSelect
