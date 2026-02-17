/**
 * useImageUpload - Hook pour l'upload d'images
 *
 * Encapsule uploadService pour les composants ImageUpload et MultiImageUpload:
 * - Upload photo de profil (USR-02)
 * - Upload photo de chantier (CHT-01)
 * - Compression côté client (FEED-19)
 * - État isUploading, error, preview
 */

import { useState, useRef } from 'react'
import { uploadService } from '../services/upload'
import { logger } from '../services/logger'

type UploadType = 'profile' | 'chantier'

interface UseImageUploadOptions {
  /** Type d'entité ciblée */
  type: UploadType
  /** ID de l'entité (ignoré pour 'profile') */
  entityId?: string
  /** Callback déclenché après upload réussi avec l'URL résultante */
  onUpload: (url: string) => void
}

interface UseImageUploadReturn {
  /** Ref à attacher à l'input[type=file] */
  inputRef: React.RefObject<HTMLInputElement | null>
  /** Upload en cours */
  isUploading: boolean
  /** Message d'erreur ou null */
  error: string | null
  /** URL de prévisualisation locale (avant confirmation serveur) */
  previewUrl: string | null
  /** Ouvre le sélecteur de fichier */
  handleClick: () => void
  /** Handler à passer à onChange de l'input file */
  handleFileChange: (e: React.ChangeEvent<HTMLInputElement>) => Promise<void>
}

/**
 * Gère le cycle complet d'upload d'image :
 * validation → preview → compression → upload → callback.
 */
export function useImageUpload({
  type,
  entityId = '',
  onUpload,
}: UseImageUploadOptions): UseImageUploadReturn {
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleClick = () => {
    inputRef.current?.click()
  }

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    if (!file.type.startsWith('image/')) {
      setError('Veuillez sélectionner une image')
      return
    }

    // Preview local immédiat
    const localUrl = URL.createObjectURL(file)
    setPreviewUrl(localUrl)
    setError(null)
    setIsUploading(true)

    try {
      const compressedFile = await uploadService.compressImage(file)

      let result
      if (type === 'profile') {
        result = await uploadService.uploadProfilePhoto(compressedFile)
      } else {
        result = await uploadService.uploadChantierPhoto(entityId, compressedFile)
      }

      onUpload(result.url)
      setPreviewUrl(null)
    } catch (err) {
      setError("Erreur lors de l'upload")
      setPreviewUrl(null)
      logger.error('Upload error', err, { context: 'useImageUpload' })
    } finally {
      setIsUploading(false)
      if (inputRef.current) {
        inputRef.current.value = ''
      }
    }
  }

  return {
    inputRef,
    isUploading,
    error,
    previewUrl,
    handleClick,
    handleFileChange,
  }
}

// ---------------------------------------------------------------------------
// Compression seule (pour MultiImageUpload)
// ---------------------------------------------------------------------------

interface UseImageCompressReturn {
  /** Compresse une image côté client */
  compressImage: (file: File, maxSizeMB?: number) => Promise<File>
}

/**
 * Expose uniquement la compression d'image (utilisé par MultiImageUpload).
 */
export function useImageCompress(): UseImageCompressReturn {
  return {
    compressImage: uploadService.compressImage.bind(uploadService),
  }
}

export default useImageUpload
