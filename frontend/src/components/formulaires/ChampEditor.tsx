/**
 * ChampEditor - Éditeur de champ pour TemplateModal
 * Permet de configurer un champ de formulaire (type, label, options, etc.)
 */

import {
  GripVertical,
  ChevronDown,
  ChevronUp,
  Trash2,
} from 'lucide-react'
import type { ChampTemplate, TypeChamp } from '../../types'
import { TYPES_CHAMPS } from '../../types'

interface ChampEditorProps {
  champ: ChampTemplate
  index: number
  isExpanded: boolean
  isFirst: boolean
  isLast: boolean
  onToggleExpand: () => void
  onUpdate: (updates: Partial<ChampTemplate>) => void
  onRemove: () => void
  onMoveUp: () => void
  onMoveDown: () => void
}

export function ChampEditor({
  champ,
  index,
  isExpanded,
  isFirst,
  isLast,
  onToggleExpand,
  onUpdate,
  onRemove,
  onMoveUp,
  onMoveDown,
}: ChampEditorProps) {
  return (
    <div className="border rounded-lg overflow-hidden">
      {/* Champ header */}
      <div
        className="flex items-center gap-2 px-3 py-2 bg-gray-50 cursor-pointer"
        onClick={onToggleExpand}
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
            onMoveUp()
          }}
          disabled={isFirst}
          className="p-1 hover:bg-gray-200 rounded disabled:opacity-30"
        >
          <ChevronUp className="w-4 h-4" />
        </button>
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation()
            onMoveDown()
          }}
          disabled={isLast}
          className="p-1 hover:bg-gray-200 rounded disabled:opacity-30"
        >
          <ChevronDown className="w-4 h-4" />
        </button>
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation()
            onRemove()
          }}
          className="p-1 hover:bg-red-100 text-red-500 rounded"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>

      {/* Champ expanded content */}
      {isExpanded && (
        <div className="p-4 space-y-3 border-t">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">
                Label <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={champ.label}
                onChange={(e) => onUpdate({ label: e.target.value })}
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
                onChange={(e) => onUpdate({ nom: e.target.value })}
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
                onChange={(e) => onUpdate({ type_champ: e.target.value as TypeChamp })}
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
                onChange={(e) => onUpdate({ placeholder: e.target.value })}
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
                  onUpdate({
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
                    onUpdate({
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
                    onUpdate({
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
              onChange={(e) => onUpdate({ obligatoire: e.target.checked })}
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
  )
}
