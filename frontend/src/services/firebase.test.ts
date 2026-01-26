/**
 * Tests unitaires pour le service Firebase
 * Gestion des notifications push FCM
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'

// Mock Firebase modules before imports
const mockInitializeApp = vi.fn()
const mockGetMessaging = vi.fn()
const mockGetToken = vi.fn()
const mockOnMessage = vi.fn()

vi.mock('firebase/app', () => ({
  initializeApp: mockInitializeApp,
}))

vi.mock('firebase/messaging', () => ({
  getMessaging: mockGetMessaging,
  getToken: mockGetToken,
  onMessage: mockOnMessage,
}))

// Mock import.meta.env
const originalEnv = import.meta.env

describe('firebase service', () => {
  const mockFirebaseApp = { name: 'test-app' }
  const mockMessaging = { type: 'messaging' }

  beforeEach(() => {
    vi.clearAllMocks()
    vi.resetModules()

    // Reset singleton state by re-importing module
    mockInitializeApp.mockReturnValue(mockFirebaseApp)
    mockGetMessaging.mockReturnValue(mockMessaging)
  })

  afterEach(() => {
    vi.unstubAllEnvs()
  })

  describe('isFirebaseConfigured', () => {
    it('retourne false si apiKey manquant', async () => {
      vi.stubEnv('VITE_FIREBASE_API_KEY', '')
      vi.stubEnv('VITE_FIREBASE_PROJECT_ID', 'test-project')
      vi.stubEnv('VITE_FIREBASE_MESSAGING_SENDER_ID', '123456')

      const { isFirebaseConfigured } = await import('./firebase')
      expect(isFirebaseConfigured()).toBe(false)
    })

    it('retourne false si projectId manquant', async () => {
      vi.stubEnv('VITE_FIREBASE_API_KEY', 'test-api-key')
      vi.stubEnv('VITE_FIREBASE_PROJECT_ID', '')
      vi.stubEnv('VITE_FIREBASE_MESSAGING_SENDER_ID', '123456')

      const { isFirebaseConfigured } = await import('./firebase')
      expect(isFirebaseConfigured()).toBe(false)
    })

    it('retourne false si messagingSenderId manquant', async () => {
      vi.stubEnv('VITE_FIREBASE_API_KEY', 'test-api-key')
      vi.stubEnv('VITE_FIREBASE_PROJECT_ID', 'test-project')
      vi.stubEnv('VITE_FIREBASE_MESSAGING_SENDER_ID', '')

      const { isFirebaseConfigured } = await import('./firebase')
      expect(isFirebaseConfigured()).toBe(false)
    })

    it('retourne true si configuration complete', async () => {
      vi.stubEnv('VITE_FIREBASE_API_KEY', 'test-api-key')
      vi.stubEnv('VITE_FIREBASE_PROJECT_ID', 'test-project')
      vi.stubEnv('VITE_FIREBASE_MESSAGING_SENDER_ID', '123456')

      const { isFirebaseConfigured } = await import('./firebase')
      expect(isFirebaseConfigured()).toBe(true)
    })
  })

  describe('initFirebase', () => {
    it('retourne null si non configure', async () => {
      vi.stubEnv('VITE_FIREBASE_API_KEY', '')
      vi.stubEnv('VITE_FIREBASE_PROJECT_ID', '')
      vi.stubEnv('VITE_FIREBASE_MESSAGING_SENDER_ID', '')

      const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})
      const { initFirebase } = await import('./firebase')

      const result = initFirebase()

      expect(result).toBeNull()
      expect(mockInitializeApp).not.toHaveBeenCalled()
      expect(consoleSpy).toHaveBeenCalledWith(
        expect.stringContaining('Firebase non configuré')
      )
      consoleSpy.mockRestore()
    })

    it('initialise Firebase avec la configuration', async () => {
      vi.stubEnv('VITE_FIREBASE_API_KEY', 'test-api-key')
      vi.stubEnv('VITE_FIREBASE_AUTH_DOMAIN', 'test.firebaseapp.com')
      vi.stubEnv('VITE_FIREBASE_PROJECT_ID', 'test-project')
      vi.stubEnv('VITE_FIREBASE_STORAGE_BUCKET', 'test.appspot.com')
      vi.stubEnv('VITE_FIREBASE_MESSAGING_SENDER_ID', '123456')
      vi.stubEnv('VITE_FIREBASE_APP_ID', 'test-app-id')

      const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {})
      const { initFirebase } = await import('./firebase')

      const result = initFirebase()

      expect(result).toBe(mockFirebaseApp)
      expect(mockInitializeApp).toHaveBeenCalledWith({
        apiKey: 'test-api-key',
        authDomain: 'test.firebaseapp.com',
        projectId: 'test-project',
        storageBucket: 'test.appspot.com',
        messagingSenderId: '123456',
        appId: 'test-app-id',
      })
      expect(consoleSpy).toHaveBeenCalledWith('Firebase initialisé')
      consoleSpy.mockRestore()
    })

    it('retourne singleton si deja initialise', async () => {
      vi.stubEnv('VITE_FIREBASE_API_KEY', 'test-api-key')
      vi.stubEnv('VITE_FIREBASE_PROJECT_ID', 'test-project')
      vi.stubEnv('VITE_FIREBASE_MESSAGING_SENDER_ID', '123456')

      vi.spyOn(console, 'log').mockImplementation(() => {})
      const { initFirebase } = await import('./firebase')

      const result1 = initFirebase()
      const result2 = initFirebase()

      expect(result1).toBe(result2)
      expect(mockInitializeApp).toHaveBeenCalledTimes(1)
    })

    it('gere les erreurs d initialisation', async () => {
      vi.stubEnv('VITE_FIREBASE_API_KEY', 'test-api-key')
      vi.stubEnv('VITE_FIREBASE_PROJECT_ID', 'test-project')
      vi.stubEnv('VITE_FIREBASE_MESSAGING_SENDER_ID', '123456')

      mockInitializeApp.mockImplementation(() => {
        throw new Error('Init error')
      })

      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      const { initFirebase } = await import('./firebase')

      const result = initFirebase()

      expect(result).toBeNull()
      expect(consoleSpy).toHaveBeenCalledWith(
        'Erreur initialisation Firebase:',
        expect.any(Error)
      )
      consoleSpy.mockRestore()
    })
  })

  describe('getFirebaseMessaging', () => {
    it('retourne null si Firebase non initialise', async () => {
      vi.stubEnv('VITE_FIREBASE_API_KEY', '')
      vi.stubEnv('VITE_FIREBASE_PROJECT_ID', '')
      vi.stubEnv('VITE_FIREBASE_MESSAGING_SENDER_ID', '')

      vi.spyOn(console, 'warn').mockImplementation(() => {})
      const { getFirebaseMessaging } = await import('./firebase')

      const result = getFirebaseMessaging()

      expect(result).toBeNull()
      expect(mockGetMessaging).not.toHaveBeenCalled()
    })

    it('initialise et retourne Messaging', async () => {
      vi.stubEnv('VITE_FIREBASE_API_KEY', 'test-api-key')
      vi.stubEnv('VITE_FIREBASE_PROJECT_ID', 'test-project')
      vi.stubEnv('VITE_FIREBASE_MESSAGING_SENDER_ID', '123456')

      vi.spyOn(console, 'log').mockImplementation(() => {})
      const { getFirebaseMessaging } = await import('./firebase')

      const result = getFirebaseMessaging()

      expect(result).toBe(mockMessaging)
      expect(mockGetMessaging).toHaveBeenCalledWith(mockFirebaseApp)
    })

    it('retourne singleton si deja initialise', async () => {
      vi.stubEnv('VITE_FIREBASE_API_KEY', 'test-api-key')
      vi.stubEnv('VITE_FIREBASE_PROJECT_ID', 'test-project')
      vi.stubEnv('VITE_FIREBASE_MESSAGING_SENDER_ID', '123456')

      vi.spyOn(console, 'log').mockImplementation(() => {})
      const { getFirebaseMessaging } = await import('./firebase')

      const result1 = getFirebaseMessaging()
      const result2 = getFirebaseMessaging()

      expect(result1).toBe(result2)
      expect(mockGetMessaging).toHaveBeenCalledTimes(1)
    })

    it('gere les erreurs de Messaging', async () => {
      vi.stubEnv('VITE_FIREBASE_API_KEY', 'test-api-key')
      vi.stubEnv('VITE_FIREBASE_PROJECT_ID', 'test-project')
      vi.stubEnv('VITE_FIREBASE_MESSAGING_SENDER_ID', '123456')

      mockGetMessaging.mockImplementation(() => {
        throw new Error('Messaging error')
      })

      vi.spyOn(console, 'log').mockImplementation(() => {})
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      const { getFirebaseMessaging } = await import('./firebase')

      const result = getFirebaseMessaging()

      expect(result).toBeNull()
      expect(consoleSpy).toHaveBeenCalledWith(
        'Erreur initialisation Messaging:',
        expect.any(Error)
      )
      consoleSpy.mockRestore()
    })
  })

  describe('requestNotificationPermission', () => {
    const originalNotification = global.Notification

    beforeEach(() => {
      // @ts-expect-error - mock Notification API
      global.Notification = {
        requestPermission: vi.fn(),
      }
    })

    afterEach(() => {
      global.Notification = originalNotification
    })

    it('retourne null si Notification non supporte', async () => {
      // @ts-expect-error - supprimer Notification pour le test
      delete global.Notification

      const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})
      const { requestNotificationPermission } = await import('./firebase')

      const result = await requestNotificationPermission()

      expect(result).toBeNull()
      expect(consoleSpy).toHaveBeenCalledWith(
        'Notifications non supportées par ce navigateur'
      )
      consoleSpy.mockRestore()
    })

    it('retourne null si permission refusee', async () => {
      // @ts-expect-error - mock Notification API
      global.Notification.requestPermission = vi.fn().mockResolvedValue('denied')

      const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})
      const { requestNotificationPermission } = await import('./firebase')

      const result = await requestNotificationPermission()

      expect(result).toBeNull()
      expect(consoleSpy).toHaveBeenCalledWith('Permission notifications refusée')
      consoleSpy.mockRestore()
    })

    it('retourne null si Firebase non configure', async () => {
      vi.stubEnv('VITE_FIREBASE_API_KEY', '')
      vi.stubEnv('VITE_FIREBASE_PROJECT_ID', '')
      vi.stubEnv('VITE_FIREBASE_MESSAGING_SENDER_ID', '')

      // @ts-expect-error - mock Notification API
      global.Notification.requestPermission = vi.fn().mockResolvedValue('granted')

      const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})
      const { requestNotificationPermission } = await import('./firebase')

      const result = await requestNotificationPermission()

      expect(result).toBeNull()
      expect(consoleSpy).toHaveBeenCalledWith('Firebase Messaging non disponible')
      consoleSpy.mockRestore()
    })

    it('retourne le token FCM si permission accordee', async () => {
      vi.stubEnv('VITE_FIREBASE_API_KEY', 'test-api-key')
      vi.stubEnv('VITE_FIREBASE_PROJECT_ID', 'test-project')
      vi.stubEnv('VITE_FIREBASE_MESSAGING_SENDER_ID', '123456')
      vi.stubEnv('VITE_FIREBASE_VAPID_KEY', 'test-vapid-key')

      // @ts-expect-error - mock Notification API
      global.Notification.requestPermission = vi.fn().mockResolvedValue('granted')
      mockGetToken.mockResolvedValue('test-fcm-token-123456789')

      vi.spyOn(console, 'log').mockImplementation(() => {})
      const { requestNotificationPermission } = await import('./firebase')

      const result = await requestNotificationPermission()

      expect(result).toBe('test-fcm-token-123456789')
      expect(mockGetToken).toHaveBeenCalledWith(mockMessaging, {
        vapidKey: 'test-vapid-key',
      })
    })

    it('retourne null si token vide', async () => {
      vi.stubEnv('VITE_FIREBASE_API_KEY', 'test-api-key')
      vi.stubEnv('VITE_FIREBASE_PROJECT_ID', 'test-project')
      vi.stubEnv('VITE_FIREBASE_MESSAGING_SENDER_ID', '123456')

      // @ts-expect-error - mock Notification API
      global.Notification.requestPermission = vi.fn().mockResolvedValue('granted')
      mockGetToken.mockResolvedValue('')

      vi.spyOn(console, 'log').mockImplementation(() => {})
      const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})
      const { requestNotificationPermission } = await import('./firebase')

      const result = await requestNotificationPermission()

      expect(result).toBeNull()
      expect(consoleSpy).toHaveBeenCalledWith('Aucun token FCM disponible')
      consoleSpy.mockRestore()
    })

    it('gere les erreurs de recuperation du token', async () => {
      vi.stubEnv('VITE_FIREBASE_API_KEY', 'test-api-key')
      vi.stubEnv('VITE_FIREBASE_PROJECT_ID', 'test-project')
      vi.stubEnv('VITE_FIREBASE_MESSAGING_SENDER_ID', '123456')

      // @ts-expect-error - mock Notification API
      global.Notification.requestPermission = vi.fn().mockResolvedValue('granted')
      mockGetToken.mockRejectedValue(new Error('Token error'))

      vi.spyOn(console, 'log').mockImplementation(() => {})
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      const { requestNotificationPermission } = await import('./firebase')

      const result = await requestNotificationPermission()

      expect(result).toBeNull()
      expect(consoleSpy).toHaveBeenCalledWith(
        'Erreur récupération token FCM:',
        expect.any(Error)
      )
      consoleSpy.mockRestore()
    })
  })

  describe('onForegroundMessage', () => {
    it('retourne null si Firebase non configure', async () => {
      vi.stubEnv('VITE_FIREBASE_API_KEY', '')
      vi.stubEnv('VITE_FIREBASE_PROJECT_ID', '')
      vi.stubEnv('VITE_FIREBASE_MESSAGING_SENDER_ID', '')

      vi.spyOn(console, 'warn').mockImplementation(() => {})
      const { onForegroundMessage } = await import('./firebase')

      const callback = vi.fn()
      const result = onForegroundMessage(callback)

      expect(result).toBeNull()
      expect(mockOnMessage).not.toHaveBeenCalled()
    })

    it('enregistre le listener et retourne cleanup', async () => {
      vi.stubEnv('VITE_FIREBASE_API_KEY', 'test-api-key')
      vi.stubEnv('VITE_FIREBASE_PROJECT_ID', 'test-project')
      vi.stubEnv('VITE_FIREBASE_MESSAGING_SENDER_ID', '123456')

      const mockUnsubscribe = vi.fn()
      mockOnMessage.mockReturnValue(mockUnsubscribe)

      vi.spyOn(console, 'log').mockImplementation(() => {})
      const { onForegroundMessage } = await import('./firebase')

      const callback = vi.fn()
      const cleanup = onForegroundMessage(callback)

      expect(cleanup).toBe(mockUnsubscribe)
      expect(mockOnMessage).toHaveBeenCalledWith(mockMessaging, expect.any(Function))
    })

    it('appelle le callback avec les donnees du message', async () => {
      vi.stubEnv('VITE_FIREBASE_API_KEY', 'test-api-key')
      vi.stubEnv('VITE_FIREBASE_PROJECT_ID', 'test-project')
      vi.stubEnv('VITE_FIREBASE_MESSAGING_SENDER_ID', '123456')

      let capturedHandler: ((payload: unknown) => void) | undefined
      mockOnMessage.mockImplementation((_msg, handler) => {
        capturedHandler = handler
        return vi.fn()
      })

      vi.spyOn(console, 'log').mockImplementation(() => {})
      const { onForegroundMessage } = await import('./firebase')

      const callback = vi.fn()
      onForegroundMessage(callback)

      // Simuler un message entrant
      const payload = {
        notification: {
          title: 'Test Title',
          body: 'Test Body',
        },
        data: {
          key: 'value',
        },
      }

      capturedHandler?.(payload)

      expect(callback).toHaveBeenCalledWith({
        title: 'Test Title',
        body: 'Test Body',
        data: { key: 'value' },
      })
    })
  })

  describe('default export', () => {
    it('exporte toutes les fonctions', async () => {
      vi.stubEnv('VITE_FIREBASE_API_KEY', '')
      const firebaseModule = await import('./firebase')

      expect(firebaseModule.default).toHaveProperty('initFirebase')
      expect(firebaseModule.default).toHaveProperty('isFirebaseConfigured')
      expect(firebaseModule.default).toHaveProperty('getFirebaseMessaging')
      expect(firebaseModule.default).toHaveProperty('requestNotificationPermission')
      expect(firebaseModule.default).toHaveProperty('onForegroundMessage')
    })
  })
})
