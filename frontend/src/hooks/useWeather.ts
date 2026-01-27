/**
 * useWeather - Hook pour charger les données météo réelles
 * Utilise la géolocalisation du device et l'API Open-Meteo
 */

import { useState, useEffect, useCallback } from 'react'
import { weatherService, type WeatherData, type WeatherAlert } from '../services/weather'
import { logger } from '../services/logger'

export interface UseWeatherReturn {
  /** Données météo actuelles */
  weather: WeatherData | null
  /** Alerte météo si présente */
  alert: WeatherAlert | null
  /** Chargement en cours */
  isLoading: boolean
  /** Erreur éventuelle */
  error: string | null
  /** Position utilisée (géoloc ou fallback) */
  locationSource: 'geolocation' | 'fallback' | 'manual'
  /** Recharger les données */
  refresh: () => Promise<void>
  /** Définir une position manuelle */
  setManualLocation: (lat: number, lon: number, city: string) => void
}

/** Cache des données météo en mémoire */
let weatherCache: {
  data: WeatherData | null
  timestamp: number
} = {
  data: null,
  timestamp: 0,
}

/** Durée de cache: 15 minutes */
const CACHE_DURATION = 15 * 60 * 1000

export function useWeather(): UseWeatherReturn {
  const [weather, setWeather] = useState<WeatherData | null>(weatherCache.data)
  const [isLoading, setIsLoading] = useState(!weatherCache.data)
  const [error, setError] = useState<string | null>(null)
  const [locationSource, setLocationSource] = useState<'geolocation' | 'fallback' | 'manual'>('geolocation')
  const [manualPosition, setManualPosition] = useState<{ lat: number; lon: number; city: string } | null>(null)

  const loadWeather = useCallback(async (force = false) => {
    // Vérifier le cache
    const now = Date.now()
    if (!force && weatherCache.data && (now - weatherCache.timestamp) < CACHE_DURATION) {
      setWeather(weatherCache.data)
      setIsLoading(false)
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      let position = undefined

      // Utiliser la position manuelle si définie
      if (manualPosition) {
        position = {
          latitude: manualPosition.lat,
          longitude: manualPosition.lon,
          city: manualPosition.city,
        }
        setLocationSource('manual')
      } else {
        // Obtenir la position par géolocalisation
        try {
          position = await weatherService.getCurrentPosition()
          // Si on a reçu la position de fallback (Chambéry), le signaler
          if (position.city === 'Chambéry' && position.latitude === 45.5646) {
            setLocationSource('fallback')
          } else {
            setLocationSource('geolocation')
          }
        } catch {
          setLocationSource('fallback')
        }
      }

      // Récupérer les données météo
      const data = await weatherService.fetchWeather(position)

      // Mettre à jour le cache
      weatherCache = {
        data,
        timestamp: now,
      }

      setWeather(data)
      logger.info('Météo chargée', { location: data.location, temp: data.temperature })
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erreur météo'
      logger.error('Erreur chargement météo', err)
      setError(message)

      // En cas d'erreur, utiliser des données fallback
      if (!weather) {
        setWeather({
          location: 'Indisponible',
          temperature: 0,
          condition: 'cloudy',
          conditionCode: 3,
          wind: 0,
          windDirection: 'N',
          rainProbability: 0,
          humidity: 0,
          minTemp: 0,
          maxTemp: 0,
          uvIndex: 0,
          sunrise: '07:00',
          sunset: '19:00',
        })
      }
    } finally {
      setIsLoading(false)
    }
  }, [manualPosition, weather])

  // Charger la météo au montage
  useEffect(() => {
    loadWeather()
  }, [loadWeather])

  // Rafraîchir toutes les 15 minutes
  useEffect(() => {
    const interval = setInterval(() => {
      loadWeather()
    }, CACHE_DURATION)

    return () => clearInterval(interval)
  }, [loadWeather])

  const setManualLocation = useCallback((lat: number, lon: number, city: string) => {
    setManualPosition({ lat, lon, city })
    // Invalider le cache pour forcer le rechargement
    weatherCache.timestamp = 0
  }, [])

  return {
    weather,
    alert: weather?.alert || null,
    isLoading,
    error,
    locationSource,
    refresh: () => loadWeather(true),
    setManualLocation,
  }
}

export type { WeatherData, WeatherAlert }
