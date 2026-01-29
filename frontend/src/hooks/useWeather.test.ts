// @vitest-environment jsdom
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'

// Mock dependencies before importing the hook
vi.mock('../services/weather', () => ({
  weatherService: {
    getCurrentPosition: vi.fn(),
    fetchWeather: vi.fn(),
  },
}))

vi.mock('../services/logger', () => ({
  logger: {
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
    debug: vi.fn(),
  },
}))

import { weatherService } from '../services/weather'

const mockGetCurrentPosition = vi.mocked(weatherService.getCurrentPosition)
const mockFetchWeather = vi.mocked(weatherService.fetchWeather)

const sampleWeatherData = {
  location: 'Paris',
  temperature: 15,
  condition: 'sunny' as const,
  conditionCode: 0,
  wind: 10,
  windDirection: 'N',
  rainProbability: 5,
  humidity: 60,
  minTemp: 10,
  maxTemp: 20,
  uvIndex: 3,
  sunrise: '07:30',
  sunset: '19:00',
}

describe('useWeather', () => {
  beforeEach(async () => {
    vi.clearAllMocks()
    // Reset the module to clear module-level cache between tests
    vi.resetModules()
  })

  async function getHook() {
    // Re-import fresh module each time to clear module-level cache
    const mod = await import('./useWeather')
    return mod.useWeather
  }

  it('should return initial loading state', async () => {
    // Make the fetch hang so we stay in loading state
    mockGetCurrentPosition.mockReturnValue(new Promise(() => {}))
    mockFetchWeather.mockReturnValue(new Promise(() => {}))

    const useWeather = await getHook()
    const { result } = renderHook(() => useWeather())

    expect(result.current.isLoading).toBe(true)
    expect(result.current.error).toBeNull()
  })

  it('should load weather data successfully with geolocation', async () => {
    mockGetCurrentPosition.mockResolvedValue({
      latitude: 48.8566,
      longitude: 2.3522,
      city: 'Paris',
    })
    mockFetchWeather.mockResolvedValue(sampleWeatherData)

    const useWeather = await getHook()
    const { result } = renderHook(() => useWeather())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(result.current.weather).toEqual(sampleWeatherData)
    expect(result.current.error).toBeNull()
    expect(result.current.locationSource).toBe('geolocation')
  })

  it('should set locationSource to fallback when position is Chambery default', async () => {
    mockGetCurrentPosition.mockResolvedValue({
      latitude: 45.5646,
      longitude: 5.9178,
      city: 'Chambéry',
    })
    mockFetchWeather.mockResolvedValue({
      ...sampleWeatherData,
      location: 'Chambéry',
    })

    const useWeather = await getHook()
    const { result } = renderHook(() => useWeather())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(result.current.locationSource).toBe('fallback')
  })

  it('should set locationSource to fallback when geolocation fails', async () => {
    mockGetCurrentPosition.mockRejectedValue(new Error('Geolocation denied'))
    mockFetchWeather.mockResolvedValue(sampleWeatherData)

    const useWeather = await getHook()
    const { result } = renderHook(() => useWeather())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(result.current.locationSource).toBe('fallback')
    expect(result.current.weather).toEqual(sampleWeatherData)
  })

  it('should handle fetchWeather error with fallback data', async () => {
    mockGetCurrentPosition.mockResolvedValue({
      latitude: 48.8566,
      longitude: 2.3522,
      city: 'Paris',
    })
    mockFetchWeather.mockRejectedValue(new Error('Network error'))

    const useWeather = await getHook()
    const { result } = renderHook(() => useWeather())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(result.current.error).toBe('Network error')
    // Should have fallback weather data
    expect(result.current.weather).not.toBeNull()
    expect(result.current.weather?.location).toBe('Indisponible')
    expect(result.current.weather?.temperature).toBe(0)
  })

  it('should return alert from weather data', async () => {
    const weatherWithAlert = {
      ...sampleWeatherData,
      alert: {
        type: 'vigilance_jaune' as const,
        title: 'Vent fort',
        description: 'Rafales attendues',
        startTime: '2026-01-29T08:00:00',
        phenomena: ['vent'],
      },
    }
    mockGetCurrentPosition.mockResolvedValue({
      latitude: 48.8566,
      longitude: 2.3522,
      city: 'Paris',
    })
    mockFetchWeather.mockResolvedValue(weatherWithAlert)

    const useWeather = await getHook()
    const { result } = renderHook(() => useWeather())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(result.current.alert).toEqual(weatherWithAlert.alert)
  })

  it('should return null alert when no alert in weather data', async () => {
    mockGetCurrentPosition.mockResolvedValue({
      latitude: 48.8566,
      longitude: 2.3522,
      city: 'Paris',
    })
    mockFetchWeather.mockResolvedValue(sampleWeatherData)

    const useWeather = await getHook()
    const { result } = renderHook(() => useWeather())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(result.current.alert).toBeNull()
  })

  it('should expose refresh function that reloads weather', async () => {
    mockGetCurrentPosition.mockResolvedValue({
      latitude: 48.8566,
      longitude: 2.3522,
      city: 'Paris',
    })
    mockFetchWeather.mockResolvedValue(sampleWeatherData)

    const useWeather = await getHook()
    const { result } = renderHook(() => useWeather())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    // Clear mocks to track refresh calls
    mockGetCurrentPosition.mockClear()
    mockFetchWeather.mockClear()

    const updatedWeather = { ...sampleWeatherData, temperature: 20 }
    mockGetCurrentPosition.mockResolvedValue({
      latitude: 48.8566,
      longitude: 2.3522,
      city: 'Paris',
    })
    mockFetchWeather.mockResolvedValue(updatedWeather)

    await act(async () => {
      await result.current.refresh()
    })

    expect(mockFetchWeather).toHaveBeenCalled()
  })

  it('should expose setManualLocation function', async () => {
    mockGetCurrentPosition.mockResolvedValue({
      latitude: 48.8566,
      longitude: 2.3522,
      city: 'Paris',
    })
    mockFetchWeather.mockResolvedValue(sampleWeatherData)

    const useWeather = await getHook()
    const { result } = renderHook(() => useWeather())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(typeof result.current.setManualLocation).toBe('function')

    const lyonWeather = { ...sampleWeatherData, location: 'Lyon' }
    mockFetchWeather.mockResolvedValue(lyonWeather)

    act(() => {
      result.current.setManualLocation(45.7640, 4.8357, 'Lyon')
    })

    await waitFor(() => {
      expect(result.current.locationSource).toBe('manual')
    })
  })
})
