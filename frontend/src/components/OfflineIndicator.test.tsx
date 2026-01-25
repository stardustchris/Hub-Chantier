/**
 * Tests pour OfflineIndicator
 * FDH-20: Mode Offline (PWA/Service Worker)
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react'
import OfflineIndicator from './OfflineIndicator'

describe('OfflineIndicator', () => {
  let originalNavigatorOnLine: boolean

  beforeEach(() => {
    vi.clearAllMocks()
    originalNavigatorOnLine = navigator.onLine

    // Mock navigator.onLine
    Object.defineProperty(navigator, 'onLine', {
      configurable: true,
      get: vi.fn(() => true),
    })
  })

  afterEach(() => {
    // Restore original onLine
    Object.defineProperty(navigator, 'onLine', {
      configurable: true,
      get: () => originalNavigatorOnLine,
    })
  })

  describe('Quand en ligne', () => {
    it('ne rend rien par defaut quand en ligne', () => {
      render(<OfflineIndicator />)
      expect(screen.queryByRole('status')).not.toBeInTheDocument()
    })

    it('applique la className personnalisee', () => {
      // Forcer offline pour voir le composant
      Object.defineProperty(navigator, 'onLine', {
        configurable: true,
        get: () => false,
      })

      const { container } = render(<OfflineIndicator className="custom-class" />)

      // Re-render pour forcer l'update
      fireEvent(window, new Event('offline'))

      const indicator = container.querySelector('.custom-class')
      expect(indicator).toBeInTheDocument()
    })
  })

  describe('Quand hors-ligne', () => {
    beforeEach(() => {
      Object.defineProperty(navigator, 'onLine', {
        configurable: true,
        get: () => false,
      })
    })

    it('affiche l\'indicateur hors-ligne', () => {
      render(<OfflineIndicator />)
      fireEvent(window, new Event('offline'))

      expect(screen.getByText('Mode hors-ligne')).toBeInTheDocument()
    })

    it('affiche le message de synchronisation', () => {
      render(<OfflineIndicator />)
      fireEvent(window, new Event('offline'))

      expect(screen.getByText(/Vos modifications seront synchronisees/)).toBeInTheDocument()
    })

    it('affiche le bouton de rechargement', () => {
      render(<OfflineIndicator />)
      fireEvent(window, new Event('offline'))

      expect(screen.getByLabelText('Recharger la page')).toBeInTheDocument()
    })

    it('recharge la page au clic sur le bouton', () => {
      const reloadMock = vi.fn()
      Object.defineProperty(window, 'location', {
        configurable: true,
        value: { reload: reloadMock },
      })

      render(<OfflineIndicator />)
      fireEvent(window, new Event('offline'))

      fireEvent.click(screen.getByLabelText('Recharger la page'))
      expect(reloadMock).toHaveBeenCalled()
    })
  })

  describe('Transitions', () => {
    it('affiche le message de reconnexion apres etre revenu en ligne', async () => {
      // Start offline
      Object.defineProperty(navigator, 'onLine', {
        configurable: true,
        get: () => false,
      })

      render(<OfflineIndicator />)
      fireEvent(window, new Event('offline'))

      // Go back online
      Object.defineProperty(navigator, 'onLine', {
        configurable: true,
        get: () => true,
      })

      await act(async () => {
        fireEvent(window, new Event('online'))
      })

      await waitFor(() => {
        expect(screen.getByText('Connexion retablie')).toBeInTheDocument()
      })
    })

    it('masque le message de reconnexion apres 3 secondes', async () => {
      vi.useFakeTimers()

      // Start offline
      Object.defineProperty(navigator, 'onLine', {
        configurable: true,
        get: () => false,
      })

      render(<OfflineIndicator />)
      fireEvent(window, new Event('offline'))

      // Go back online
      Object.defineProperty(navigator, 'onLine', {
        configurable: true,
        get: () => true,
      })

      await act(async () => {
        fireEvent(window, new Event('online'))
      })

      expect(screen.getByText('Connexion retablie')).toBeInTheDocument()

      // Advance time by 3 seconds
      await act(async () => {
        vi.advanceTimersByTime(3000)
      })

      expect(screen.queryByText('Connexion retablie')).not.toBeInTheDocument()

      vi.useRealTimers()
    })
  })

  describe('Accessibilite', () => {
    it('a le role status', () => {
      Object.defineProperty(navigator, 'onLine', {
        configurable: true,
        get: () => false,
      })

      render(<OfflineIndicator />)
      fireEvent(window, new Event('offline'))

      expect(screen.getByRole('status')).toBeInTheDocument()
    })

    it('a aria-live polite', () => {
      Object.defineProperty(navigator, 'onLine', {
        configurable: true,
        get: () => false,
      })

      render(<OfflineIndicator />)
      fireEvent(window, new Event('offline'))

      expect(screen.getByRole('status')).toHaveAttribute('aria-live', 'polite')
    })
  })
})
