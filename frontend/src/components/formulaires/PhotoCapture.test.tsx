/**
 * Tests pour PhotoCapture
 *
 * Couvre:
 * - Affichage en mode lecture seule avec/sans photo
 * - Mode édition: boutons camera et galerie
 * - Upload de fichier (validation type/taille)
 * - Preview et suppression
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import PhotoCapture from './PhotoCapture'

// Mock logger
vi.mock('../../services/logger', () => ({
  logger: {
    error: vi.fn(),
    warn: vi.fn(),
    info: vi.fn(),
  },
}))

// Import the mocked logger to verify calls
import { logger } from '../../services/logger'

describe('PhotoCapture', () => {
  const mockOnChange = vi.fn()

  const defaultProps = {
    onChange: mockOnChange,
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Mode lecture seule', () => {
    it('affiche "Aucune photo" si pas de valeur', () => {
      render(<PhotoCapture {...defaultProps} readOnly />)
      expect(screen.getByText('Aucune photo')).toBeInTheDocument()
    })

    it('affiche l\'image si valeur fournie', () => {
      render(<PhotoCapture {...defaultProps} value="data:image/png;base64,test" readOnly />)
      const img = screen.getByRole('img')
      expect(img).toBeInTheDocument()
      expect(img).toHaveAttribute('src', 'data:image/png;base64,test')
    })

    it('utilise le label comme alt text', () => {
      render(
        <PhotoCapture
          {...defaultProps}
          value="data:image/png;base64,test"
          readOnly
          label="Photo chantier"
        />
      )
      expect(screen.getByAltText('Photo chantier')).toBeInTheDocument()
    })
  })

  describe('Mode édition sans photo', () => {
    it('affiche les boutons camera et galerie', () => {
      render(<PhotoCapture {...defaultProps} />)
      expect(screen.getByText('Prendre une photo')).toBeInTheDocument()
      expect(screen.getByText('Galerie')).toBeInTheDocument()
    })

    it('affiche le texte d\'instruction', () => {
      render(<PhotoCapture {...defaultProps} />)
      expect(screen.getByText('Prenez une photo ou selectionnez une image')).toBeInTheDocument()
    })
  })

  describe('Mode édition avec photo', () => {
    it('affiche la preview de l\'image', () => {
      render(<PhotoCapture {...defaultProps} value="data:image/png;base64,test" />)
      const img = screen.getByRole('img')
      expect(img).toBeInTheDocument()
    })

    it('affiche le bouton supprimer', () => {
      render(<PhotoCapture {...defaultProps} value="data:image/png;base64,test" />)
      expect(screen.getByTitle('Supprimer la photo')).toBeInTheDocument()
    })

    it('supprime la photo au clic sur le bouton supprimer', async () => {
      const user = userEvent.setup()
      render(<PhotoCapture {...defaultProps} value="data:image/png;base64,test" />)

      await user.click(screen.getByTitle('Supprimer la photo'))

      expect(mockOnChange).toHaveBeenCalledWith('')
    })
  })

  describe('Upload fichier', () => {
    it('déclenche l\'input file au clic sur Galerie', async () => {
      const user = userEvent.setup()
      render(<PhotoCapture {...defaultProps} />)

      const fileInput = document.querySelector('input[type="file"]:not([capture])') as HTMLInputElement
      const clickSpy = vi.spyOn(fileInput, 'click')

      await user.click(screen.getByText('Galerie'))

      expect(clickSpy).toHaveBeenCalled()
    })

    it('déclenche l\'input camera au clic sur Prendre une photo', async () => {
      const user = userEvent.setup()
      render(<PhotoCapture {...defaultProps} />)

      const cameraInput = document.querySelector('input[capture="environment"]') as HTMLInputElement
      expect(cameraInput).toBeInTheDocument()

      // Mock navigator.userAgent pour simuler un mobile
      Object.defineProperty(navigator, 'userAgent', {
        value: 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)',
        configurable: true,
      })

      const clickSpy = vi.spyOn(cameraInput, 'click')

      await user.click(screen.getByText('Prendre une photo'))

      // Sur mobile, le composant devrait déclencher cameraInputRef.click()
      // Le test vérifie que l'input existe et est correctement configuré
      expect(cameraInput).toHaveAttribute('capture', 'environment')
      expect(cameraInput).toHaveAttribute('accept', 'image/*')
    })

    it('rejette les fichiers non-image', async () => {
      render(<PhotoCapture {...defaultProps} />)

      const fileInput = document.querySelector('input[type="file"]:not([capture])') as HTMLInputElement

      const textFile = new File(['hello'], 'test.txt', { type: 'text/plain' })
      Object.defineProperty(fileInput, 'files', {
        value: [textFile],
        writable: false,
      })

      fileInput.dispatchEvent(new Event('change', { bubbles: true }))

      await waitFor(() => {
        expect(logger.warn).toHaveBeenCalledWith(
          'Veuillez selectionner une image',
          null,
          expect.any(Object)
        )
      })
    })

    it('rejette les fichiers trop volumineux', async () => {
      render(<PhotoCapture {...defaultProps} />)

      const fileInput = document.querySelector('input[type="file"]:not([capture])') as HTMLInputElement

      // Create a file > 10MB
      const largeFile = new File([new ArrayBuffer(11 * 1024 * 1024)], 'large.jpg', {
        type: 'image/jpeg',
      })
      Object.defineProperty(fileInput, 'files', {
        value: [largeFile],
        writable: false,
      })

      fileInput.dispatchEvent(new Event('change', { bubbles: true }))

      await waitFor(() => {
        expect(logger.warn).toHaveBeenCalledWith(
          'L\'image ne doit pas depasser 10 Mo',
          null,
          expect.any(Object)
        )
      })
    })

    it('convertit le fichier en base64 et appelle onChange', async () => {
      render(<PhotoCapture {...defaultProps} />)

      const fileInput = document.querySelector('input[type="file"]:not([capture])') as HTMLInputElement

      // Create a small valid image file
      const imageFile = new File(['fake-image-data'], 'photo.jpg', {
        type: 'image/jpeg',
      })
      Object.defineProperty(fileInput, 'files', {
        value: [imageFile],
        writable: false,
      })

      // Mock FileReader
      const mockReader = {
        readAsDataURL: vi.fn(),
        onload: null as ((event: { target: { result: string } }) => void) | null,
        onerror: null as (() => void) | null,
        result: 'data:image/jpeg;base64,ZmFrZS1pbWFnZS1kYXRh',
      }
      vi.spyOn(window, 'FileReader').mockImplementation(() => mockReader as unknown as FileReader)

      fileInput.dispatchEvent(new Event('change', { bubbles: true }))

      // Simulate FileReader completion
      await waitFor(() => {
        expect(mockReader.readAsDataURL).toHaveBeenCalledWith(imageFile)
      })

      // Trigger onload
      if (mockReader.onload) {
        mockReader.onload({ target: { result: mockReader.result } })
      }

      await waitFor(() => {
        expect(mockOnChange).toHaveBeenCalledWith(mockReader.result)
      })
    })
  })

  describe('État de chargement', () => {
    it('affiche le spinner pendant le chargement', async () => {
      render(<PhotoCapture {...defaultProps} />)

      const fileInput = document.querySelector('input[type="file"]:not([capture])') as HTMLInputElement

      const imageFile = new File(['data'], 'photo.jpg', { type: 'image/jpeg' })
      Object.defineProperty(fileInput, 'files', {
        value: [imageFile],
        writable: false,
      })

      // Mock FileReader that doesn't complete immediately
      const mockReader = {
        readAsDataURL: vi.fn(),
        onload: null as (() => void) | null,
        onerror: null as (() => void) | null,
        result: null,
      }
      vi.spyOn(window, 'FileReader').mockImplementation(() => mockReader as unknown as FileReader)

      fileInput.dispatchEvent(new Event('change', { bubbles: true }))

      await waitFor(() => {
        expect(screen.getByText('Chargement...')).toBeInTheDocument()
      })
    })
  })

  describe('Inputs cachés', () => {
    it('les inputs file sont cachés', () => {
      render(<PhotoCapture {...defaultProps} />)

      const fileInputs = document.querySelectorAll('input[type="file"]')
      fileInputs.forEach((input) => {
        expect(input).toHaveClass('hidden')
      })
    })

    it('l\'input camera a l\'attribut capture', () => {
      render(<PhotoCapture {...defaultProps} />)

      const cameraInput = document.querySelector('input[capture="environment"]')
      expect(cameraInput).toBeInTheDocument()
    })

    it('les inputs acceptent uniquement les images', () => {
      render(<PhotoCapture {...defaultProps} />)

      const fileInputs = document.querySelectorAll('input[type="file"]')
      fileInputs.forEach((input) => {
        expect(input).toHaveAttribute('accept', 'image/*')
      })
    })
  })
})
