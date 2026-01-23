/**
 * SignaturePad - Composant de signature electronique (FOR-05)
 * Canvas pour dessiner une signature avec support tactile
 */

import { useState, useRef, useEffect, useCallback } from 'react'
import { PenTool, Trash2, Check, X } from 'lucide-react'

interface SignaturePadProps {
  value?: string // URL ou base64
  onChange: (value: string) => void
  readOnly?: boolean
  signatureNom?: string
  onSignatureNomChange?: (nom: string) => void
}

export default function SignaturePad({
  value,
  onChange,
  readOnly = false,
  signatureNom = '',
  onSignatureNomChange,
}: SignaturePadProps) {
  const [isDrawing, setIsDrawing] = useState(false)
  const [hasSignature, setHasSignature] = useState(!!value)
  const [showModal, setShowModal] = useState(false)
  const [localNom, setLocalNom] = useState(signatureNom)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const contextRef = useRef<CanvasRenderingContext2D | null>(null)

  // Initialiser le canvas
  const initCanvas = useCallback(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    // Definir la taille du canvas
    const rect = canvas.getBoundingClientRect()
    canvas.width = rect.width * window.devicePixelRatio
    canvas.height = rect.height * window.devicePixelRatio

    const context = canvas.getContext('2d')
    if (!context) return

    context.scale(window.devicePixelRatio, window.devicePixelRatio)
    context.lineCap = 'round'
    context.lineJoin = 'round'
    context.strokeStyle = '#1f2937'
    context.lineWidth = 2
    contextRef.current = context

    // Fond blanc
    context.fillStyle = '#ffffff'
    context.fillRect(0, 0, rect.width, rect.height)
  }, [])

  useEffect(() => {
    if (showModal) {
      // Petit delai pour que le modal soit rendu
      const timer = setTimeout(initCanvas, 100)
      return () => clearTimeout(timer)
    }
  }, [showModal, initCanvas])

  const getCoordinates = (event: React.MouseEvent | React.TouchEvent): { x: number; y: number } | null => {
    const canvas = canvasRef.current
    if (!canvas) return null

    const rect = canvas.getBoundingClientRect()

    if ('touches' in event) {
      const touch = event.touches[0]
      return {
        x: touch.clientX - rect.left,
        y: touch.clientY - rect.top,
      }
    } else {
      return {
        x: event.clientX - rect.left,
        y: event.clientY - rect.top,
      }
    }
  }

  const startDrawing = (event: React.MouseEvent | React.TouchEvent) => {
    event.preventDefault()
    const coords = getCoordinates(event)
    if (!coords || !contextRef.current) return

    contextRef.current.beginPath()
    contextRef.current.moveTo(coords.x, coords.y)
    setIsDrawing(true)
    setHasSignature(true)
  }

  const draw = (event: React.MouseEvent | React.TouchEvent) => {
    event.preventDefault()
    if (!isDrawing || !contextRef.current) return

    const coords = getCoordinates(event)
    if (!coords) return

    contextRef.current.lineTo(coords.x, coords.y)
    contextRef.current.stroke()
  }

  const stopDrawing = () => {
    if (contextRef.current) {
      contextRef.current.closePath()
    }
    setIsDrawing(false)
  }

  const clearCanvas = () => {
    const canvas = canvasRef.current
    const context = contextRef.current
    if (!canvas || !context) return

    const rect = canvas.getBoundingClientRect()
    context.fillStyle = '#ffffff'
    context.fillRect(0, 0, rect.width, rect.height)
    setHasSignature(false)
  }

  const saveSignature = () => {
    const canvas = canvasRef.current
    if (!canvas || !hasSignature) return

    try {
      // Exporter en PNG base64
      const dataUrl = canvas.toDataURL('image/png')
      onChange(dataUrl)

      if (onSignatureNomChange && localNom) {
        onSignatureNomChange(localNom)
      }

      setShowModal(false)
    } catch (err) {
      console.error('Error exporting signature:', err)
      alert('Erreur lors de l\'export de la signature')
    }
  }

  const removeSignature = () => {
    onChange('')
    setHasSignature(false)
    if (onSignatureNomChange) {
      onSignatureNomChange('')
    }
    setLocalNom('')
  }

  // Affichage en mode lecture seule
  if (readOnly) {
    return (
      <div className="border-2 border-gray-200 rounded-lg overflow-hidden">
        {value ? (
          <div className="p-4 bg-white">
            <img
              src={value}
              alt="Signature"
              className="max-h-24 mx-auto"
            />
            {signatureNom && (
              <p className="text-sm text-gray-600 text-center mt-2">
                Signe par {signatureNom}
              </p>
            )}
          </div>
        ) : (
          <div className="p-6 flex items-center justify-center bg-gray-50">
            <div className="text-center text-gray-400">
              <PenTool className="w-10 h-10 mx-auto mb-2" />
              <p className="text-sm">Aucune signature</p>
            </div>
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="space-y-2">
      {/* Zone d'affichage de la signature */}
      <div className="border-2 border-dashed border-gray-300 rounded-lg overflow-hidden">
        {value ? (
          <div className="relative p-4 bg-white">
            <img
              src={value}
              alt="Signature"
              className="max-h-24 mx-auto"
            />
            {signatureNom && (
              <p className="text-sm text-gray-600 text-center mt-2">
                {signatureNom}
              </p>
            )}
            <button
              type="button"
              onClick={removeSignature}
              className="absolute top-2 right-2 p-1.5 bg-red-500 text-white rounded-full hover:bg-red-600 transition-colors"
              title="Supprimer la signature"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <div className="p-6 text-center">
            <PenTool className="w-10 h-10 mx-auto text-gray-400 mb-3" />
            <p className="text-sm text-gray-600 mb-4">
              Signez ce formulaire
            </p>
            <button
              type="button"
              onClick={() => setShowModal(true)}
              className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm font-medium"
            >
              Signer
            </button>
          </div>
        )}
      </div>

      {/* Modal de signature */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="fixed inset-0 bg-black/50" onClick={() => setShowModal(false)} />
          <div className="relative bg-white rounded-xl shadow-xl w-full max-w-md">
            <div className="flex items-center justify-between px-4 py-3 border-b">
              <h3 className="font-semibold text-gray-900">Signature</h3>
              <button
                onClick={() => setShowModal(false)}
                className="p-1.5 hover:bg-gray-100 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-4 space-y-4">
              {/* Champ nom */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nom du signataire
                </label>
                <input
                  type="text"
                  value={localNom}
                  onChange={(e) => setLocalNom(e.target.value)}
                  placeholder="Votre nom"
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>

              {/* Canvas de signature */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Signez ci-dessous
                </label>
                <div className="border-2 border-gray-300 rounded-lg overflow-hidden bg-white">
                  <canvas
                    ref={canvasRef}
                    className="w-full h-40 cursor-crosshair touch-none"
                    role="img"
                    aria-label="Zone de signature - dessinez votre signature"
                    onMouseDown={startDrawing}
                    onMouseMove={draw}
                    onMouseUp={stopDrawing}
                    onMouseLeave={stopDrawing}
                    onTouchStart={startDrawing}
                    onTouchMove={draw}
                    onTouchEnd={stopDrawing}
                  />
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center justify-between">
                <button
                  type="button"
                  onClick={clearCanvas}
                  className="flex items-center gap-2 px-3 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors text-sm"
                >
                  <Trash2 className="w-4 h-4" />
                  Effacer
                </button>
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => setShowModal(false)}
                    className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors text-sm"
                  >
                    Annuler
                  </button>
                  <button
                    type="button"
                    onClick={saveSignature}
                    disabled={!hasSignature || !localNom.trim()}
                    className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <Check className="w-4 h-4" />
                    Valider
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
