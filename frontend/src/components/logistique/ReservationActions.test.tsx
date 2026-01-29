/**
 * Tests unitaires pour ReservationActions
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import ReservationActions from './ReservationActions'

describe('ReservationActions', () => {
  const defaultProps = {
    isViewMode: false,
    reservation: null,
    canValidate: false,
    loading: false,
    motifRefus: '',
    showMotifRefus: false,
    onValider: vi.fn(),
    onRefuser: vi.fn(),
    onAnnuler: vi.fn(),
    onClose: vi.fn(),
    onShowMotifRefus: vi.fn(),
    onMotifRefusChange: vi.fn(),
  }

  it('affiche Annuler et Reserver en mode creation', () => {
    // Arrange & Act
    render(<ReservationActions {...defaultProps} isViewMode={false} />)

    // Assert
    expect(screen.getByText('Annuler')).toBeInTheDocument()
    expect(screen.getByText('Réserver')).toBeInTheDocument()
  })

  it('affiche Valider et Refuser pour reservation en_attente avec canValidate', () => {
    // Arrange
    const reservation: any = {
      id: 1,
      statut: 'en_attente',
    }

    // Act
    render(
      <ReservationActions
        {...defaultProps}
        isViewMode={true}
        reservation={reservation}
        canValidate={true}
      />
    )

    // Assert
    expect(screen.getByText('Valider')).toBeInTheDocument()
    expect(screen.getByText('Refuser')).toBeInTheDocument()
  })

  it('affiche le champ motif de refus quand showMotifRefus est true', () => {
    // Arrange
    const reservation: any = {
      id: 1,
      statut: 'en_attente',
    }

    // Act
    render(
      <ReservationActions
        {...defaultProps}
        isViewMode={true}
        reservation={reservation}
        canValidate={true}
        showMotifRefus={true}
      />
    )

    // Assert
    expect(screen.getByText('Motif du refus')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Motif optionnel...')).toBeInTheDocument()
  })

  it('affiche "Annuler la reservation" pour reservation validee', () => {
    // Arrange
    const reservation: any = {
      id: 1,
      statut: 'validee',
    }

    // Act
    render(
      <ReservationActions
        {...defaultProps}
        isViewMode={true}
        reservation={reservation}
      />
    )

    // Assert
    expect(screen.getByText('Annuler la réservation')).toBeInTheDocument()
  })

  it('affiche le bouton Fermer en mode vue', () => {
    // Arrange
    const reservation: any = {
      id: 1,
      statut: 'en_attente',
    }

    // Act
    render(
      <ReservationActions
        {...defaultProps}
        isViewMode={true}
        reservation={reservation}
      />
    )

    // Assert
    expect(screen.getByText('Fermer')).toBeInTheDocument()
  })

  it('appelle onValider au clic sur Valider', () => {
    // Arrange
    const onValider = vi.fn()
    const reservation: any = { id: 1, statut: 'en_attente' }
    render(
      <ReservationActions
        {...defaultProps}
        isViewMode={true}
        reservation={reservation}
        canValidate={true}
        onValider={onValider}
      />
    )

    // Act
    fireEvent.click(screen.getByText('Valider'))

    // Assert
    expect(onValider).toHaveBeenCalled()
  })

  it('appelle onShowMotifRefus au clic sur Refuser', () => {
    // Arrange
    const onShowMotifRefus = vi.fn()
    const reservation: any = { id: 1, statut: 'en_attente' }
    render(
      <ReservationActions
        {...defaultProps}
        isViewMode={true}
        reservation={reservation}
        canValidate={true}
        onShowMotifRefus={onShowMotifRefus}
      />
    )

    // Act
    fireEvent.click(screen.getByText('Refuser'))

    // Assert
    expect(onShowMotifRefus).toHaveBeenCalledWith(true)
  })

  it('appelle onRefuser au clic sur Confirmer refus', () => {
    // Arrange
    const onRefuser = vi.fn()
    const reservation: any = { id: 1, statut: 'en_attente' }
    render(
      <ReservationActions
        {...defaultProps}
        isViewMode={true}
        reservation={reservation}
        canValidate={true}
        showMotifRefus={true}
        onRefuser={onRefuser}
      />
    )

    // Act
    fireEvent.click(screen.getByText('Confirmer refus'))

    // Assert
    expect(onRefuser).toHaveBeenCalled()
  })

  it('appelle onClose au clic sur Annuler ou Fermer', () => {
    // Arrange - mode creation
    const onClose = vi.fn()
    render(<ReservationActions {...defaultProps} isViewMode={false} onClose={onClose} />)

    // Act
    fireEvent.click(screen.getByText('Annuler'))

    // Assert
    expect(onClose).toHaveBeenCalled()
  })
})
