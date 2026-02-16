/**
 * ArticlesPage - Gestion de la bibliotheque d'articles (prix unitaires)
 * Module Devis (Module 20) - DEV-01
 */

import { useState, useEffect, useCallback } from 'react'
import Layout from '../components/Layout'
import ArticleModal from '../components/devis/ArticleModal'
import { devisService } from '../services/devis'
import { formatEUR } from '../utils/format'
import type { Article, ArticleCreate, ArticleUpdate } from '../types'
import { TYPE_DEBOURSE_LABELS } from '../types'
import { useDocumentTitle } from '../hooks/useDocumentTitle'
import {
  Loader2,
  AlertCircle,
  Plus,
  Search,
  Edit2,
  Trash2,
  Package,
} from 'lucide-react'

export default function ArticlesPage() {
  useDocumentTitle('Articles')
  const [articles, setArticles] = useState<Article[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Filtres
  const [search, setSearch] = useState('')
  const [categorie, setCategorie] = useState('')
  const [categories, setCategories] = useState<string[]>([])

  // Modal
  const [showModal, setShowModal] = useState(false)
  const [editingArticle, setEditingArticle] = useState<Article | null>(null)

  const loadArticles = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      const params: Record<string, unknown> = {
        limit: 100,
        offset: 0,
        actif_seulement: true,
      }
      if (search) params.search = search
      if (categorie) params.categorie = categorie

      const result = await devisService.listArticles(params as Parameters<typeof devisService.listArticles>[0])
      setArticles(result.items)
      setTotal(result.total)

      // Extraire les categories uniques
      const cats = new Set<string>()
      result.items.forEach((a) => {
        if (a.categorie) cats.add(a.categorie)
      })
      setCategories(Array.from(cats).sort())
    } catch {
      setError('Erreur lors du chargement des articles')
    } finally {
      setLoading(false)
    }
  }, [search, categorie])

  useEffect(() => {
    loadArticles()
  }, [loadArticles])

  const handleCreate = async (data: ArticleCreate | ArticleUpdate) => {
    await devisService.createArticle(data as ArticleCreate)
    setShowModal(false)
    await loadArticles()
  }

  const handleUpdate = async (data: ArticleCreate | ArticleUpdate) => {
    if (!editingArticle) return
    await devisService.updateArticle(editingArticle.id, data as ArticleUpdate)
    setEditingArticle(null)
    setShowModal(false)
    await loadArticles()
  }

  const handleDelete = async (id: number) => {
    if (!window.confirm('Supprimer cet article ?')) return
    try {
      await devisService.deleteArticle(id)
      await loadArticles()
    } catch {
      setError('Erreur lors de la suppression')
    }
  }

  const openCreate = () => {
    setEditingArticle(null)
    setShowModal(true)
  }

  const openEdit = (article: Article) => {
    setEditingArticle(article)
    setShowModal(true)
  }

  return (
    <Layout>
      <div className="space-y-6" role="main" aria-label="Bibliotheque d'articles">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-gray-900">Articles</h1>
            <p className="text-sm text-gray-500 mt-1">
              Bibliotheque de prix unitaires ({total} article{total > 1 ? 's' : ''})
            </p>
          </div>
          <button
            onClick={openCreate}
            className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
          >
            <Plus className="w-4 h-4" />
            Nouvel article
          </button>
        </div>

        {/* Barre de recherche et filtre categorie */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-600" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Rechercher par code, designation..."
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <select
              value={categorie}
              onChange={(e) => setCategorie(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Toutes categories</option>
              {categories.map((cat) => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Loading */}
        {loading && (
          <div className="flex items-center justify-center py-16">
            <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-start gap-2" role="alert">
            <AlertCircle className="flex-shrink-0 mt-0.5" size={18} />
            <div>
              <p>{error}</p>
              <button onClick={loadArticles} className="text-sm underline mt-1">Reessayer</button>
            </div>
          </div>
        )}

        {/* Tableau */}
        {!loading && !error && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm" aria-label="Liste des articles">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">Code</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">Designation</th>
                    <th className="px-4 py-3 text-center text-xs font-medium text-gray-500">Unite</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500">Prix unitaire HT</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">Categorie</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">Type</th>
                    <th className="px-4 py-3 text-center text-xs font-medium text-gray-500">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {articles.map((article) => (
                    <tr key={article.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-4 py-3 font-mono text-xs text-gray-500">{article.code}</td>
                      <td className="px-4 py-3 font-medium text-gray-900">{article.designation}</td>
                      <td className="px-4 py-3 text-center text-gray-600">{article.unite}</td>
                      <td className="px-4 py-3 text-right font-medium">{formatEUR(article.prix_unitaire_ht)}</td>
                      <td className="px-4 py-3 text-gray-600">
                        {article.categorie && (
                          <span className="px-2 py-0.5 text-xs bg-gray-100 rounded-full">
                            {article.categorie}
                          </span>
                        )}
                      </td>
                      <td className="px-4 py-3 text-gray-600 text-xs">
                        {TYPE_DEBOURSE_LABELS[article.type_debourse]}
                      </td>
                      <td className="px-4 py-3 text-center">
                        <div className="flex items-center justify-center gap-1">
                          <button
                            onClick={() => openEdit(article)}
                            className="p-1.5 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                            aria-label={`Modifier ${article.designation}`}
                          >
                            <Edit2 className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleDelete(article.id)}
                            className="p-1.5 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                            aria-label={`Supprimer ${article.designation}`}
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {articles.length === 0 && (
                <div className="text-center py-12 text-gray-500">
                  <Package className="w-12 h-12 mx-auto text-gray-500 mb-3" />
                  <p className="font-medium">Aucun article trouve</p>
                  <p className="text-sm mt-1">
                    {search || categorie
                      ? 'Essayez de modifier vos filtres'
                      : 'Creez votre premier article pour commencer'}
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Modal */}
        {showModal && (
          <ArticleModal
            article={editingArticle}
            onSubmit={editingArticle ? handleUpdate : handleCreate}
            onClose={() => { setShowModal(false); setEditingArticle(null) }}
          />
        )}
      </div>
    </Layout>
  )
}
