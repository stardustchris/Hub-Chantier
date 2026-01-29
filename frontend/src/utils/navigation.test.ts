/**
 * Tests unitaires pour les utilitaires de navigation
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { openNavigationApp } from './navigation'

describe('openNavigationApp', () => {
  let originalUserAgent: string
  let hrefSetter: ReturnType<typeof vi.fn>
  let originalOpen: typeof window.open

  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers()
    originalUserAgent = navigator.userAgent
    originalOpen = window.open
    window.open = vi.fn()

    // Spy on window.location.href assignments
    hrefSetter = vi.fn()
    const originalLocation = window.location
    // @ts-expect-error - mocking location
    delete window.location
    // @ts-expect-error - assigning mock location object
    window.location = {
      ...originalLocation as any,
      set href(val: string) {
        hrefSetter(val)
      },
      get href() {
        return 'http://localhost:3000/'
      },
    } as Location
  })

  afterEach(() => {
    vi.useRealTimers()
    Object.defineProperty(navigator, 'userAgent', {
      value: originalUserAgent,
      configurable: true,
    })
    window.open = originalOpen
    // Restore location - jsdom will handle this on next test file
  })

  function setUserAgent(ua: string) {
    Object.defineProperty(navigator, 'userAgent', {
      value: ua,
      configurable: true,
    })
  }

  describe('sur iOS', () => {
    beforeEach(() => {
      setUserAgent('Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)')
    })

    it('tente Waze en premier', () => {
      openNavigationApp('123 Rue de Paris')

      const encoded = encodeURIComponent('123 Rue de Paris')
      expect(hrefSetter).toHaveBeenCalledWith(`waze://?q=${encoded}&navigate=yes`)
    })

    it('fallback Apple Maps apres 500ms', () => {
      openNavigationApp('123 Rue de Paris')

      const encoded = encodeURIComponent('123 Rue de Paris')
      vi.advanceTimersByTime(500)

      expect(hrefSetter).toHaveBeenCalledWith(`maps://maps.apple.com/?q=${encoded}`)
    })

    it('fallback Google Maps web apres 1000ms', () => {
      openNavigationApp('123 Rue de Paris')

      const encoded = encodeURIComponent('123 Rue de Paris')
      vi.advanceTimersByTime(1000)

      expect(window.open).toHaveBeenCalledWith(
        `https://maps.google.com/?q=${encoded}`,
        '_blank'
      )
    })
  })

  describe('sur Android', () => {
    beforeEach(() => {
      setUserAgent('Mozilla/5.0 (Linux; Android 13; Pixel 7)')
    })

    it('tente Waze en premier', () => {
      openNavigationApp('456 Avenue de Lyon')

      const encoded = encodeURIComponent('456 Avenue de Lyon')
      expect(hrefSetter).toHaveBeenCalledWith(`waze://?q=${encoded}&navigate=yes`)
    })

    it('fallback Google Maps app apres 500ms', () => {
      openNavigationApp('456 Avenue de Lyon')

      const encoded = encodeURIComponent('456 Avenue de Lyon')
      vi.advanceTimersByTime(500)

      expect(hrefSetter).toHaveBeenCalledWith(`google.navigation:q=${encoded}`)
    })

    it('fallback Google Maps web apres 1000ms', () => {
      openNavigationApp('456 Avenue de Lyon')

      const encoded = encodeURIComponent('456 Avenue de Lyon')
      vi.advanceTimersByTime(1000)

      expect(window.open).toHaveBeenCalledWith(
        `https://maps.google.com/?q=${encoded}`,
        '_blank'
      )
    })
  })

  describe('sur Desktop', () => {
    beforeEach(() => {
      setUserAgent('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36')
    })

    it('ouvre Google Maps web directement', () => {
      openNavigationApp('789 Boulevard de Marseille')

      const encoded = encodeURIComponent('789 Boulevard de Marseille')
      expect(window.open).toHaveBeenCalledWith(
        `https://maps.google.com/?q=${encoded}`,
        '_blank'
      )
    })

    it('ne tente pas Waze ni Apple Maps', () => {
      openNavigationApp('Test Address')

      // Should not set location.href at all on desktop
      expect(hrefSetter).not.toHaveBeenCalled()
    })
  })

  describe('encodage adresse', () => {
    beforeEach(() => {
      setUserAgent('Mozilla/5.0 (X11; Linux x86_64)')
    })

    it('encode correctement les caracteres speciaux', () => {
      openNavigationApp('10 Rue de l\'Eglise, 73000 Chambery')

      expect(window.open).toHaveBeenCalledWith(
        expect.stringContaining(encodeURIComponent('10 Rue de l\'Eglise, 73000 Chambery')),
        '_blank'
      )
    })

    it('encode les espaces', () => {
      openNavigationApp('Rue de la Paix')

      expect(window.open).toHaveBeenCalledWith(
        expect.stringContaining('Rue%20de%20la%20Paix'),
        '_blank'
      )
    })
  })
})
