/**
 * Tests pour ImageUpload et MultiImageUpload
 * Composants d'upload d'images
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import ImageUpload, { MultiImageUpload } from './ImageUpload'

// Mock upload service
vi.mock('../services/upload', () => ({
  uploadService: {
    compressImage: vi.fn((file) => Promise.resolve(file)),
    uploadProfilePhoto: vi.fn(() => Promise.resolve({ url: 'https://example.com/profile.jpg' })),
    uploadChantierPhoto: vi.fn(() => Promise.resolve({ url: 'https://example.com/chantier.jpg' })),
  },
}))

vi.mock('../services/logger', () => ({
  logger: {
    error: vi.fn(),
    warn: vi.fn(),
    info: vi.fn(),
  },
}))

import { uploadService } from '../services/upload'

describe('ImageUpload', () => {
  const defaultProps = {
    onUpload: vi.fn(),
    type: 'profile' as const,
    entityId: '123',
  }

  beforeEach(() => {
    vi.clearAllMocks()
    // Mock URL.createObjectURL
    ;(globalThis as any).URL.createObjectURL = vi.fn(() => 'blob:http://localhost/test')
    ;(globalThis as any).URL.revokeObjectURL = vi.fn()
  })

  describe('Rendu', () => {
    it('affiche le bouton d\'upload sans image', () => {
      render(<ImageUpload {...defaultProps} />)
      expect(screen.getByLabelText('Ajouter une photo')).toBeInTheDocument()
    })

    it('affiche l\'image actuelle si fournie', () => {
      render(<ImageUpload {...defaultProps} currentImage="https://example.com/photo.jpg" />)
      expect(screen.getByAltText('Photo')).toHaveAttribute('src', 'https://example.com/photo.jpg')
      expect(screen.getByLabelText('Modifier la photo')).toBeInTheDocument()
    })

    it('affiche le placeholder si fourni et pas d\'image', () => {
      render(
        <ImageUpload
          {...defaultProps}
          placeholder={<span data-testid="placeholder">Placeholder</span>}
        />
      )
      expect(screen.getByTestId('placeholder')).toBeInTheDocument()
    })

    it('applique les classes de taille correctes', () => {
      const { rerender } = render(<ImageUpload {...defaultProps} size="small" />)
      let button = screen.getByLabelText('Ajouter une photo')
      expect(button).toHaveClass('w-16', 'h-16')

      rerender(<ImageUpload {...defaultProps} size="default" />)
      button = screen.getByLabelText('Ajouter une photo')
      expect(button).toHaveClass('w-24', 'h-24')

      rerender(<ImageUpload {...defaultProps} size="large" />)
      button = screen.getByLabelText('Ajouter une photo')
      expect(button).toHaveClass('w-32', 'h-32')
    })

    it('applique la classe CSS personnalisee', () => {
      const { container } = render(<ImageUpload {...defaultProps} className="custom-class" />)
      expect(container.firstChild).toHaveClass('custom-class')
    })
  })

  describe('Upload de fichier', () => {
    it('ouvre le selecteur de fichier au clic', () => {
      render(<ImageUpload {...defaultProps} />)
      const input = document.querySelector('input[type="file"]') as HTMLInputElement
      const clickSpy = vi.spyOn(input, 'click')

      fireEvent.click(screen.getByLabelText('Ajouter une photo'))
      expect(clickSpy).toHaveBeenCalled()
    })

    it('accepte uniquement les images', () => {
      render(<ImageUpload {...defaultProps} />)
      const input = document.querySelector('input[type="file"]') as HTMLInputElement
      expect(input).toHaveAttribute('accept', 'image/*')
    })

    it('upload une photo de profil correctement', async () => {
      const onUpload = vi.fn()
      render(<ImageUpload {...defaultProps} onUpload={onUpload} type="profile" />)

      const input = document.querySelector('input[type="file"]') as HTMLInputElement
      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })

      fireEvent.change(input, { target: { files: [file] } })

      await waitFor(() => {
        expect(uploadService.compressImage).toHaveBeenCalledWith(file)
        expect(uploadService.uploadProfilePhoto).toHaveBeenCalled()
        expect(onUpload).toHaveBeenCalledWith('https://example.com/profile.jpg')
      })
    })

    it('upload une photo de chantier correctement', async () => {
      const onUpload = vi.fn()
      render(<ImageUpload {...defaultProps} onUpload={onUpload} type="chantier" entityId="456" />)

      const input = document.querySelector('input[type="file"]') as HTMLInputElement
      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })

      fireEvent.change(input, { target: { files: [file] } })

      await waitFor(() => {
        expect(uploadService.uploadChantierPhoto).toHaveBeenCalledWith('456', file)
        expect(onUpload).toHaveBeenCalledWith('https://example.com/chantier.jpg')
      })
    })

    it('affiche une erreur si le fichier n\'est pas une image', async () => {
      render(<ImageUpload {...defaultProps} />)

      const input = document.querySelector('input[type="file"]') as HTMLInputElement
      const file = new File(['test'], 'test.pdf', { type: 'application/pdf' })

      fireEvent.change(input, { target: { files: [file] } })

      await waitFor(() => {
        expect(screen.getByText('Veuillez sélectionner une image')).toBeInTheDocument()
      })
    })

    it('affiche le loader pendant l\'upload', async () => {
      // Delayer la resolution du mock
      vi.mocked(uploadService.uploadProfilePhoto).mockImplementation(
        () => new Promise((resolve) => setTimeout(() => resolve({ url: 'test.jpg' }), 100))
      )

      render(<ImageUpload {...defaultProps} />)

      const input = document.querySelector('input[type="file"]') as HTMLInputElement
      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })

      fireEvent.change(input, { target: { files: [file] } })

      // Le bouton devrait etre desactive pendant l'upload
      await waitFor(() => {
        const button = screen.getByRole('button')
        expect(button).toBeDisabled()
      })
    })

    it('gere les erreurs d\'upload', async () => {
      vi.mocked(uploadService.uploadProfilePhoto).mockRejectedValue(new Error('Upload failed'))

      render(<ImageUpload {...defaultProps} />)

      const input = document.querySelector('input[type="file"]') as HTMLInputElement
      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })

      fireEvent.change(input, { target: { files: [file] } })

      await waitFor(() => {
        expect(screen.getByText("Erreur lors de l'upload")).toBeInTheDocument()
      })
    })
  })
})

describe('MultiImageUpload', () => {
  const defaultProps = {
    onFilesSelected: vi.fn(),
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Rendu', () => {
    it('affiche le bouton d\'upload', () => {
      render(<MultiImageUpload {...defaultProps} />)
      expect(screen.getByLabelText(/Ajouter des photos/)).toBeInTheDocument()
    })

    it('affiche le nombre max de fichiers dans l\'aria-label', () => {
      render(<MultiImageUpload {...defaultProps} maxFiles={3} />)
      expect(screen.getByLabelText('Ajouter des photos (max 3)')).toBeInTheDocument()
    })

    it('desactive le bouton si disabled', () => {
      render(<MultiImageUpload {...defaultProps} disabled />)
      expect(screen.getByRole('button')).toBeDisabled()
    })
  })

  describe('Selection de fichiers', () => {
    it('accepte plusieurs images', () => {
      render(<MultiImageUpload {...defaultProps} />)
      const input = document.querySelector('input[type="file"]') as HTMLInputElement
      expect(input).toHaveAttribute('multiple')
      expect(input).toHaveAttribute('accept', 'image/*')
    })

    it('compresse et retourne les fichiers', async () => {
      const onFilesSelected = vi.fn()
      render(<MultiImageUpload {...defaultProps} onFilesSelected={onFilesSelected} />)

      const input = document.querySelector('input[type="file"]') as HTMLInputElement
      const files = [
        new File(['test1'], 'test1.jpg', { type: 'image/jpeg' }),
        new File(['test2'], 'test2.jpg', { type: 'image/jpeg' }),
      ]

      fireEvent.change(input, { target: { files } })

      await waitFor(() => {
        expect(uploadService.compressImage).toHaveBeenCalledTimes(2)
        expect(onFilesSelected).toHaveBeenCalledWith(files)
      })
    })

    it('limite le nombre de fichiers', async () => {
      const onFilesSelected = vi.fn()
      render(<MultiImageUpload {...defaultProps} onFilesSelected={onFilesSelected} maxFiles={2} />)

      const input = document.querySelector('input[type="file"]') as HTMLInputElement
      const files = [
        new File(['test1'], 'test1.jpg', { type: 'image/jpeg' }),
        new File(['test2'], 'test2.jpg', { type: 'image/jpeg' }),
        new File(['test3'], 'test3.jpg', { type: 'image/jpeg' }),
      ]

      fireEvent.change(input, { target: { files } })

      await waitFor(() => {
        // Seulement 2 fichiers doivent etre compresses
        expect(uploadService.compressImage).toHaveBeenCalledTimes(2)
      })
    })

    it('filtre les fichiers non-images', async () => {
      const onFilesSelected = vi.fn()
      render(<MultiImageUpload {...defaultProps} onFilesSelected={onFilesSelected} />)

      const input = document.querySelector('input[type="file"]') as HTMLInputElement
      const files = [
        new File(['test1'], 'test1.jpg', { type: 'image/jpeg' }),
        new File(['test2'], 'test2.pdf', { type: 'application/pdf' }),
      ]

      fireEvent.change(input, { target: { files } })

      await waitFor(() => {
        // Seulement 1 fichier image doit etre compresse
        expect(uploadService.compressImage).toHaveBeenCalledTimes(1)
      })
    })
  })
})
