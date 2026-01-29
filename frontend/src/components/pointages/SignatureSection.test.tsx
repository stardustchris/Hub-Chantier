/**
 * Tests unitaires pour SignatureSection
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { SignatureSection } from './SignatureSection'

vi.mock('date-fns', () => ({
  format: vi.fn().mockReturnValue('15/01/2024 10:00'),
}))

const mockPointage: any = {
  id: 1,
  utilisateur_id: 1,
  date: '2024-01-15',
  signature_utilisateur: null,
  signature_date: null,
}

describe('SignatureSection', () => {
  const defaultProps = {
    pointage: mockPointage,
    signature: '',
    setSignature: vi.fn(),
    onSign: vi.fn().mockResolvedValue(undefined),
    saving: false,
  }

  it('affiche le label "Signature electronique"', () => {
    // Arrange & Act
    render(<SignatureSection {...defaultProps} />)

    // Assert
    expect(screen.getByText('Signature electronique')).toBeInTheDocument()
  })

  it('affiche l\'input de signature', () => {
    // Arrange & Act
    render(<SignatureSection {...defaultProps} />)

    // Assert
    expect(screen.getByPlaceholderText('Saisir votre nom pour signer')).toBeInTheDocument()
  })

  it('affiche le bouton Signer', () => {
    // Arrange & Act
    render(<SignatureSection {...defaultProps} />)

    // Assert
    expect(screen.getByText('Signer')).toBeInTheDocument()
  })

  it('le bouton Signer est desactive quand signature est vide', () => {
    // Arrange & Act
    render(<SignatureSection {...defaultProps} signature="" />)

    // Assert
    expect(screen.getByText('Signer')).toBeDisabled()
  })

  it('le bouton Signer est desactive quand saving est true', () => {
    // Arrange & Act
    render(<SignatureSection {...defaultProps} signature="Jean Dupont" saving={true} />)

    // Assert
    expect(screen.getByText('Signer')).toBeDisabled()
  })

  it('appelle onSign au clic sur Signer', () => {
    // Arrange
    const onSign = vi.fn().mockResolvedValue(undefined)
    render(<SignatureSection {...defaultProps} signature="Jean Dupont" onSign={onSign} />)

    // Act
    fireEvent.click(screen.getByText('Signer'))

    // Assert
    expect(onSign).toHaveBeenCalled()
  })

  it('appelle setSignature quand on tape dans l\'input', () => {
    // Arrange
    const setSignature = vi.fn()
    render(<SignatureSection {...defaultProps} setSignature={setSignature} />)

    // Act
    const input = screen.getByPlaceholderText('Saisir votre nom pour signer')
    fireEvent.change(input, { target: { value: 'Jean' } })

    // Assert
    expect(setSignature).toHaveBeenCalled()
  })

  it('affiche le message de signature existante quand pointage.signature_utilisateur est present', () => {
    // Arrange
    const pointageSigne: any = {
      ...mockPointage,
      signature_utilisateur: 'Jean Dupont',
      signature_date: '2024-01-15T10:00:00Z',
    }

    // Act
    render(<SignatureSection {...defaultProps} pointage={pointageSigne} />)

    // Assert
    expect(screen.getByText(/Signe par Jean Dupont/)).toBeInTheDocument()
  })
})
