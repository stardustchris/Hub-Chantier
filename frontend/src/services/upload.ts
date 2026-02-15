import api from './api'

export interface UploadResponse {
  url: string
  thumbnail_url?: string
}

export interface MultiUploadResponse {
  files: UploadResponse[]
}

// Configuration
const MAX_FILE_SIZE_MB = 2
const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']

/**
 * Erreur de validation d'upload.
 */
export class UploadValidationError extends Error {
  constructor(message: string) {
    super(message)
    this.name = 'UploadValidationError'
  }
}

/**
 * Valide un fichier avant upload.
 * @throws UploadValidationError si le fichier n'est pas valide.
 */
function validateFile(file: File): void {
  if (!ALLOWED_TYPES.includes(file.type)) {
    throw new UploadValidationError(
      `Type de fichier non supporté. Formats acceptés: JPEG, PNG, GIF, WebP`
    )
  }
  if (file.size > MAX_FILE_SIZE_BYTES) {
    throw new UploadValidationError(
      `Fichier trop volumineux (max ${MAX_FILE_SIZE_MB} Mo). Utilisez la compression automatique.`
    )
  }
}

/**
 * Service d'upload de fichiers.
 * Implémente USR-02, FEED-02, FEED-19, CHT-01.
 */
export const uploadService = {
  /**
   * Upload une photo de profil (USR-02).
   * @throws UploadValidationError si le fichier n'est pas valide.
   */
  async uploadProfilePhoto(file: File): Promise<UploadResponse> {
    validateFile(file)
    const formData = new FormData()
    formData.append('file', file)

    const response = await api.post<UploadResponse>('/api/uploads/profile', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  /**
   * Upload des médias pour un post (FEED-02).
   * Maximum 5 photos, compressées automatiquement (FEED-19).
   * @throws UploadValidationError si un fichier n'est pas valide.
   */
  async uploadPostMedia(postId: string, files: File[]): Promise<MultiUploadResponse> {
    // Valider tous les fichiers avant upload
    files.forEach(validateFile)

    const formData = new FormData()
    files.forEach((file) => {
      formData.append('files', file)
    })

    const response = await api.post<MultiUploadResponse>(
      `/api/uploads/posts/${postId}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )
    return response.data
  },

  /**
   * Upload une photo de couverture de chantier (CHT-01).
   * @throws UploadValidationError si le fichier n'est pas valide.
   */
  async uploadChantierPhoto(chantierId: string, file: File): Promise<UploadResponse> {
    validateFile(file)
    const formData = new FormData()
    formData.append('file', file)

    const response = await api.post<UploadResponse>(
      `/api/uploads/chantiers/${chantierId}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )
    return response.data
  },

  /**
   * Compresse une image côté client avant upload (FEED-19).
   * Réduit à max 1920px et qualité 85%.
   *
   * TODO Performance: Le backend devrait également générer des thumbnails WebP
   * à différentes tailles (thumbnail, medium, large) pour optimiser le chargement.
   * Cela permettrait d'utiliser des srcset responsive et de réduire la bande passante.
   */
  async compressImage(file: File, maxSizeMB: number = 2): Promise<File> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = (event) => {
        const img = new Image()
        img.onload = () => {
          const canvas = document.createElement('canvas')
          const ctx = canvas.getContext('2d')
          if (!ctx) {
            reject(new Error('Cannot create canvas context'))
            return
          }

          // Calculer les nouvelles dimensions
          const MAX_DIM = 1920
          let { width, height } = img
          if (width > MAX_DIM || height > MAX_DIM) {
            if (width > height) {
              height = (height / width) * MAX_DIM
              width = MAX_DIM
            } else {
              width = (width / height) * MAX_DIM
              height = MAX_DIM
            }
          }

          canvas.width = width
          canvas.height = height
          ctx.drawImage(img, 0, 0, width, height)

          // Compression progressive
          let quality = 0.9
          const maxSizeBytes = maxSizeMB * 1024 * 1024

          const tryCompress = () => {
            canvas.toBlob(
              (blob) => {
                if (!blob) {
                  reject(new Error('Compression failed'))
                  return
                }

                if (blob.size <= maxSizeBytes || quality <= 0.3) {
                  const compressedFile = new File([blob], file.name, {
                    type: 'image/jpeg',
                    lastModified: Date.now(),
                  })
                  resolve(compressedFile)
                } else {
                  quality -= 0.1
                  tryCompress()
                }
              },
              'image/jpeg',
              quality
            )
          }

          tryCompress()
        }
        img.onerror = () => reject(new Error('Failed to load image'))
        img.src = event.target?.result as string
      }
      reader.onerror = () => reject(new Error('Failed to read file'))
      reader.readAsDataURL(file)
    })
  },
}
