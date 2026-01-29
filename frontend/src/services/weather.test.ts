/**
 * Tests unitaires pour le service weather
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'

// Mock des dependances
vi.mock('./logger', () => ({
  logger: {
    warn: vi.fn(),
    info: vi.fn(),
    error: vi.fn(),
    debug: vi.fn(),
  },
}))

vi.mock('./consent', () => ({
  consentService: {
    hasConsent: vi.fn(),
  },
}))

import { consentService } from './consent'
import { getCurrentPosition, fetchWeather, fetchHourlyForecast, fetchDailyForecast } from './weather'

// Mock global fetch
const mockFetch = vi.fn()
global.fetch = mockFetch

describe('weather service', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockFetch.mockReset()
  })

  describe('getCurrentPosition', () => {
    it('rejette si pas de consentement geolocalisation', async () => {
      vi.mocked(consentService.hasConsent).mockResolvedValue(false)

      await expect(getCurrentPosition()).rejects.toThrow('Consentement géolocalisation requis')
    })

    it('rejette si geolocalisation non supportee', async () => {
      vi.mocked(consentService.hasConsent).mockResolvedValue(true)

      const originalGeo = navigator.geolocation
      Object.defineProperty(navigator, 'geolocation', {
        value: undefined,
        configurable: true,
      })

      await expect(getCurrentPosition()).rejects.toThrow('Géolocalisation non supportée')

      Object.defineProperty(navigator, 'geolocation', {
        value: originalGeo,
        configurable: true,
      })
    })

    it('retourne la position avec reverse geocoding', async () => {
      vi.mocked(consentService.hasConsent).mockResolvedValue(true)

      const mockGeolocation = {
        getCurrentPosition: vi.fn((success) => {
          success({
            coords: { latitude: 45.5, longitude: 5.9 },
          })
        }),
      }
      Object.defineProperty(navigator, 'geolocation', {
        value: mockGeolocation,
        configurable: true,
      })

      mockFetch.mockResolvedValue({
        json: () => Promise.resolve({
          address: { city: 'Chambery', postcode: '73000' },
        }),
      })

      const result = await getCurrentPosition()

      expect(result.latitude).toBe(45.5)
      expect(result.longitude).toBe(5.9)
      expect(result.city).toBe('Chambery')
      expect(result.postalCode).toBe('73000')
    })

    it('retourne position par defaut si reverse geocoding echoue', async () => {
      vi.mocked(consentService.hasConsent).mockResolvedValue(true)

      const mockGeolocation = {
        getCurrentPosition: vi.fn((success) => {
          success({
            coords: { latitude: 48.8, longitude: 2.3 },
          })
        }),
      }
      Object.defineProperty(navigator, 'geolocation', {
        value: mockGeolocation,
        configurable: true,
      })

      mockFetch.mockRejectedValue(new Error('Network error'))

      const result = await getCurrentPosition()

      expect(result.latitude).toBe(48.8)
      expect(result.longitude).toBe(2.3)
      expect(result.city).toBe('Position actuelle')
    })

    it('fallback sur Chambery si geolocalisation refusee', async () => {
      vi.mocked(consentService.hasConsent).mockResolvedValue(true)

      const mockGeolocation = {
        getCurrentPosition: vi.fn((_success, error) => {
          error({ message: 'User denied Geolocation' })
        }),
      }
      Object.defineProperty(navigator, 'geolocation', {
        value: mockGeolocation,
        configurable: true,
      })

      const result = await getCurrentPosition()

      expect(result.latitude).toBe(45.5646)
      expect(result.longitude).toBe(5.9178)
      expect(result.city).toBe('Chambéry')
      expect(result.postalCode).toBe('73000')
    })
  })

  describe('fetchWeather', () => {
    const mockPosition = { latitude: 45.5, longitude: 5.9, city: 'Chambery', postalCode: '73000' }

    it('retourne les donnees meteo formatees', async () => {
      const mockApiResponse = {
        current: {
          temperature_2m: 18.3,
          relative_humidity_2m: 65,
          weather_code: 0,
          wind_speed_10m: 12.5,
          wind_direction_10m: 180,
        },
        daily: {
          temperature_2m_max: [22],
          temperature_2m_min: [14],
          precipitation_probability_max: [20],
          uv_index_max: [5],
          sunrise: ['2026-01-29T07:30'],
          sunset: ['2026-01-29T18:00'],
          weather_code: [0],
        },
      }

      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockApiResponse),
      })

      const result = await fetchWeather(mockPosition)

      expect(result.location).toBe('Chambery')
      expect(result.temperature).toBe(18)
      expect(result.condition).toBe('sunny')
      expect(result.wind).toBe(13)
      expect(result.windDirection).toBe('S')
      expect(result.humidity).toBe(65)
      expect(result.minTemp).toBe(14)
      expect(result.maxTemp).toBe(22)
      expect(result.sunrise).toBe('07:30')
      expect(result.sunset).toBe('18:00')
      expect(result.coordinates).toEqual({ latitude: 45.5, longitude: 5.9 })
      expect(result.postalCode).toBe('73000')
      expect(result.bulletin).toBeDefined()
    })

    it('leve une erreur si API echoue', async () => {
      mockFetch.mockResolvedValue({
        ok: false,
        status: 500,
      })

      await expect(fetchWeather(mockPosition)).rejects.toThrow('Erreur API météo: 500')
    })

    it('genere une alerte vent fort (>80 km/h)', async () => {
      const mockApiResponse = {
        current: {
          temperature_2m: 10,
          relative_humidity_2m: 80,
          weather_code: 3,
          wind_speed_10m: 85,
          wind_direction_10m: 270,
        },
        daily: {
          temperature_2m_max: [15],
          temperature_2m_min: [5],
          precipitation_probability_max: [40],
          uv_index_max: [2],
          sunrise: ['2026-01-29T07:30'],
          sunset: ['2026-01-29T18:00'],
          weather_code: [3],
        },
      }

      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockApiResponse),
      })

      const result = await fetchWeather(mockPosition)

      expect(result.alert).toBeDefined()
      expect(result.alert?.type).toBe('vigilance_orange')
      expect(result.alert?.phenomena).toContain('vent')
    })

    it('genere une alerte orage', async () => {
      const mockApiResponse = {
        current: {
          temperature_2m: 25,
          relative_humidity_2m: 90,
          weather_code: 95,
          wind_speed_10m: 40,
          wind_direction_10m: 90,
        },
        daily: {
          temperature_2m_max: [30],
          temperature_2m_min: [20],
          precipitation_probability_max: [90],
          uv_index_max: [3],
          sunrise: ['2026-01-29T06:30'],
          sunset: ['2026-01-29T20:00'],
          weather_code: [95],
        },
      }

      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockApiResponse),
      })

      const result = await fetchWeather(mockPosition)

      expect(result.condition).toBe('stormy')
      expect(result.alert).toBeDefined()
      expect(result.alert?.type).toBe('vigilance_orange')
      expect(result.alert?.phenomena).toContain('orages')
    })

    it('genere une alerte canicule (>35C)', async () => {
      const mockApiResponse = {
        current: {
          temperature_2m: 35,
          relative_humidity_2m: 30,
          weather_code: 0,
          wind_speed_10m: 5,
          wind_direction_10m: 0,
        },
        daily: {
          temperature_2m_max: [38],
          temperature_2m_min: [25],
          precipitation_probability_max: [0],
          uv_index_max: [9],
          sunrise: ['2026-07-15T06:00'],
          sunset: ['2026-07-15T21:30'],
          weather_code: [0],
        },
      }

      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockApiResponse),
      })

      const result = await fetchWeather(mockPosition)

      expect(result.alert).toBeDefined()
      expect(result.alert?.type).toBe('vigilance_orange')
      expect(result.alert?.phenomena).toContain('canicule')
    })

    it('pas d alerte pour conditions normales', async () => {
      const mockApiResponse = {
        current: {
          temperature_2m: 20,
          relative_humidity_2m: 50,
          weather_code: 2,
          wind_speed_10m: 15,
          wind_direction_10m: 45,
        },
        daily: {
          temperature_2m_max: [25],
          temperature_2m_min: [15],
          precipitation_probability_max: [10],
          uv_index_max: [4],
          sunrise: ['2026-05-15T06:30'],
          sunset: ['2026-05-15T20:30'],
          weather_code: [2],
        },
      }

      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockApiResponse),
      })

      const result = await fetchWeather(mockPosition)

      expect(result.alert).toBeUndefined()
    })
  })

  describe('fetchHourlyForecast', () => {
    const mockPosition = { latitude: 45.5, longitude: 5.9, city: 'Chambery' }

    it('retourne les previsions horaires', async () => {
      const hours = Array.from({ length: 24 }, (_, i) => ({
        time: `2026-01-29T${String(i).padStart(2, '0')}:00`,
        temp: 10 + i,
        code: 0,
        precip: 0,
      }))

      const mockApiResponse = {
        hourly: {
          time: hours.map((h) => h.time),
          temperature_2m: hours.map((h) => h.temp),
          weather_code: hours.map((h) => h.code),
          precipitation_probability: hours.map((h) => h.precip),
        },
      }

      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockApiResponse),
      })

      const result = await fetchHourlyForecast(mockPosition)

      expect(Array.isArray(result)).toBe(true)
      // Should return up to 12 hours from current hour
      expect(result.length).toBeLessThanOrEqual(12)
      if (result.length > 0) {
        expect(result[0]).toHaveProperty('time')
        expect(result[0]).toHaveProperty('temperature')
        expect(result[0]).toHaveProperty('condition')
        expect(result[0]).toHaveProperty('rainProbability')
      }
    })
  })

  describe('fetchDailyForecast', () => {
    const mockPosition = { latitude: 45.5, longitude: 5.9, city: 'Chambery' }

    it('retourne les previsions sur 7 jours', async () => {
      const mockApiResponse = {
        daily: {
          time: [
            '2026-01-29', '2026-01-30', '2026-01-31',
            '2026-02-01', '2026-02-02', '2026-02-03', '2026-02-04',
          ],
          temperature_2m_max: [10, 12, 8, 15, 14, 11, 9],
          temperature_2m_min: [2, 4, 1, 6, 5, 3, 1],
          weather_code: [0, 2, 61, 0, 3, 71, 45],
          precipitation_probability_max: [0, 10, 80, 5, 20, 60, 30],
        },
      }

      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockApiResponse),
      })

      const result = await fetchDailyForecast(mockPosition)

      expect(result).toHaveLength(7)
      expect(result[0].dayName).toBe("Aujourd'hui")
      expect(result[0]).toHaveProperty('date')
      expect(result[0]).toHaveProperty('minTemp')
      expect(result[0]).toHaveProperty('maxTemp')
      expect(result[0]).toHaveProperty('condition')
      expect(result[0]).toHaveProperty('rainProbability')
    })
  })
})
