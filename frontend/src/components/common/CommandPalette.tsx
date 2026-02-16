import { useEffect, useRef } from 'react'
import {
  Search,
  Building2,
  Users,
  FileText,
  Home,
  Calendar,
  Clock,
  Truck,
  BarChart3,
  Euro,
  ShoppingCart,
  Handshake,
  Settings,
  Layout,
} from 'lucide-react'
import { useCommandPalette } from '../../hooks/useCommandPalette'
import type { SearchResult } from '../../hooks/useCommandPalette'

// Icon mapping
const ICON_MAP = {
  Home,
  Building2,
  Users,
  FileText,
  Calendar,
  Clock,
  Truck,
  BarChart3,
  Euro,
  ShoppingCart,
  Handshake,
  Settings,
  Layout,
} as const

type IconName = keyof typeof ICON_MAP

function getIcon(iconName: string) {
  return ICON_MAP[iconName as IconName] || FileText
}

// Category labels
const CATEGORY_LABELS: Record<SearchResult['type'], string> = {
  chantier: 'Chantiers',
  user: 'Utilisateurs',
  document: 'Documents',
  page: 'Pages',
}

export default function CommandPalette() {
  const {
    isOpen,
    query,
    setQuery,
    results,
    selectedIndex,
    setSelectedIndex,
    recentSearches,
    close,
    selectResult,
  } = useCommandPalette()

  const inputRef = useRef<HTMLInputElement>(null)
  const resultsRef = useRef<HTMLDivElement>(null)

  // Focus input when opened
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus()
    }
  }, [isOpen])

  // Scroll selected item into view
  useEffect(() => {
    if (resultsRef.current) {
      const selectedElement = resultsRef.current.querySelector(
        `[data-index="${selectedIndex}"]`
      )
      if (selectedElement) {
        selectedElement.scrollIntoView({ block: 'nearest', behavior: 'smooth' })
      }
    }
  }, [selectedIndex])

  if (!isOpen) return null

  const displayResults = query.trim() ? results : recentSearches
  const showRecentLabel = !query.trim() && recentSearches.length > 0

  // Group results by category
  const groupedResults = displayResults.reduce((acc, result) => {
    if (!acc[result.type]) {
      acc[result.type] = []
    }
    acc[result.type].push(result)
    return acc
  }, {} as Record<SearchResult['type'], SearchResult[]>)

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center bg-black/50 pt-[20vh]"
      onClick={close}
      role="dialog"
      aria-label="Recherche globale"
      aria-modal="true"
    >
      <div
        className="w-full max-w-lg bg-white rounded-xl shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Search Input */}
        <div className="flex items-center gap-3 px-4 py-3 border-b">
          <Search className="w-5 h-5 text-gray-400 flex-shrink-0" />
          <input
            ref={inputRef}
            type="text"
            className="flex-1 text-base outline-none placeholder-gray-400"
            placeholder="Rechercher chantiers, utilisateurs, pages..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            aria-autocomplete="list"
            aria-controls="search-results"
            aria-activedescendant={
              displayResults[selectedIndex]
                ? `result-${selectedIndex}`
                : undefined
            }
          />
          <kbd className="hidden sm:block px-2 py-1 text-xs font-semibold text-gray-500 bg-gray-100 border border-gray-300 rounded">
            ESC
          </kbd>
        </div>

        {/* Results */}
        <div
          ref={resultsRef}
          id="search-results"
          className="max-h-[60vh] overflow-y-auto"
          role="listbox"
        >
          {displayResults.length === 0 ? (
            <div className="px-4 py-8 text-center text-gray-500">
              {query.trim() ? (
                <>
                  <Search className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                  <p className="font-medium">Aucun resultat</p>
                  <p className="text-sm">
                    Essayez avec d'autres termes de recherche
                  </p>
                </>
              ) : (
                <>
                  <Search className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                  <p className="font-medium">Commencez a taper</p>
                  <p className="text-sm">
                    Recherchez des chantiers, utilisateurs ou pages
                  </p>
                </>
              )}
            </div>
          ) : (
            <>
              {showRecentLabel && (
                <div className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wide bg-gray-50">
                  Recherches recentes
                </div>
              )}

              {Object.entries(groupedResults).map(([category, items]) => (
                <div key={category}>
                  {query.trim() && (
                    <div className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wide bg-gray-50">
                      {
                        CATEGORY_LABELS[
                          category as SearchResult['type']
                        ]
                      }
                    </div>
                  )}

                  {items.map((result) => {
                    const globalIndex = displayResults.indexOf(result)
                    const isSelected = globalIndex === selectedIndex
                    const Icon = getIcon(result.icon)

                    return (
                      <button
                        key={result.id}
                        id={`result-${globalIndex}`}
                        data-index={globalIndex}
                        className={`w-full flex items-center gap-3 px-4 py-3 text-left transition-colors ${
                          isSelected
                            ? 'bg-blue-50 border-l-2 border-blue-500'
                            : 'hover:bg-gray-100'
                        }`}
                        onClick={() => selectResult(result)}
                        onMouseEnter={() => setSelectedIndex(globalIndex)}
                        role="option"
                        aria-selected={isSelected}
                      >
                        <div
                          className={`flex-shrink-0 w-10 h-10 rounded-lg flex items-center justify-center ${
                            isSelected ? 'bg-blue-100' : 'bg-gray-100'
                          }`}
                        >
                          <Icon
                            className={`w-5 h-5 ${
                              isSelected ? 'text-blue-600' : 'text-gray-600'
                            }`}
                          />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p
                            className={`font-medium truncate ${
                              isSelected ? 'text-blue-900' : 'text-gray-900'
                            }`}
                          >
                            {result.title}
                          </p>
                          {result.subtitle && (
                            <p
                              className={`text-sm truncate ${
                                isSelected ? 'text-blue-600' : 'text-gray-500'
                              }`}
                            >
                              {result.subtitle}
                            </p>
                          )}
                        </div>
                      </button>
                    )
                  })}
                </div>
              ))}
            </>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between px-4 py-2 text-xs text-gray-500 border-t bg-gray-50">
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1">
              <kbd className="px-1.5 py-0.5 font-semibold bg-white border border-gray-300 rounded">
                ↑
              </kbd>
              <kbd className="px-1.5 py-0.5 font-semibold bg-white border border-gray-300 rounded">
                ↓
              </kbd>
              <span className="ml-1">pour naviguer</span>
            </span>
            <span className="flex items-center gap-1">
              <kbd className="px-1.5 py-0.5 font-semibold bg-white border border-gray-300 rounded">
                ↵
              </kbd>
              <span className="ml-1">pour selectionner</span>
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}
