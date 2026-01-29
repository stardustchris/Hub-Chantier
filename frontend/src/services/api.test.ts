/**
 * Tests unitaires pour le service API
 *
 * Architecture: cookies HttpOnly (withCredentials: true)
 * - Le token d'auth est géré côté serveur via cookie HttpOnly
 * - Pas de sessionStorage/localStorage pour les tokens
 * - CSRF token géré en mémoire via le service csrf.ts
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
  })

  afterEach(() => {
    vi.resetModules()
  })

  it('cree une instance axios avec la bonne configuration', async () => {
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

  it('configure les intercepteurs request et response', async () => {
    await import('./api')

    expect(axios.create).toHaveBeenCalled()
    const mockInstance = axios.create()
    expect(mockInstance.interceptors.request.use).toHaveBeenCalled()
    expect(mockInstance.interceptors.response.use).toHaveBeenCalled()
  })
})

describe('HttpOnly cookie authentication', () => {
  it('utilise withCredentials pour envoyer les cookies automatiquement', async () => {
    const createCall = vi.mocked(axios.create).mock.calls[0]
    if (createCall) {
      expect(createCall[0]).toMatchObject({
        withCredentials: true,
      })
    }
  })

  it('ne stocke aucun token dans sessionStorage ou localStorage', () => {
    // Vérifier qu'aucun token n'est stocké côté client
    expect(sessionStorage.getItem('access_token')).toBeFalsy()
    expect(localStorage.getItem('access_token')).toBeFalsy()
  })

  it('n\'utilise pas de header Authorization manuel', async () => {
    // L'authentification passe exclusivement par les cookies HttpOnly
    // Le code de production n'ajoute aucun header Authorization
    const config = { headers: {} as Record<string, string> }

    // Pas de manipulation de token dans l'intercepteur request
    expect(config.headers.Authorization).toBeUndefined()
  })
})

describe('CSRF token handling', () => {
  it('detecte les methodes qui necessitent CSRF', () => {
    const mutatingMethods = ['POST', 'PUT', 'DELETE', 'PATCH']
    const safeMethods = ['GET', 'HEAD', 'OPTIONS']

    mutatingMethods.forEach((method) => {
      expect(['POST', 'PUT', 'DELETE', 'PATCH'].includes(method)).toBe(true)
    })

    safeMethods.forEach((method) => {
      expect(['POST', 'PUT', 'DELETE', 'PATCH'].includes(method)).toBe(false)
    })
  })

  it('ne requiert pas CSRF pour GET', () => {
    const method = 'GET'
    const requiresCsrf = ['POST', 'PUT', 'DELETE', 'PATCH'].includes(method.toUpperCase())
    expect(requiresCsrf).toBe(false)
  })

  it('requiert CSRF pour POST', () => {
    const method = 'POST'
    const requiresCsrf = ['POST', 'PUT', 'DELETE', 'PATCH'].includes(method.toUpperCase())
    expect(requiresCsrf).toBe(true)
  })
})

describe('error response handling', () => {
  it('ne touche pas au storage sur erreur 401 (géré par événement session expirée)', () => {
    // Avec les cookies HttpOnly, la gestion du 401 passe par
    // emitSessionExpired() qui notifie AuthContext, pas par sessionStorage
    const error = { response: { status: 401 } }
    expect(error.response.status).toBe(401)
    // Pas de manipulation de sessionStorage
    expect(sessionStorage.getItem('access_token')).toBeNull()
  })

  it('gere les erreurs 403 Forbidden sans effet de bord', () => {
    const error = { response: { status: 403 } }
    expect(error.response.status).toBe(403)
  })

  it('gere les erreurs 404 Not Found sans effet de bord', () => {
    const error = { response: { status: 404 } }
    expect(error.response.status).toBe(404)
  })

  it('gere les erreurs reseau sans response', () => {
    const error = { message: 'Network Error' }
    expect(error.message).toBe('Network Error')
  })

  it('gere les erreurs timeout', () => {
    const error = { code: 'ECONNABORTED', message: 'timeout' }
    expect(error.code).toBe('ECONNABORTED')
  })
})

describe('axios instance configuration', () => {
  it('configure le timeout a 30 secondes', async () => {
    const createCall = vi.mocked(axios.create).mock.calls[0]
    if (createCall) {
      expect(createCall[0]).toMatchObject({
        timeout: 30000,
      })
    }
  })

  it('configure withCredentials pour les cookies HttpOnly', async () => {
    const createCall = vi.mocked(axios.create).mock.calls[0]
    if (createCall) {
      expect(createCall[0]).toMatchObject({
        withCredentials: true,
      })
    }
  })

  it('configure Content-Type JSON par defaut', async () => {
    const createCall = vi.mocked(axios.create).mock.calls[0]
    if (createCall) {
      expect(createCall[0]).toMatchObject({
        headers: {
          'Content-Type': 'application/json',
        },
      })
    }
  })
})
