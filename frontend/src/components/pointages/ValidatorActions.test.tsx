/**
 * Tests unitaires pour ValidatorActions
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { ValidatorActions } from './ValidatorActions'

describe('ValidatorActions', () => {
  const defaultProps = {
    showRejectForm: false,
    setShowRejectForm: vi.fn(),
    motifRejet: '',
    setMotifRejet: vi.fn(),
    onValidate: vi.fn().mockResolvedValue(undefined),
    onReject: vi.fn().mockResolvedValue(undefined),
    saving: false,
  }

  it('affiche les boutons Valider et Rejeter par defaut', () => {
    // Arrange & Act
    render(<ValidatorActions {...defaultProps} />)

    // Assert
    expect(screen.getByText('Valider')).toBeInTheDocument()
    expect(screen.getByText('Rejeter')).toBeInTheDocument()
  })

  it('affiche le formulaire de rejet quand showRejectForm est true', () => {
    // Arrange & Act
    render(<ValidatorActions {...defaultProps} showRejectForm={true} />)

    // Assert
    expect(screen.getByPlaceholderText('Motif du rejet...')).toBeInTheDocument()
    expect(screen.getByText('Confirmer le rejet')).toBeInTheDocument()
  })

  it('le bouton Confirmer le rejet est desactive sans motif', () => {
    // Arrange & Act
    render(<ValidatorActions {...defaultProps} showRejectForm={true} motifRejet="" />)

    // Assert
    expect(screen.getByText('Confirmer le rejet')).toBeDisabled()
  })

  it('le bouton Confirmer le rejet est desactive quand saving est true', () => {
    // Arrange & Act
    render(
      <ValidatorActions {...defaultProps} showRejectForm={true} motifRejet="Motif" saving={true} />
    )

    // Assert
    expect(screen.getByText('Confirmer le rejet')).toBeDisabled()
  })

  it('appelle onValidate au clic sur Valider', () => {
    // Arrange
    const onValidate = vi.fn().mockResolvedValue(undefined)
    render(<ValidatorActions {...defaultProps} onValidate={onValidate} />)

    // Act
    fireEvent.click(screen.getByText('Valider'))

    // Assert
    expect(onValidate).toHaveBeenCalled()
  })

  it('appelle setShowRejectForm(true) au clic sur Rejeter', () => {
    // Arrange
    const setShowRejectForm = vi.fn()
    render(<ValidatorActions {...defaultProps} setShowRejectForm={setShowRejectForm} />)

    // Act
    fireEvent.click(screen.getByText('Rejeter'))

    // Assert
    expect(setShowRejectForm).toHaveBeenCalledWith(true)
  })

  it('appelle onReject au clic sur Confirmer le rejet', () => {
    // Arrange
    const onReject = vi.fn().mockResolvedValue(undefined)
    render(
      <ValidatorActions
        {...defaultProps}
        showRejectForm={true}
        motifRejet="Heures incorrectes"
        onReject={onReject}
      />
    )

    // Act
    fireEvent.click(screen.getByText('Confirmer le rejet'))

    // Assert
    expect(onReject).toHaveBeenCalled()
  })

  it('appelle setShowRejectForm(false) au clic sur Annuler dans le formulaire de rejet', () => {
    // Arrange
    const setShowRejectForm = vi.fn()
    render(
      <ValidatorActions
        {...defaultProps}
        showRejectForm={true}
        setShowRejectForm={setShowRejectForm}
      />
    )

    // Act
    fireEvent.click(screen.getByText('Annuler'))

    // Assert
    expect(setShowRejectForm).toHaveBeenCalledWith(false)
  })
})
