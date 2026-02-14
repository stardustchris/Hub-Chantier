/**
 * ArticleLibraryPanel - Panneau lateral de la bibliotheque d'articles
 * Module Devis (Module 20) - DEV-01
 *
 * Permet de rechercher, filtrer et ajouter des articles depuis la
 * bibliotheque de prix dans un devis en cours d'edition.
 */

import { useState, useEffect, useCallback, useRef } from 'react'
import {
  X,
  Search,
  Loader2,
  Package,
  Plus,
  BookOpen,
  Filter,
  ChevronDown,
} from 'lucide-react'
import { devisService } from '../../services/devis'
import type { Article, ArticleCreate } from '../../types'
import ArticleModal from './ArticleModal'
import { formatEUR } from '../../utils/format'

/** Categories BTP correspondant au backend CategorieArticle. */
const CATEGORIES_ARTICLES: { value: string; label: string }[] = [
  { value: 'gros_oeuvre', label: 'Gros oeuvre' },
  { value: 'second_oeuvre', label: 'Second oeuvre' },
  { value: 'electricite', label: 'Electricite' },
  { value: 'plomberie', label: 'Plomberie' },
  { value: 'chauffage_clim', label: 'Chauffage / Clim' },
  { value: 'menuiserie', label: 'Menuiserie' },
  { value: 'peinture', label: 'Peinture' },
  { value: 'couverture', label: 'Couverture' },
  { value: 'terrassement', label: 'Terrassement' },
  { value: 'vrd', label: 'VRD' },
  { value: 'charpente', label: 'Charpente' },
  { value: 'isolation', label: 'Isolation' },
  { value: 'carrelage', label: 'Carrelage' },
  { value: 'main_oeuvre', label: "Main d'oeuvre" },
  { value: 'materiel', label: 'Materiel' },
  { value: 'divers', label: 'Divers' },
]

interface ArticleLibraryPanelProps {
  /** Appelee quand l'utilisateur selectionne un article a ajouter au devis. */
  onAddArticle: (article: Article) => void
  /** Ferme le panneau. */
  onClose: () => void
}

export default function ArticleLibraryPanel({
  onAddArticle,
  onClose,
}: ArticleLibraryPanelProps) {
  const [articles, setArticles] = useState<Article[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Filtres
  const [search, setSearch] = useState('')
  const [categorie, setCategorie] = useState('')
  const [showFilters, setShowFilters] = useState(false)

  // Modal creation
  const [showCreateModal, setShowCreateModal] = useState(false)

  // Debounce search
  const debounceRef = useRef<ReturnType<typeof setTimeout>>(undefined)

  const loadArticles = useCallback(async (searchTerm: string, cat: string) => {
    try {
      setLoading(true)
      setError(null)

      const params: {
        search?: string
        categorie?: string
        limit: number
        offset: number
      } = { limit: 100, offset: 0 }

      if (searchTerm) params.search = searchTerm
      if (cat) params.categorie = cat

      const result = await devisService.listArticles(params)
      setArticles(result.items)
      setTotal(result.total)
    } catch {
      setError('Erreur lors du chargement des articles')
    } finally {
      setLoading(false)
    }
  }, [])

  // Chargement initial
  useEffect(() => {
    loadArticles('', '')
  }, [loadArticles])

  // Recherche avec debounce
  useEffect(() => {
    clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(() => {
      loadArticles(search, categorie)
    }, 300)
    return () => clearTimeout(debounceRef.current)
  }, [search, categorie, loadArticles])

  const handleCreateArticle = async (data: ArticleCreate) => {
    await devisService.createArticle(data as ArticleCreate)
    setShowCreateModal(false)
    loadArticles(search, categorie)
  }

  const handleSelectArticle = (article: Article) => {
    onAddArticle(article)
  }

  // Fermeture via Escape
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [onClose])

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 z-40 bg-black/30 transition-opacity"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Panel */}
      <div
        className="fixed inset-y-0 right-0 z-50 w-full max-w-md bg-white shadow-2xl flex flex-col"
        role="dialog"
        aria-label="Bibliotheque d'articles"
      >
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-gray-200 bg-gradient-to-r from-indigo-50 to-white">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 bg-indigo-100 rounded-lg flex items-center justify-center">
              <BookOpen className="w-5 h-5 text-indigo-600" />
            </div>
            <div>
              <h2 className="font-semibold text-gray-900">Bibliotheque</h2>
              <p className="text-xs text-gray-500">{total} article{total > 1 ? 's' : ''}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            aria-label="Fermer la bibliotheque"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Search bar */}
        <div className="px-5 py-3 border-b border-gray-100 space-y-2">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-600" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Rechercher par code ou designation..."
              className="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
              autoFocus
            />
          </div>

          {/* Filtre categorie */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`flex items-center gap-1 px-2.5 py-1.5 text-xs rounded-lg border transition-colors ${
                categorie
                  ? 'bg-indigo-50 border-indigo-200 text-indigo-700'
                  : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50'
              }`}
            >
              <Filter className="w-3.5 h-3.5" />
              {categorie
                ? CATEGORIES_ARTICLES.find(c => c.value === categorie)?.label || categorie
                : 'Categorie'}
              <ChevronDown className={`w-3 h-3 transition-transform ${showFilters ? 'rotate-180' : ''}`} />
            </button>
            {categorie && (
              <button
                onClick={() => setCategorie('')}
                className="text-xs text-gray-600 hover:text-gray-800"
              >
                Effacer
              </button>
            )}
            <div className="flex-1" />
            <button
              onClick={() => setShowCreateModal(true)}
              className="flex items-center gap-1 px-2.5 py-1.5 text-xs font-medium bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
            >
              <Plus className="w-3.5 h-3.5" /> Nouvel article
            </button>
          </div>

          {/* Dropdown categories */}
          {showFilters && (
            <div className="grid grid-cols-2 gap-1 p-2 bg-gray-50 rounded-lg border border-gray-100 max-h-48 overflow-y-auto">
              <button
                onClick={() => { setCategorie(''); setShowFilters(false) }}
                className={`text-left px-2 py-1.5 text-xs rounded transition-colors ${
                  !categorie ? 'bg-indigo-100 text-indigo-700 font-medium' : 'hover:bg-gray-100 text-gray-600'
                }`}
              >
                Toutes
              </button>
              {CATEGORIES_ARTICLES.map(cat => (
                <button
                  key={cat.value}
                  onClick={() => { setCategorie(cat.value); setShowFilters(false) }}
                  className={`text-left px-2 py-1.5 text-xs rounded transition-colors ${
                    categorie === cat.value
                      ? 'bg-indigo-100 text-indigo-700 font-medium'
                      : 'hover:bg-gray-100 text-gray-600'
                  }`}
                >
                  {cat.label}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Articles list */}
        <div className="flex-1 overflow-y-auto">
          {loading && (
            <div className="flex items-center justify-center py-16">
              <Loader2 className="w-6 h-6 animate-spin text-indigo-500" />
            </div>
          )}

          {error && (
            <div className="m-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
              {error}
              <button
                onClick={() => loadArticles(search, categorie)}
                className="block mt-1 text-xs underline"
              >
                Reessayer
              </button>
            </div>
          )}

          {!loading && !error && articles.length === 0 && (
            <div className="text-center py-16 px-6">
              <Package className="w-12 h-12 mx-auto text-gray-500 mb-3" />
              <p className="font-medium text-gray-600">Aucun article trouve</p>
              <p className="text-sm text-gray-600 mt-1">
                {search || categorie
                  ? 'Modifiez vos filtres ou creez un nouvel article'
                  : 'Creez votre premier article pour commencer'}
              </p>
              <button
                onClick={() => setShowCreateModal(true)}
                className="mt-4 inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg transition-colors"
              >
                <Plus className="w-4 h-4" />
                Creer un article
              </button>
            </div>
          )}

          {!loading && !error && articles.length > 0 && (
            <div className="divide-y divide-gray-100">
              {articles.map((article) => (
                <div
                  key={article.id}
                  className="px-5 py-3 hover:bg-indigo-50/50 transition-colors group cursor-pointer"
                  onClick={() => handleSelectArticle(article)}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-0.5">
                        <span className="font-medium text-gray-900 text-sm group-hover:text-indigo-700 truncate">
                          {article.designation}
                        </span>
                      </div>
                      <div className="flex items-center gap-2 flex-wrap">
                        {article.code && (
                          <span className="px-1.5 py-0.5 bg-blue-50 text-blue-700 text-xs rounded font-mono">
                            {article.code}
                          </span>
                        )}
                        <span className="text-xs text-gray-600">{article.unite}</span>
                        {article.categorie && (
                          <span className="text-xs text-gray-600">
                            {CATEGORIES_ARTICLES.find(c => c.value === article.categorie)?.label || article.categorie}
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="text-right flex-shrink-0">
                      <span className="font-semibold text-indigo-600 text-sm">
                        {formatEUR(Number(article.prix_unitaire_ht))}
                      </span>
                      <p className="text-xs text-gray-600">HT / {article.unite}</p>
                    </div>
                  </div>
                  {/* Bouton ajouter visible au hover */}
                  <div className="mt-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        handleSelectArticle(article)
                      }}
                      className="w-full flex items-center justify-center gap-1.5 px-3 py-1.5 text-xs font-medium text-indigo-700 bg-indigo-100 hover:bg-indigo-200 rounded-lg transition-colors"
                    >
                      <Plus className="w-3.5 h-3.5" /> Ajouter au devis
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-5 py-3 border-t border-gray-200 bg-gray-50">
          <p className="text-xs text-gray-600 text-center">
            Cliquez sur un article pour l&apos;ajouter au dernier lot du devis
          </p>
        </div>
      </div>

      {/* Modal creation article */}
      {showCreateModal && (
        <ArticleModal
          onSubmit={handleCreateArticle}
          onClose={() => setShowCreateModal(false)}
        />
      )}
    </>
  )
}
