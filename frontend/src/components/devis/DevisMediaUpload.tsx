/**
 * DevisMediaUpload - Composant d'upload de photos/fiches techniques pour devis
 * DEV-07: Insertion multimédia
 *
 * Features:
 * - Upload drag & drop
 * - Preview miniatures
 * - Support images (JPEG, PNG, GIF, WebP) et documents (PDF, Word)
 * - Gestion visibilité client
 * - Accessibilité complète
 */

import { useCallback, useRef, useState } from 'react'
import {
  Upload,
  X,
  Eye,
  EyeOff,
  FileText,
  Image as ImageIcon,
  Loader2,
  AlertCircle,
} from 'lucide-react'
import type { PieceJointeDevis } from '../../types'

interface DevisMediaUploadProps {
  pieces: PieceJointeDevis[]
  uploading: boolean
  uploadProgress: number
  error: string | null
  onUpload: (files: File[], visibleClient?: boolean) => Promise<boolean>
  onRemove: (pieceId: number) => Promise<boolean>
  onToggleVisibility: (pieceId: number, visible: boolean) => Promise<boolean>
}

const ACCEPTED_TYPES = {
  'image/jpeg': ['.jpg', '.jpeg'],
  'image/png': ['.png'],
  'image/gif': ['.gif'],
  'image/webp': ['.webp'],
  'application/pdf': ['.pdf'],
  'application/msword': ['.doc'],
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
}

export default function DevisMediaUpload({
  pieces,
  uploading,
  uploadProgress,
  error,
  onUpload,
  onRemove,
  onToggleVisibility,
}: DevisMediaUploadProps) {
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [dragActive, setDragActive] = useState(false)
  const [visibleClient, setVisibleClient] = useState(true)

  // Gérer le drag over
  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }, [])

  // Gérer le drop
  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      e.stopPropagation()
      setDragActive(false)

      if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        const files = Array.from(e.dataTransfer.files)
        onUpload(files, visibleClient)
      }
    },
    [onUpload, visibleClient]
  )

  // Gérer la sélection de fichiers
  const handleFileSelect = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      if (e.target.files && e.target.files.length > 0) {
        const files = Array.from(e.target.files)
        onUpload(files, visibleClient)
        // Reset input
        if (fileInputRef.current) {
          fileInputRef.current.value = ''
        }
      }
    },
    [onUpload, visibleClient]
  )

  // Ouvrir le sélecteur de fichiers
  const handleBrowseClick = useCallback(() => {
    fileInputRef.current?.click()
  }, [])

  // Formater la taille de fichier
  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} o`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} Ko`
    return `${(bytes / (1024 * 1024)).toFixed(1)} Mo`
  }

  return (
    <div className="space-y-4">
      {/* Zone d'upload */}
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        className={`relative border-2 border-dashed rounded-xl p-8 transition-colors ${
          dragActive
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 bg-gray-50 hover:border-gray-400'
        } ${uploading ? 'pointer-events-none opacity-50' : ''}`}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept={Object.keys(ACCEPTED_TYPES).join(',')}
          onChange={handleFileSelect}
          className="hidden"
          aria-label="Sélectionner des fichiers"
          disabled={uploading}
        />

        <div className="flex flex-col items-center justify-center gap-4 text-center">
          <div className="p-4 bg-white rounded-full shadow-sm">
            <Upload className="w-8 h-8 text-gray-600" />
          </div>

          <div>
            <p className="text-sm font-medium text-gray-900 mb-1">
              Glissez-déposez vos fichiers ici
            </p>
            <p className="text-xs text-gray-600">
              ou{' '}
              <button
                onClick={handleBrowseClick}
                className="text-blue-600 hover:text-blue-700 underline focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded"
                disabled={uploading}
              >
                parcourez
              </button>
            </p>
            <p className="text-xs text-gray-500 mt-2">
              Images (JPEG, PNG, GIF, WebP) ou documents (PDF, Word) - Max 10MB
            </p>
          </div>

          {/* Option visibilité */}
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="visible-client"
              checked={visibleClient}
              onChange={(e) => setVisibleClient(e.target.checked)}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              disabled={uploading}
            />
            <label htmlFor="visible-client" className="text-sm text-gray-700">
              Visible par le client
            </label>
          </div>
        </div>

        {/* Progress bar */}
        {uploading && (
          <div className="absolute inset-0 flex items-center justify-center bg-white/80 rounded-xl">
            <div className="w-64 text-center">
              <Loader2 className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-2" />
              <p className="text-sm text-gray-700 mb-2">Upload en cours...</p>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all"
                  style={{ width: `${uploadProgress}%` }}
                  role="progressbar"
                  aria-valuenow={uploadProgress}
                  aria-valuemin={0}
                  aria-valuemax={100}
                />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Erreur */}
      {error && (
        <div
          className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-start gap-2"
          role="alert"
        >
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <div className="text-sm whitespace-pre-wrap">{error}</div>
        </div>
      )}

      {/* Liste des fichiers uploadés */}
      {pieces.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-sm font-medium text-gray-900">
            Fichiers joints ({pieces.length})
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {pieces.map((piece) => (
              <MediaThumbnail
                key={piece.id}
                piece={piece}
                onRemove={() => onRemove(piece.id)}
                onToggleVisibility={() => onToggleVisibility(piece.id, !piece.visible_client)}
                formatFileSize={formatFileSize}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

// Miniature de fichier
interface MediaThumbnailProps {
  piece: PieceJointeDevis
  onRemove: () => void
  onToggleVisibility: () => void
  formatFileSize: (bytes: number) => string
}

function MediaThumbnail({
  piece,
  onRemove,
  onToggleVisibility,
  formatFileSize,
}: MediaThumbnailProps) {
  const isImage = piece.type_fichier === 'image'

  return (
    <div className="relative group bg-white border border-gray-200 rounded-lg p-3 hover:shadow-md transition-shadow">
      {/* Icon ou preview */}
      <div className="flex items-center justify-center h-32 bg-gray-50 rounded-lg mb-2">
        {isImage ? (
          <ImageIcon className="w-12 h-12 text-gray-600" />
        ) : (
          <FileText className="w-12 h-12 text-gray-600" />
        )}
      </div>

      {/* Info */}
      <div className="space-y-1">
        <p className="text-sm font-medium text-gray-900 truncate" title={piece.nom_fichier ?? undefined}>
          {piece.nom_fichier}
        </p>
        <p className="text-xs text-gray-500">{formatFileSize(piece.taille_octets ?? 0)}</p>
      </div>

      {/* Actions */}
      <div className="absolute top-2 right-2 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
        <button
          onClick={onToggleVisibility}
          className="p-2 bg-white rounded-lg shadow-sm border border-gray-200 hover:bg-gray-50 min-h-[44px] min-w-[44px] flex items-center justify-center"
          aria-label={piece.visible_client ? 'Masquer au client' : 'Afficher au client'}
          title={piece.visible_client ? 'Masquer au client' : 'Afficher au client'}
        >
          {piece.visible_client ? (
            <Eye className="w-4 h-4 text-blue-600" />
          ) : (
            <EyeOff className="w-4 h-4 text-gray-600" />
          )}
        </button>

        <button
          onClick={onRemove}
          className="p-2 bg-white rounded-lg shadow-sm border border-gray-200 hover:bg-red-50 hover:border-red-200 min-h-[44px] min-w-[44px] flex items-center justify-center"
          aria-label="Supprimer"
          title="Supprimer"
        >
          <X className="w-4 h-4 text-red-600" />
        </button>
      </div>

      {/* Badge visibilité */}
      {piece.visible_client && (
        <div className="absolute bottom-2 left-2">
          <span className="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full">
            <Eye className="w-3 h-3" />
            Client
          </span>
        </div>
      )}
    </div>
  )
}
