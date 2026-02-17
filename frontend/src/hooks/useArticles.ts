/**
 * useArticles - Hook pour gerer la bibliotheque d'articles (prix unitaires)
 * DEV-01: Bibliotheque d'articles
 */

import { useState, useCallback } from 'react'
import { devisService } from '../services/devis'
import { logger } from '../services/logger'
import type { Article, ArticleCreate, ArticleUpdate } from '../types'

export interface UseArticlesParams {
  search?: string
  categorie?: string
  actif?: boolean
  limit?: number
  offset?: number
}

export interface UseArticlesReturn {
  articles: Article[]
  total: number
  loading: boolean
  error: string | null
  loadArticles: (params?: UseArticlesParams) => Promise<void>
  createArticle: (data: ArticleCreate) => Promise<Article>
  updateArticle: (id: number, data: ArticleUpdate) => Promise<Article>
  deleteArticle: (id: number) => Promise<void>
}

export function useArticles(): UseArticlesReturn {
  const [articles, setArticles] = useState<Article[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadArticles = useCallback(async (params?: UseArticlesParams) => {
    try {
      setLoading(true)
      setError(null)
      const result = await devisService.listArticles(
        params as Parameters<typeof devisService.listArticles>[0]
      )
      setArticles(result.items)
      setTotal(result.total)
    } catch (err) {
      const message = 'Erreur lors du chargement des articles'
      setError(message)
      logger.error('useArticles loadArticles error', err, { context: 'useArticles' })
    } finally {
      setLoading(false)
    }
  }, [])

  const createArticle = useCallback(async (data: ArticleCreate): Promise<Article> => {
    const created = await devisService.createArticle(data)
    return created
  }, [])

  const updateArticle = useCallback(async (id: number, data: ArticleUpdate): Promise<Article> => {
    const updated = await devisService.updateArticle(id, data)
    return updated
  }, [])

  const deleteArticle = useCallback(async (id: number): Promise<void> => {
    await devisService.deleteArticle(id)
  }, [])

  return {
    articles,
    total,
    loading,
    error,
    loadArticles,
    createArticle,
    updateArticle,
    deleteArticle,
  }
}

export default useArticles
