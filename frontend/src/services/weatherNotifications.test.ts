/**
 * Tests unitaires pour le service weatherNotifications
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'

// Mock du logger
vi.mock('./logger', () => ({
  logger: {
    warn: vi.fn(),
    info: vi.fn(),
    error: vi.fn(),
    debug: vi.fn(),
  },
}))

import type { WeatherAlert } from './weather'

// Helper to set up Notification mock
function setupNotificationMock(permission: NotificationPermission = 'granted') {
  const mockNotification = vi.fn().mockImplementation(() => ({
    onclick: null,
    close: vi.fn(),
  })) as any
  mockNotification.permission = permission
  mockNotification.requestPermission = vi.fn().mockResolvedValue(permission)

  Object.defineProperty(window, 'Notification', {
    value: mockNotification,
    configurable: true,
    writable: true,
  })

  return mockNotification
}

// We need to re-import the module for each test to reset module-level state
// (lastAlertKey, lastBulletinDate)
async function importFresh() {
  vi.resetModules()
  // Re-mock logger after resetModules
  vi.doMock('./logger', () => ({
    logger: {
      warn: vi.fn(),
      info: vi.fn(),
      error: vi.fn(),
      debug: vi.fn(),
    },
  }))
  return await import('./weatherNotifications')
}

describe('weatherNotifications', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  describe('areNotificationsSupported', () => {
    it('retourne true si Notification existe dans window', async () => {
      setupNotificationMock()
      const mod = await importFresh()
      expect(mod.areNotificationsSupported()).toBe(true)
    })

    it('retourne false si Notification n existe pas', async () => {
      const original = window.Notification
      // @ts-expect-error - removing Notification for testing
      delete window.Notification

      const mod = await importFresh()
      expect(mod.areNotificationsSupported()).toBe(false)

      Object.defineProperty(window, 'Notification', {
        value: original,
        configurable: true,
        writable: true,
      })
    })
  })

  describe('requestNotificationPermission', () => {
    it('retourne la permission accordee', async () => {
      setupNotificationMock('granted')
      const mod = await importFresh()
      const result = await mod.requestNotificationPermission()
      expect(result).toBe('granted')
    })

    it('retourne denied si notifications non supportees', async () => {
      const original = window.Notification
      // @ts-expect-error - removing Notification for testing
      delete window.Notification

      const mod = await importFresh()
      const result = await mod.requestNotificationPermission()
      expect(result).toBe('denied')

      Object.defineProperty(window, 'Notification', {
        value: original,
        configurable: true,
        writable: true,
      })
    })

    it('retourne denied si requestPermission echoue', async () => {
      const mock = setupNotificationMock()
      mock.requestPermission = vi.fn().mockRejectedValue(new Error('Failed'))

      const mod = await importFresh()
      const result = await mod.requestNotificationPermission()
      expect(result).toBe('denied')
    })
  })

  describe('areNotificationsAllowed', () => {
    it('retourne true si supportees et permission granted', async () => {
      setupNotificationMock('granted')
      const mod = await importFresh()
      expect(mod.areNotificationsAllowed()).toBe(true)
    })

    it('retourne false si permission denied', async () => {
      setupNotificationMock('denied')
      const mod = await importFresh()
      expect(mod.areNotificationsAllowed()).toBe(false)
    })

    it('retourne false si permission default', async () => {
      setupNotificationMock('default')
      const mod = await importFresh()
      expect(mod.areNotificationsAllowed()).toBe(false)
    })
  })

  describe('sendWeatherAlertNotification', () => {
    const alert: WeatherAlert = {
      type: 'vigilance_orange',
      title: 'Vigilance orange - Vent violent',
      description: 'Rafales de vent attendues',
      startTime: '2026-01-29T10:00:00Z',
      phenomena: ['vent'],
    }

    it('cree une notification si permission accordee', async () => {
      const mock = setupNotificationMock('granted')
      const mod = await importFresh()

      mod.sendWeatherAlertNotification(alert)

      expect(mock).toHaveBeenCalledWith(alert.title, expect.objectContaining({
        body: alert.description,
        tag: 'weather-alert',
      }))
    })

    it('ne cree pas de notification si permission refusee', async () => {
      const mock = setupNotificationMock('denied')
      const mod = await importFresh()

      mod.sendWeatherAlertNotification(alert)

      expect(mock).not.toHaveBeenCalled()
    })

    it('ne notifie pas la meme alerte deux fois', async () => {
      const mock = setupNotificationMock('granted')
      const mod = await importFresh()

      mod.sendWeatherAlertNotification(alert)
      mod.sendWeatherAlertNotification(alert)

      expect(mock).toHaveBeenCalledTimes(1)
    })

    it('notifie une alerte differente', async () => {
      const mock = setupNotificationMock('granted')
      const mod = await importFresh()

      mod.sendWeatherAlertNotification(alert)

      const differentAlert: WeatherAlert = {
        type: 'vigilance_jaune',
        title: 'Vigilance jaune - Pluie',
        description: 'Pluie forte',
        startTime: '2026-01-29T12:00:00Z',
        phenomena: ['pluie-inondation'],
      }
      mod.sendWeatherAlertNotification(differentAlert)

      expect(mock).toHaveBeenCalledTimes(2)
    })

    it('vigilance rouge utilise requireInteraction true', async () => {
      const mock = setupNotificationMock('granted')
      const mod = await importFresh()

      const rougeAlert: WeatherAlert = {
        type: 'vigilance_rouge',
        title: 'Vigilance rouge',
        description: 'Danger extreme',
        startTime: '2026-01-29T10:00:00Z',
        phenomena: ['vent'],
      }
      mod.sendWeatherAlertNotification(rougeAlert)

      expect(mock).toHaveBeenCalledWith(rougeAlert.title, expect.objectContaining({
        requireInteraction: true,
      }))
    })
  })

  describe('sendMorningBulletinNotification', () => {
    it('cree une notification bulletin si permission accordee', async () => {
      const mock = setupNotificationMock('granted')
      const mod = await importFresh()

      mod.sendMorningBulletinNotification('Chambery', 15, 'sunny', 'Temps ensoleille')

      expect(mock).toHaveBeenCalledWith(
        expect.stringContaining('Chambery'),
        expect.objectContaining({
          body: 'Temps ensoleille',
          tag: 'weather-bulletin',
        })
      )
    })

    it('ne cree pas de notification si permission refusee', async () => {
      const mock = setupNotificationMock('denied')
      const mod = await importFresh()

      mod.sendMorningBulletinNotification('Chambery', 15, 'sunny', 'Temps ensoleille')

      expect(mock).not.toHaveBeenCalled()
    })

    it('n envoie pas le bulletin deux fois le meme jour', async () => {
      const mock = setupNotificationMock('granted')
      const mod = await importFresh()

      mod.sendMorningBulletinNotification('Chambery', 15, 'sunny', 'Bulletin 1')
      mod.sendMorningBulletinNotification('Chambery', 18, 'cloudy', 'Bulletin 2')

      expect(mock).toHaveBeenCalledTimes(1)
    })
  })

  describe('registerPushNotifications', () => {
    it('retourne false si serviceWorker non supporte', async () => {
      const originalSW = navigator.serviceWorker
      Object.defineProperty(navigator, 'serviceWorker', {
        value: undefined,
        configurable: true,
      })

      const mod = await importFresh()
      const result = await mod.registerPushNotifications()
      expect(result).toBe(false)

      Object.defineProperty(navigator, 'serviceWorker', {
        value: originalSW,
        configurable: true,
      })
    })

    it('retourne false si PushManager non supporte', async () => {
      const originalPM = window.PushManager
      // @ts-expect-error - removing PushManager for testing
      delete window.PushManager

      Object.defineProperty(navigator, 'serviceWorker', {
        value: { ready: Promise.resolve({ pushManager: { getSubscription: vi.fn() } }) },
        configurable: true,
      })

      const mod = await importFresh()
      const result = await mod.registerPushNotifications()
      expect(result).toBe(false)

      Object.defineProperty(window, 'PushManager', {
        value: originalPM,
        configurable: true,
        writable: true,
      })
    })

    it('retourne true si deja abonne', async () => {
      const mockSubscription = { endpoint: 'https://push.example.com' }
      const mockRegistration = {
        pushManager: {
          getSubscription: vi.fn().mockResolvedValue(mockSubscription),
        },
      }

      Object.defineProperty(navigator, 'serviceWorker', {
        value: { ready: Promise.resolve(mockRegistration) },
        configurable: true,
      })

      Object.defineProperty(window, 'PushManager', {
        value: class PushManager {},
        configurable: true,
        writable: true,
      })

      const mod = await importFresh()
      const result = await mod.registerPushNotifications()
      expect(result).toBe(true)
    })

    it('retourne true si pas encore abonne (mode local)', async () => {
      const mockRegistration = {
        pushManager: {
          getSubscription: vi.fn().mockResolvedValue(null),
        },
      }

      Object.defineProperty(navigator, 'serviceWorker', {
        value: { ready: Promise.resolve(mockRegistration) },
        configurable: true,
      })

      Object.defineProperty(window, 'PushManager', {
        value: class PushManager {},
        configurable: true,
        writable: true,
      })

      const mod = await importFresh()
      const result = await mod.registerPushNotifications()
      expect(result).toBe(true)
    })
  })

  describe('scheduleWeatherAlertCheck', () => {
    it('planifie une verification apres 1 minute', async () => {
      const checkFn = vi.fn().mockResolvedValue(null)
      const mod = await importFresh()

      mod.scheduleWeatherAlertCheck(checkFn)

      expect(checkFn).not.toHaveBeenCalled()

      // Advance 1 minute
      vi.advanceTimersByTime(60 * 1000)
      // Allow async to resolve
      await vi.advanceTimersByTimeAsync(0)

      expect(checkFn).toHaveBeenCalledTimes(1)
    })

    it('planifie des verifications toutes les 30 minutes', async () => {
      const checkFn = vi.fn().mockResolvedValue(null)
      const mod = await importFresh()

      mod.scheduleWeatherAlertCheck(checkFn)

      // Advance 1 minute (first check)
      await vi.advanceTimersByTimeAsync(60 * 1000)
      expect(checkFn).toHaveBeenCalledTimes(1)

      // Advance 30 minutes (periodic check)
      await vi.advanceTimersByTimeAsync(30 * 60 * 1000)
      expect(checkFn).toHaveBeenCalledTimes(2)

      // Advance another 30 minutes
      await vi.advanceTimersByTimeAsync(30 * 60 * 1000)
      expect(checkFn).toHaveBeenCalledTimes(3)
    })
  })
})
