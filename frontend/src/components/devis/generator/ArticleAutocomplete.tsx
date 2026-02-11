import { useState, useEffect, useRef } from 'react'
import { Search, Loader2, BookOpen } from 'lucide-react'
import { devisService } from '../../../services/devis'
import type { Article } from '../../../types'
import { formatEUR } from '../../../utils/format'

interface ArticleAutocompleteProps {
  value: string
  onChange: (value: string) => void
  onSelectArticle: (article: Article) => void
  disabled?: boolean
  placeholder?: string
}

export default function ArticleAutocomplete({
  value, onChange, onSelectArticle, disabled,
  placeholder = 'Rechercher un ouvrage...',
}: ArticleAutocompleteProps) {
  const [query, setQuery] = useState(value)
  const [results, setResults] = useState<Article[]>([])
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
        const res = await devisService.listArticles({ search: query, limit: 10 })
        setResults(res.items || [])
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
          className="w-full pl-9 pr-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none text-sm disabled:bg-gray-50"
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
            <span className="text-xs text-gray-500">Resultats bibliotheque</span>
            <span className="text-xs text-gray-400">{results.length} resultat{results.length > 1 ? 's' : ''}</span>
          </div>
          <div className="max-h-64 overflow-y-auto">
            {results.map(article => (
              <div
                key={article.id}
                onClick={() => { onSelectArticle(article); setShowDropdown(false); setQuery(article.designation) }}
                className="px-3 py-3 hover:bg-indigo-50 cursor-pointer border-b border-gray-50 group"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-gray-900 group-hover:text-indigo-600 truncate">{article.designation}</span>
                      {article.code && <span className="px-1.5 py-0.5 bg-blue-100 text-blue-700 text-xs rounded flex-shrink-0">{article.code}</span>}
                    </div>
                    {article.description && <p className="text-sm text-gray-500 mt-0.5 truncate">{article.description}</p>}
                    <div className="flex items-center gap-3 mt-1.5">
                      <span className="text-xs text-gray-400">Unite: {article.unite}</span>
                      {article.categorie && <span className="text-xs text-gray-400">| Cat: {article.categorie}</span>}
                    </div>
                  </div>
                  <div className="text-right ml-4 flex-shrink-0">
                    <span className="font-semibold text-indigo-600">{formatEUR(Number(article.prix_unitaire_ht))}</span>
                    <p className="text-xs text-gray-400">HT / {article.unite}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
          <div className="px-3 py-2 bg-gray-50 border-t border-gray-100 flex items-center justify-between">
            <button className="text-xs text-gray-500 hover:text-gray-700">Creer un ouvrage personnalise</button>
            <a href="/devis/articles" className="text-xs text-indigo-600 hover:text-indigo-700 flex items-center gap-1">
              <BookOpen className="w-3 h-3" /> Bibliotheque
            </a>
          </div>
        </div>
      )}
    </div>
  )
}
