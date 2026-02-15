/**
 * PhotoAnnotator - Canvas-based photo annotation component
 * Supports arrow, circle, rectangle, text, and pen drawing tools
 * Works on mobile (touch) and desktop (mouse)
 */

import { useState, useRef, useEffect, useCallback } from 'react'
import {
  ArrowRight,
  Circle,
  Square,
  Type,
  Pencil,
  Undo,
  Trash2,
  Save,
  X,
} from 'lucide-react'
import { logger } from '../../services/logger'

type Tool = 'arrow' | 'circle' | 'rectangle' | 'text' | 'pen'
type Color = 'red' | 'yellow' | 'blue' | 'white'
type Thickness = 2 | 4 | 6

interface Point {
  x: number
  y: number
}

interface PhotoAnnotatorProps {
  imageUrl: string
  onSave: (annotatedImageDataUrl: string) => void
  onCancel: () => void
  width?: number
}

const COLORS: { value: Color; label: string; hex: string }[] = [
  { value: 'red', label: 'Rouge', hex: '#EF4444' },
  { value: 'yellow', label: 'Jaune', hex: '#F59E0B' },
  { value: 'blue', label: 'Bleu', hex: '#3B82F6' },
  { value: 'white', label: 'Blanc', hex: '#FFFFFF' },
]

const THICKNESSES: Thickness[] = [2, 4, 6]

export default function PhotoAnnotator({
  imageUrl,
  onSave,
  onCancel,
  width,
}: PhotoAnnotatorProps) {
  // Tool state
  const [tool, setTool] = useState<Tool>('pen')
  const [color, setColor] = useState<Color>('red')
  const [thickness, setThickness] = useState<Thickness>(4)

  // Drawing state
  const [isDrawing, setIsDrawing] = useState(false)
  const [startPoint, setStartPoint] = useState<Point | null>(null)
  const [currentPoint, setCurrentPoint] = useState<Point | null>(null)
  const [penPoints, setPenPoints] = useState<Point[]>([])

  // Text input state
  const [showTextInput, setShowTextInput] = useState(false)
  const [textPosition, setTextPosition] = useState<Point | null>(null)
  const [textValue, setTextValue] = useState('')

  // Canvas refs
  const containerRef = useRef<HTMLDivElement>(null)
  const imageRef = useRef<HTMLImageElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const tempCanvasRef = useRef<HTMLCanvasElement>(null)

  // History for undo
  const [history, setHistory] = useState<ImageData[]>([])

  // Image loaded state
  const [imageLoaded, setImageLoaded] = useState(false)
  const [imageDimensions, setImageDimensions] = useState({ width: 0, height: 0 })

  // Load image and initialize canvas
  useEffect(() => {
    const img = new Image()
    img.crossOrigin = 'anonymous'
    img.onload = () => {
      const maxWidth = width || 800
      const scale = maxWidth / img.width
      const canvasWidth = Math.min(img.width, maxWidth)
      const canvasHeight = img.height * scale

      setImageDimensions({ width: canvasWidth, height: canvasHeight })
      setImageLoaded(true)

      // Initialize canvas
      if (canvasRef.current) {
        canvasRef.current.width = canvasWidth
        canvasRef.current.height = canvasHeight
      }
      if (tempCanvasRef.current) {
        tempCanvasRef.current.width = canvasWidth
        tempCanvasRef.current.height = canvasHeight
      }
    }
    img.onerror = () => {
      logger.error('Failed to load image for annotation', null, {
        context: 'PhotoAnnotator',
        showToast: true,
      })
    }
    img.src = imageUrl
  }, [imageUrl, width])

  // Get canvas context
  const getContext = useCallback(() => {
    return canvasRef.current?.getContext('2d')
  }, [])

  // Get normalized coordinates from mouse/touch event
  const getCoordinates = useCallback(
    (event: React.MouseEvent | React.TouchEvent): Point | null => {
      const canvas = canvasRef.current
      if (!canvas) return null

      const rect = canvas.getBoundingClientRect()
      let clientX: number
      let clientY: number

      if ('touches' in event) {
        if (event.touches.length === 0) return null
        clientX = event.touches[0].clientX
        clientY = event.touches[0].clientY
      } else {
        clientX = event.clientX
        clientY = event.clientY
      }

      const x = clientX - rect.left
      const y = clientY - rect.top

      return { x, y }
    },
    []
  )

  // Save current canvas state to history
  const saveToHistory = useCallback(() => {
    const ctx = getContext()
    if (!ctx || !canvasRef.current) return

    const imageData = ctx.getImageData(
      0,
      0,
      canvasRef.current.width,
      canvasRef.current.height
    )
    setHistory((prev) => [...prev.slice(-19), imageData]) // Keep last 20
  }, [getContext])

  // Undo last action
  const handleUndo = useCallback(() => {
    if (history.length === 0) return

    const ctx = getContext()
    if (!ctx || !canvasRef.current) return

    const previousState = history[history.length - 1]
    ctx.putImageData(previousState, 0, 0)
    setHistory((prev) => prev.slice(0, -1))
  }, [history, getContext])

  // Clear all annotations
  const handleClear = useCallback(() => {
    const ctx = getContext()
    if (!ctx || !canvasRef.current) return

    ctx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height)
    setHistory([])
  }, [getContext])

  // Draw arrow
  const drawArrow = useCallback(
    (ctx: CanvasRenderingContext2D, start: Point, end: Point) => {
      const headLength = 15 + thickness * 2
      const angle = Math.atan2(end.y - start.y, end.x - start.x)

      // Draw line
      ctx.beginPath()
      ctx.moveTo(start.x, start.y)
      ctx.lineTo(end.x, end.y)
      ctx.stroke()

      // Draw arrowhead
      ctx.beginPath()
      ctx.moveTo(end.x, end.y)
      ctx.lineTo(
        end.x - headLength * Math.cos(angle - Math.PI / 6),
        end.y - headLength * Math.sin(angle - Math.PI / 6)
      )
      ctx.moveTo(end.x, end.y)
      ctx.lineTo(
        end.x - headLength * Math.cos(angle + Math.PI / 6),
        end.y - headLength * Math.sin(angle + Math.PI / 6)
      )
      ctx.stroke()
    },
    [thickness]
  )

  // Draw circle
  const drawCircle = useCallback(
    (ctx: CanvasRenderingContext2D, center: Point, radius: number) => {
      ctx.beginPath()
      ctx.arc(center.x, center.y, radius, 0, 2 * Math.PI)
      ctx.stroke()
    },
    []
  )

  // Draw rectangle
  const drawRectangle = useCallback(
    (ctx: CanvasRenderingContext2D, start: Point, end: Point) => {
      const width = end.x - start.x
      const height = end.y - start.y
      ctx.strokeRect(start.x, start.y, width, height)
    },
    []
  )

  // Draw text
  const drawText = useCallback(
    (ctx: CanvasRenderingContext2D, position: Point, text: string) => {
      const fontSize = 16 + thickness * 2
      ctx.font = `bold ${fontSize}px sans-serif`

      // Measure text
      const metrics = ctx.measureText(text)
      const textWidth = metrics.width
      const textHeight = fontSize

      // Draw background
      ctx.fillStyle = 'rgba(0, 0, 0, 0.6)'
      ctx.fillRect(
        position.x - 4,
        position.y - textHeight - 4,
        textWidth + 8,
        textHeight + 8
      )

      // Draw text
      ctx.fillStyle = COLORS.find((c) => c.value === color)?.hex || '#EF4444'
      ctx.fillText(text, position.x, position.y)
    },
    [color, thickness]
  )

  // Draw pen stroke
  const drawPen = useCallback(
    (ctx: CanvasRenderingContext2D, points: Point[]) => {
      if (points.length < 2) return

      ctx.beginPath()
      ctx.moveTo(points[0].x, points[0].y)
      for (let i = 1; i < points.length; i++) {
        ctx.lineTo(points[i].x, points[i].y)
      }
      ctx.stroke()
    },
    []
  )

  // Setup drawing context
  const setupContext = useCallback(
    (ctx: CanvasRenderingContext2D) => {
      ctx.strokeStyle = COLORS.find((c) => c.value === color)?.hex || '#EF4444'
      ctx.lineWidth = thickness
      ctx.lineCap = 'round'
      ctx.lineJoin = 'round'
    },
    [color, thickness]
  )

  // Handle start drawing
  const handleStartDrawing = useCallback(
    (event: React.MouseEvent | React.TouchEvent) => {
      event.preventDefault()
      const point = getCoordinates(event)
      if (!point) return

      if (tool === 'text') {
        setTextPosition(point)
        setShowTextInput(true)
        return
      }

      setIsDrawing(true)
      setStartPoint(point)
      setCurrentPoint(point)

      if (tool === 'pen') {
        setPenPoints([point])
      }
    },
    [tool, getCoordinates]
  )

  // Handle drawing
  const handleDrawing = useCallback(
    (event: React.MouseEvent | React.TouchEvent) => {
      event.preventDefault()
      if (!isDrawing) return

      const point = getCoordinates(event)
      if (!point) return

      setCurrentPoint(point)

      if (tool === 'pen') {
        setPenPoints((prev) => [...prev, point])
      }
    },
    [isDrawing, tool, getCoordinates]
  )

  // Handle end drawing
  const handleEndDrawing = useCallback(
    (event: React.MouseEvent | React.TouchEvent) => {
      event.preventDefault()
      if (!isDrawing || !startPoint || !currentPoint) return

      const ctx = getContext()
      if (!ctx) return

      saveToHistory()
      setupContext(ctx)

      switch (tool) {
        case 'arrow':
          drawArrow(ctx, startPoint, currentPoint)
          break
        case 'circle': {
          const radius = Math.sqrt(
            Math.pow(currentPoint.x - startPoint.x, 2) +
              Math.pow(currentPoint.y - startPoint.y, 2)
          )
          drawCircle(ctx, startPoint, radius)
          break
        }
        case 'rectangle':
          drawRectangle(ctx, startPoint, currentPoint)
          break
        case 'pen':
          drawPen(ctx, penPoints)
          break
      }

      setIsDrawing(false)
      setStartPoint(null)
      setCurrentPoint(null)
      setPenPoints([])

      // Clear temp canvas
      const tempCtx = tempCanvasRef.current?.getContext('2d')
      if (tempCtx && tempCanvasRef.current) {
        tempCtx.clearRect(
          0,
          0,
          tempCanvasRef.current.width,
          tempCanvasRef.current.height
        )
      }
    },
    [
      isDrawing,
      startPoint,
      currentPoint,
      penPoints,
      tool,
      getContext,
      saveToHistory,
      setupContext,
      drawArrow,
      drawCircle,
      drawRectangle,
      drawPen,
    ]
  )

  // Draw preview on temp canvas
  useEffect(() => {
    if (!isDrawing || !startPoint || !currentPoint) return

    const tempCtx = tempCanvasRef.current?.getContext('2d')
    if (!tempCtx || !tempCanvasRef.current) return

    // Clear temp canvas
    tempCtx.clearRect(
      0,
      0,
      tempCanvasRef.current.width,
      tempCanvasRef.current.height
    )

    setupContext(tempCtx)

    switch (tool) {
      case 'arrow':
        drawArrow(tempCtx, startPoint, currentPoint)
        break
      case 'circle': {
        const radius = Math.sqrt(
          Math.pow(currentPoint.x - startPoint.x, 2) +
            Math.pow(currentPoint.y - startPoint.y, 2)
        )
        drawCircle(tempCtx, startPoint, radius)
        break
      }
      case 'rectangle':
        drawRectangle(tempCtx, startPoint, currentPoint)
        break
      case 'pen':
        drawPen(tempCtx, penPoints)
        break
    }
  }, [
    isDrawing,
    startPoint,
    currentPoint,
    penPoints,
    tool,
    setupContext,
    drawArrow,
    drawCircle,
    drawRectangle,
    drawPen,
  ])

  // Handle text input submit
  const handleTextSubmit = useCallback(() => {
    if (!textPosition || !textValue.trim()) {
      setShowTextInput(false)
      setTextValue('')
      return
    }

    const ctx = getContext()
    if (!ctx) return

    saveToHistory()
    setupContext(ctx)
    drawText(ctx, textPosition, textValue.trim())

    setShowTextInput(false)
    setTextValue('')
    setTextPosition(null)
  }, [textPosition, textValue, getContext, saveToHistory, setupContext, drawText])

  // Handle save
  const handleSave = useCallback(() => {
    if (!imageRef.current || !canvasRef.current) return

    try {
      // Create temporary canvas for merging
      const mergeCanvas = document.createElement('canvas')
      mergeCanvas.width = imageDimensions.width
      mergeCanvas.height = imageDimensions.height

      const mergeCtx = mergeCanvas.getContext('2d')
      if (!mergeCtx) return

      // Draw image
      mergeCtx.drawImage(
        imageRef.current,
        0,
        0,
        imageDimensions.width,
        imageDimensions.height
      )

      // Draw annotations
      mergeCtx.drawImage(canvasRef.current, 0, 0)

      // Export as PNG
      const dataUrl = mergeCanvas.toDataURL('image/png', 0.9)
      onSave(dataUrl)
    } catch (err) {
      logger.error('Failed to export annotated image', err, {
        context: 'PhotoAnnotator',
        showToast: true,
      })
    }
  }, [imageDimensions, onSave])

  if (!imageLoaded) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600" />
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full bg-gray-100">
      {/* Header */}
      <div className="bg-white border-b px-4 py-3 flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-800">Annoter la photo</h3>
        <button
          onClick={onCancel}
          className="p-2 hover:bg-gray-100 rounded-full transition-colors"
          aria-label="Fermer"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Canvas container */}
      <div
        ref={containerRef}
        className="flex-1 overflow-auto flex items-center justify-center p-4"
      >
        <div className="relative" style={{ touchAction: 'none' }}>
          {/* Background image */}
          <img
            ref={imageRef}
            src={imageUrl}
            alt="Image to annotate"
            className="block"
            style={{
              width: imageDimensions.width,
              height: imageDimensions.height,
            }}
          />

          {/* Annotation canvas */}
          <canvas
            ref={canvasRef}
            className="absolute top-0 left-0 cursor-crosshair"
            style={{
              width: imageDimensions.width,
              height: imageDimensions.height,
            }}
            onMouseDown={handleStartDrawing}
            onMouseMove={handleDrawing}
            onMouseUp={handleEndDrawing}
            onMouseLeave={handleEndDrawing}
            onTouchStart={handleStartDrawing}
            onTouchMove={handleDrawing}
            onTouchEnd={handleEndDrawing}
          />

          {/* Temp preview canvas */}
          <canvas
            ref={tempCanvasRef}
            className="absolute top-0 left-0 pointer-events-none"
            style={{
              width: imageDimensions.width,
              height: imageDimensions.height,
            }}
          />
        </div>
      </div>

      {/* Toolbar */}
      <div className="bg-white border-t px-4 py-3">
        <div className="flex flex-col gap-3">
          {/* Tools */}
          <div className="flex items-center gap-2" role="toolbar" aria-label="Outils d'annotation">
            <button
              onClick={() => setTool('arrow')}
              className={`p-2 rounded-lg transition-colors ${
                tool === 'arrow'
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 hover:bg-gray-200'
              }`}
              aria-label="Flèche"
              aria-pressed={tool === 'arrow'}
            >
              <ArrowRight className="w-5 h-5" />
            </button>
            <button
              onClick={() => setTool('circle')}
              className={`p-2 rounded-lg transition-colors ${
                tool === 'circle'
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 hover:bg-gray-200'
              }`}
              aria-label="Cercle"
              aria-pressed={tool === 'circle'}
            >
              <Circle className="w-5 h-5" />
            </button>
            <button
              onClick={() => setTool('rectangle')}
              className={`p-2 rounded-lg transition-colors ${
                tool === 'rectangle'
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 hover:bg-gray-200'
              }`}
              aria-label="Rectangle"
              aria-pressed={tool === 'rectangle'}
            >
              <Square className="w-5 h-5" />
            </button>
            <button
              onClick={() => setTool('text')}
              className={`p-2 rounded-lg transition-colors ${
                tool === 'text'
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 hover:bg-gray-200'
              }`}
              aria-label="Texte"
              aria-pressed={tool === 'text'}
            >
              <Type className="w-5 h-5" />
            </button>
            <button
              onClick={() => setTool('pen')}
              className={`p-2 rounded-lg transition-colors ${
                tool === 'pen'
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 hover:bg-gray-200'
              }`}
              aria-label="Crayon"
              aria-pressed={tool === 'pen'}
            >
              <Pencil className="w-5 h-5" />
            </button>

            <div className="h-8 w-px bg-gray-300 mx-2" />

            {/* Colors */}
            {COLORS.map((c) => (
              <button
                key={c.value}
                onClick={() => setColor(c.value)}
                className={`w-8 h-8 rounded-full border-2 transition-all ${
                  color === c.value ? 'border-gray-800 scale-110' : 'border-gray-300'
                }`}
                style={{ backgroundColor: c.hex }}
                aria-label={c.label}
                aria-pressed={color === c.value}
              />
            ))}

            <div className="h-8 w-px bg-gray-300 mx-2" />

            {/* Thickness */}
            {THICKNESSES.map((t) => (
              <button
                key={t}
                onClick={() => setThickness(t)}
                className={`p-2 rounded-lg transition-colors ${
                  thickness === t
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 hover:bg-gray-200'
                }`}
                aria-label={`Épaisseur ${t}px`}
                aria-pressed={thickness === t}
              >
                <div
                  className="rounded-full bg-current"
                  style={{ width: `${t * 2}px`, height: `${t * 2}px` }}
                />
              </button>
            ))}

            <div className="h-8 w-px bg-gray-300 mx-2" />

            {/* Actions */}
            <button
              onClick={handleUndo}
              disabled={history.length === 0}
              className="p-2 rounded-lg bg-gray-100 hover:bg-gray-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              aria-label="Annuler"
            >
              <Undo className="w-5 h-5" />
            </button>
            <button
              onClick={handleClear}
              className="p-2 rounded-lg bg-gray-100 hover:bg-gray-200 transition-colors"
              aria-label="Tout effacer"
            >
              <Trash2 className="w-5 h-5" />
            </button>
          </div>

          {/* Save/Cancel buttons */}
          <div className="flex gap-2">
            <button
              onClick={onCancel}
              className="flex-1 py-2 px-4 border border-gray-300 rounded-lg font-medium hover:bg-gray-50 transition-colors"
            >
              Annuler
            </button>
            <button
              onClick={handleSave}
              className="flex-1 py-2 px-4 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition-colors flex items-center justify-center gap-2"
            >
              <Save className="w-5 h-5" />
              Enregistrer
            </button>
          </div>
        </div>
      </div>

      {/* Text input modal */}
      {showTextInput && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h4 className="text-lg font-semibold mb-4">Ajouter du texte</h4>
            <input
              type="text"
              value={textValue}
              onChange={(e) => setTextValue(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  handleTextSubmit()
                } else if (e.key === 'Escape') {
                  setShowTextInput(false)
                  setTextValue('')
                }
              }}
              placeholder="Saisissez votre texte..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 mb-4"
              autoFocus
            />
            <div className="flex gap-2">
              <button
                onClick={() => {
                  setShowTextInput(false)
                  setTextValue('')
                }}
                className="flex-1 py-2 px-4 border border-gray-300 rounded-lg font-medium hover:bg-gray-50 transition-colors"
              >
                Annuler
              </button>
              <button
                onClick={handleTextSubmit}
                disabled={!textValue.trim()}
                className="flex-1 py-2 px-4 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Ajouter
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
