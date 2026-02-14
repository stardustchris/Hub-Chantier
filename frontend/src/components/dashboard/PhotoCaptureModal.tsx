/**
 * PhotoCaptureModal - Modal pour capturer/uploader une photo depuis le dashboard
 * Utilise le composant PhotoCapture existant pour la capture
 */

import { useState } from 'react'
import { X, Loader2 } from 'lucide-react'
import PhotoCapture from '../formulaires/PhotoCapture'
import { useFocusTrap } from '../../hooks/useFocusTrap'

interface PhotoCaptureModalProps {
  isOpen: boolean
  onClose: () => void
  onSubmit: (photoBase64: string, description: string) => Promise<void>
}

export default function PhotoCaptureModal({
  isOpen,
  onClose,
  onSubmit,
}: PhotoCaptureModalProps) {
  const focusTrapRef = useFocusTrap({ enabled: isOpen, onClose })
  const [photo, setPhoto] = useState<string>('')
  const [description, setDescription] = useState<string>('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  if (!isOpen) return null

  const handleSubmit = async () => {
    if (!photo) return

    setIsSubmitting(true)
    try {
      await onSubmit(photo, description)
      // Reset et fermer
      setPhoto('')
      setDescription('')
      onClose()
    } catch (error) {
      // L'erreur sera gérée par le composant parent
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleClose = () => {
    if (!isSubmitting) {
      setPhoto('')
      setDescription('')
      onClose()
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div
        ref={focusTrapRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
        className="bg-white rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <h2 id="modal-title" className="text-xl font-semibold text-gray-800">
            Ajouter une photo
          </h2>
          <button
            onClick={handleClose}
            disabled={isSubmitting}
            className="p-2 hover:bg-gray-100 rounded-full transition-colors disabled:opacity-50"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 space-y-4">
          {/* Photo Capture */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Photo
            </label>
            <PhotoCapture
              value={photo}
              onChange={setPhoto}
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Description (optionnelle)
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Ajouter une description à votre photo..."
              rows={3}
              className="w-full border border-gray-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>
        </div>

        {/* Footer */}
        <div className="flex gap-3 p-6 border-t">
          <button
            onClick={handleClose}
            disabled={isSubmitting}
            className="flex-1 py-3 border border-gray-300 rounded-xl font-medium hover:bg-gray-50 transition-colors disabled:opacity-50"
          >
            Annuler
          </button>
          <button
            onClick={handleSubmit}
            disabled={!photo || isSubmitting}
            className="flex-1 py-3 bg-green-600 text-white rounded-xl font-medium hover:bg-green-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Publication...
              </>
            ) : (
              'Publier'
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
