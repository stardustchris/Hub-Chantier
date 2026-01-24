/**
 * Tests unitaires pour authEvents
 * Module d'evenements d'authentification avec synchronisation multi-onglets
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'

// Note: On doit tester le module de maniere isolee car il a un etat global
describe('authEvents', () => {
  let originalBroadcastChannel: typeof BroadcastChannel | undefined
  let originalLocalStorage: Storage

  beforeEach(() => {
    // Sauvegarder les originaux
    originalBroadcastChannel = globalThis.BroadcastChannel
    originalLocalStorage = globalThis.localStorage

    vi.clearAllMocks()
    vi.resetModules()
  })

  afterEach(() => {
    // Restaurer les originaux
    if (originalBroadcastChannel) {
      globalThis.BroadcastChannel = originalBroadcastChannel
    }
    vi.resetModules()
  })

  describe('avec BroadcastChannel disponible', () => {
    let mockPostMessage: ReturnType<typeof vi.fn>
    let mockOnMessage: ((event: MessageEvent) => void) | null = null

    beforeEach(() => {
      mockPostMessage = vi.fn()

      // Mock BroadcastChannel
      globalThis.BroadcastChannel = vi.fn().mockImplementation(() => ({
        postMessage: mockPostMessage,
        set onmessage(handler: (event: MessageEvent) => void) {
          mockOnMessage = handler
        },
        close: vi.fn(),
      })) as unknown as typeof BroadcastChannel
    })

    it('cree un BroadcastChannel nomme hub-chantier-auth', async () => {
      await import('./authEvents')

      expect(BroadcastChannel).toHaveBeenCalledWith('hub-chantier-auth')
    })

    it('emitSessionExpired notifie les listeners locaux', async () => {
      const { emitSessionExpired, onSessionExpired } = await import('./authEvents')
      const listener = vi.fn()

      onSessionExpired(listener)
      emitSessionExpired()

      expect(listener).toHaveBeenCalled()
    })

    it('emitSessionExpired broadcast aux autres onglets', async () => {
      const { emitSessionExpired } = await import('./authEvents')

      emitSessionExpired()

      expect(mockPostMessage).toHaveBeenCalledWith('logout')
    })

    it('emitLogout broadcast sans notifier les listeners locaux', async () => {
      const { emitLogout, onSessionExpired } = await import('./authEvents')
      const listener = vi.fn()

      onSessionExpired(listener)
      emitLogout()

      // emitLogout ne notifie pas les listeners locaux, seulement broadcast
      expect(listener).not.toHaveBeenCalled()
      expect(mockPostMessage).toHaveBeenCalledWith('logout')
    })

    it('onSessionExpired retourne une fonction de desinscription', async () => {
      const { emitSessionExpired, onSessionExpired } = await import('./authEvents')
      const listener = vi.fn()

      const unsubscribe = onSessionExpired(listener)

      // Avant desinscription
      emitSessionExpired()
      expect(listener).toHaveBeenCalledTimes(1)

      // Desinscription
      unsubscribe()

      // Apres desinscription
      emitSessionExpired()
      expect(listener).toHaveBeenCalledTimes(1) // Pas d'appel supplementaire
    })

    it('plusieurs listeners peuvent etre enregistres', async () => {
      const { emitSessionExpired, onSessionExpired } = await import('./authEvents')
      const listener1 = vi.fn()
      const listener2 = vi.fn()
      const listener3 = vi.fn()

      onSessionExpired(listener1)
      onSessionExpired(listener2)
      onSessionExpired(listener3)

      emitSessionExpired()

      expect(listener1).toHaveBeenCalled()
      expect(listener2).toHaveBeenCalled()
      expect(listener3).toHaveBeenCalled()
    })

    it('reagit aux messages des autres onglets', async () => {
      const { onSessionExpired } = await import('./authEvents')
      const listener = vi.fn()

      onSessionExpired(listener)

      // Simuler un message recu d'un autre onglet
      if (mockOnMessage) {
        mockOnMessage({ data: 'logout' } as MessageEvent)
      }

      expect(listener).toHaveBeenCalled()
    })

    it('ignore les messages non-logout', async () => {
      const { onSessionExpired } = await import('./authEvents')
      const listener = vi.fn()

      onSessionExpired(listener)

      // Simuler un message non-logout
      if (mockOnMessage) {
        mockOnMessage({ data: 'other-message' } as MessageEvent)
      }

      expect(listener).not.toHaveBeenCalled()
    })
  })

  describe('avec fallback localStorage', () => {
    let mockLocalStorage: {
      getItem: ReturnType<typeof vi.fn>
      setItem: ReturnType<typeof vi.fn>
      removeItem: ReturnType<typeof vi.fn>
    }
    let storageEventHandler: ((event: StorageEvent) => void) | null = null

    beforeEach(() => {
      // Desactiver BroadcastChannel
      // @ts-expect-error - intentionnel pour tester le fallback
      delete globalThis.BroadcastChannel

      mockLocalStorage = {
        getItem: vi.fn(),
        setItem: vi.fn(),
        removeItem: vi.fn(),
      }

      Object.defineProperty(globalThis, 'localStorage', {
        value: mockLocalStorage,
        writable: true,
      })

      // Capturer le handler de l'event storage
      vi.spyOn(window, 'addEventListener').mockImplementation((event, handler) => {
        if (event === 'storage') {
          storageEventHandler = handler as (event: StorageEvent) => void
        }
      })
    })

    it('utilise localStorage comme fallback', async () => {
      const { emitLogout } = await import('./authEvents')

      emitLogout()

      expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
        'hub-chantier-logout-event',
        expect.any(String)
      )
      expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('hub-chantier-logout-event')
    })

    it('ecoute l\'evenement storage pour sync multi-onglets', async () => {
      await import('./authEvents')

      expect(window.addEventListener).toHaveBeenCalledWith('storage', expect.any(Function))
    })

    it('reagit aux evenements storage de logout', async () => {
      const { onSessionExpired } = await import('./authEvents')
      const listener = vi.fn()

      onSessionExpired(listener)

      // Simuler un evenement storage
      if (storageEventHandler) {
        storageEventHandler({
          key: 'hub-chantier-logout-event',
          newValue: Date.now().toString(),
        } as StorageEvent)
      }

      expect(listener).toHaveBeenCalled()
    })

    it('ignore les evenements storage sans nouvelle valeur', async () => {
      const { onSessionExpired } = await import('./authEvents')
      const listener = vi.fn()

      onSessionExpired(listener)

      // Simuler un evenement sans newValue
      if (storageEventHandler) {
        storageEventHandler({
          key: 'hub-chantier-logout-event',
          newValue: null,
        } as StorageEvent)
      }

      expect(listener).not.toHaveBeenCalled()
    })

    it('ignore les evenements storage pour d\'autres cles', async () => {
      const { onSessionExpired } = await import('./authEvents')
      const listener = vi.fn()

      onSessionExpired(listener)

      // Simuler un evenement pour une autre cle
      if (storageEventHandler) {
        storageEventHandler({
          key: 'other-key',
          newValue: 'some-value',
        } as StorageEvent)
      }

      expect(listener).not.toHaveBeenCalled()
    })
  })

  describe('gestion des erreurs', () => {
    it('passe en fallback si BroadcastChannel echoue', async () => {
      // Mock BroadcastChannel qui throw
      globalThis.BroadcastChannel = vi.fn().mockImplementation(() => {
        throw new Error('BroadcastChannel not available')
      }) as unknown as typeof BroadcastChannel

      const mockSetItem = vi.fn()
      const mockRemoveItem = vi.fn()
      Object.defineProperty(globalThis, 'localStorage', {
        value: {
          getItem: vi.fn(),
          setItem: mockSetItem,
          removeItem: mockRemoveItem,
        },
        writable: true,
      })

      vi.spyOn(window, 'addEventListener').mockImplementation(() => {})

      const { emitLogout } = await import('./authEvents')

      emitLogout()

      // Doit utiliser le fallback localStorage
      expect(mockSetItem).toHaveBeenCalled()
    })
  })
})
