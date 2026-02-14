/**
 * Tests unitaires pour le service API
 *
 * Architecture: cookies HttpOnly (withCredentials: true)
 * - Le token d'auth est gere cote serveur via cookie HttpOnly
 * - Pas de sessionStorage/localStorage pour les tokens
 * - CSRF token gere en memoire via le service csrf.ts
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import type { InternalAxiosRequestConfig, AxiosHeaders } from 'axios'

// Mock des dependances AVANT import de api.ts
const mockEmitSessionExpired = vi.fn()
vi.mock('./authEvents', () => ({
  emitSessionExpired: mockEmitSessionExpired,
}))

const mockGetCsrfToken = vi.fn()
const mockRequiresCsrf = vi.fn()
const mockFetchCsrfToken = vi.fn()
vi.mock('./csrf', () => ({
  getCsrfToken: mockGetCsrfToken,
  requiresCsrf: mockRequiresCsrf,
  CSRF_HEADER: 'X-CSRF-Token',
  fetchCsrfToken: mockFetchCsrfToken,
}))

// Capture the interceptor callbacks
let requestInterceptor: ((config: InternalAxiosRequestConfig) => Promise<InternalAxiosRequestConfig>) | null = null
let responseSuccessInterceptor: ((response: unknown) => unknown) | null = null
let responseErrorInterceptor: ((error: unknown) => Promise<unknown>) | null = null

vi.mock('axios', () => {
  const mockAxios = {
    create: vi.fn(() => mockAxios),
    interceptors: {
      request: {
        use: vi.fn((onFulfilled: (config: InternalAxiosRequestConfig) => Promise<InternalAxiosRequestConfig>) => {
          requestInterceptor = onFulfilled
        }),
      },
      response: {
        use: vi.fn((onSuccess: (response: unknown) => unknown, onError: (error: unknown) => Promise<unknown>) => {
          responseSuccessInterceptor = onSuccess
          responseErrorInterceptor = onError
        }),
      },
    },
    defaults: { headers: { common: {} } },
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  }
  return { default: mockAxios }
})

function makeConfig(overrides: Partial<InternalAxiosRequestConfig> = {}): InternalAxiosRequestConfig {
  return {
    headers: {
      set: vi.fn(),
      get: vi.fn(),
      has: vi.fn(),
      delete: vi.fn(),
      clear: vi.fn(),
    } as unknown as AxiosHeaders,
    method: 'get',
    url: '',
    ...overrides,
  } as InternalAxiosRequestConfig
}

describe('api service', () => {
  beforeEach(async () => {
    vi.clearAllMocks()
    requestInterceptor = null
    responseSuccessInterceptor = null
    responseErrorInterceptor = null
    // Import the module to trigger interceptor registration
    await import('./api')
  })

  afterEach(() => {
    vi.resetModules()
  })

  it('cree une instance axios avec la bonne configuration', async () => {
    const axios = (await import('axios')).default
    expect(axios.create).toHaveBeenCalledWith({
      baseURL: expect.any(String),
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000,
      withCredentials: true,
    })
  })

  it('configure les intercepteurs request et response', async () => {
    const axios = (await import('axios')).default
    const mockInstance = axios.create()
    expect(mockInstance.interceptors.request.use).toHaveBeenCalled()
    expect(mockInstance.interceptors.response.use).toHaveBeenCalled()
  })
})

describe('Request interceptor - CSRF token injection', () => {
  beforeEach(async () => {
    vi.clearAllMocks()
    requestInterceptor = null
    responseSuccessInterceptor = null
    responseErrorInterceptor = null
    await import('./api')
  })

  afterEach(() => {
    vi.resetModules()
  })

  it('ajoute le token CSRF pour les methodes POST', async () => {
    mockRequiresCsrf.mockReturnValue(true)
    mockGetCsrfToken.mockReturnValue('test-csrf-token')

    const config = makeConfig({ method: 'post', url: '/api/chantiers' })
    const result = await requestInterceptor!(config)

    expect(mockRequiresCsrf).toHaveBeenCalledWith('post')
    expect(result.headers['X-CSRF-Token']).toBe('test-csrf-token')
  })

  it('ajoute le token CSRF pour les methodes PUT', async () => {
    mockRequiresCsrf.mockReturnValue(true)
    mockGetCsrfToken.mockReturnValue('test-csrf-token')

    const config = makeConfig({ method: 'put', url: '/api/chantiers/1' })
    const result = await requestInterceptor!(config)

    expect(result.headers['X-CSRF-Token']).toBe('test-csrf-token')
  })

  it('ajoute le token CSRF pour les methodes DELETE', async () => {
    mockRequiresCsrf.mockReturnValue(true)
    mockGetCsrfToken.mockReturnValue('test-csrf-token')

    const config = makeConfig({ method: 'delete', url: '/api/chantiers/1' })
    const result = await requestInterceptor!(config)

    expect(result.headers['X-CSRF-Token']).toBe('test-csrf-token')
  })

  it('ajoute le token CSRF pour les methodes PATCH', async () => {
    mockRequiresCsrf.mockReturnValue(true)
    mockGetCsrfToken.mockReturnValue('test-csrf-token')

    const config = makeConfig({ method: 'patch', url: '/api/chantiers/1' })
    const result = await requestInterceptor!(config)

    expect(result.headers['X-CSRF-Token']).toBe('test-csrf-token')
  })

  it('ne modifie pas le header CSRF pour les methodes GET', async () => {
    mockRequiresCsrf.mockReturnValue(false)

    const config = makeConfig({ method: 'get', url: '/api/chantiers' })
    const result = await requestInterceptor!(config)

    expect(result.headers['X-CSRF-Token']).toBeUndefined()
  })

  it('skip le CSRF pour /api/auth/login', async () => {
    mockRequiresCsrf.mockReturnValue(true)
    mockGetCsrfToken.mockReturnValue('test-csrf-token')

    const config = makeConfig({ method: 'post', url: '/api/auth/login' })
    const result = await requestInterceptor!(config)

    expect(result.headers['X-CSRF-Token']).toBeUndefined()
  })

  it('skip le CSRF pour /api/auth/csrf-token', async () => {
    mockRequiresCsrf.mockReturnValue(true)
    mockGetCsrfToken.mockReturnValue('test-csrf-token')

    const config = makeConfig({ method: 'post', url: '/api/auth/csrf-token' })
    const result = await requestInterceptor!(config)

    expect(result.headers['X-CSRF-Token']).toBeUndefined()
  })

  it('fetch le CSRF token si aucun token en memoire', async () => {
    mockRequiresCsrf.mockReturnValue(true)
    mockGetCsrfToken.mockReturnValue(null)
    mockFetchCsrfToken.mockResolvedValue('fetched-csrf-token')

    const config = makeConfig({ method: 'post', url: '/api/chantiers' })
    const result = await requestInterceptor!(config)

    expect(mockFetchCsrfToken).toHaveBeenCalled()
    expect(result.headers['X-CSRF-Token']).toBe('fetched-csrf-token')
  })

  it('ne fait pas de fetch CSRF si le token est deja en memoire', async () => {
    mockRequiresCsrf.mockReturnValue(true)
    mockGetCsrfToken.mockReturnValue('existing-token')

    const config = makeConfig({ method: 'post', url: '/api/chantiers' })
    await requestInterceptor!(config)

    expect(mockFetchCsrfToken).not.toHaveBeenCalled()
  })

  it('gere le cas ou config.method est undefined', async () => {
    mockRequiresCsrf.mockReturnValue(false)

    const config = makeConfig({ method: undefined, url: '/api/chantiers' })
    const result = await requestInterceptor!(config)

    expect(mockRequiresCsrf).not.toHaveBeenCalled()
    expect(result.headers['X-CSRF-Token']).toBeUndefined()
  })
})

describe('Response interceptor - success', () => {
  beforeEach(async () => {
    vi.clearAllMocks()
    requestInterceptor = null
    responseSuccessInterceptor = null
    responseErrorInterceptor = null
    await import('./api')
  })

  afterEach(() => {
    vi.resetModules()
  })

  it('passe la reponse sans modification', () => {
    const response = { data: { ok: true }, status: 200 }
    const result = responseSuccessInterceptor!(response)
    expect(result).toBe(response)
  })
})

describe('Response interceptor - 401 handling', () => {
  beforeEach(async () => {
    vi.clearAllMocks()
    mockEmitSessionExpired.mockClear()
    requestInterceptor = null
    responseSuccessInterceptor = null
    responseErrorInterceptor = null
    await import('./api')
  })

  afterEach(() => {
    vi.resetModules()
  })

  it('ne declenche pas emitSessionExpired sur un seul 401 (non-auth URL)', async () => {
    const error = {
      response: { status: 401 },
      config: { url: '/api/chantiers' },
    }

    await expect(responseErrorInterceptor!(error)).rejects.toBe(error)
    expect(mockEmitSessionExpired).not.toHaveBeenCalled()
  })

  it('declenche emitSessionExpired apres 2 erreurs 401 consecutives (non-auth)', async () => {
    // Reset consecutive counter by sending a success first
    responseSuccessInterceptor!({ data: {}, status: 200 })

    const error = {
      response: { status: 401 },
      config: { url: '/api/chantiers' },
    }

    // First 401
    await expect(responseErrorInterceptor!(error)).rejects.toBe(error)
    expect(mockEmitSessionExpired).not.toHaveBeenCalled()

    // Second 401 -> triggers session expired
    await expect(responseErrorInterceptor!(error)).rejects.toBe(error)
    expect(mockEmitSessionExpired).toHaveBeenCalledTimes(1)
  })

  it('ne declenche pas emitSessionExpired pour 401 sur /api/auth/me', async () => {
    // Reset counter
    responseSuccessInterceptor!({ data: {}, status: 200 })

    const error = {
      response: { status: 401 },
      config: { url: '/api/auth/me' },
    }

    await expect(responseErrorInterceptor!(error)).rejects.toBe(error)
    await expect(responseErrorInterceptor!(error)).rejects.toBe(error)
    await expect(responseErrorInterceptor!(error)).rejects.toBe(error)
    expect(mockEmitSessionExpired).not.toHaveBeenCalled()
  })

  it('ne declenche pas emitSessionExpired pour 401 sur /api/auth/login', async () => {
    responseSuccessInterceptor!({ data: {}, status: 200 })

    const error = {
      response: { status: 401 },
      config: { url: '/api/auth/login' },
    }

    await expect(responseErrorInterceptor!(error)).rejects.toBe(error)
    await expect(responseErrorInterceptor!(error)).rejects.toBe(error)
    expect(mockEmitSessionExpired).not.toHaveBeenCalled()
  })

  it('ne declenche pas emitSessionExpired pour 401 sur /api/auth/logout', async () => {
    responseSuccessInterceptor!({ data: {}, status: 200 })

    const error = {
      response: { status: 401 },
      config: { url: '/api/auth/logout' },
    }

    await expect(responseErrorInterceptor!(error)).rejects.toBe(error)
    await expect(responseErrorInterceptor!(error)).rejects.toBe(error)
    expect(mockEmitSessionExpired).not.toHaveBeenCalled()
  })

  it('ne declenche pas emitSessionExpired pour 401 sur /api/auth/csrf-token', async () => {
    responseSuccessInterceptor!({ data: {}, status: 200 })

    const error = {
      response: { status: 401 },
      config: { url: '/api/auth/csrf-token' },
    }

    await expect(responseErrorInterceptor!(error)).rejects.toBe(error)
    await expect(responseErrorInterceptor!(error)).rejects.toBe(error)
    expect(mockEmitSessionExpired).not.toHaveBeenCalled()
  })

  it('reset le compteur 401 sur une reponse reussie', async () => {
    // First 401
    const error = {
      response: { status: 401 },
      config: { url: '/api/chantiers' },
    }
    await expect(responseErrorInterceptor!(error)).rejects.toBe(error)

    // Successful response resets counter
    responseSuccessInterceptor!({ data: {}, status: 200 })

    // Another 401 - should NOT trigger because counter was reset
    await expect(responseErrorInterceptor!(error)).rejects.toBe(error)
    expect(mockEmitSessionExpired).not.toHaveBeenCalled()
  })

  it('rejette toujours l erreur meme pour les erreurs non-401', async () => {
    const error = {
      response: { status: 403 },
      config: { url: '/api/chantiers' },
    }
    await expect(responseErrorInterceptor!(error)).rejects.toBe(error)
    expect(mockEmitSessionExpired).not.toHaveBeenCalled()
  })

  it('rejette les erreurs reseau (sans response)', async () => {
    const error = {
      message: 'Network Error',
      config: { url: '/api/chantiers' },
    }
    await expect(responseErrorInterceptor!(error)).rejects.toBe(error)
    expect(mockEmitSessionExpired).not.toHaveBeenCalled()
  })

  it('gere les erreurs sans config', async () => {
    const error = {
      response: { status: 401 },
    }
    // No config.url -> falls into auth URL check with empty string
    await expect(responseErrorInterceptor!(error)).rejects.toBe(error)
  })
})

describe('HttpOnly cookie authentication', () => {
  it('ne stocke aucun token dans sessionStorage ou localStorage', () => {
    expect(sessionStorage.getItem('access_token')).toBeFalsy()
    expect(localStorage.getItem('access_token')).toBeFalsy()
  })
})
