/**
 * useDevisMediaUpload - Hook pour gérer l'upload de photos/fiches techniques par ligne de devis
 * DEV-07: Insertion multimédia
 * Utilise le service documents existant
 */

import { useState, useCallback } from 'react'

import { devisService } from '../services/devis'
import type { PieceJointeDevis } from '../types'
import { logger } from '../services/logger'

export interface UseDevisMediaUploadOptions {
  devisId: number
  onUploadComplete?: (pieces: PieceJointeDevis[]) => void
}

export interface UseDevisMediaUploadReturn {
  // Data
  pieces: PieceJointeDevis[]

  // State
  uploading: boolean
  uploadProgress: number
  error: string | null

  // Actions
  uploadFiles: (files: File[], visibleClient?: boolean) => Promise<boolean>
  removeFile: (pieceId: number) => Promise<boolean>
  toggleVisibility: (pieceId: number, visible: boolean) => Promise<boolean>
  reload: () => Promise<void>
}

const ACCEPTED_TYPES = {
  image: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
  document: ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
  all: [] as string[],
}
ACCEPTED_TYPES.all = [...ACCEPTED_TYPES.image, ...ACCEPTED_TYPES.document]

const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB

export function useDevisMediaUpload({
  devisId,
  onUploadComplete,
}: UseDevisMediaUploadOptions): UseDevisMediaUploadReturn {
  const [pieces, setPieces] = useState<PieceJointeDevis[]>([])
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [error, setError] = useState<string | null>(null)

  // Charger les pièces jointes
  const reload = useCallback(async () => {
    try {
      const result = await devisService.listPiecesJointes(devisId)
      setPieces(result)
    } catch (err) {
      logger.error('useDevisMediaUpload reload error', err, { context: 'useDevisMediaUpload', devisId })
    }
  }, [devisId])

  // Valider un fichier
  const validateFile = useCallback((file: File): string | null => {
    if (!ACCEPTED_TYPES.all.includes(file.type)) {
      return `Type de fichier non supporté: ${file.type}`
    }

    if (file.size > MAX_FILE_SIZE) {
      return `Fichier trop volumineux (max 10MB): ${(file.size / 1024 / 1024).toFixed(2)}MB`
    }

    return null
  }, [])

  // Upload de fichiers
  const uploadFiles = useCallback(async (files: File[], visibleClient = false): Promise<boolean> => {
    try {
      setUploading(true)
      setUploadProgress(0)
      setError(null)

      const validFiles: File[] = []
      const errors: string[] = []

      // Valider tous les fichiers
      for (const file of files) {
        const validationError = validateFile(file)
        if (validationError) {
          errors.push(`${file.name}: ${validationError}`)
        } else {
          validFiles.push(file)
        }
      }

      if (errors.length > 0) {
        setError(errors.join('\n'))
        return false
      }

      if (validFiles.length === 0) {
        setError('Aucun fichier valide à uploader')
        return false
      }

      // Upload des fichiers un par un avec suivi de progression
      const uploaded: PieceJointeDevis[] = []
      for (let i = 0; i < validFiles.length; i++) {
        const file = validFiles[i]

        // Pour l'instant, on utilise le service documents directement
        // TODO: Créer un dossier spécifique pour les devis ou utiliser un dossier temporaire
        // const doc = await uploadDocument(dossierId, devisId, file)

        // Upload via le service devis
        const piece = await devisService.uploadPieceJointe(devisId, {
          nom_fichier: file.name,
          type_fichier: file.type.startsWith('image/') ? 'image' : 'document',
          taille_octets: file.size,
          mime_type: file.type,
          visible_client: visibleClient,
        })

        uploaded.push(piece)
        setUploadProgress(Math.round(((i + 1) / validFiles.length) * 100))
      }

      await reload()

      if (onUploadComplete) {
        onUploadComplete(uploaded)
      }

      return true
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erreur lors de l\'upload'
      setError(message)
      logger.error('useDevisMediaUpload uploadFiles error', err, {
        context: 'useDevisMediaUpload',
        devisId,
        fileCount: files.length,
      })
      return false
    } finally {
      setUploading(false)
      setUploadProgress(0)
    }
  }, [devisId, validateFile, reload, onUploadComplete])

  // Supprimer un fichier
  const removeFile = useCallback(async (pieceId: number): Promise<boolean> => {
    try {
      await devisService.deletePieceJointe(pieceId)
      await reload()
      return true
    } catch (err) {
      logger.error('useDevisMediaUpload removeFile error', err, {
        context: 'useDevisMediaUpload',
        pieceId,
      })
      return false
    }
  }, [reload])

  // Basculer la visibilité client
  const toggleVisibility = useCallback(async (pieceId: number, visible: boolean): Promise<boolean> => {
    try {
      await devisService.toggleVisibilitePieceJointe(pieceId, visible)
      await reload()
      return true
    } catch (err) {
      logger.error('useDevisMediaUpload toggleVisibility error', err, {
        context: 'useDevisMediaUpload',
        pieceId,
        visible,
      })
      return false
    }
  }, [reload])

  return {
    // Data
    pieces,

    // State
    uploading,
    uploadProgress,
    error,

    // Actions
    uploadFiles,
    removeFile,
    toggleVisibility,
    reload,
  }
}

export default useDevisMediaUpload
