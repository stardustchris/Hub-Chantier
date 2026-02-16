/**
 * Tests for PhotoAnnotator component
 */

import { describe, it, expect, vi, beforeAll, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import PhotoAnnotator from './PhotoAnnotator'

// Mock logger
vi.mock('../../services/logger', () => ({
  logger: {
    error: vi.fn(),
    warn: vi.fn(),
    info: vi.fn(),
  },
}))

// Mock canvas methods
const mockGetContext = vi.fn()
const mockToDataURL = vi.fn()
const mockDrawImage = vi.fn()
const mockBeginPath = vi.fn()
const mockMoveTo = vi.fn()
const mockLineTo = vi.fn()
const mockStroke = vi.fn()
const mockArc = vi.fn()
const mockStrokeRect = vi.fn()
const mockFillRect = vi.fn()
const mockFillText = vi.fn()
const mockMeasureText = vi.fn()
const mockGetImageData = vi.fn()
const mockPutImageData = vi.fn()
const mockClearRect = vi.fn()

beforeAll(() => {
  // Mock HTMLCanvasElement methods
  HTMLCanvasElement.prototype.getContext = mockGetContext.mockReturnValue({
    drawImage: mockDrawImage,
    beginPath: mockBeginPath,
    moveTo: mockMoveTo,
    lineTo: mockLineTo,
    stroke: mockStroke,
    arc: mockArc,
    strokeRect: mockStrokeRect,
    fillRect: mockFillRect,
    fillText: mockFillText,
    measureText: mockMeasureText.mockReturnValue({ width: 100 }),
    getImageData: mockGetImageData.mockReturnValue({
      data: new Uint8ClampedArray(100),
      width: 100,
      height: 100,
    }),
    putImageData: mockPutImageData,
    clearRect: mockClearRect,
    strokeStyle: '',
    lineWidth: 0,
    lineCap: '',
    lineJoin: '',
    fillStyle: '',
    font: '',
  })

  HTMLCanvasElement.prototype.toDataURL = mockToDataURL.mockReturnValue(
    'data:image/png;base64,mock'
  )

  // Mock Image
  global.Image = class {
    onload: (() => void) | null = null
    onerror: (() => void) | null = null
    src = ''
    width = 800
    height = 600
    crossOrigin = ''

    constructor() {
      setTimeout(() => {
        if (this.onload) {
          this.onload()
        }
      }, 0)
    }
  } as any
})

beforeEach(() => {
  vi.clearAllMocks()
})

describe('PhotoAnnotator', () => {
  const mockImageUrl = 'data:image/png;base64,test'
  const mockOnSave = vi.fn()
  const mockOnCancel = vi.fn()

  const defaultProps = {
    imageUrl: mockImageUrl,
    onSave: mockOnSave,
    onCancel: mockOnCancel,
  }

  it('should render loading state initially', () => {
    render(<PhotoAnnotator {...defaultProps} />)
    const spinner = document.querySelector('.animate-spin')
    expect(spinner).toBeInTheDocument()
  })

  it('should render annotation tools after image loads', async () => {
    render(<PhotoAnnotator {...defaultProps} />)

    await waitFor(() => {
      expect(screen.getByText('Annoter la photo')).toBeInTheDocument()
    })

    expect(screen.getByLabelText('Flèche')).toBeInTheDocument()
    expect(screen.getByLabelText('Cercle')).toBeInTheDocument()
    expect(screen.getByLabelText('Rectangle')).toBeInTheDocument()
    expect(screen.getByLabelText('Texte')).toBeInTheDocument()
    expect(screen.getByLabelText('Crayon')).toBeInTheDocument()
  })

  it('should select tool when clicked', async () => {
    render(<PhotoAnnotator {...defaultProps} />)

    await waitFor(() => {
      expect(screen.getByLabelText('Flèche')).toBeInTheDocument()
    })

    const arrowButton = screen.getByLabelText('Flèche')
    fireEvent.click(arrowButton)

    expect(arrowButton).toHaveAttribute('aria-pressed', 'true')
  })

  it('should render color options', async () => {
    render(<PhotoAnnotator {...defaultProps} />)

    await waitFor(() => {
      expect(screen.getByLabelText('Rouge')).toBeInTheDocument()
    })

    expect(screen.getByLabelText('Jaune')).toBeInTheDocument()
    expect(screen.getByLabelText('Bleu')).toBeInTheDocument()
    expect(screen.getByLabelText('Blanc')).toBeInTheDocument()
  })

  it('should select color when clicked', async () => {
    render(<PhotoAnnotator {...defaultProps} />)

    await waitFor(() => {
      expect(screen.getByLabelText('Bleu')).toBeInTheDocument()
    })

    const blueButton = screen.getByLabelText('Bleu')
    fireEvent.click(blueButton)

    expect(blueButton).toHaveAttribute('aria-pressed', 'true')
  })

  it('should render thickness options', async () => {
    render(<PhotoAnnotator {...defaultProps} />)

    await waitFor(() => {
      expect(screen.getByLabelText('Épaisseur 2px')).toBeInTheDocument()
    })

    expect(screen.getByLabelText('Épaisseur 4px')).toBeInTheDocument()
    expect(screen.getByLabelText('Épaisseur 6px')).toBeInTheDocument()
  })

  it('should handle undo button - disabled when no history', async () => {
    render(<PhotoAnnotator {...defaultProps} />)

    await waitFor(() => {
      expect(screen.getByLabelText('Annuler')).toBeInTheDocument()
    })

    const undoButton = screen.getByLabelText('Annuler')
    expect(undoButton).toBeDisabled()
  })

  it('should handle clear button', async () => {
    render(<PhotoAnnotator {...defaultProps} />)

    await waitFor(() => {
      expect(screen.getByLabelText('Tout effacer')).toBeInTheDocument()
    })

    const clearButton = screen.getByLabelText('Tout effacer')
    fireEvent.click(clearButton)

    await waitFor(() => {
      expect(mockClearRect).toHaveBeenCalled()
    })
  })

  it('should show text input modal when text tool is used', async () => {
    render(<PhotoAnnotator {...defaultProps} />)

    await waitFor(() => {
      expect(screen.getByLabelText('Texte')).toBeInTheDocument()
    })

    // Select text tool
    const textButton = screen.getByLabelText('Texte')
    fireEvent.click(textButton)

    // Get canvas and simulate click
    const canvases = document.querySelectorAll('canvas')
    const canvas = canvases[0]
    expect(canvas).toBeInTheDocument()

    if (canvas) {
      fireEvent.mouseDown(canvas, { clientX: 100, clientY: 100 })
    }

    await waitFor(() => {
      expect(screen.getByPlaceholderText('Saisissez votre texte...')).toBeInTheDocument()
    })
  })

  it('should handle text input submission', async () => {
    render(<PhotoAnnotator {...defaultProps} />)

    await waitFor(() => {
      expect(screen.getByLabelText('Texte')).toBeInTheDocument()
    })

    // Select text tool and click canvas
    fireEvent.click(screen.getByLabelText('Texte'))
    const canvases = document.querySelectorAll('canvas')
    const canvas = canvases[0]
    if (canvas) {
      fireEvent.mouseDown(canvas, { clientX: 100, clientY: 100 })
    }

    await waitFor(() => {
      expect(screen.getByPlaceholderText('Saisissez votre texte...')).toBeInTheDocument()
    })

    const input = screen.getByPlaceholderText('Saisissez votre texte...')
    fireEvent.change(input, { target: { value: 'Test annotation' } })

    const addButtons = screen.getAllByRole('button')
    const addButton = addButtons.find((btn) => btn.textContent === 'Ajouter')
    if (addButton) {
      fireEvent.click(addButton)
    }

    await waitFor(() => {
      expect(mockFillText).toHaveBeenCalled()
    })
  })

  it('should handle save button', async () => {
    render(<PhotoAnnotator {...defaultProps} />)

    await waitFor(() => {
      expect(screen.getByText('Enregistrer')).toBeInTheDocument()
    })

    const saveButton = screen.getByText('Enregistrer')
    fireEvent.click(saveButton)

    await waitFor(() => {
      expect(mockOnSave).toHaveBeenCalledWith('data:image/png;base64,mock')
    })
  })

  it('should handle cancel button', async () => {
    render(<PhotoAnnotator {...defaultProps} />)

    await waitFor(() => {
      expect(screen.getByText('Annoter la photo')).toBeInTheDocument()
    })

    const closeButton = screen.getByLabelText('Fermer')
    fireEvent.click(closeButton)

    expect(mockOnCancel).toHaveBeenCalled()
  })

  it('should handle mouse drawing events', async () => {
    render(<PhotoAnnotator {...defaultProps} />)

    await waitFor(() => {
      expect(screen.getByLabelText('Crayon')).toBeInTheDocument()
    })

    // Pen tool is default
    const canvases = document.querySelectorAll('canvas')
    const canvas = canvases[0]
    expect(canvas).toBeInTheDocument()

    if (canvas) {
      // Simulate drawing
      fireEvent.mouseDown(canvas, { clientX: 10, clientY: 10 })
      fireEvent.mouseMove(canvas, { clientX: 20, clientY: 20 })
      fireEvent.mouseMove(canvas, { clientX: 30, clientY: 30 })
      fireEvent.mouseUp(canvas, { clientX: 30, clientY: 30 })

      await waitFor(() => {
        expect(mockBeginPath).toHaveBeenCalled()
      })
    }
  })

  it('should handle touch drawing events', async () => {
    render(<PhotoAnnotator {...defaultProps} />)

    await waitFor(() => {
      expect(screen.getByLabelText('Crayon')).toBeInTheDocument()
    })

    const canvases = document.querySelectorAll('canvas')
    const canvas = canvases[0]
    expect(canvas).toBeInTheDocument()

    if (canvas) {
      // Simulate touch drawing
      const touch = { clientX: 10, clientY: 10 }
      fireEvent.touchStart(canvas, { touches: [touch] })

      const touch2 = { clientX: 20, clientY: 20 }
      fireEvent.touchMove(canvas, { touches: [touch2] })

      fireEvent.touchEnd(canvas, { changedTouches: [touch2] })

      await waitFor(() => {
        expect(mockBeginPath).toHaveBeenCalled()
      })
    }
  })

  it('should respect custom width prop', async () => {
    render(<PhotoAnnotator {...defaultProps} width={600} />)

    await waitFor(() => {
      expect(screen.getByText('Annoter la photo')).toBeInTheDocument()
    })

    // Image should be loaded with scaled dimensions
    const img = screen.getByAltText('Image to annotate') as HTMLImageElement
    expect(img).toBeInTheDocument()
  })

  it('should have proper ARIA labels for accessibility', async () => {
    render(<PhotoAnnotator {...defaultProps} />)

    await waitFor(() => {
      expect(screen.getByRole('toolbar', { name: /outils d'annotation/i })).toBeInTheDocument()
    })

    expect(screen.getByLabelText('Flèche')).toHaveAttribute('aria-pressed')
    expect(screen.getByLabelText('Cercle')).toHaveAttribute('aria-pressed')
    expect(screen.getByLabelText('Rectangle')).toHaveAttribute('aria-pressed')
    expect(screen.getByLabelText('Texte')).toHaveAttribute('aria-pressed')
    expect(screen.getByLabelText('Crayon')).toHaveAttribute('aria-pressed')
  })
})
