/**
 * Hook pour charger les documents récents de l'utilisateur
 * et les ouvrir sur toutes les plateformes (desktop, iOS, Android)
 *
 * Les documents sont chargés depuis les chantiers du planning du jour
 * ou depuis des documents de démonstration si pas de données API
 */

import { useState, useEffect, useCallback } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { useToast } from '../contexts/ToastContext'
import { planningService } from '../services/planning'
import * as documentsService from '../services/documents'
import { logger } from '../services/logger'

export interface RecentDocument {
  id: string
  name: string
  siteName: string
  type: 'pdf' | 'doc' | 'image' | 'other'
  chantierId: number
  documentId: number
  /** URL directe pour les documents de démo */
  demoUrl?: string
}

interface UseRecentDocumentsReturn {
  documents: RecentDocument[]
  isLoading: boolean
  hasMore: boolean
  openDocument: (doc: RecentDocument) => Promise<void>
  loadMore: () => void
  refreshDocuments: () => Promise<void>
}

/** Nombre de documents affichés initialement */
const INITIAL_DISPLAY_COUNT = 4
/** Nombre de documents ajoutés à chaque "voir plus" */
const LOAD_MORE_COUNT = 4

function getDocumentType(filename: string): 'pdf' | 'doc' | 'image' | 'other' {
  const ext = filename.split('.').pop()?.toLowerCase() || ''
  if (ext === 'pdf') return 'pdf'
  if (['doc', 'docx', 'odt', 'rtf'].includes(ext)) return 'doc'
  if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'].includes(ext)) return 'image'
  return 'other'
}

function detectPlatform(): 'ios' | 'android' | 'desktop' {
  const userAgent = navigator.userAgent.toLowerCase()
  if (/iphone|ipad|ipod/.test(userAgent)) return 'ios'
  if (/android/.test(userAgent)) return 'android'
  return 'desktop'
}

export function useRecentDocuments(): UseRecentDocumentsReturn {
  const { user } = useAuth()
  const { addToast } = useToast()
  const [allDocuments, setAllDocuments] = useState<RecentDocument[]>([])
  const [displayCount, setDisplayCount] = useState(INITIAL_DISPLAY_COUNT)
  const [isLoading, setIsLoading] = useState(true)

  const loadDocuments = useCallback(async () => {
    if (!user?.id) {
      setIsLoading(false)
      return
    }

    try {
      setIsLoading(true)

      const today = new Date().toISOString().split('T')[0]
      const isAdminOrConducteur = user.role === 'admin' || user.role === 'conducteur'

      // Charger les affectations du jour (même logique que useTodayPlanning)
      let todayAffectations = await planningService.getByUtilisateur(user.id, today, today)

      // Si admin/conducteur sans affectation personnelle, charger toutes les affectations
      if (isAdminOrConducteur && todayAffectations.length === 0) {
        todayAffectations = await planningService.getAffectations({
          date_debut: today,
          date_fin: today,
        })
      }

      // Dédupliquer par chantier
      const chantiersUniques = new Map<string, { id: string; nom: string }>()
      for (const a of todayAffectations) {
        if (!chantiersUniques.has(a.chantier_id)) {
          chantiersUniques.set(a.chantier_id, {
            id: a.chantier_id,
            nom: a.chantier_nom || 'Chantier',
          })
        }
      }

      const recentDocs: RecentDocument[] = []

      // Limiter à 5 chantiers max pour éviter trop de requêtes
      const chantiersArray = Array.from(chantiersUniques.values()).slice(0, 5)

      // Pour chaque chantier du planning, récupérer les documents
      for (const chantier of chantiersArray) {
        try {
          const chantierId = parseInt(chantier.id, 10)

          // Chercher les documents du chantier
          const docsResponse = await documentsService.searchDocuments(
            chantierId,
            undefined, // query
            undefined, // type
            undefined, // dossierId
            0,         // skip
            4          // limit - 4 docs par chantier max
          )

          for (const doc of docsResponse.documents) {
            recentDocs.push({
              id: `${chantier.id}-${doc.id}`,
              name: doc.nom,
              siteName: chantier.nom,
              type: getDocumentType(doc.nom),
              chantierId,
              documentId: doc.id,
            })
          }
        } catch (error) {
          // Ignorer les erreurs pour un chantier (peut ne pas avoir de documents)
          logger.debug('No documents for chantier', { chantierId: chantier.id })
        }
      }

      // Définir les documents (vide si aucun trouvé)
      setAllDocuments(recentDocs)
    } catch (error) {
      logger.error('Error loading recent documents', error)
      // En cas d'erreur, afficher liste vide
      setAllDocuments([])
    } finally {
      setIsLoading(false)
    }
  }, [user?.id, user?.role])

  const openDocument = useCallback(async (doc: RecentDocument) => {
    try {
      addToast({ message: `Ouverture de "${doc.name}"...`, type: 'info' })

      let url: string

      // Si c'est un document de démo, utiliser l'URL directe
      if (doc.demoUrl) {
        url = doc.demoUrl
      } else {
        // Sinon, récupérer le blob via l'API et créer une URL
        const blob = await documentsService.downloadDocument(doc.documentId)
        url = window.URL.createObjectURL(blob)
      }

      const platform = detectPlatform()

      // Ouvrir selon la plateforme
      if (platform === 'ios') {
        // iOS: Ouvrir dans un nouvel onglet (Safari gérera le PDF/image)
        window.open(url, '_blank')
      } else if (platform === 'android') {
        // Android: Créer un lien de téléchargement puis ouvrir
        const link = document.createElement('a')
        link.href = url
        link.target = '_blank'
        link.rel = 'noopener noreferrer'
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
      } else {
        // Desktop: Ouvrir dans un nouvel onglet
        window.open(url, '_blank', 'noopener,noreferrer')
      }

      addToast({ message: `Document "${doc.name}" ouvert`, type: 'success' })
    } catch (error) {
      logger.error('Error opening document', error)
      addToast({
        message: `Impossible d'ouvrir le document. Veuillez réessayer.`,
        type: 'error'
      })
    }
  }, [addToast])

  const loadMore = useCallback(() => {
    setDisplayCount(prev => prev + LOAD_MORE_COUNT)
  }, [])

  useEffect(() => {
    loadDocuments()
  }, [loadDocuments])

  // Documents à afficher (limités par displayCount)
  const documents = allDocuments.slice(0, displayCount)
  const hasMore = displayCount < allDocuments.length

  return {
    documents,
    isLoading,
    hasMore,
    openDocument,
    loadMore,
    refreshDocuments: loadDocuments,
  }
}
