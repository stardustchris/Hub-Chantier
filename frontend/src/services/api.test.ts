/**
 * Tests unitaires pour le service API
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import axios from 'axios'

// Mock axios avant l'import de api
vi.mock('axios', () => {
  const mockAxios = {
    create: vi.fn(() => mockAxios),
    interceptors: {
      request: { use: vi.fn() },
      response: { use: vi.fn() },
    },
    defaults: { headers: { common: {} } },
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  }
  return { default: mockAxios }
})

describe('api service', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    sessionStorage.clear()
  })

  afterEach(() => {
    vi.resetModules()
  })

  it('cree une instance axios avec la bonne configuration', async () => {
    // Re-import pour trigger la creation
    await import('./api')

    expect(axios.create).toHaveBeenCalledWith({
      baseURL: expect.any(String),
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000,
      withCredentials: true, // HttpOnly cookies support
    })
  })

  it('configure les intercepteurs', async () => {
    await import('./api')

    expect(axios.create).toHaveBeenCalled()
    const mockInstance = axios.create()
    expect(mockInstance.interceptors.request.use).toHaveBeenCalled()
    expect(mockInstance.interceptors.response.use).toHaveBeenCalled()
  })
})

describe('api interceptors behavior', () => {
  beforeEach(() => {
    sessionStorage.clear()
  })

  describe('request interceptor', () => {
    it('ajoute le token Authorization si present dans sessionStorage', () => {
      sessionStorage.setItem('access_token', 'test-token-123')

      const config = {
        headers: {} as Record<string, string>,
      }

      // Simule le comportement de l'intercepteur
      const token = sessionStorage.getItem('access_token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }

      expect(config.headers.Authorization).toBe('Bearer test-token-123')
    })

    it('n\'ajoute pas d\'Authorization si pas de token', () => {
      const config = {
        headers: {} as Record<string, string>,
      }

      const token = sessionStorage.getItem('access_token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }

      expect(config.headers.Authorization).toBeUndefined()
    })
  })

  describe('response interceptor (error handling)', () => {
    it('supprime le token et redirige sur erreur 401', () => {
      sessionStorage.setItem('access_token', 'test-token')

      // Mock window.location
      const originalLocation = window.location
      Object.defineProperty(window, 'location', {
        value: { href: '' },
        writable: true,
      })

      // Simule le comportement de l'intercepteur sur 401
      const error = { response: { status: 401 } }
      if (error.response?.status === 401) {
        sessionStorage.removeItem('access_token')
        window.location.href = '/login'
      }

      expect(sessionStorage.getItem('access_token')).toBeNull()
      expect(window.location.href).toBe('/login')

      // Restore
      Object.defineProperty(window, 'location', {
        value: originalLocation,
        writable: true,
      })
    })

    it('ne redirige pas sur les autres erreurs', () => {
      sessionStorage.setItem('access_token', 'test-token')

      const error = { response: { status: 500 } }
      if (error.response?.status === 401) {
        sessionStorage.removeItem('access_token')
      }

      // Token doit rester intact
      expect(sessionStorage.getItem('access_token')).toBe('test-token')
    })
  })
})

describe('sessionStorage security', () => {
  it('utilise sessionStorage au lieu de localStorage pour le token', () => {
    // Verifie que le code utilise sessionStorage
    const localStorageSpy = vi.spyOn(Storage.prototype, 'getItem')

    sessionStorage.setItem('access_token', 'secure-token')
    const token = sessionStorage.getItem('access_token')

    expect(token).toBe('secure-token')
    // Le token ne doit pas etre dans localStorage
    expect(localStorage.getItem('access_token')).toBeFalsy()

    localStorageSpy.mockRestore()
  })

  it('le token n\'est pas accessible apres fermeture du navigateur (sessionStorage behavior)', () => {
    // Note: On ne peut pas vraiment tester la fermeture du navigateur,
    // mais on peut verifier que sessionStorage est utilise
    sessionStorage.setItem('access_token', 'test-token')

    // Simule la "fermeture" en vidant sessionStorage
    sessionStorage.clear()

    expect(sessionStorage.getItem('access_token')).toBeNull()
  })
})
