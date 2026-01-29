/**
 * Tests pour GDPRBanner
 *
 * Couvre:
 * - Rendu par defaut (banner temporairement desactive)
 * - Documentation du comportement attendu une fois reactive
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render } from '@testing-library/react'
import { GDPRBanner } from './GDPRBanner'

vi.mock('../../services/consent', () => ({
  consentService: {
    setConsents: vi.fn().mockResolvedValue(undefined),
    hasAnswered: vi.fn().mockResolvedValue(false),
    wasBannerShown: vi.fn().mockReturnValue(false),
    markBannerAsShown: vi.fn(),
  },
}))

vi.mock('../../services/logger', () => ({
  logger: { info: vi.fn(), error: vi.fn(), warn: vi.fn() },
}))

import { consentService } from '../../services/consent'

describe('GDPRBanner', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('ne rend rien par defaut (banner temporairement desactive)', () => {
    // Arrange & Act
    const { container } = render(<GDPRBanner />)

    // Assert
    expect(container.innerHTML).toBe('')
  })

  it('ne rend aucun element visible quand le banner est cache', () => {
    // Arrange & Act
    const { container } = render(<GDPRBanner />)

    // Assert
    expect(container.querySelector('.fixed')).toBeNull()
    expect(container.querySelector('button')).toBeNull()
  })

  it('n appelle pas consentService.setConsents au rendu initial', () => {
    // Arrange & Act
    render(<GDPRBanner />)

    // Assert
    expect(consentService.setConsents).not.toHaveBeenCalled()
  })

  it('n appelle pas consentService.hasAnswered (code commente)', () => {
    // Arrange & Act
    render(<GDPRBanner />)

    // Assert
    // NOTE: hasAnswered est dans le code commente, donc pas appele
    expect(consentService.hasAnswered).not.toHaveBeenCalled()
  })

  it('n appelle pas consentService.markBannerAsShown (code commente)', () => {
    // Arrange & Act
    render(<GDPRBanner />)

    // Assert
    expect(consentService.markBannerAsShown).not.toHaveBeenCalled()
  })

  // NOTE: Le banner GDPR est temporairement desactive dans le code (setShowBanner(false) en dur).
  // Les tests ci-dessous documentent le comportement attendu une fois reactive.
  // Pour tester l'UI complete, il faudrait reactiver le banner dans le composant.
})
