/**
 * Tests unitaires pour FileUploadZone
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import FileUploadZone from './FileUploadZone'

vi.mock('../../types/documents', () => ({
  MAX_FILE_SIZE: 50 * 1024 * 1024,
  MAX_FILES_UPLOAD: 10,
  ACCEPTED_EXTENSIONS: ['.pdf', '.png', '.jpg'],
}))

vi.mock('../../services/documents', () => ({
  formatFileSize: vi.fn().mockReturnValue('50 Mo'),
}))

describe('FileUploadZone', () => {
  const defaultProps = {
    onFilesSelected: vi.fn(),
  }

  it('affiche la zone de drop par defaut', () => {
    // Arrange
    const { container } = render(<FileUploadZone {...defaultProps} />)

    // Act - rien

    // Assert
    const dropZone = container.querySelector('.border-dashed')
    expect(dropZone).toBeInTheDocument()
  })

  it('affiche le texte "Cliquez pour selectionner"', () => {
    // Arrange & Act
    render(<FileUploadZone {...defaultProps} />)

    // Assert
    expect(screen.getByText('Cliquez pour sélectionner')).toBeInTheDocument()
  })

  it('affiche les limites (max fichiers, taille)', () => {
    // Arrange & Act
    render(<FileUploadZone {...defaultProps} />)

    // Assert
    expect(screen.getByText(/Max 10 fichiers/)).toBeInTheDocument()
    expect(screen.getByText(/50 Mo/)).toBeInTheDocument()
  })

  it('affiche "Upload en cours..." quand uploading est true', () => {
    // Arrange & Act
    render(<FileUploadZone {...defaultProps} uploading={true} />)

    // Assert
    expect(screen.getByText('Upload en cours...')).toBeInTheDocument()
  })

  it('affiche la barre de progression avec le pourcentage', () => {
    // Arrange & Act
    render(<FileUploadZone {...defaultProps} uploading={true} uploadProgress={65} />)

    // Assert
    expect(screen.getByText('65%')).toBeInTheDocument()
  })

  it('la zone est desactivee quand disabled est true', () => {
    // Arrange & Act
    const { container } = render(<FileUploadZone {...defaultProps} disabled={true} />)

    // Assert
    const input = container.querySelector('input[type="file"]') as HTMLInputElement
    expect(input).toBeDisabled()
  })

  it('appelle onFilesSelected quand des fichiers sont choisis via input', () => {
    // Arrange
    const onFilesSelected = vi.fn()
    const { container } = render(<FileUploadZone onFilesSelected={onFilesSelected} />)
    const input = container.querySelector('input[type="file"]') as HTMLInputElement

    const file = new File(['contenu'], 'test.pdf', { type: 'application/pdf' })

    // Act
    fireEvent.change(input, { target: { files: [file] } })

    // Assert
    expect(onFilesSelected).toHaveBeenCalledWith([file])
  })
})
