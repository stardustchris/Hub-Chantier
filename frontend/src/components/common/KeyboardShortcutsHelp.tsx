/**
 * KeyboardShortcutsHelp - Modale d'aide pour les raccourcis clavier
 * Section 4.4 - Raccourcis clavier
 */

import { X, Navigation, FileText, FolderOpen, Building2, DollarSign } from 'lucide-react'

export interface KeyboardShortcutsHelpProps {
  isOpen: boolean
  onClose: () => void
}

interface Shortcut {
  key: string
  description: string
  icon?: React.ReactNode
}

const shortcuts: { category: string; items: Shortcut[] }[] = [
  {
    category: 'Navigation',
    items: [
      {
        key: 'Alt + P',
        description: 'Planning',
        icon: <Navigation className="w-4 h-4" />,
      },
      {
        key: 'Alt + H',
        description: 'Feuilles d\'heures',
        icon: <FileText className="w-4 h-4" />,
      },
      {
        key: 'Alt + D',
        description: 'Documents',
        icon: <FolderOpen className="w-4 h-4" />,
      },
      {
        key: 'Alt + C',
        description: 'Chantiers',
        icon: <Building2 className="w-4 h-4" />,
      },
      {
        key: 'Alt + F',
        description: 'Finances',
        icon: <DollarSign className="w-4 h-4" />,
      },
    ],
  },
  {
    category: 'Actions',
    items: [
      {
        key: '?',
        description: 'Afficher cette aide',
      },
      {
        key: 'Escape',
        description: 'Fermer les modales',
      },
    ],
  },
]

export default function KeyboardShortcutsHelp({ isOpen, onClose }: KeyboardShortcutsHelpProps) {
  if (!isOpen) return null

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="shortcuts-title"
    >
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />

      {/* Modal */}
      <div className="relative w-full max-w-lg bg-white rounded-2xl shadow-xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b bg-gradient-to-r from-primary-600 to-primary-700">
          <h2 id="shortcuts-title" className="text-lg font-semibold text-white">
            Raccourcis clavier
          </h2>
          <button
            onClick={onClose}
            className="p-2 -m-2 text-white/80 hover:text-white transition-colors"
            aria-label="Fermer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="px-6 py-4 max-h-[70vh] overflow-y-auto">
          {shortcuts.map((section, sectionIndex) => (
            <div key={sectionIndex} className={sectionIndex > 0 ? 'mt-6' : ''}>
              <h3 className="text-sm font-semibold text-gray-900 mb-3">{section.category}</h3>
              <div className="space-y-2">
                {section.items.map((shortcut, itemIndex) => (
                  <div
                    key={itemIndex}
                    className="flex items-center justify-between py-2 px-3 rounded-lg hover:bg-gray-50"
                  >
                    <div className="flex items-center gap-3">
                      {shortcut.icon && (
                        <div className="text-gray-600">{shortcut.icon}</div>
                      )}
                      <span className="text-gray-700">{shortcut.description}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      {shortcut.key.split(' + ').map((key, keyIndex, arr) => (
                        <span key={keyIndex}>
                          <kbd className="px-2 py-1 text-xs font-semibold text-gray-800 bg-gray-100 border border-gray-300 rounded shadow-sm">
                            {key}
                          </kbd>
                          {keyIndex < arr.length - 1 && (
                            <span className="mx-1 text-gray-500">+</span>
                          )}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t bg-gray-50">
          <p className="text-sm text-gray-600 text-center">
            Appuyez sur <kbd className="px-2 py-1 text-xs font-semibold text-gray-800 bg-white border border-gray-300 rounded">?</kbd> à tout moment pour afficher cette aide
          </p>
        </div>
      </div>
    </div>
  )
}
