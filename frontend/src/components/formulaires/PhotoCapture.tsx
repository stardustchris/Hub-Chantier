/**
 * PhotoCapture - Composant de capture/upload de photo (FOR-04)
 * Supporte la prise de photo camera ou l'upload de fichier
 */

import { useState, useRef } from 'react'
import { Camera, X, Upload, Image as ImageIcon } from 'lucide-react'

interface PhotoCaptureProps {
  value?: string // URL ou base64
  onChange: (value: string) => void
  readOnly?: boolean
  label?: string
}

export default function PhotoCapture({
  value,
  onChange,
  readOnly = false,
  label,
}: PhotoCaptureProps) {
  const [preview, setPreview] = useState<string | null>(value || null)
  const [isLoading, setIsLoading] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const cameraInputRef = useRef<HTMLInputElement>(null)

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    // Valider le type de fichier
    if (!file.type.startsWith('image/')) {
      alert('Veuillez selectionner une image')
      return
    }

    // Valider la taille (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      alert('L\'image ne doit pas depasser 10 Mo')
      return
    }

    setIsLoading(true)

    try {
      // Convertir en base64
      const base64 = await fileToBase64(file)
      setPreview(base64)
      onChange(base64)
    } catch (err) {
      console.error('Error converting file:', err)
      alert('Erreur lors du traitement de l\'image')
    } finally {
      setIsLoading(false)
    }
  }

  const fileToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = () => {
        if (typeof reader.result === 'string') {
          resolve(reader.result)
        } else {
          reject(new Error('Failed to read file'))
        }
      }
      reader.onerror = reject
      reader.readAsDataURL(file)
    })
  }

  const handleRemove = () => {
    setPreview(null)
    onChange('')
    if (fileInputRef.current) fileInputRef.current.value = ''
    if (cameraInputRef.current) cameraInputRef.current.value = ''
  }

  const triggerCamera = () => {
    cameraInputRef.current?.click()
  }

  const triggerFileUpload = () => {
    fileInputRef.current?.click()
  }

  // Affichage en mode lecture seule
  if (readOnly) {
    return (
      <div className="border-2 border-gray-200 rounded-lg overflow-hidden">
        {preview ? (
          <div className="relative aspect-video">
            <img
              src={preview}
              alt={label || 'Photo'}
              className="w-full h-full object-cover"
            />
          </div>
        ) : (
          <div className="aspect-video flex items-center justify-center bg-gray-50">
            <div className="text-center text-gray-400">
              <ImageIcon className="w-10 h-10 mx-auto mb-2" />
              <p className="text-sm">Aucune photo</p>
            </div>
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="space-y-2">
      {/* Input fichiers caches */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleFileChange}
        className="hidden"
      />
      <input
        ref={cameraInputRef}
        type="file"
        accept="image/*"
        capture="environment"
        onChange={handleFileChange}
        className="hidden"
      />

      {/* Zone de preview ou upload */}
      <div className="border-2 border-dashed border-gray-300 rounded-lg overflow-hidden">
        {preview ? (
          <div className="relative">
            <img
              src={preview}
              alt={label || 'Photo capturee'}
              className="w-full h-48 object-cover"
            />
            <button
              type="button"
              onClick={handleRemove}
              className="absolute top-2 right-2 p-1.5 bg-red-500 text-white rounded-full hover:bg-red-600 transition-colors"
              title="Supprimer la photo"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <div className="p-6 text-center">
            {isLoading ? (
              <div className="py-4">
                <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto" />
                <p className="text-sm text-gray-500 mt-2">Chargement...</p>
              </div>
            ) : (
              <>
                <Camera className="w-10 h-10 mx-auto text-gray-400 mb-3" />
                <p className="text-sm text-gray-600 mb-4">
                  Prenez une photo ou selectionnez une image
                </p>
                <div className="flex items-center justify-center gap-3">
                  <button
                    type="button"
                    onClick={triggerCamera}
                    className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm font-medium"
                  >
                    <Camera className="w-4 h-4" />
                    Prendre une photo
                  </button>
                  <button
                    type="button"
                    onClick={triggerFileUpload}
                    className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium"
                  >
                    <Upload className="w-4 h-4" />
                    Galerie
                  </button>
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
