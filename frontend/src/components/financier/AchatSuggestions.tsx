/**
 * AchatSuggestions - Autocomplete sur les achats passes.
 *
 * Propose des suggestions basees sur l'historique des achats (libelle + prix + fournisseur).
 * Pattern identique a ArticleAutocomplete: debounce 300ms, min 3 chars, dropdown.
 */

import { useState, useEffect, useRef } from 'react'
import { Search, Loader2 } from 'lucide-react'
import { financierService } from '../../services/financier'
import type { AchatSuggestion } from '../../services/financier'

const formatEUR = (val: string | number) =>
  new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(Number(val) || 0)

interface AchatSuggestionsProps {
  value: string
  onChange: (value: string) => void
  onSelect: (suggestion: AchatSuggestion) => void
  disabled?: boolean
  placeholder?: string
}

export default function AchatSuggestions({
  value,
  onChange,
  onSelect,
  disabled,
  placeholder = 'Rechercher un achat passe...',
}: AchatSuggestionsProps) {
  const [query, setQuery] = useState(value)
  const [results, setResults] = useState<AchatSuggestion[]>([])
  const [loading, setLoading] = useState(false)
  const [showDropdown, setShowDropdown] = useState(false)
  const debounceRef = useRef<ReturnType<typeof setTimeout>>(undefined)
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => { setQuery(value) }, [value])

  useEffect(() => {
    if (query.length < 3) { setResults([]); setShowDropdown(false); return }
    clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(async () => {
      setLoading(true)
      try {
        const res = await financierService.getAchatSuggestions(query, 10)
        setResults(res)
        setShowDropdown(true)
      } catch { setResults([]) }
      finally { setLoading(false) }
    }, 300)
    return () => clearTimeout(debounceRef.current)
  }, [query])

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) setShowDropdown(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  return (
    <div ref={containerRef} className="relative">
      <div className="relative">
        <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input
          type="text"
          value={query}
          onChange={e => { setQuery(e.target.value); onChange(e.target.value) }}
          onFocus={() => results.length > 0 && setShowDropdown(true)}
          disabled={disabled}
          className="w-full pl-9 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none text-sm disabled:bg-gray-50"
          placeholder={placeholder}
        />
        {loading && (
          <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1">
            <Loader2 className="w-4 h-4 animate-spin text-amber-500" />
            <span className="text-xs text-amber-600">Recherche</span>
          </div>
        )}
      </div>
      {showDropdown && results.length > 0 && (
        <div className="absolute left-0 right-0 top-full mt-1 bg-white border border-gray-200 rounded-xl shadow-xl z-50 overflow-hidden">
          <div className="px-3 py-2 bg-gray-50 border-b border-gray-100 flex items-center justify-between">
            <span className="text-xs text-gray-500">Achats precedents</span>
            <span className="text-xs text-gray-400">{results.length} suggestion{results.length > 1 ? 's' : ''}</span>
          </div>
          <div className="max-h-64 overflow-y-auto">
            {results.map((suggestion, idx) => (
              <div
                key={`${suggestion.libelle}-${idx}`}
                onClick={() => { onSelect(suggestion); setShowDropdown(false); setQuery(suggestion.libelle) }}
                className="px-3 py-3 hover:bg-blue-50 cursor-pointer border-b border-gray-50 group"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <span className="font-medium text-gray-900 group-hover:text-blue-600 truncate block">
                      {suggestion.libelle}
                    </span>
                    <div className="flex items-center gap-3 mt-1">
                      {suggestion.fournisseur_nom && (
                        <span className="text-xs text-gray-500">{suggestion.fournisseur_nom}</span>
                      )}
                      {suggestion.type_achat && (
                        <span className="px-1.5 py-0.5 bg-gray-100 text-gray-600 text-xs rounded">
                          {suggestion.type_achat}
                        </span>
                      )}
                      {suggestion.unite && (
                        <span className="text-xs text-gray-400">Unite: {suggestion.unite}</span>
                      )}
                    </div>
                  </div>
                  <div className="text-right ml-4 flex-shrink-0">
                    <span className="font-semibold text-blue-600">{formatEUR(suggestion.prix_unitaire_ht)}</span>
                    <p className="text-xs text-gray-400">HT / {suggestion.unite || 'u'}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
