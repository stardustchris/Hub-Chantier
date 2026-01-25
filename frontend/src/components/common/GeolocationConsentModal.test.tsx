/**
 * Tests pour GeolocationConsentModal
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import GeolocationConsentModal from './GeolocationConsentModal'

describe('GeolocationConsentModal', () => {
  const defaultProps = {
    isOpen: true,
    onAccept: vi.fn(),
    onDecline: vi.fn(),
    onClose: vi.fn(),
  }

  it('n\'affiche rien si isOpen est false', () => {
    const { container } = render(
      <GeolocationConsentModal {...defaultProps} isOpen={false} />
    )

    expect(container.firstChild).toBeNull()
  })

  it('affiche le modal si isOpen est true', () => {
    render(<GeolocationConsentModal {...defaultProps} />)

    expect(screen.getByText('Autorisation de localisation')).toBeInTheDocument()
  })

  it('affiche les informations RGPD', () => {
    render(<GeolocationConsentModal {...defaultProps} />)

    expect(screen.getByText('Pourquoi cette demande ?')).toBeInTheDocument()
    expect(screen.getByText('Donnees collectees')).toBeInTheDocument()
    expect(screen.getByText(/Duree de conservation/)).toBeInTheDocument()
  })

  it('affiche l\'explication de la finalite', () => {
    render(<GeolocationConsentModal {...defaultProps} />)

    expect(screen.getByText(/position geographique sera enregistree/)).toBeInTheDocument()
  })

  it('affiche l\'explication des donnees collectees', () => {
    render(<GeolocationConsentModal {...defaultProps} />)

    expect(screen.getByText(/coordonnees GPS/)).toBeInTheDocument()
    expect(screen.getByText(/Aucun suivi continu/)).toBeInTheDocument()
  })

  it('affiche la duree de conservation', () => {
    render(<GeolocationConsentModal {...defaultProps} />)

    expect(screen.getByText(/5 ans/)).toBeInTheDocument()
    expect(screen.getByText(/obligation legale BTP/)).toBeInTheDocument()
  })

  it('affiche les droits RGPD', () => {
    render(<GeolocationConsentModal {...defaultProps} />)

    expect(screen.getByText(/Conformement au RGPD/)).toBeInTheDocument()
    expect(screen.getByText(/acces, rectification, suppression/)).toBeInTheDocument()
  })

  it('affiche les boutons Accepter et Refuser', () => {
    render(<GeolocationConsentModal {...defaultProps} />)

    expect(screen.getByText('Accepter')).toBeInTheDocument()
    expect(screen.getByText('Refuser')).toBeInTheDocument()
  })

  it('appelle onAccept au clic sur Accepter', () => {
    const onAccept = vi.fn()
    render(<GeolocationConsentModal {...defaultProps} onAccept={onAccept} />)

    fireEvent.click(screen.getByText('Accepter'))

    expect(onAccept).toHaveBeenCalled()
  })

  it('appelle onDecline au clic sur Refuser', () => {
    const onDecline = vi.fn()
    render(<GeolocationConsentModal {...defaultProps} onDecline={onDecline} />)

    fireEvent.click(screen.getByText('Refuser'))

    expect(onDecline).toHaveBeenCalled()
  })

  it('appelle onClose au clic sur le bouton fermer', () => {
    const onClose = vi.fn()
    render(<GeolocationConsentModal {...defaultProps} onClose={onClose} />)

    fireEvent.click(screen.getByLabelText('Fermer'))

    expect(onClose).toHaveBeenCalled()
  })

  it('appelle onClose au clic sur le backdrop', () => {
    const onClose = vi.fn()
    const { container } = render(<GeolocationConsentModal {...defaultProps} onClose={onClose} />)

    const backdrop = container.querySelector('[aria-hidden="true"]')
    fireEvent.click(backdrop!)

    expect(onClose).toHaveBeenCalled()
  })

  it('a l\'attribut role dialog', () => {
    render(<GeolocationConsentModal {...defaultProps} />)

    expect(screen.getByRole('dialog')).toBeInTheDocument()
  })

  it('a l\'attribut aria-modal', () => {
    render(<GeolocationConsentModal {...defaultProps} />)

    expect(screen.getByRole('dialog')).toHaveAttribute('aria-modal', 'true')
  })

  it('a un titre accessible', () => {
    render(<GeolocationConsentModal {...defaultProps} />)

    const dialog = screen.getByRole('dialog')
    expect(dialog).toHaveAttribute('aria-labelledby', 'consent-title')
    expect(screen.getByText('Autorisation de localisation').id).toBe('consent-title')
  })
})
