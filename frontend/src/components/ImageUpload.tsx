import { useState, useRef } from 'react'
import { Camera, Loader2, AlertCircle } from 'lucide-react'
import { uploadService } from '../services/upload'

interface ImageUploadProps {
  /** URL de l'image actuelle */
  currentImage?: string
  /** Callback appelé après un upload réussi */
  onUpload: (url: string) => void
  /** Type d'upload: profile, post, ou chantier */
  type: 'profile' | 'chantier'
  /** ID de l'entité (utilisateur ou chantier) */
  entityId: string
  /** Classe CSS additionnelle pour le conteneur */
  className?: string
  /** Taille du placeholder (default, small, large) */
  size?: 'small' | 'default' | 'large'
  /** Placeholder à afficher si pas d'image */
  placeholder?: React.ReactNode
}

/**
 * Composant d'upload d'image réutilisable.
 * Implémente USR-02 et CHT-01.
 */
export default function ImageUpload({
  currentImage,
  onUpload,
  type,
  entityId,
  className = '',
  size = 'default',
  placeholder,
}: ImageUploadProps) {
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const sizeClasses = {
    small: 'w-16 h-16',
    default: 'w-24 h-24',
    large: 'w-32 h-32',
  }

  const handleClick = () => {
    inputRef.current?.click()
  }

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    // Validation basique
    if (!file.type.startsWith('image/')) {
      setError('Veuillez sélectionner une image')
      return
    }

    // Preview local
    const localUrl = URL.createObjectURL(file)
    setPreviewUrl(localUrl)
    setError(null)
    setIsUploading(true)

    try {
      // Compresser l'image (FEED-19)
      const compressedFile = await uploadService.compressImage(file)

      // Upload selon le type
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
      console.error('Upload error:', err)
    } finally {
      setIsUploading(false)
      // Reset input
      if (inputRef.current) {
        inputRef.current.value = ''
      }
    }
  }

  const displayImage = previewUrl || currentImage

  return (
    <div className={`relative ${className}`}>
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        onChange={handleFileChange}
        className="hidden"
      />

      <button
        type="button"
        onClick={handleClick}
        disabled={isUploading}
        className={`
          ${sizeClasses[size]}
          relative rounded-full overflow-hidden
          bg-gray-100 hover:bg-gray-200
          flex items-center justify-center
          transition-all cursor-pointer
          border-2 border-dashed border-gray-300 hover:border-primary-400
          group
        `}
      >
        {displayImage ? (
          <>
            <img
              src={displayImage}
              alt="Photo"
              className="w-full h-full object-cover"
            />
            <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
              <Camera className="w-6 h-6 text-white" />
            </div>
          </>
        ) : placeholder ? (
          <div className="flex items-center justify-center w-full h-full group-hover:opacity-70">
            {placeholder}
          </div>
        ) : (
          <Camera className="w-8 h-8 text-gray-400 group-hover:text-primary-500" />
        )}

        {isUploading && (
          <div className="absolute inset-0 bg-white/80 flex items-center justify-center">
            <Loader2 className="w-6 h-6 animate-spin text-primary-600" />
          </div>
        )}
      </button>

      {error && (
        <div className="absolute -bottom-6 left-0 right-0 flex items-center justify-center gap-1 text-xs text-red-500">
          <AlertCircle className="w-3 h-3" />
          {error}
        </div>
      )}
    </div>
  )
}

interface MultiImageUploadProps {
  /** Callback appelé quand des fichiers sont sélectionnés */
  onFilesSelected: (files: File[]) => void
  /** Nombre maximum de fichiers */
  maxFiles?: number
  /** Désactivé */
  disabled?: boolean
}

/**
 * Composant d'upload multi-images pour les posts.
 * Implémente FEED-02.
 */
export function MultiImageUpload({
  onFilesSelected,
  maxFiles = 5,
  disabled = false,
}: MultiImageUploadProps) {
  const inputRef = useRef<HTMLInputElement>(null)

  const handleClick = () => {
    inputRef.current?.click()
  }

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || [])
    if (files.length === 0) return

    // Limiter le nombre de fichiers
    const validFiles = files.slice(0, maxFiles).filter((f) => f.type.startsWith('image/'))

    // Compresser toutes les images
    const compressedFiles = await Promise.all(
      validFiles.map((f) => uploadService.compressImage(f))
    )

    onFilesSelected(compressedFiles)

    // Reset
    if (inputRef.current) {
      inputRef.current.value = ''
    }
  }

  return (
    <>
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        multiple
        onChange={handleFileChange}
        className="hidden"
      />
      <button
        type="button"
        onClick={handleClick}
        disabled={disabled}
        className="p-2 text-gray-500 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        title={`Ajouter des photos (max ${maxFiles})`}
      >
        <Camera className="w-5 h-5" />
      </button>
    </>
  )
}
