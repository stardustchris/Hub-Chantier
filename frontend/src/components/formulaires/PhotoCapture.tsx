/**
 * PhotoCapture - Composant de capture/upload de photo (FOR-04)
 * Supporte la prise de photo camera ou l'upload de fichier
 * Solution hybride : détecte mobile/desktop et adapte le comportement
 */

import { useState, useRef, useEffect } from 'react'
import { Camera, X, Upload, Image as ImageIcon } from 'lucide-react'
import { logger } from '../../services/logger'

interface AttachedPhoto {
  url: string
  nom_fichier: string
}

interface PhotoCaptureProps {
  value?: string // URL ou base64
  onChange: (value: string) => void
  readOnly?: boolean
  label?: string
  attachedPhotos?: AttachedPhoto[]
}

// Détection de l'environnement
const isMobileDevice = (): boolean => {
  return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
    navigator.userAgent
  ) || ('ontouchstart' in window && navigator.maxTouchPoints > 0)
}

export default function PhotoCapture({
  value,
  onChange,
  readOnly = false,
  label,
  attachedPhotos,
}: PhotoCaptureProps) {
  const [preview, setPreview] = useState<string | null>(value || null)
  const [isLoading, setIsLoading] = useState(false)
  const [isMobile, setIsMobile] = useState(false)
  const [showCameraModal, setShowCameraModal] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const cameraInputRef = useRef<HTMLInputElement>(null)
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const streamRef = useRef<MediaStream | null>(null)

  useEffect(() => {
    setIsMobile(isMobileDevice())
  }, [])

  useEffect(() => {
    // Cleanup du stream vidéo au démontage
    return () => {
      stopCamera()
    }
  }, [])

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    // Valider le type de fichier
    if (!file.type.startsWith('image/')) {
      logger.warn('Veuillez selectionner une image', null, { context: 'PhotoCapture', showToast: true })
      return
    }

    // Valider la taille (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      logger.warn('L\'image ne doit pas depasser 10 Mo', null, { context: 'PhotoCapture', showToast: true })
      return
    }

    setIsLoading(true)

    try {
      // Convertir en base64
      const base64 = await fileToBase64(file)
      setPreview(base64)
      onChange(base64)
    } catch (err) {
      logger.error('Erreur lors du traitement de l\'image', err, { context: 'PhotoCapture', showToast: true })
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

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop())
      streamRef.current = null
    }
  }

  const startCamera = async () => {
    try {
      // Vérifier si mediaDevices est disponible
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        logger.warn('La capture vidéo n\'est pas disponible sur ce navigateur. Utilisez la galerie.', null, {
          context: 'PhotoCapture',
          showToast: true
        })
        // Fallback immédiat vers sélecteur de fichier
        setTimeout(() => fileInputRef.current?.click(), 100)
        return
      }

      // Vérifier d'abord si la permission est déjà refusée
      if (navigator.permissions) {
        try {
          const permissionStatus = await navigator.permissions.query({ name: 'camera' as PermissionName })
          if (permissionStatus.state === 'denied') {
            logger.warn('Accès à la caméra refusé. Cliquez sur "Galerie" pour sélectionner une image, ou autorisez la caméra dans les paramètres du navigateur.', null, {
              context: 'PhotoCapture',
              showToast: true
            })
            return // Ne pas ouvrir automatiquement le file picker pour éviter la confusion
          }
        } catch {
          // Ignorer si permissions API n'est pas supportée
        }
      }

      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment' }, // Caméra arrière sur mobile
        audio: false,
      })

      if (videoRef.current) {
        videoRef.current.srcObject = stream
        streamRef.current = stream
        setShowCameraModal(true)
      }
    } catch (err) {
      const error = err as Error
      // Identifier le type d'erreur pour un message approprié
      if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
        logger.warn('Accès à la caméra refusé. Cliquez sur "Galerie" pour sélectionner une image, ou autorisez la caméra dans les paramètres du navigateur.', null, {
          context: 'PhotoCapture',
          showToast: true
        })
      } else if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
        logger.warn('Aucune caméra détectée. Utilisez la galerie pour sélectionner une image.', null, {
          context: 'PhotoCapture',
          showToast: true
        })
      } else {
        logger.error('Impossible d\'accéder à la caméra', err, {
          context: 'PhotoCapture',
          showToast: true
        })
      }
      // Ne pas ouvrir automatiquement le file picker - l'utilisateur peut cliquer sur Galerie
    }
  }

  const capturePhoto = () => {
    if (!videoRef.current || !canvasRef.current) return

    const video = videoRef.current
    const canvas = canvasRef.current

    // Configurer la taille du canvas
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight

    // Dessiner l'image
    const ctx = canvas.getContext('2d')
    if (ctx) {
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height)

      // Convertir en base64
      const base64 = canvas.toDataURL('image/jpeg', 0.9)
      setPreview(base64)
      onChange(base64)

      // Fermer la caméra
      stopCamera()
      setShowCameraModal(false)
    }
  }

  const cancelCamera = () => {
    stopCamera()
    setShowCameraModal(false)
  }

  const triggerCamera = () => {
    if (isMobile) {
      // Sur mobile : utiliser l'input natif (fonctionne mieux)
      cameraInputRef.current?.click()
    } else {
      // Sur desktop : ouvrir la modal avec preview vidéo
      startCamera()
    }
  }

  const triggerFileUpload = () => {
    fileInputRef.current?.click()
  }

  // Affichage en mode lecture seule
  if (readOnly) {
    // Afficher les photos attachees si disponibles
    if (attachedPhotos && attachedPhotos.length > 0) {
      return (
        <div className="grid grid-cols-2 gap-2">
          {attachedPhotos.map((photo, index) => (
            <div key={index} className="border-2 border-gray-200 rounded-lg overflow-hidden">
              <div className="relative aspect-video">
                <img
                  src={photo.url}
                  alt={photo.nom_fichier}
                  className="w-full h-full object-cover"
                />
              </div>
              <p className="text-xs text-gray-500 px-2 py-1 truncate">{photo.nom_fichier}</p>
            </div>
          ))}
        </div>
      )
    }

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
            <div className="text-center text-gray-600">
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

      {/* Canvas caché pour capture desktop */}
      <canvas ref={canvasRef} className="hidden" />

      {/* Modal caméra desktop */}
      {showCameraModal && (
        <div className="fixed inset-0 bg-black/90 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl w-full max-w-2xl overflow-hidden">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b">
              <h3 className="text-lg font-semibold">Prendre une photo</h3>
              <button
                onClick={cancelCamera}
                className="p-2 hover:bg-gray-100 rounded-full transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Vidéo preview */}
            <div className="relative bg-black">
              <video
                ref={videoRef}
                autoPlay
                playsInline
                className="w-full h-[400px] object-cover"
              />
            </div>

            {/* Footer avec bouton capture */}
            <div className="p-4 flex justify-center gap-3">
              <button
                onClick={cancelCamera}
                className="px-6 py-3 border border-gray-300 rounded-xl font-medium hover:bg-gray-50 transition-colors"
              >
                Annuler
              </button>
              <button
                onClick={capturePhoto}
                className="px-6 py-3 bg-primary-600 text-white rounded-xl font-medium hover:bg-primary-700 transition-colors flex items-center gap-2"
              >
                <Camera className="w-5 h-5" />
                Capturer
              </button>
            </div>
          </div>
        </div>
      )}

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
                <Camera className="w-10 h-10 mx-auto text-gray-600 mb-3" />
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
